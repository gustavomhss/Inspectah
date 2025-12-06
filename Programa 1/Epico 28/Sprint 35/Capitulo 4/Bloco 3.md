# Bloco 3 — Cenários de teste por gate (G0–G4)
- **G0:** varredura de docs (24 arquivos 6×4), catálogo presente/assinado; script G0 PASS.
- **G1:** migração aplica (DB limpo + pós-S34); catálogo carrega; políticas por domínio/mode ativas; limites/flags aplicados; rollback inválido bloqueado.
- **G2:** console/API iniciam canary/teste, promovem e fazem rollback com autorização; auditoria/logs completos; catálogo/hash exibidos; scripts PASS.
- **G3:** métricas/logs com labels de fluxo/versão/mode; painel não vazio; alertas disparam; SLOs rollout ligados a métricas reais; script PASS.
- **G4:** pilotos notícias/contestação v0 com canary/teste → promoção/rollback evidenciados; catálogo publicado; bundle gerado; scorecards G4 PASS.
