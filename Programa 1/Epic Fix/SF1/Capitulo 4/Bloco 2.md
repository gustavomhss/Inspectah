# Bloco 2 — Estrutura de requisitos
- Modelagem: deadlines/hash/actor/operation_id/slo_breach persistidos; contadores de rollback/violação.
- Catálogo: hash/assinatura obrigatórios; comparação publish/runtime em cada operação e gate.
- Políticas/SLO: engine consulta s35_slos.md; bloqueia promo se alerta/SLO negativo.
- APIs: validar actor/hash/limites; logs com campos completos; eventos para OracleOps/Truth.
- Observabilidade: queries PromQL mínimas e alertas simulados; painel com dados reais exportado.
- Pilotos: datasets oficiais; API/UI headless; captura de evidências.
