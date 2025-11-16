# G5 — Operator Scenario

## Fonte de teste
- **ID:** `api_teste_operador`
- **Tipo:** `api`
- **Fixture sugerido:** `fixtures/s5/api_feed.json`
- **Configuração mínima:**
  - `url`: `fixtures/s5/api_feed.json`
  - `frequency`: `PT30M`
  - `timeout`: `5`
  - `parse_spec.fixture`: `api_feed.json`
  - `enabled`: `true`

## Passos propostos
1. **Abrir UI Admin**
   - Rodar `python -m inspectah.ui.admin_sources` a partir da raiz do projeto.
   - Listar fontes existentes e, se necessário, adicionar/editar `api_teste_operador` com os campos acima.
   - Confirmar que `enabled = true` e salvar (opção "Salvar e sair").
2. **Executar ingestão/pipeline**
   - Rodar `python -m inspectah.pipeline.pipeline_fixtures` (ou o comando equivalente `bin/s5_gate_g3_pipeline_fixtures.sh`) para gerar itens S3/S4 usando os fixtures.
   - Verificar no console que o summary indica `items_total > 0`.
3. **Abrir UI Explore**
   - Rodar `python -m inspectah.ui.explore`.
   - Selecionar a fonte `api_teste_operador`.
   - (Opcional) Informar um `equivalence_key` específico mostrado na lista.
   - Listar os itens e escolher um para abrir o detalhe.
4. **Validar detalhe do item**
   - Confirmar que os campos principais (source_id, item_id, state, equivalence_key, headline, published_at) aparecem na tela.
   - Verificar o `bundle_path` e, se desejar, abrir o arquivo `text.txt` para ler a evidência completa.
   - Conferir os claims estruturados retornados pelo normalizer.
5. **Registrar feedback**
   - Abrir `out/s5_gates/G5_operator_journey/report.md` e anotar:
     - Passos executados.
     - Tempo total gasto.
     - Problemas ou fricções encontradas.
