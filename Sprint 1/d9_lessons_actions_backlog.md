# D9 — Lessons Actions Backlog

Para cada lição registrada, use a estrutura:

```
ID [TAGS] descrição curta
  - AÇÃO: TIPO — descrição; dono; prazo (se aplicável); artefatos impactados
```

Tipos de ação: PATCH_D9, PATCH_DNA, BACKLOG_PROX_SPRINT, ALERTA_RISCO.

Arquivo append-only por convenção.
D9-FD-001 [FD, COD] Linguagem de computed fields (subset JSONata) precisa de carimbo oficial do PO.
  - AÇÃO: PATCH_D9 — Reunir PO + Leslie para confirmar linguagem e atualizar D9.2 §7 e D9.7 conforme decisão; dono: Leslie; prazo: antes da sprint de implementação do Field Designer. (STATUS: DONE em 2025-11-13 — IEL documentada em D9.2 §7 e superprompt atualizado.)

D9-LGPD-001 [LGPD, PROC] Definição do storage do Evidence Vault (S3 compatível) depende da equipe de infra/segurança.
  - AÇÃO: PATCH_D9 — Registrar no D9.4 §2/§4 a tecnologia final e controles de criptografia assim que aprovados; dono: Guardião LGPD + Infra; prazo: antes do provisioning do ambiente prod. (STATUS: DONE em 2025-11-13 — CE Object Store/S3 compatível com SSE-KMS documentado em D9.4/D9.5.)
  - AÇÃO: ALERTA_RISCO — Notificar PO caso a região/appliance disponível viole requisitos LGPD internacionais. (STATUS: MONITORAMENTO CONTÍNUO — nenhum desvio registrado até 2025-11-13.)

D9-API-001 [API, COD] Rate limit inicial de 120 req/min precisa ser validado com medições reais.
  - AÇÃO: PATCH_D9 — Documentar explicitamente o limite v0 (120 req/min + burst) e cabeçalhos de throttle em D9.3, com referência ao plano de revisão; dono: Leslie; prazo: imediato. (STATUS: DONE em 2025-11-13 — ver D9.3 §7 e evidências G3.)
  - AÇÃO: BACKLOG_PROX_SPRINT — Rodar teste de carga após implementação v0 e ajustar limites em D9.3 + config Explore API; dono: Engineering Lead; prazo: Sprint imediatamente após entrega v0. (STATUS: ABERTO — executar assim que ambiente v0 estiver estável.)
