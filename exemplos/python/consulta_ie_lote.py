"""
FiscalAPI — Consulta de Inscricao Estadual em lote (todos os estados)
https://fiscalapi.com.br

Le uma lista de CPFs/CNPJs, consulta cada um em /api/consultar-ie-todos com
varias chamadas em paralelo, respeitando o limite por minuto da conta, e
grava os resultados em CSV.

Uso:
    pip install httpx
    export FISCALAPI_KEY="sua_chave"
    python consulta_ie_lote.py documentos.csv

documentos.csv: um CPF ou CNPJ por linha, na primeira coluna, com ou sem
mascara. Zeros a esquerda perdidos no Excel sao recolocados (CNPJ com 13
digitos, CPF com 10...), e o CNPJ alfanumerico e aceito. Linhas repetidas
sao ignoradas; documentos invalidos (digito verificador errado) sao
contados e listados no inicio da execucao.

Saida:
    resultado.csv    uma linha por IE encontrada; documento sem IE em nenhum
                     estado sai numa linha so, com os campos da IE vazios.
    incompletos.csv  documentos em que algum estado nao respondeu na hora
                     (coluna "completo" = False no resultado) ou que falharam.

Pode interromper (Ctrl+C) e rodar de novo: quem ja esta em resultado.csv e
pulado. Documentos que falharam por completo sao tentados de novo.

Opcoes:
    --paralelo N     chamadas simultaneas (padrao 16)
    --por-minuto N   teto de chamadas iniciadas por minuto (padrao 115; o
                     limite da conta aparece no header X-RateLimit-Limit)
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import re
import sys
import time

import httpx

BASE_URL = "https://api.fiscalapi.com.br"

CAMPOS_IE = [
    "uf_ie", "inscricao_estadual", "situacao_ie", "situacao_cadastral",
    "data_situacao", "razao_social", "nome_fantasia", "cpf_cnpj", "tipo_ie",
    "regime_apuracao_icms", "regime_pagamento", "situacao_contribuinte",
    "situacao_nfe", "data_inicio_atividade", "cnae_codigo", "cnae_descricao",
    "logradouro", "numero", "complemento", "bairro", "municipio",
    "municipio_ibge", "cep",
]
COLUNAS = ["documento", "tipo", "completo"] + CAMPOS_IE


class SemCredito(Exception):
    pass


def _dv_cnpj(base: str) -> str:
    """Digitos verificadores do CNPJ (numerico ou alfanumerico: cada
    caractere vale seu codigo ASCII - 48, como define a Receita)."""
    for pesos in ([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
                  [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]):
        resto = sum((ord(c) - 48) * p for c, p in zip(base, pesos)) % 11
        base += "0" if resto < 2 else str(11 - resto)
    return base[-2:]


def cnpj_valido(doc: str) -> bool:
    return (len(doc) == 14 and doc[:12].isalnum() and doc[12:].isdigit()
            and len(set(doc)) > 1 and _dv_cnpj(doc[:12]) == doc[12:])


def cpf_valido(doc: str) -> bool:
    if len(doc) != 11 or not doc.isdigit() or len(set(doc)) == 1:
        return False
    for n in (9, 10):
        soma = sum(int(doc[i]) * (n + 1 - i) for i in range(n))
        if (soma * 10 % 11) % 10 != int(doc[n]):
            return False
    return True


def normalizar(valor: str) -> str | None:
    """CPF/CNPJ com os zeros a esquerda de volta, ou None se invalido.

    Planilha salva no Excel perde o zero inicial (CNPJ 01.234.567/0001-89
    vira 1234567000189). O digito verificador decide se e CPF ou CNPJ."""
    bruto = re.sub(r"[^0-9A-Za-z]", "", valor).upper()
    if not bruto or len(bruto) > 14:
        return None
    if not bruto.isdigit():
        return bruto if cnpj_valido(bruto) else None
    cpf, cnpj = bruto.zfill(11), bruto.zfill(14)
    e_cpf = len(bruto) <= 11 and cpf_valido(cpf)
    e_cnpj = cnpj_valido(cnpj)
    if e_cpf and e_cnpj:
        # Os dois digitos batem (ex.: CNPJ 00.000.000/0001-91 vira "191"):
        # CPF perde no maximo 2 zeros; menos de 9 digitos e CNPJ.
        return cpf if len(bruto) >= 9 else cnpj
    return cpf if e_cpf else (cnpj if e_cnpj else None)


def ler_documentos(caminho: str) -> tuple[list[str], list[str]]:
    """(documentos validos sem repeticao, valores invalidos)."""
    docs, invalidos = [], []
    with open(caminho, newline="", encoding="utf-8-sig") as arquivo:
        for linha in csv.reader(arquivo):
            if not linha or not re.search(r"\d", linha[0]):
                continue  # linha vazia ou cabecalho
            doc = normalizar(linha[0])
            if doc:
                docs.append(doc)
            else:
                invalidos.append(linha[0].strip())
    return list(dict.fromkeys(docs)), invalidos


def ja_consultados(caminho: str) -> set[str]:
    if not os.path.exists(caminho):
        return set()
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        return {linha["documento"] for linha in csv.DictReader(arquivo)}


class Ritmo:
    """No maximo `por_minuto` chamadas iniciadas por minuto, espacadas."""

    def __init__(self, por_minuto: int):
        self.intervalo = 60.0 / por_minuto
        self.proxima = time.monotonic()
        self.trava = asyncio.Lock()

    async def aguardar(self) -> None:
        async with self.trava:
            espera = self.proxima - time.monotonic()
            if espera > 0:
                await asyncio.sleep(espera)
            self.proxima = max(self.proxima, time.monotonic()) + self.intervalo


async def consultar(cliente: httpx.AsyncClient, ritmo: Ritmo, doc: str):
    """Devolve (tipo, resposta, erro). Tenta de novo em falha de rede e 5xx;
    429 espera o Retry-After e segue sem contar como falha."""
    tipo = "cpf" if len(doc) == 11 else "cnpj"
    falhas = 0
    while True:
        await ritmo.aguardar()
        try:
            r = await cliente.get(f"{BASE_URL}/api/consultar-ie-todos",
                                  params={tipo: doc})
        except httpx.HTTPError as exc:
            erro = f"rede: {type(exc).__name__}"
        else:
            if r.status_code == 200:
                return tipo, r.json(), None
            if r.status_code == 429:
                await asyncio.sleep(float(r.headers.get("Retry-After") or 5))
                continue
            if r.status_code == 402:
                raise SemCredito(r.text[:300])
            erro = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code < 500:
                return tipo, None, erro  # parametro invalido: repetir nao resolve
        falhas += 1
        if falhas >= 3:
            return tipo, None, erro
        await asyncio.sleep(2 ** falhas)


def estados_sem_resposta(resposta: dict) -> list[str]:
    return [uf["uf"] for uf in resposta.get("results", [])
            if uf.get("source_status", {}).get("status") not in ("success", "skipped")]


async def processar(docs: list[str], cliente: httpx.AsyncClient, saida: str,
                    incompletos: str, paralelo: int, por_minuto: int) -> dict:
    novo_resultado = not os.path.exists(saida)
    novo_incompleto = not os.path.exists(incompletos)
    contagem = {"ok": 0, "incompletos": 0, "falhas": 0}
    fila = iter(docs)
    ritmo = Ritmo(por_minuto)
    inicio = time.monotonic()
    with open(saida, "a", newline="", encoding="utf-8") as fr, \
            open(incompletos, "a", newline="", encoding="utf-8") as fi:
        resultado = csv.DictWriter(fr, fieldnames=COLUNAS, extrasaction="ignore")
        pendente = csv.writer(fi)
        if novo_resultado:
            resultado.writeheader()
        if novo_incompleto:
            pendente.writerow(["documento", "motivo"])

        async def trabalhador():
            for doc in fila:
                tipo, resposta, erro = await consultar(cliente, ritmo, doc)
                if resposta is None:
                    pendente.writerow([doc, erro])
                    contagem["falhas"] += 1
                else:
                    completo = bool(resposta.get("complete", True))
                    ies = [ie for uf in resposta.get("results", [])
                           for ie in uf.get("results", [])]
                    for ie in ies or [{}]:
                        resultado.writerow({**ie, "documento": doc, "tipo": tipo,
                                            "completo": completo})
                    if completo:
                        contagem["ok"] += 1
                    else:
                        contagem["incompletos"] += 1
                        pendente.writerow(
                            [doc, "sem resposta: " + ",".join(estados_sem_resposta(resposta))])
                fr.flush()
                fi.flush()
                feitos = sum(contagem.values())
                if feitos % 100 == 0:
                    ritmo_min = feitos / max(time.monotonic() - inicio, 1) * 60
                    print(f"{feitos}/{len(docs)} ({ritmo_min:.0f}/min) {contagem}", flush=True)

        await asyncio.gather(*(trabalhador() for _ in range(paralelo)))
    return contagem


async def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta de IE em lote (FiscalAPI)")
    parser.add_argument("arquivo")
    parser.add_argument("--paralelo", type=int, default=16)
    parser.add_argument("--por-minuto", type=int, default=115)
    parser.add_argument("--saida", default="resultado.csv")
    parser.add_argument("--incompletos", default="incompletos.csv")
    args = parser.parse_args()

    chave = os.environ.get("FISCALAPI_KEY")
    if not chave:
        print("Defina a variavel FISCALAPI_KEY com a sua chave de API.", file=sys.stderr)
        return 2
    docs, invalidos = ler_documentos(args.arquivo)
    if invalidos:
        exemplos = ", ".join(invalidos[:5])
        print(f"{len(invalidos)} linhas ignoradas por documento invalido (ex.: {exemplos})", flush=True)
    feitos = ja_consultados(args.saida)
    fila = [d for d in docs if d not in feitos]
    print(f"{len(docs)} documentos, {len(feitos)} ja consultados, {len(fila)} na fila", flush=True)

    async with httpx.AsyncClient(headers={"X-API-Key": chave}, timeout=120) as cliente:
        try:
            contagem = await processar(fila, cliente, args.saida, args.incompletos,
                                       args.paralelo, args.por_minuto)
        except SemCredito as exc:
            print(f"Creditos esgotados, parei aqui: {exc}", file=sys.stderr)
            return 1
    print(f"Fim: {contagem}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
