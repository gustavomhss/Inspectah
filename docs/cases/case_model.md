# Modelo de Caso Inspectah (Sprint 24)

Cada arquivo `docs/cases/case_<slug>.yaml` segue esta estrutura mínima para S24:

- `case_id`: identificador único e estável (slug).
- `title`: título legível do caso.
- `summary`: descrição curta em linguagem natural.
- `theme`: tema macro (ex.: economia, saúde, política).
- `tags`: lista de palavras-chave.
- `claims`: lista de claims relevantes, cada um com:
  - `claim_id`: ID de claim ou alvo no Truth-DB.
  - `description`: frase ou afirmação a ser acompanhada.
  - `truth_state`: estado atual esperado na verdade (quando disponível).
  - `debunk_target_id`: ID usado pelo Debunker v0 para abrir issues (default: mesmo que claim_id).
  - `tags`: etiquetas específicas do claim.
- `timeline`: eventos textuais ou referências para ajudar na narrativa.
- `sources`: links ou descritores de evidências principais.
- `metadata`: bloco livre para anotações editoriais (não usar TODO/WIP).

Nenhum caso canônico deve ser registrado sem arquivo YAML correspondente, e nenhuma demo deve depender de campos fora desse modelo sem explicitar no Cap.3/5.
