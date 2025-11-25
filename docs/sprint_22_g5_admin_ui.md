# Sprint 22 — G5 UI de Admin para Ingestão

## 1. Objetivo
Permitir que operador humano visualize e opere ingestão 2.0 sem acesso de dev: status por fonte, histórico de runs, detalhe e acionamento manual.

## 2. Fluxos mínimos
- **F1 — Listar fontes com status de ingestão**: tabela com colunas `Fonte`, `Modo`, `Enabled`, `Última ingestão (timestamp + estado + duração)`, ação “Ver detalhes”.
- **F2 — Detalhe da fonte**: exibe resumo da config, gráfico/linha do tempo recente, tabela paginada de runs com estados e links para evidência.
- **F3 — Acionar ingestão manual**: botão na página de detalhe que chama `POST /admin/ingestion/{source_id}/run`, mostra feedback imediato e atualiza histórico.
- **F4 — Alternar modo**: controle de toggle MANUAL_ONLY/AUTOMATIC + enabled/disabled, com avisos se fonte estiver em estado incompatível.

## 3. Requisitos de UX
- Responder “modo, ligado/desligado, última ingestão, estado” em ≤ 3 cliques.
- Erros legíveis: mensagem humanizada usando códigos de erro do serviço.
- Breadcrumbs/links claros para voltar à lista e abrir run específico.

## 4. Evidências
- Capturas de tela dos fluxos F1–F4 salvas em `out/evidence/S22_G5_admin_ui/`.
- Checklist interno com observações de usabilidade (campo `ux_test_non_dev_participant=true`).

## 5. Métricas do gate G5
- `max_clicks_to_last_run_info` ≤ 3.
- `admin_flows_covered`: 4 (F1–F4).
- `ux_test_non_dev_participant`: true (teste cruzado por membro que não implementou).
