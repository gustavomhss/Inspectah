# Inspectah — Sprint 35 — Capítulo 9
## UI + UX (Bret Victor captain)

### 9.1 Experiência desejada
- Operador entende em segundos **qual modo** cada fluxo está, **quanto** está em canary/teste e **o que precisa para promover/rollback**.
- Ações críticas (iniciar, promover, rollback) são guiadas, com microcopy clara e confirmação dupla; erros são específicos e recuperáveis.
- Diferenças de versão e drift são explícitas, evitando surpresas; evidências ficam a um clique.

### 9.2 Princípios e heurísticas
- **Transparência radical:** mostrar modo, percentuais, tempo restante, SLO/alertas, hash de catálogo sempre visíveis.
- **Clareza de decisão:** botões ativam só quando critérios atendidos; microcopy explica bloqueios (ex.: “SLO breach: p95>2500ms”).
- **Auditabilidade:** timeline e badges sempre visíveis; operation_id exibido e copiável; links diretos para evidências.
- **Ergonomia 24/7:** fluxo de teclado completo, foco visível, toasts não bloqueantes; estados críticos têm contraste forte e textos curtos.
- **Segurança por design:** rollback e promoção pedem confirmação e mostram impacto (modo atual → modo destino).

### 9.3 Estados visuais críticos
- **Canary/teste:** badge colorida + percentual + tempo restante; card de critérios com status (pass/fail/pending).
- **Promoção bloqueada:** botão desabilitado com tooltip “Drift de catálogo” ou “Alertas ativos”; linha da tabela mostra ícone de bloqueio.
- **Rollback em andamento:** linha sombreada, spinner; toast “Rollback acionado (op-123)” com opção de ver timeline.
- **Drift de catálogo:** banner persistente no painel; badge vermelho na lista; CTA para abrir runbook/CLI.
- **Erro de API:** mensagem inline “Falha ao iniciar canary: percentual > limite”; usuário pode editar e reenviar.

### 9.4 Motion, microcopy e acessibilidade
- Motion minimalista: fade/slide curto em abertura de dialog; atualização de cards com animação leve para mudanças de modo; timeline adiciona itens com highlight de 1s.
- Microcopy exemplo:
  - Iniciar: “Rodar canary em 10% por 45min. Critérios: p95<=2500ms, sem alertas ativos.”
  - Promoção bloqueada: “Promoção travada — drift de catálogo. Sincronize catálogo para continuar.”
  - Rollback: “Rollback agora? Fluxo volta para v2.0 ativo. Informe motivo.”
- Acessibilidade: contraste 4.5:1, foco visível, atalhos de teclado para abrir dialog/confirmar, labels textuais para ícones, sem depender só de cor.
