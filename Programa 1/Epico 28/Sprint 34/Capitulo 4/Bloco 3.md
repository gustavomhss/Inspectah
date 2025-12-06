# Bloco 3 — Cenários de teste por gate (G0–G4)
- **G0:** varredura de docs (24 arquivos 6×4), templates e mapa de SLO/componentes presentes; script G0 retorna 0.
- **G1:** migração aplica em DB limpo + pós-S32; templates carregam; políticas mínimas por domínio ativas; limites/flags aplicados; rollback inválido bloqueado.
- **G2:** console/API lista fluxos/versões/diffs; rollback/promoção/teste funcionam com autorização; cockpit mostra SLO/incident; logs/auditoria presentes.
- **G3:** métricas/logs com labels de fluxo/versão/teste; painel não vazio; alertas disparam; SLOs ligados a métricas reais.
- **G4:** pilotos notícias + contestação v0 rodados em teste/ativo; rollback exercitado; evidências completas (dataset, ingest_log, exec_dump, metrics/logs, screenshots); bundle multi-fluxo gerado.
