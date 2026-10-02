# Tratamento de Erros

Todos os erros da FiscalAPI seguem o mesmo formato JSON:

```json
{
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "error": "CODIGO_DO_ERRO",
  "message": "Descricao legivel do erro"
}
```

## Codigos de Erro

### Autenticacao (HTTP 403)

| Codigo | Descricao |
|--------|-----------|
| `API_KEY_ERROR` | API key ausente, invalida ou revogada |
| `ACESSO_NEGADO` | Chave demo tentando acessar endpoint restrito |

### Parametros (HTTP 400)

| Codigo | Descricao |
|--------|-----------|
| `UF_NAO_SUPORTADA` | UF informada nao e suportada |
| `PARAMETRO_AUSENTE` | Documento obrigatorio nao informado |
| `PARAMETRO_CONFLITANTE` | Mais de um documento informado |
| `DOCUMENTO_INVALIDO` | CPF, CNPJ ou IE com formato invalido |
| `IE_NAO_SUPORTADO` | IE nao aceito neste endpoint (use CPF ou CNPJ) |

### Creditos (HTTP 402)

| Codigo | Descricao |
|--------|-----------|
| `LIMITE_ATINGIDO` | Creditos do mes esgotados. A resposta traz `usage`, `limit`, `extra_credits` e o `cost` da consulta |

### Rate Limiting (HTTP 429)

| Codigo | Descricao |
|--------|-----------|
| `RATE_LIMIT_EXCEEDED` | Limite de requisicoes por minuto do plano excedido (Lite 5, Starter 20, Pro 60, Enterprise 120). Veja o header `Retry-After` |

### Fontes Externas (HTTP 502/503)

| Codigo | Descricao |
|--------|-----------|
| `CAPTCHA_FALHOU` | Falha na resolucao do CAPTCHA da SEFAZ |
| `SITE_INDISPONIVEL` | Portal da SEFAZ temporariamente fora do ar |
| `TODAS_FONTES_FALHARAM` | Nenhuma fonte de dados respondeu |

### Interno (HTTP 500)

| Codigo | Descricao |
|--------|-----------|
| `ERRO_INTERNO` | Erro inesperado no servidor |

## Boas Praticas

1. **Sempre verifique o `request_id`** — use-o para suporte e rastreamento
2. **Trate erros 502/503 com retry** — portais SEFAZ sao intermitentes
3. **Respeite o rate limit** — implemente backoff exponencial no 429
4. **Erros 400 sao definitivos** — nao faca retry, corrija o parametro

### Exemplo de Retry (Python)

```python
import time
import requests

def consultar_com_retry(url, headers, params, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers, params=params, timeout=90)

        if response.status_code == 429:
            wait = 2 ** attempt
            time.sleep(wait)
            continue

        if response.status_code in (502, 503):
            wait = 5 * (attempt + 1)
            time.sleep(wait)
            continue

        return response

    return response  # ultima tentativa
```
