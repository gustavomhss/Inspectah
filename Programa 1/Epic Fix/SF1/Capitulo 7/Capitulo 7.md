# SF1 — Capítulo 7 — Riscos, Trade-offs & Futuro

## 7.1 Riscos
- Ambiente sem Prom/Alertmanager/IdP impede evidência real → risco de NO-GO.
- Flakiness de UI/metrics pode consumir tempo → risco de janela estourar.
- Dependência de fixtures/datasets reais; ausência leva a placeholders (inaceitável).
- Scripts legados podem mascarar rc (herança de S35) → risco de PASS falso.

## 7.2 Trade-offs
- Preferir bloqueio agressivo (drift/alerta) vs velocidade; aceitar NO-GO se não há prova real.
- Smoke enxuto mas real (API/UI/metrics) vs cobertura extensa: priorizar realismo mínimo com evidência.

## 7.3 Futuro
- Se mocks necessários por ambiente, registrar GAP e agendar retry; não marcar PASS.
- Preparar automação de rerun periódico dos gates de rollout para evitar regressões futuras.
- Revisitar scripts herdados e remover qualquer bypass de rc/erro silencioso.
