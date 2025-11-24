## Scorecard Sprint 21.1 — Copiloto de Fontes

- **M1 (sanidade backend/agents):** tests/sources e tests/agents em PASS.
- **M2 (UX widget):** widget carregando e enviando mensagens no AdminSourceFormPage; painel flutuante acessível.
- **M3 (sync form):** ações set_field/mark_suggested aplicam tipo/temas/info_types/endpoint sem sobrescrever manual.
- **M4 (files):** upload via widget → backend gera file_id → agente lê textos (.txt) e sugere descrição; PDFs retornam aviso seguro.
- **M5 (safety):** testes de segurança cobrindo auto-cadastro, fora de escopo e prompt injection em PASS.

Estado final: todos os indicadores acima cumpridos; decisão consolidada em S21_1_G8 como GO.
