# Sprint 32 — Capítulo 6 (learnings & anti-gaps)

Registros desta execução (alinhar/expandir conforme Cap.6 oficial):

- Fallbacks sem pytest funcionaram bem para gates; manter script compatível com ambientes mínimos.
- Métricas estão mockadas em `app/truthdb/metrics.py` (memória). Gap: ligar a stack real (Prometheus/OTEL) em sprint futura.
- Claim prioritária fixada em `news_fact_simple` no adaptador; gap: generalizar suporte a múltiplos tipos de claim e validar no PromotionService.
- Sanidade cruzada: S21 rodou PASS; S24_G1 rodou com fallback e ficou WARN (sem pytest/fastapi). Gap: rerodar S24 em ambiente com dependências completas e registrar resultado/waiver.
- Contestação v1 simples (marca estado contestado e cria DecisionBlock). Gap: lógica mais rica de outcomes, políticas e audit trail detalhado.
