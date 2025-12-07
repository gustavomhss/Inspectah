# Bloco 1 — Visão geral e ancoragem
- S35 encerra E28 no Programa 1: governança avançada de rollout (limites aplicados + catálogo assinado + SLO/OracleOps/Truth).
- Público: operações 24/7, arquitetos de fluxo, Conselho (GO/NO-GO), Observabilidade, OracleOps, Truth/Contestação.
- Pain points atuais: GO falso (G3/G4 simulados), SLO/alertas ignorados, RBAC opcional, pilotos sintéticos.
- Pilotos obrigatórios: news_v2 e contestacao_v0 via API/UI reais, com métricas/alertas e hash de catálogo conferidos.
- Resultado esperado: Conselho só libera GO quando catálogo e runtime batem, SLO/alertas são exercitados, auditoria exige actor e eventos chegam a OracleOps/Truth.
