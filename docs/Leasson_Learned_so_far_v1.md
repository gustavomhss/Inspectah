<!-- Inspectah Sprint 3 canonical doc header -->
> **Título:** Leasson Learned so far  
> **Versão:** v1  
> **Atualizado em:** 2025-11-15  
> **Resumo rápido:**  
> - Log append-only de lições observadas ao longo das sprints do Inspectah.
> - Tags por área (P, FD, API, LGPD, PROC, COD) e origem para rastrear contexto.
> - Base obrigatória para revisar decisões antes de novos ajustes de Gate.

# D9 — Lessons Log (Raw)

Formato: `AAAA-MM-DD [TAGS] [ORIGEM] descrição breve da lição`. Tags válidas: P, FD, API, LGPD, PROC, COD (podem ser combinadas).

Este arquivo é append-only por convenção. Novas lições devem ser adicionadas ao final, sem remover histórico.
2025-11-13 [FD, COD] [D9.2 revisão] A linguagem proposta para computed fields (subset JSONata) atende aos requisitos de determinismo, mas precisa de validação formal do PO para evitar divergência com futuras preferências de stack.
2025-11-13 [LGPD, PROC] [D9.4/D9.5 revisão] O uso de storage compatível com S3 para o Evidence Vault simplifica auditoria, porém requer confirmação da equipe de infra quanto a criptografia gerenciada e região autorizada.
2025-11-13 [API, COD] [D9.3 revisão] O limite inicial de 120 req/min por token foi definido com base em estimativa; é necessário medir cargas reais antes do go-live para ajustar sem afetar consumidores MBP.
