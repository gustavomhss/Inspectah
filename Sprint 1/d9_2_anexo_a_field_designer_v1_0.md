# D9.2 — Anexo A: Field Designer (v1.0)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

## 1. Papel do Field Designer
O Field Designer é o **contrato declarativo** que explica como um payload bruto vira campos estruturados no Inspectah. Ele é usado em três momentos:
1. **Cadastro/edição**: Operators definem campos, tipos, transforms e computed fields diretamente no painel/CLI.
2. **Execução do pipeline**: o motor de ingestão interpreta a definição e aplica as regras de forma determinística.
3. **Auditoria**: Evidence Vault guarda a versão da definição aplicada a cada item, permitindo reproduzir resultados.

## 2. Escopo do v0
- Definir campos usando YAML/JSON declarativo armazenado na tabela `field_definition` (vide D9.4).
- Reutilizar transforms out-of-the-box; não há sandbox para código arbitrário.
- Computed fields usam linguagem de expressões restrita (descrito na seção 7).
- Versionamento explícito com `version` inteiro e `status` (`draft`, `active`, `deprecated`).

## 3. Estrutura de Definição
```yaml
version: 3
source_id: price_delivery_br
fields:
  - id: price
    type: number
    required: true
    description: Preço em BRL
    transforms:
      - parse_number(locale: "pt_BR")
      - clamp(min: 0, max: 500)
  - id: collected_at
    type: timestamp
    required: true
    transforms:
      - parse_date(format: "YYYY-MM-DDTHH:mm:ssZ")
  - id: city
    type: enum
    enum_values: ["sp", "rj", "poa"]
    required: true
  - id: price_delta
    type: number
    computed:
      expression: price - lag(price, window: 1)
      fallback: 0
```

## 4. Tipos de Campo Suportados
| Tipo | Descrição | Metadados obrigatórios | Observações |
|------|-----------|------------------------|-------------|
| `text` | String UTF-8 até 4 KB | `normalizer` opcional (`lowercase`, `strip_tags`) | Armazena em `item_kv` como TEXT |
| `longtext` | String até 64 KB | idem | Usado para resumos; não indexado por padrão |
| `number` | Decimal com precisão configurável | `precision`, `scale`, `unit` opcional | Persistido como NUMERIC |
| `integer` | Inteiro 64 bits | — | Validado contra limites `min`/`max` |
| `bool` | Booleano | — | Aceita `true/false`, `1/0`, `yes/no` |
| `timestamp` | Data-hora UTC | `timezone_hint` opcional | Sempre convertido para UTC ISO8601 |
| `date` | Data sem hora | — | Armazena `DATE` |
| `enum` | Valor discreto | `enum_values` obrigatório | Validado na ingestão; mismatch cai para fallback |
| `json` | Blob JSON validado | `schema_ref` opcional | Armazenado como JSONB (Postgres) |
| `geo_point` | Ponto geográfico | `format` (`lat_lon`, `WKT`) | Indexável em extensões futuras |

## 5. Atributos Comuns
- `required`: `true/false`. Falhas geram erro de item (ver seção 8).
- `description`: texto usado em Explore e documentação.
- `pii`: flag booleana para marcar dado pessoal (alinha com D9.5).
- `source_path`: JSONPath ou XPath indicando onde o valor bruto é encontrado.
- `transform_profile`: alias para conjunto padrão de transforms.

## 6. Catálogo de Transforms
### 6.1 Transforms básicos
| Nome | Entradas | Saída | Comportamento de erro |
|------|----------|-------|-----------------------|
| `parse_number(locale)` | string | number | Registra erro `FD_NUM_INVALID`; aplica fallback se definido |
| `parse_date(format)` | string | timestamp/date | Erro `FD_DATE_INVALID`; se `optional` então retorna `null` |
| `regex_extract(pattern, group)` | string | string | Erro `FD_REGEX_NO_MATCH` | 
| `split_pick(delimiter, index)` | string | string | Retorna `null` se índice inexistente |
| `map_table(table_name)` | string | string/enum | Usa tabela de correspondência mantida no config store |
| `math_scale(factor)` | number | number | Aplica multiplicação, default 1 |
| `round(decimals)` | number | number | Usa `HALF_UP` |
| `bool_cast()` | string/number | bool | Converte `"yes"`, `1` etc. |

### 6.2 Transforms compostos
- `pipeline`: lista ordenada de transforms; falha se qualquer etapa obrigatória falhar.
- `branch_if(condition)` permite caminhos diferentes sem abrir mão da determinismo (sem loops).
- `redact(pattern)` substitui trechos sensíveis por máscara antes de persistir.

### 6.3 Transforms reservados
- `snapshot_url`: gera link para snapshot no Evidence Vault.
- `hash_raw(algorithm)` retorna hash do valor bruto para auditoria.

## 7. Computed Fields

### 7.1 Linguagem e Sintaxe
- Computed fields usam a **Inspectah Expression Language (IEL)**, um subconjunto determinístico do JSONata.
- Sintaxe infix com operadores aritméticos `+ - * / %`, relacionais `= != < <= > >=` e booleanos `and`, `or`, `not`.
- Funções permitidas:
  - Numéricas: `min()`, `max()`, `abs()`, `round(decimals)`, `clamp(min,max)`.
  - Texto: `concat()`, `length()`, `substr()`, `lower()`, `upper()`.
  - Datas: `to_timestamp(value, format)`, `date_diff(unit, a, b)`.
  - Utilidades: `coalesce()`, `if(condition, when_true, when_false)`.
  - Janelas: `lag(field_id, window=1)`, `lead(field_id, window=1)` (máx. window 5).

### 7.2 Escopo e Dependências
- Computed fields só podem ler:
  - Campos primários do **mesmo item_version** já validados;
  - Resultados de computed fields declarados anteriormente no mesmo documento (o Field Designer valida DAG acíclica);
  - Janelas `lag/lead` do mesmo `item_key` (nenhum acesso cross-source ou cross-field arbitrário).
- É proibido acessar coleções externas, executar consultas adicionais ou referenciar fontes com `pii=true` que estejam mascaradas.

### 7.3 Regras de Pureza e Segurança
- IEL não possui loops livres, atribuições ou mutações; toda expressão é funcional.
- Proibido qualquer tipo de I/O (HTTP, filesystem, rede), geração de random, uso de tempo atual ou side effects.
- Computed fields que manipulem campos marcados `pii=true` só podem produzir saídas igualmente marcadas ou mascaradas.
- Violação das regras acima causa falha de validação em `fd_validate` e bloqueia publicação da versão.

### 7.4 Avaliação e Fallback
- Avaliação ocorre após transforms básicos: campos primários → computed independentes → computed dependentes.
- Toda expressão precisa definir `fallback`: valor literal, `null` ou função simples, usado quando:
  - A expressão lança erro (ex.: divisão por zero);
  - Dependência ausente (`lag` sem histórico).
- Erros são registrados com código `FD_COMPUTED_ERROR` e contam na métrica `fields_invalid`; item permanece válido se fallback existir.

### 7.5 Exemplo completo
```yaml
- id: price_delta_pct
  type: number
  description: Variação percentual em relação ao último registro do mesmo item_key
  computed:
    expression: ((price - lag("price", window: 1)) / lag("price", window: 1)) * 100
    fallback: 0
    precision: 6
    scale: 2
```
- Neste exemplo:
  - `lag("price", window: 1)` busca o último valor do campo `price` do mesmo item.
  - Caso não exista histórico ou o valor seja zero, a expressão falha e o fallback `0` é aplicado.
  - Como o campo original `price` não é `pii`, `price_delta_pct` também permanece não-PII.


## 8. Tratamento de Erros
| Tipo de erro | Ação padrão | Configurável? |
|--------------|-------------|---------------|
| Campo obrigatório sem valor | Item marcado como `failed`; log + alerta | Pode ser `skip_field` mediante justificativa |
| Transform falha | Marca campo como `invalid`, aplica fallback se existir | `error_policy` por campo |
| Computed field falha | Campo recebe fallback; item segue válido | — |
| Validação enum falha | Campo recebe `null`, item continua mas gera aviso | — |
| Violação LGPD flag (`pii` sem consentimento) | Item bloqueado antes de persistir | Não |

Além de logs, cada execução gera métricas: `fields_total`, `fields_invalid`, `fields_redacted`.

## 9. Versionamento e Publicação
1. Draft criado → validado automaticamente (lint de schema + testes com amostras).
2. Revisão dupla (Operator + guardião LGPD quando houver `pii:true`).
3. Publicação muda `status` para `active` e incrementa `version` global.
4. Pipelines referenciam Field Designer por `version`; upgrade pode ser `rolling` (fonte a fonte) ou `instantâneo`.
5. Versões `deprecated` permanecem disponíveis para reprocessamentos históricos.

## 10. Observabilidade e Evidências
- Cada pipeline registra `field_version` no manifest.
- Métricas por campo: percentil de preenchimento, quantidade de redactions, top erros.
- Diff automático entre versões exibe alterações em tipos/transforms antes de publish.

## 11. Exemplos Práticos
### 11.1 Fonte RSS de notícias econômicas
- Campos: `title (text)`, `published_at (timestamp)`, `category (enum)`, `impact_score (integer computed via map_table + weight)`, `excerpt (longtext redacted)`.
- Transforms: `strip_html`, `regex_extract`, `parse_date`.

### 11.2 API JSON de preços médios
- Campos: `city (enum)`, `average_price (number)`, `currency (enum)`, `window_start/end (date)`, `price_delta (computed)`, `source_manifest (json)`.
- Computed: `price_delta = average_price - lag(average_price)`.

### 11.3 HTML oficial de regulamentos
- Campos: `doc_version (text)`, `effective_date (date)`, `body_hash (text via hash_raw)`, `diff_summary (text computed via diff engine externo e feed manual)`, `robots_ok (bool)`.
- Snapshot obrigatório, com `redact` aplicado para dados pessoais.

## 12. Processo de Revisão e Checklist
1. Operator propõe mudança e inclui amostras (`sample_payloads`).
2. Guardião LGPD valida flags `pii` e referências a D9.5.
3. Revisor técnico executa `fd_validate` (script) que roda transforms sobre amostras.
4. Uma vez aprovado, checklist D9-G2 é atualizado e referência vai para `d9_summary_gate_matrix.json`.

O Field Designer, definido por este anexo, garante que qualquer ingestão do Inspectah seja previsível, auditável e compatível com os princípios de segurança e governança estabelecidos nos Capítulos 1–3.
