# FiscalAPI — API de Consulta Fiscal para o Brasil

[![Site](https://img.shields.io/badge/site-fiscalapi.com.br-blue)](https://fiscalapi.com.br)
[![Docs](https://img.shields.io/badge/docs-docs.fiscalapi.com.br-green)](https://docs.fiscalapi.com.br)
[![Status](https://img.shields.io/badge/status-production-brightgreen)]()

**API REST para consulta automatizada de Inscricao Estadual, CNPJ, CND Estadual e imoveis rurais (CNIR/CAFIR) em todos os 27 estados brasileiros.**

Ideal para ERPs, plataformas de emissao de NF-e, sistemas contabeis, agritechs e qualquer aplicacao que precise validar dados fiscais de produtores rurais.

---

## Por que usar a FiscalAPI?

| Problema | Solucao FiscalAPI |
|----------|-------------------|
| Cada SEFAZ tem um portal diferente | Uma unica API padronizada para todos os estados |
| Portais exigem CAPTCHA e certificado digital | Resolvemos CAPTCHA e autenticacao automaticamente |
| Consulta manual, uma UF por vez | Consulta simultanea em todos os 27 estados |
| Dados fragmentados entre Receita, SEFAZ e CNIR | Perfil consolidado do produtor em uma chamada |

## Endpoints Disponiveis

| Endpoint | Descricao | Docs |
|----------|-----------|------|
| `GET /api/consultar` | Consulta IE por UF (CPF, CNPJ ou IE) | [Ver docs](docs/endpoints/consultar-ie.md) |
| `GET /api/consultar-ie-todos` | Consulta IE em todos os estados | [Ver docs](docs/endpoints/consultar-ie-todos.md) |
| `GET /api/consultar-cnpj` | Consulta CNPJ na Receita Federal | [Ver docs](docs/endpoints/consultar-cnpj.md) |
| `GET /api/perfil-produtor` | Perfil completo do produtor rural | [Ver docs](docs/endpoints/perfil-produtor.md) |
| `GET /api/consultar-cnd` | CND Estadual (ICMS) por UF | [Ver docs](docs/endpoints/consultar-cnd.md) |
| `GET /api/consultar-cnd-todos` | CND em todos os estados | [Ver docs](docs/endpoints/consultar-cnd-todos.md) |
| `GET /api/consultar-cnd-federal` | CND Federal (Receita Federal + PGFN) | [docs.fiscalapi.com.br](https://docs.fiscalapi.com.br) |
| `GET /api/consultar-cndt` | CNDT trabalhista (TST) | [docs.fiscalapi.com.br](https://docs.fiscalapi.com.br) |
| `GET /api/consultar-crf-fgts` | CRF/FGTS (Caixa) | [docs.fiscalapi.com.br](https://docs.fiscalapi.com.br) |
| `GET /api/certidoes-todas` | Todas as certidoes (estaduais + federais) de uma vez | [docs.fiscalapi.com.br](https://docs.fiscalapi.com.br) |
| `GET /api/consultar-cnir` | Imoveis rurais CNIR/CAFIR | [Ver docs](docs/endpoints/consultar-cnir.md) |
| `GET /api/consultar-sigef` | Parcelas SIGEF (INCRA) | [docs.fiscalapi.com.br](https://docs.fiscalapi.com.br) |
| `POST /api/consultar-nfe-xml` | XML completo (nfeProc) da NF-e pela chave de acesso, com o seu certificado A1 | [Ver pagina](https://fiscalapi.com.br/nfe-por-chave/) |

## Inicio Rapido

### 1. Obtenha sua API Key

Crie uma conta em [app.fiscalapi.com.br](https://app.fiscalapi.com.br), assine um plano (a API comeca no Lite, R$ 19,99/mes) e gere a chave em **Chave API** no painel. As 10 consultas gratis por mes da conta valem so no painel, sem API.

### 2. Faca sua primeira consulta

```bash
curl -X GET "https://api.fiscalapi.com.br/api/consultar?uf=MT&cpf=12345678900" \
  -H "X-API-Key: sua_api_key_aqui"
```

### 3. Receba os dados estruturados

```json
{
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "document": "12345678900",
  "document_type": "cpf",
  "uf": "MT",
  "cached": false,
  "results": [
    {
      "inscricao_estadual": "13.123.456-7",
      "razao_social": "JOAO DA SILVA FAZENDA SANTA MARIA",
      "situacao_ie": "ATIVA",
      "tipo_ie": "PRODUTOR RURAL",
      "municipio": "RONDONOPOLIS",
      "cnae_codigo": "0111-3/01",
      "cnae_descricao": "CULTIVO DE ARROZ",
      "situacao_cadastral": "ATIVA",
      "regime_apuracao_icms": "NORMAL",
      "situacao_nfe": "HABILITADO"
    }
  ]
}
```

## Exemplos por Linguagem

| Linguagem | Exemplo |
|-----------|---------|
| Python | [exemplos/python/](exemplos/python/) |
| JavaScript/Node.js | [exemplos/javascript/](exemplos/javascript/) |
| PHP | [exemplos/php/](exemplos/php/) |
| Java | [exemplos/java/](exemplos/java/) |
| C# / .NET | [exemplos/csharp/](exemplos/csharp/) |
| Ruby | [exemplos/ruby/](exemplos/ruby/) |
| cURL | [exemplos/curl/](exemplos/curl/) |

**Consulta em lote:** [exemplos/python/consulta_ie_lote.py](exemplos/python/consulta_ie_lote.py) consulta a IE de milhares de CPFs e CNPJs em todos os estados, em paralelo e dentro do limite por minuto da conta, salvando o resultado em CSV.

## Autenticacao

Todas as requisicoes exigem a header `X-API-Key`:

```
X-API-Key: sua_api_key_aqui
```

Detalhes completos em [docs/autenticacao.md](docs/autenticacao.md).

## Casos de Uso

- **Emissao de NF-e**: Validar IE do destinatario antes de emitir nota fiscal
- **Onboarding de fornecedores**: Verificar situacao cadastral de produtores rurais
- **Compliance fiscal**: Consultar CND estadual para due diligence
- **Agritech**: Enriquecer cadastro de produtores com dados de todos os estados
- **ERP/Contabilidade**: Automatizar consultas que hoje sao feitas manualmente nos portais SEFAZ
- **Credito rural**: Consultar imoveis rurais no CNIR/CAFIR para analise de credito

## Limites e Planos

| Plano | Preco | Creditos/mes | Requisicoes/min | Acesso |
|-------|-------|--------------|-----------------|--------|
| **Gratis** | R$ 0 | 10 consultas | — | So no painel: IE (uma UF por vez) e CNPJ. Sem API |
| **Lite** | R$ 19,99/mes | 30 | 5 | Painel + API |
| **Starter** | R$ 50/mes | 500 | 20 | Painel + API |
| **Pro** | R$ 130/mes | 2.000 | 60 | Painel + API |
| **Enterprise** | R$ 250/mes | 10.000 | 120 | Painel + API |

- A maioria das consultas consome 1 credito; NF-e por chave consome 3 (so quando o XML vem) e CNPJ ao vivo consome 3.
- Consulta com erro da fonte nao cobra.
- Creditos extras a partir do Starter: R$ 0,12 (Starter), R$ 0,07 (Pro) e R$ 0,02 (Enterprise) por credito. No Lite, o caminho e o upgrade.
- Quando os creditos acabam, a API responde `402` com o codigo `LIMITE_ATINGIDO`.

Tabela completa em [fiscalapi.com.br/precos](https://fiscalapi.com.br/precos/).

## Links

- **Site**: [fiscalapi.com.br](https://fiscalapi.com.br)
- **Documentacao completa**: [docs.fiscalapi.com.br](https://docs.fiscalapi.com.br)
- **Dashboard**: [app.fiscalapi.com.br](https://app.fiscalapi.com.br)
- **Contato**: contato@fiscalapi.com.br

## Contribuicoes

Encontrou um erro na documentacao? Quer adicionar um exemplo em outra linguagem? Contribuicoes sao bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licenca

Este repositorio de documentacao e exemplos e licenciado sob [MIT](LICENSE).

---

Feito com dedicacao no Brasil para simplificar a burocracia fiscal.
