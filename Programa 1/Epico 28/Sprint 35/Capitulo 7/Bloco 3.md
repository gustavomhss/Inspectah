# Bloco 3 — Exemplos e bordas (R1–R5)
- **R1 incidente canary:** percentual setado para 80% em prod → alerta de limite dispara e bloqueia operação; rollback automático se breach de SLO; evidência no timeline.
- **R2 drift catálogo:** hash publicado `abc`, runtime `def`; G1/G3 falham; botão de promoção desabilitado; operador segue runbook de sync.
- **R3 pilotos sem dados:** tentativa de promoção sem datasets reais → G4 falha; Conselho exige nova coleta antes de GO.
- **R4 integração lógica:** log sem label `flow_version_id` em incidente de verdade; checklist de validação reprova gate; bug precisa ser corrigido antes de promoção.
- **R5 observabilidade:** painel vazio para canary; alerta `panel_empty` dispara; bloqueia rollout até instrumentação corrigida.
