# Bloco 2 — Estrutura e decomposição de requisitos
- **Modelagem:** entidades/colunas de rollout, políticas e catálogo; validação de limites/flags em serviço.
- **Catálogo:** esquema YAML, assinatura/hash, validação CLI, publicação/Sync entre ambientes, diffs runtime vs publicado.
- **Políticas e critérios:** engine que avalia SLO/alertas e bloqueia promoções; suporte a regras por domínio/mode.
- **Contratos e APIs:** rotas REST + schemas; erros padronizados; RBAC; contratos para lógica/Truth (labels + `flow_version_id`).
- **Observabilidade:** instrumentação (metrics/logs), painéis, alertas; SLOs rollout; dumps de evidência.
- **FE/Console:** componentes para lista, painel, timeline, dialogs de operações; estados de drift/alerta; confirmações/locks.
- **CI/ORR:** scripts de gate, workflow CI, bundle, scorecards; runbooks ensaiados; flags/limites configuráveis por ambiente.
