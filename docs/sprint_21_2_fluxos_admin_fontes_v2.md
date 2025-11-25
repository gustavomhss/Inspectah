# Sprint 21.2 — Fluxos de Admin de Fontes v2

Este documento descreve como o Console de Fontes e o Copiloto v2 conduzem **criação**, **edição** e **mudança de status** de fontes. Ele se ancora nos fluxos base da S21 (`docs/sprint_21_fluxos_admin_fontes.md`) e os estende sem quebrar contratos existentes.

## 1. Princípios de UX/operacionais

- Copiloto aberto por padrão em “Nova fonte”; criação só habilita após pelo menos uma interação com o agente.
- O admin continua no controle: toda ação (criar/editar/status) é confirmada manualmente antes de persistir.
- `agent_mode` torna o Copiloto mais proativo (on) ou apenas orientador (off); sempre visível e sincronizado com backend.
- Refresh_interval, tipo e status são campos de primeira classe em todas as telas (listagem, formulário, detalhe).

## 2. Fluxo de criação (nova fonte)

1. **Abertura automática** do Copiloto ao entrar em `AdminSourceFormPage`.
2. **Escolha de tipo**: agente pergunta e registra (`news`, `weather/sports/fofoca` conforme S21, ou `official_open`).
3. **Coleta do que o admin já sabe**: URL base, temas, info_types, descrição.
4. **Preenchimento de lacunas**: agente sugere endpoints, temas faltantes, refresh_interval compatível com o tipo.
5. **Revisão**: ações estruturadas retornam para o formulário (destacadas) e o admin revisa/edita.
6. **Confirmação**: somente após o admin confirmar é feita a chamada real de criação; botão “Criar fonte” permanece bloqueado até haver interação com o Copiloto.

## 3. Fluxo de edição (fonte existente)

1. Em `AdminSourceDetailPage`, o Copiloto recebe `source_id` e snapshot atual via tool de leitura.
2. Admin pode pedir ajustes de **endpoint**, **temas**, **info_types**, **refresh_interval** ou **descrição**.
3. Copiloto monta **plano de alteração** (antes/depois) usando update_planner e envia actions para UI com diffs destacados.
4. Admin confirma alterações e aciona endpoint de update; nada é aplicado automaticamente.

## 4. Fluxo de status (aprovar, suspender, desativar, reativar)

1. Copiloto lê estado atual e exibe explicação em linguagem simples.
2. Admin escolhe intenção (aprovar/ativar, suspender, desativar, reativar); agente valida contra a tabela de transições da S21.
3. status_planner gera plano (de → para, motivo) e devolve action de proposta.
4. Admin confirma; serviço aplica transição e registra histórico. Transições inválidas são recusadas com mensagem segura.

## 5. Campos críticos e descrições curtas (UI)

- **Tipo**: enum incluindo “fonte oficial aberta”; explica exemplos e limitações.
- **Temas / info_types**: obrigatórios para classificação; Copiloto sugere conforme tipo.
- **Endpoint/URL base**: URL pública, preferir ponto de entrada principal.
- **refresh_interval**: frequência desejada de atualização; explicado como contrato de coleta.
- **Status**: mostra estado atual e próximas ações válidas.

## 6. Relação com FSM do Copiloto

- Estados de conversa e transições estão em `docs/sprint_21_2_maquina_estados_copiloto.md`.
- Fluxos acima são as trilhas que a FSM deve respeitar (criação, edição, status), variando por tipo de fonte e por `agent_mode`.

## 7. Segurança e limites

- Fora de escopo (verdades/fatos, Debunker, usuários) são recusados e redirecionados ao contexto de fontes.
- Para **fontes oficiais abertas**, o Copiloto reforça que a ingestão automática não está coberta na 21.2 e mantém refresh sugerido conservador.

## 8. Evidência e testes

- Fluxos são validados nos testes de domínio (`tests/sources/*`) e de agente (`tests/agents/test_s21_2_copiloto_flows.py`).
- Gate S21_2_G4 cobre a UX das telas; S21_2_G7 mede experiência ponta-a-ponta.
