# Inspectah — Sprint 35 — Capítulo 6
## Referências, Estado da Arte & Benchmark

### 6.1 Referências técnicas
- **Argo Rollouts / Flagger:** padrões de canary/teste percentual, métricas/SLO, rollback automático — inspira limites e critérios (mas sem copiar UI complexa).
- **LaunchDarkly Experiments:** governança de experimentos com trilha de auditoria e porcentagens; reforça necessidade de labels e hash de config.
- **Kubernetes Admission/Webhooks:** analogia para catálogo assinado e enforcement de políticas em tempo de operação.
- **Airflow DAG versioning:** referência para versionamento/assinatura e drift detection.
- **SLO by Mode (SRE):** práticas de SRE para separar métricas/alertas por estágio (experimento vs produção).

### 6.2 Como aplicar ao Inspectah
- Usar labels/operation_id como Argo/LaunchDarkly para rastreio de rollout e auditoria.
- Adotar diffs de catálogo e assinatura (sem criar editor visual) inspirado em AdmissionControllers.
- Painel OracleOps inspirado em Flagger/Argo, mas simplificado e aderente a E26 (tabelas/cards/linhas).
- SLO/alertas por modo seguindo práticas SRE; bloquear promoções quando breach.

### 6.3 Material interno relevante
- S34 (multi-fluxo) — base de entidades e UI de múltiplos fluxos.
- E26 — gramática de Console/Admin (componentes, estados).
- E40.5 — requisitos de lógica/Truth (uso de `flow_version_id` e políticas).
- Lessons de incidentes anteriores (Programa 7) sobre canary sem limites e drift de config.
