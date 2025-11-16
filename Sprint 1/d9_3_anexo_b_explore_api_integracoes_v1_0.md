# D9.3 — Anexo B: Explore API & Superfícies de Integração (v1.0)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

## 1. Princípios
- API **read-mostly**, stateless, autenticada via token Bearer ou chave assinatura + HMAC (para webhooks).
- Todas as respostas em JSON UTF-8; exportações suportam CSV e JSON lines.
- Versionamento por header `X-Inspectah-Version: v0`. Mudanças breaking exigem nova versão (vide D9.8).
- Paginação cursor-based para coleções; limite padrão 200 itens por página, máximo 1000.

## 2. Autenticação e Autorização
| Cenário | Mecanismo |
|---------|-----------|
| Explore API | `Authorization: Bearer <token>` emitido para squads/serviços. Escopos: `items:read`, `sources:read`, `exports:create`, `webhooks:manage`.
| Export jobs | Mesma chave Bearer; responses assinadas com checksum SHA256.
| Webhooks | Secret compartilhado. Payload inclui `X-Inspectah-Signature: sha256=<HMAC>`.

Tokens são emitidos pelo módulo IAM interno; não há self-service público no v0.

## 3. Endpoints Principais
### 3.1 GET `/sources`
- **Filtros**: `status` (`active`, `paused`), `tag`, `requires_snapshot` (`true/false`).
- **Resposta**:
```json
{
  "data": [
    {
      "id": "price_delivery_br",
      "name": "Preço Delivery Brasil",
      "status": "active",
      "schedule": "0 */2 * * *",
      "last_run_status": "success",
      "last_run_at": "2025-05-12T14:02:00Z",
      "lgpd_profile": {"pii": false, "robots_ok": true},
      "field_version": 3
    }
  ],
  "next_cursor": "eyJpZCI6InByaWNlIn0="
}
```

### 3.2 GET `/items`
- **Parâmetros de query**:
  - `source_id` (obrigatório para paginação eficiente).
  - `tag`, `field[price][gte]`, `field[city]=sp`, `collected_at[gte]`, `collected_at[lte]`.
  - `sort` (default `collected_at:desc`).
  - `cursor` (token opaco).
- **Resposta**: lista de itens com campos normalizados + manifest mínimo.
```json
{
  "data": [
    {
      "id": "itm_01h9z...",
      "source_id": "price_delivery_br",
      "collected_at": "2025-05-12T14:02:10Z",
      "fields": {
        "city": "sp",
        "average_price": 38.55,
        "currency": "BRL",
        "price_delta": -0.35
      },
      "manifest": {
        "field_version": 3,
        "hash": "sha256:...",
        "snapshot_available": true
      }
    }
  ],
  "next_cursor": null,
  "meta": {
    "count": 1,
    "source_status": "success"
  }
}
```

### 3.3 GET `/items/{id}`
- Retorna item completo + histórico de versões.
- Pode incluir `include=snapshot` para gerar URL pré-assinada (expira em 15 min) quando permitido por LGPD/ToS.

### 3.4 GET `/items/{id}/diff`
- Compara duas versões; parâmetros `from`, `to` (IDs de versões). Retorna campos alterados e resumo textual.

### 3.5 GET `/stats/sources/{id}`
- Entrega métricas (execuções, falhas, itens/dia, campos inválidos) para auxiliar operadores.

### 3.6 POST `/exports`
- Cria job de export. Payload:
```json
{
  "format": "csv",
  "filters": {
    "source_id": "price_delivery_br",
    "collected_at": {"gte": "2025-05-01"}
  },
  "fields": ["city","average_price","currency","manifest.hash"],
  "notification": {
    "type": "webhook",
    "endpoint": "https://mbp.internal/hooks/inspectah",
    "secret": "***"
  }
}
```
- Resposta contém `export_id`, `status`, `estimated_rows`.
- Resultados ficam disponíveis via GET `/exports/{id}` (signed URL para arquivo). Limite 1 GB por job.

## 4. Webhooks
| Evento | Descrição | Payload |
|--------|-----------|---------|
| `item.created` | Novo item disponível pós-pipeline | `item_id`, `source_id`, `collected_at`, `highlight_fields`, `manifest.hash` |
| `item.updated` | Novo snapshot do mesmo item lógico | inclui `diff_summary` |
| `source.error` | Falha em execução | `source_id`, `error_code`, `run_id`, `next_retry_at` |
| `lgpd.alert` | Deteção de dado pessoal fora de política | `source_id`, `item_id`, `flag`, `action_taken` |

Todos os webhooks trazem `attempt`, `timestamp`, `signature`. Reentregas com backoff exponencial (máx. 10 tentativas). Consumidor deve responder 2xx; qualquer outro status gera retry.

## 5. Views e BI interno
- Banco expõe `view_inspectah_items_latest` (um registro por item lógico) e `view_inspectah_items_history` (todas as versões) para ferramentas de BI internas (Metabase/Looker). Acesso read-only.
- Views adicionam colunas `pii_masked` para evitar vazamento; queries que pedirem campos `pii=true` exigem credencial especial.

## 6. Fluxos de Integração
### 6.1 MBP Consumindo Inspectah
1. Webhook `item.created` dispara job no MBP para atualizar indicadores de probabilidade.
2. MBP chama `/items/{id}` para obter manifest e snapshot.
3. Manifest ID é gravado no registro da resolução, permitindo auditoria cruzada.

### 6.2 Scripts internos
- Podem usar `/exports` para gerar CSVs diários com mudanças relevantes.
- Recomendado agendar exports fora do horário crítico para evitar atingir limite simultâneo (máx. 3 exports ativos por token).

### 6.3 Outros oráculos / parceiros
- Recebem acesso segregado a fontes específicas (scopes limitados). Webhooks opcionais.
- Sempre sujeitos a D9.5: sem repasse de dados proibidos.

## 7. Erros e Rate Limiting
- Formato padrão:
```json
{
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "Item itm_... não existe ou não pertence ao token.",
    "reference": "run_01hk..."
  }
}
```
- Códigos comuns: `INVALID_FILTER`, `RATE_LIMITED`, `SOURCE_PAUSED`, `UNAUTHORIZED_SCOPE`, `EXPORT_TOO_LARGE`.
- Rate limit v0: **120 requests/min por token**, com burst de 240 em janelas de 1 min. Cabeçalhos retornados:
  - `X-RateLimit-Limit: 120`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`
  - `X-RateLimit-Policy: v0-default`
- Clientes que excederem o limite recebem `429 RATE_LIMITED` com campo `retry_after` (segundos). Recomenda-se backoff exponencial e cache local.
- Este limite foi definido para o dataset alvo (≤ 1M itens). Há uma ação registrada (D9-API-001) para executar teste de carga pós-implantação; qualquer ajuste futuro seguirá o playbook de evolução (D9.8) e será comunicado com no mínimo 14 dias de antecedência.

## 8. Segurança e Compliance
- Logs de acesso retidos por 180 dias.
- Campos marcados como `pii` nunca retornam por padrão; consumidor precisa solicitar `include_pii=true` e ter escopo.
- Export files criptografados em repouso, com chave rotate a cada 90 dias.
- Webhooks somente HTTPS; certificados verificados.

## 9. Observabilidade e Evidências
- Cada chamada REST gera entry no `api_audit_log` com `token_id`, `scope`, filtros aplicados e contagem de registros retornados.
- Exports registram `estimated_rows` vs `delivered_rows` e link para manifest do job.
- Webhooks possuem tabela `webhook_delivery` para acompanhar tentativas e respostas.

## 10. Checklist de Implantação
1. Configurar tokens e escopos por squad.
2. Validar lista de fontes visíveis para cada token (multitenancy leve).
3. Registrar endpoints de webhook + secrets.
4. Testar export com dataset pequeno e validar assinaturas.
5. Preencher checklist D9-G3 e atualizar `d9_summary_gate_matrix.json`.

Este anexo garante que consumidores saibam exatamente como interagir com o Inspectah, evitando contratos implícitos e permitindo implementação consistente do Explore API e das integrações associadas.
