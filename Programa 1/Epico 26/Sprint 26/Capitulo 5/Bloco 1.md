# Inspectah — Sprint 26 (S26)
## Capítulo 5 — Bloco 5.1
### Cenários End-to-end de Validação

> Arquivo-alvo no repo: `docs/s26_cap_5_1_cenarios_e2e_validacao.md`
>
> Função: definir de forma explícita os **cenários end-to-end** usados para validar a Sprint 26, conectando:
> - estados-alvo da S26 (Cap.1),
> - gates e métricas (Cap.2),
> - arquitetura/filemap (Cap.3),
> - plano operacional (Cap.4).
>
> Cada cenário descreve: contexto, passos (input → ações → output esperado), gates/scripts que o exercitam e evidências esperadas.

A S26 tem foco em **Design System Inspectah Admin v1** e no **Console de Fontes v2** como primeiro cliente sério desse design system. Os cenários abaixo foram escolhidos para provar, na prática, que:

- a UI/admin deixou de ser um mosaico e passou a ser **coerente e reutilizável**;
- operadores conseguem **operar fontes ponta a ponta** via console, sem scripts secretos;
- contratos de API e gates S26 (G0–G6) sustentam esses fluxos com evidência rastreável.

---

## Cenário E2E-01 — Navegar pelo Admin e chegar ao Console de Fontes v2

### 1. Objetivo

Validar que o **Design System Inspectah Admin v1** e o **roteamento/admin shell** estão funcionando como base única de UI para consoles, e que o Console de Fontes v2 está devidamente plugado nessa estrutura.

Este cenário toca principalmente:

- State-of-truth S26 relacionado a "Design System Admin v1 existente e adotado";
- gates **G0**, **G1** e **G3** (escopo & baseline, integridade estática do design system, qualidade geral do frontend).

### 2. Contexto inicial

- Ambiente: dev/local, banco em estado consistente pós-S25.
- Usuário: operador interno com permissão de acesso ao admin.
- Repo: branch de release da S26 (ou equivalente), com `bin/s26_g0..g3` disponíveis.

### 3. Passos (input → ações → output esperado)

1. Operador acessa a URL principal do Inspectah Admin.
   - Esperado: layout padrão do Design System Admin v1 (`AdminShell`) é carregado, com sidebar e header consistentes.
2. Operador localiza e clica na entrada **"Fontes"** na sidebar.
   - Esperado: transição suave para a rota do Console de Fontes v2.
3. Tela de **listagem de fontes** é exibida.
   - Esperado: uso claro de componentes do design system (tabela padrão, botões, badges de status), sem CSS "mágico" ou estilos divergentes.
4. Operador inspeciona estados de loading/erro/vazio (usando filtros ou ambiente seedado para isso, se necessário).
   - Esperado: mensagens e visuais seguem o padrão de `Banner`, `Skeleton` e estados vazios definidos em `ui/admin`.

### 4. Gates/scripts que exercitam o cenário

- `bin/s26_g0_scope_and_baseline.sh` — garante estrutura mínima de docs e filemap.
- `bin/s26_g1_design_system_static.sh` — compila e linta `ui/admin`.
- `bin/s26_g3_frontend_quality.sh` — roda lint, testes e build do frontend completo.

### 5. Evidências esperadas

- Logs de G0, G1 e G3 nas pastas:
  - `out/evidence/S26_G0_scope_and_baseline/`;
  - `out/evidence/S26_G1_design_system_static/`;
  - `out/evidence/S26_G3_frontend_quality/`.
- Opcional: captura de tela `e2e01_admin_sources_list.png` em `out/evidence/S26_G3_frontend_quality/` mostrando a UI do Console de Fontes v2 com layout admin v1.

---

## Cenário E2E-02 — Ciclo básico de vida de uma fonte (criar → ativar → verificar)

### 1. Objetivo

Provar que um operador consegue **criar, configurar e ativar uma fonte** usando apenas o Console de Fontes v2, com UI baseada no Design System Admin v1 e contratos de backend coerentes.

Este cenário toca principalmente:

- states-of-truth ligados a "100% das fontes em uso podem ser operadas via UI" (E26);
- gates **G2** (fluxos do Console de Fontes), **G4** (contratos de API de fontes) e, indiretamente, **G1** e **G3**.

### 2. Contexto inicial

- Ambiente: dev/local, com ao menos uma fonte seedada (para comparação) e permissão para criar novas fontes.
- Usuário: operador interno com permissão de gerenciar fontes.

### 3. Passos (input → ações → output esperado)

1. Operador acessa a tela de listagem de fontes (como em E2E-01).
2. Operador clica em **"Nova fonte"**.
   - Esperado: `SourceEditPage` abre com `SourceForm` vazio.
3. Operador preenche dados mínimos da fonte (ex.: nome, tipo `RSS`, URL do feed, parâmetros básicos de ingestão) e clica em **Salvar**.
   - Esperado: requisição `POST /api/sources` é enviada; backend retorna `201` com payload alinhado ao tipo `Source`; UI mostra feedback de sucesso.
4. Operador é redirecionado (ou volta) à listagem de fontes.
   - Esperado: a nova fonte aparece na lista com status inicial esperado (ex.: `INACTIVE`).
5. Operador seleciona ação para **ativar** a fonte (ex.: botão `Ativar`).
   - Esperado: chamada à rota de ativação (`POST /api/sources/{id}/activate` ou equivalente); status muda para `ACTIVE`; `SourceStatusBadge` reflete o novo estado usando cores/tokens corretos.
6. Operador verifica, em painel de ingestão ou logs (fora do escopo estrito de UI, mas visível), que a fonte passou a ser considerada nas rotinas de ingestão 2.0.
   - Esperado: sistema trata a fonte como ativa, sem necessidade de script manual.

### 4. Gates/scripts que exercitam o cenário

- `bin/s26_g2_sources_console_flows.sh` — testa fluxo de criação/edição/ativação de fonte na UI.
- `bin/s26_g4_sources_api_contracts.sh` — testa contratos de API de fontes (criar, editar, ativar, etc.).
- `bin/s26_g3_frontend_quality.sh` — garante que o build/test geral não quebrou.

### 5. Evidências esperadas

- Logs de G2 e G4 em:
  - `out/evidence/S26_G2_sources_console_flows/g2_sources_flows_tests.log`;
  - `out/evidence/S26_G4_sources_api_contracts/g4_sources_api_tests.log`.
- Arquivo índice de cenários de teste de G2 (`g2_flows_index.md`) listando explicitamente um caso equivalente a este E2E-02.
- Opcional: JSON de request/response anonimizado para `create_source` e `activate_source` em `S26_G4_sources_api_contracts/`.

---

## Cenário E2E-03 — Tratar uma fonte problemática (desativar/arquivar com segurança)

### 1. Objetivo

Validar que a nova UI/admin e o Console de Fontes v2 permitem **agir rapidamente sobre uma fonte problemática** (erros recorrentes, dados ruins) de maneira segura e auditável, sem fuçar em scripts ou banco.

Este cenário toca principalmente:

- states-of-truth ligados a operação segura de fontes;
- gates **G2**, **G4** e **G5** (runbook de operação de fontes).

### 2. Contexto inicial

- Ambiente: dev/local com seed que simule ao menos uma fonte com histórico problemático (falhas de ingestão recorrentes, por exemplo).
- Usuário: operador interno com permissão de gerenciar fontes.

### 3. Passos (input → ações → output esperado)

1. Operador acessa o Console de Fontes v2.
2. Operador identifica uma fonte marcada como "em risco" ou com flag de erro recorrente (dependendo de como a saúde é exposta em S26; no mínimo, uma fonte manualmente identificada).
3. Operador abre detalhes da fonte.
   - Esperado: UI exibe informações relevantes (config básica, status atual, possivelmente últimos erros/resumos simples se já existirem na versão atual do produto).
4. Operador decide **desativar** a fonte (ação `Desativar`).
   - Esperado: chamada à rota de desativação; status muda para `INACTIVE`; UI confirma.
5. Se o caso exigir, operador pode **arquivar** a fonte (ação `Arquivar`).
   - Esperado: status muda para `ARCHIVED` e a fonte sai dos fluxos ativos de ingestão.
6. Operador registra, via runbook, a decisão e o motivo.
   - Esperado: o runbook de operação de fontes (`runbook_operacao_fontes_v1.md`) possui seção explicando este fluxo, e o operador consegue seguir os passos sem ambiguidade.

### 4. Gates/scripts que exercitam o cenário

- `bin/s26_g2_sources_console_flows.sh` — cobre as transições de status (ativo → inativo → arquivado) na UI.
- `bin/s26_g4_sources_api_contracts.sh` — cobre as rotas de mudança de status no backend.
- `bin/s26_g5_docs_and_runbooks.sh` — verifica existência e qualidade mínima do runbook de fontes.

### 5. Evidências esperadas

- Logs de G2, G4 e G5 nas respectivas pastas de evidências.
- Runbook `docs/runbook_operacao_fontes_v1.md` contendo pelo menos uma seção equivalente a este cenário (ex.: "Como desativar/arquivar uma fonte problemática").
- Opcional: notas de operação específicas (ex.: `ux_notes_*.md` ou `ops_notes_*.md`) em `S26_G5_docs_and_runbooks/`.

---

## Cenário E2E-04 — Extensão pequena do Design System usada pelo Console de Fontes

### 1. Objetivo

Demonstrar que o Design System Inspectah Admin v1 **não é uma peça rígida**, mas sim uma base extensível e coerente, onde pequenas extensões (ex.: nova variante de botão ou badge) podem ser introduzidas e rapidamente adotadas pelo Console de Fontes v2 **sem quebrar gates**.

Este cenário toca principalmente:

- states-of-truth sobre o design system como base viva e reutilizável;
- gates **G1**, **G2**, **G3** e, indiretamente, **G5**.

### 2. Contexto inicial

- Ambiente: dev/local, S26 já com design system e console de fontes funcionando.
- Usuário: dev/frontend + revisão de UX.

### 3. Passos (input → ações → output esperado)

1. Dev introduz uma nova variante de `Button` em `ui/admin/components/Button.tsx` (ex.: `variant="danger"` usada para ações destrutivas como "Arquivar fonte").
2. Dev adapta `SourceStatusBadge` ou as ações de fontes para usar essa variante na UI (por exemplo, botão "Arquivar" usando o novo `danger`).
3. Dev roda localmente:
   - `bin/s26_g1_design_system_static.sh`;
   - `bin/s26_g2_sources_console_flows.sh`;
   - `bin/s26_g3_frontend_quality.sh`.
   - Esperado: todos rodam em exit 0.
4. Operador navega até o Console de Fontes v2 e verifica o novo botão/variante em uso em um fluxo real (ex.: arquivar fonte).
   - Esperado: UI coerente, sem regressões visuais nas outras ações/botões.

### 4. Gates/scripts que exercitam o cenário

- `bin/s26_g1_design_system_static.sh` — garante que a extensão respeita invariantes de design system.
- `bin/s26_g2_sources_console_flows.sh` — garante que fluxos de fontes continuam íntegros.
- `bin/s26_g3_frontend_quality.sh` — garante que o frontend geral continua saudável.

### 5. Evidências esperadas

- Novos logs de G1, G2 e G3 pós-extensão na respectiva pasta de evidências.
- Opcional: nota curta em `docs/design_system_admin_v1.md` citando a nova variante e seu uso.

---

## 6. Síntese do Bloco 5.1

Os quatro cenários E2E definidos aqui garantem que a S26 seja avaliada como um todo coerente, e não apenas por testes unitários isolados:

- **E2E-01** prova que o Design System Admin v1 existe de fato e é a porta de entrada para consoles.  
- **E2E-02** prova que o ciclo básico de vida de fontes (criar → ativar → usar) é totalmente operável via UI.  
- **E2E-03** prova que problemas em fontes podem ser mitigados com segurança e com apoio de runbooks.  
- **E2E-04** prova que o design system é extensível sem quebrar a disciplina de gates.

Na prática, se esses cenários forem reexecutáveis e estiverem cobertos por testes/ evidências descritas no Cap.4.3, o ORR da S26 tem base concreta para declarar GO com confiança.

