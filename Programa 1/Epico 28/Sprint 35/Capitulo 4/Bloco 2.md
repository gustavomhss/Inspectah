# Bloco 2 — Estrutura e decomposição de requisitos
- **Modelagem:** rollout com deadlines, `operation_id`, `actor`, `catalog_hash`; contadores de rollback/violações; registro `slo_breach`. Limites aplicados no serviço.
- **Catálogo:** schema YAML com hash/assinatura; CLI para publicar/validar; comparação publish vs runtime; drift bloqueia operações e registra métrica.
- **Políticas e critérios:** engine avalia SLO/alertas; regras por domínio/mode; produz eventos e métricas; suporta testes negativos (limite tempo/percentual/rollbacks).
- **Contratos e APIs:** rotas REST exigem actor + hash; erros padronizados; hooks de auditoria; eventos para Truth/OracleOps com flow/mode/version.
- **Observabilidade:** instrumentação real; painel com dados; alertas testados; promtool obrigatório; fontes de SLO = s35_slos.md.
- **FE/Console:** lista/painel/dialogs/timeline; estados drift/alerta/SLO breach; bloqueio sem actor; confirmações para promo/rollback; coleta de screenshots reais.
- **CI/ORR:** scripts de gate rodando negativos, promtool, smoke HTTP; workflow CI; bundle + scorecards; runbooks ensaiados; flags/limites versionados.
