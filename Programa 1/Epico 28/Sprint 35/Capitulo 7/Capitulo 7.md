# Inspectah — Sprint 35 — Capítulo 7
## Riscos, Trade-offs & Futuro da Sprint

### 7.1 Riscos críticos (prioridade)
- **R1 Incidente de canary mal protegido:** percentuais/limites errados ou rollback lento causam impacto em produção.
- **R2 Drift de catálogo/config:** hash divergente entre publicado e runtime leva a decisões baseadas em políticas diferentes.
- **R3 Falta de dados reais em pilotos:** promoção sem evidências sólidas gera falsa sensação de segurança.
- **R4 Integração lógica/Truth incompleta:** ausência de `flow_version_id`/políticas quebra rastreabilidade de incidentes.
- **R5 Observabilidade insuficiente:** métricas/logs sem labels de modo/versão/operation inviabilizam auditoria e alertas.

### 7.2 Trade-offs e escolhas de design
- **Simplicidade vs poder:** optar por rollout percentual simples (sem auto-tuning) para entregar governança rápida; dívida de automação fica registrada.
- **Catálogo assinado vs editor visual:** priorizar assinatura/hash e CLI/CI em vez de UI avançada de edição; reduz superfície de erro.
- **Bloqueios agressivos vs velocidade:** drift/alertas bloqueiam promoções por default; mais seguro, pode atrasar releases — manter override só via flags bem auditadas.
- **Labels mínimos vs verbosidade:** insistir em labels completos (`flow_id`, `flow_version_id`, `mode`, `operation_id`, `catalog_hash`) mesmo aumentando custo de log/metric.

### 7.3 Futuro próximo e dívidas (pós-S35)
- **DT-001:** canary multi-step auto-ajustável (percentuais dinâmicos, rollback automático).
- **DT-002:** editor visual/lightweight para catálogo/rollout (sem perder assinatura/hash).
- **DT-003:** integração profunda com E40.5 (validações lógicas automáticas em promoção/rollback).
- **DT-004:** template store assinada/OTA com locks de ambiente.
- **DT-005:** roteamento condicional avançado e multi-tenant/quotas.

### 7.4 Gaps/decisões para Stakeholder/Conselho
- Percentuais máximos permitidos em produção (default 10–20% canary) — confirmar com Conselho.
- Política de quem pode promover/rollback (RBAC) — confirmar papéis/autorizadores.
- Limites de SLO/alertas que bloqueiam promoções — validar thresholds com Observabilidade.
- Escopo de pilotos adicionais além de notícias/contestação v0 — Conselho decide se inclui terceiro domínio.
