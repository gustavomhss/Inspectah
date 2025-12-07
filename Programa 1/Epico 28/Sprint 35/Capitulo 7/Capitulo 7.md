# Inspectah — Sprint 35 — Capítulo 7
## Riscos, Trade-offs & Futuro da Sprint

### 7.1 Riscos críticos (prioridade)
- **R1 GO falso por placeholders:** repetição de G3/G4 simulados (SQLite, screenshots falsas) → produção sem validação real.
- **R2 Incidente por limites/SLO não aplicados:** canary infinito ou promoção com SLO quebrado → impacto em produção.
- **R3 Drift de catálogo/config:** hash divergente entre publicado e runtime leva a políticas diferentes e promoções erradas.
- **R4 RBAC/auditoria falha:** operações sem actor/operation_id inviabilizam investigação e compliance.
- **R5 Observabilidade/alerta vazios:** métricas inexistentes ou alertas sem firing → OracleOps cego, Truth sem eventos.
- **R6 Pilotos sem tráfego real:** datasets duplicados ou ausência de API/UI real distorcem resultados.

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
