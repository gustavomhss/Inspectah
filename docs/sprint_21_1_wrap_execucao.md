## Sprint 21.1 — Wrap de Execução

- **Objetivo:** entregar o Copiloto de Fontes em modo agente, sugerindo preenchimento do Console de Fontes sem ação autônoma, com upload de arquivos e política de segurança explícita.

- **Gates (S21_1_G0…G8):** todos em PASS/GO, scorecards em out/scorecards/S21_1_G*.json e evidências em out/evidence/S21_1_G*/.

- **Entregas principais:**
  - Backend: router /admin/copiloto-fontes, sessões/arquivos em memória, agente s21_1_copiloto_fontes com tools de form_state, file_reader, logging.
  - Frontend: widget flutuante, painel de chat, hook useCopilotoAgent, integração no AdminSourceFormPage aplicando actions; upload de arquivos integrado.
  - Segurança: política aplicada no agente e testes de safety cobrindo auto-cadastro, fora de escopo e prompt injection.
  - Cenários: conversas guiadas para notícias, esportes, clima, fofoca; logs em out/evidence/S21_1_G6_cenarios/.

- **Riscos/pontos de atenção:** integração futura de LLM real deve respeitar o prompt-base e ferramentas; leitura de PDF ainda retornando aviso; .git bloqueado para escrita (sem commits nesta rodada).

- **Próximos passos (S22):** plugar LLM real com as tools definidas, ampliar suporte a formatos de arquivo, adicionar testes e2e UI automatizados e observabilidade do Copiloto.
