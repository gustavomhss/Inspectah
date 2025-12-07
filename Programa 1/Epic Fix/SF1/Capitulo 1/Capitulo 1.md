# SF1 — Sprint Fix 1 (Remediação S35 Rollout Governado)
## Contexto & Problema
- Posição: SF1 (E36/Epic Fix) foca em refazer S35 (rollout governado) para eliminar GO falso (F1–F5) e cobrir spillover F6–F8 quando afetarem rollout.
- Problema: G3/G4 simulados, limites/SLO/RBAC não aplicados, catálogo/observabilidade/pilotos falsos; OracleOps/Truth sem eventos; GO inválido.
- Missão: entregar rollout governado real (news_v2, contestacao_v0) com limites/SLO/alertas aplicados, RBAC/auditoria obrigatórios, catálogo assinado validado em runtime, observabilidade e pilotos reais com evidências.

## Objetivos e estados-alvo
- Rollout aplica limites (tempo/percentual/rollbacks) e bloqueia promo/rollback se SLO/alerta negativo ou drift de catálogo.
- SLO/alertas vivos (s35_slos.md como fonte única), promtool + firing/resolution com evidências.
- Catálogo assinado/hashes comparados publish vs runtime; drift bloqueia operação e gera alerta.
- API/UI exigem actor/operation_id; auditoria completa; eventos OracleOps/Truth com flow/mode/version + `slo_breach`.
- Pilotos reais via API/UI; screenshots reais; bundle/scorecards fresh sem placeholders.

## Escopo IN / OUT
- IN: refazer G0–G5 de S35; limites/SLO/alertas; promtool/firing; hash drift; RBAC/auditoria; eventos OracleOps/Truth; pilotos reais; bundles e scorecards rerodados.
- OUT: novos fluxos/agentes; auto-tuning canary; blockchain/blocos; multi-tenant; lógica de agentes (Programa 2).
