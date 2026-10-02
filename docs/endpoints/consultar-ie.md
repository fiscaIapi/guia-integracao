# Consultar Inscricao Estadual

Consulta a inscricao estadual de um produtor rural na SEFAZ de um estado especifico.

**Endpoint:** `GET /api/consultar`

## Parametros

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| `uf` | string | Sim | Sigla do estado (ex: MT, SP, GO) |
| `cpf` | string | Um dos tres | CPF do produtor |
| `cnpj` | string | Um dos tres | CNPJ da empresa |
| `ie` | string | Um dos tres | Inscricao Estadual direta |

> Informe **apenas um** documento: `cpf`, `cnpj` ou `ie`.

## Exemplo de Requisicao

```bash
curl -X GET "https://api.fiscalapi.com.br/api/consultar?uf=MT&cpf=12345678900" \
  -H "X-API-Key: sua_api_key_aqui"
```

## Exemplo de Resposta

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
      "nome_fantasia": "FAZENDA SANTA MARIA",
      "situacao_ie": "ATIVA",
      "uf_ie": "MT",
      "tipo_ie": "PRODUTOR RURAL",
      "logradouro": "ROD MT-130 KM 42",
      "complemento": "ZONA RURAL",
      "bairro": "ZONA RURAL",
      "numero": "S/N",
      "municipio": "RONDONOPOLIS",
      "cep": "78700-000",
      "regime_pagamento": "NORMAL",
      "data_situacao": "15/03/2020",
      "situacao_contribuinte": "ATIVO",
      "data_inicio_atividade": "01/06/2015",
      "cnae_codigo": "0111-3/01",
      "cnae_descricao": "CULTIVO DE ARROZ",
      "regime_apuracao_icms": "NORMAL",
      "situacao_nfe": "HABILITADO",
      "cpf_cnpj": "123.456.789-00",
      "situacao_cadastral": "ATIVA"
    }
  ]
}
```

## Campos da Resposta

| Campo | Descricao |
|-------|-----------|
| `request_id` | ID unico da requisicao para rastreamento |
| `document` | Documento enviado na consulta |
| `document_type` | Tipo do documento: `cpf`, `cnpj` ou `ie` |
| `uf` | Estado consultado |
| `cached` | `true` se o resultado veio do cache |
| `results` | Lista de inscricoes estaduais encontradas |

### Campos de cada resultado (IEResult)

| Campo | Descricao |
|-------|-----------|
| `inscricao_estadual` | Numero da IE |
| `razao_social` | Nome/razao social do contribuinte |
| `nome_fantasia` | Nome fantasia |
| `situacao_ie` | Situacao da IE (ATIVA, SUSPENSA, CANCELADA, etc.) |
| `uf_ie` | UF da inscricao |
| `tipo_ie` | Tipo (PRODUTOR RURAL, NORMAL, etc.) |
| `municipio` | Municipio do contribuinte |
| `cnae_codigo` | Codigo CNAE da atividade |
| `cnae_descricao` | Descricao da atividade economica |
| `regime_apuracao_icms` | Regime de apuracao ICMS |
| `situacao_nfe` | Habilitacao para emissao de NF-e |
| `situacao_cadastral` | Situacao cadastral geral |

## Erros

| HTTP | Codigo | Descricao |
|------|--------|-----------|
| 400 | `UF_NAO_SUPORTADA` | UF informada nao e suportada |
| 400 | `PARAMETRO_AUSENTE` | Nenhum documento informado |
| 400 | `PARAMETRO_CONFLITANTE` | Mais de um documento informado |
| 400 | `DOCUMENTO_INVALIDO` | CPF, CNPJ ou IE com formato invalido |
| 402 | `LIMITE_ATINGIDO` | Creditos do mes esgotados |
| 429 | `RATE_LIMIT_EXCEEDED` | Limite de requisicoes por minuto do plano excedido |
| 502 | `CAPTCHA_FALHOU` | Falha na resolucao do CAPTCHA da SEFAZ |
| 503 | `SITE_INDISPONIVEL` | Portal da SEFAZ fora do ar |

## UFs Suportadas

A lista de UFs suportadas cresce constantemente. Para verificar as UFs disponiveis em tempo real, envie uma UF invalida e a mensagem de erro listara todas as opcoes.
