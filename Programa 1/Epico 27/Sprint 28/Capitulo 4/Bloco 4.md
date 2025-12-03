# Inspectah — Sprint 28
## Capítulo 4 — Bloco 4
### Plano Detalhado por Gate (G5, G6, G7), Execução Local, CI e Checklist Final de GO/NO_GO

---

#### 4.4.1 Objetivo deste bloco

Este bloco fecha o Capítulo 4 da Sprint 28 cobrindo:

- **S28_G5 — Observability & Legacy Sanity (S21/S22)**  
- **S28_G6 — Demo Interna & UX**  
- **S28_G7 — GO/NO_GO Final**  
- Execução local consolidada (comandos-chave).  
- Uso do CI (workflow s28-gates).  
- Checklist final de GO/NO_GO.

Aqui a pergunta é: **como garantir, de forma reproduzível e auditável, que o que foi feito na Sprint 28 não quebrou nada, está utilizável por humanos e merece ser integrado à linha principal do Inspectah?**

---

#### 4.4.2 Gate S28_G5 — Observability & Legacy Sanity

**Pergunta que G5 responde:**
> “Depois das mudanças da Sprint 28, os fluxos de fontes e ingestão continuam saudáveis, sem regressões nos scripts e gates herdados de sprints anteriores (S21/S22)?”

G5 é o gate que protege o passado contra o presente.

---

##### 4.4.2.1 Escopo de G5

1. **Rodar scripts de sanidade de fontes e ingestão das sprints 21/22**  
   - Foco em scripts que validam:
     - domínio de fontes,  
     - APIs relacionadas a fontes,  
     - ingestão 2.0 e suas métricas básicas.

2. **Detectar regressões**  
   - Qualquer falha nova nesses scripts, causada por S28, deve ser tratada como P0/P1.  
   - Ajustes em scripts antigos são permitidos **apenas** se forem para alinhar com uma melhoria objetiva de modelo/contrato.

3. **Registrar evidências de execução e resultado**  
   - Logs completos.  
   - Scorecard específico de G5.

---

##### 4.4.2.2 Tarefas concretas de G5

1. **Mapear scripts relevantes de S21/S22**  
   Exemplos (nomes ilustrativos, ajustar para o repo real):
   - `bin/s21_g1_sources_domain.sh`  
   - `bin/s21_g2_sources_api.sh`  
   - `bin/s22_g1_ingestion_core.sh`  
   - `bin/s22_g2_ingestion_metrics.sh`

2. **Rodar cada script em ambiente com S28 aplicada**  
   - Comandos típicos na raiz do repo:
     - `bin/s21_g1_sources_domain.sh`  
     - `bin/s21_g2_sources_api.sh`  
     - `bin/s22_g1_ingestion_core.sh`  
     - `bin/s22_g2_ingestion_metrics.sh`

3. **Analisar falhas**  
   - Se um script falhar:
     - Verificar se a causa é:
       - bug introduzido em S28 (modelo/API/ingestão), ou  
       - mudança legítima de contrato que exige atualização do script.  
     - Para bugs de S28: corrigir código, repetir execução.  
     - Para mudanças legítimas: atualizar script + documentação, registrando claramente o porquê.

4. **Rodar script de gate G5**  
   - `bin/s28_g5_observability_and_legacy_sanity.sh`
   - Este script deve:
     - Rodar, em sequência, os scripts de S21/S22 mapeados.  
     - Capturar logs de cada script.  
     - Gerar scorecard consolidando resultado.

##### 4.4.2.3 Evidências de G5

- Pasta de evidências:  
  - `out/evidence/S28_G5_observability_and_legacy_sanity/`
- Conteúdo sugerido:
  - `s21_g1_sources_domain.log`  
  - `s21_g2_sources_api.log`  
  - `s22_g1_ingestion_core.log`  
  - `s22_g2_ingestion_metrics.log`  
  - `summary.log` (resumo geral, opcional).
- Scorecard G5:  
  - `out/scorecards/S28_G5_observability_and_legacy_sanity.json`
  - Campos chave:
    - `gate_id`  
    - `status` (PASS/FAIL)  
    - `scripts_run`  
    - `regressions_detected` (lista ou vazia)  
    - `notes`

Erros a evitar:
- Ignorar falhas de scripts antigos justificando com “mas o novo modelo é melhor” sem atualizar os próprios scripts.  
- Deixar G5 rodar só parcialmente (por exemplo, rodar apenas um subconjunto de scripts).

---

#### 4.4.3 Gate S28_G6 — Demo Interna & UX

**Pergunta que G6 responde:**
> “O console de fontes v2 é utilizável por humanos reais, com fluxos principais funcionando como prometido, e o time registrou evidências dessa demo?”

G6 valida a realidade prática e a experiência humana, não apenas testes automatizados.

---

##### 4.4.3.1 Preparação para a demo

1. **Ambiente**  
   - Backend rodando com migrations de S28 aplicadas.  
   - Frontend buildado e servindo o console de fontes v2.  
   - Ingestão 2.0 com uma forma controlada de disparo (scheduler de teste ou endpoint interno).

2. **Dados**  
   - Banco com algumas fontes de exemplo, ou criação durante a própria demo.  
   - Pelo menos um exemplo de fonte `AUTO+ACTIVE` e outro `AUTO+DISABLED`.

3. **Participantes**  
   - Pelo menos um operador ou pessoa que represente o usuário final do console.  
   - Alguém do backend e alguém do frontend disponíveis para observar e anotar.

4. **Roteiro da demo**  
   - Baseado nos casos A–D:
     - A: criar nova fonte.  
     - B: desativar fonte problemática.  
     - C: reativar fonte após manutenção.  
     - D: editar fonte.
   - Mais cenários: lista vazia, erro de API simulado (se fizer sentido), navegação geral.

---

##### 4.4.3.2 Execução da demo (passo a passo)

1. Apresentar brevemente o objetivo:  
   - "Hoje vamos operar fontes pelo console, ligando/desligando, e verificar se isso reflete na ingestão e se a experiência faz sentido para vocês."

2. Percorrer os fluxos:
   - **Fluxo A – Criar fonte**: participante preenche o formulário sem ajuda, se possível.  
   - **Fluxo B – Desativar**: a partir da lista, desativar uma fonte e discutir o feedback visual.  
   - **Fluxo C – Reativar**: reativar fonte desativada, observar resposta do sistema.  
   - **Fluxo D – Editar**: editar campos da fonte, verificar clareza do formulário.

3. Durante a demo, o time deve observar:
   - Dúvidas recorrentes de UX (campos confusos, labels ruins).  
   - Erros ou respostas lentas.  
   - Pontos de atrito (ex.: falta de confirmação, ausência de mensagens).

4. Registrar tudo em um documento simples:
   - `out/evidence/S28_G6_demo_internal/demo_notes.md`
   - Estrutura sugerida:
     - Participantes.  
     - Data/hora.  
     - Cenários executados.  
     - Problemas encontrados.  
     - Melhorias sugeridas.  
     - Ações que entram no backlog vs. ações que são tratadas ainda na sprint.

---

##### 4.4.3.3 Script e evidências de G6

Script oficial:
- `bin/s28_g6_demo_internal.sh`

Função do script:
- Não "rodar" a demo em si (isso é humano), mas registrar que a demo foi feita e consolidar o scorecard.

Comportamento conceitual:
1. Verificar se o arquivo `demo_notes.md` existe em `out/evidence/S28_G6_demo_internal/`.  
2. Opcionalmente, verificar presença de capturas de tela ou outros anexos.  
3. Gerar scorecard:
   - `out/scorecards/S28_G6_demo_internal.json`
   - Campos sugeridos:
     - `gate_id`: "S28_G6_demo_internal"  
     - `status`: "PASS" | "FAIL"  
     - `participants_count`  
     - `ux_issues_logged`  
     - `must_fix_before_go` (lista de issues P0/P1 de UX, se existirem).

Erros a evitar:
- Fazer a demo "de boca" sem registrar nada.  
- Marcar G6 como PASS sem que um operador real tenha usado o console.

---

#### 4.4.4 Gate S28_G7 — GO/NO_GO Final

**Pergunta que G7 responde:**
> “Com todos os gates anteriores verificados, a Sprint 28 está em estado GO para integração na linha principal (main), com riscos conhecidos e aceitáveis?”

G7 é o gate que transforma uma sprint em algo realmente entregue.

---

##### 4.4.4.1 Pré-condições para G7

Antes de rodar o script de G7, o Sprint Owner deve garantir:

1. Todos os scripts `bin/s28_g0_*.sh`…`bin/s28_g6_*.sh` já foram executados na branch da sprint (local e/ou CI).  
2. Todos os scorecards `S28_G0_*.json`…`S28_G6_*.json` existem em `out/scorecards/`.  
3. Não há gates em FAIL sem plano claro de correção — G7 não é para "esconder" falhas.

---

##### 4.4.4.2 Comportamento do script de G7

Script oficial:
- `bin/s28_g7_go_no_go.sh`

Função do script:
- Ser o orquestrador da decisão final, **não** o decisor solitário.  
- Consolidar scorecards e gerar o resumo da sprint.

Comportamento conceitual:

1. Ler scorecards de G0–G6
   - `out/scorecards/S28_G0_scope_and_baseline.json`  
   - `out/scorecards/S28_G1_sources_model_and_schema.json`  
   - `out/scorecards/S28_G2_sources_admin_api.json`  
   - `out/scorecards/S28_G3_sources_console_front.json`  
   - `out/scorecards/S28_G4_sources_ingestion_integration.json`  
   - `out/scorecards/S28_G5_observability_and_legacy_sanity.json`  
   - `out/scorecards/S28_G6_demo_internal.json`

2. Verificar se todos têm `status = "PASS"`  
   - Se um ou mais gates estiverem `FAIL`, o script deve produzir `S28_overall.status = "NO_GO"` automaticamente.

3. Gerar scorecard consolidado da sprint
   - Arquivo: `out/scorecards/S28_overall.json`
   - Campos sugeridos:
     - `sprint_id`: "S28"  
     - `program`: "Programa 1"  
     - `epic`: "E27.1"  
     - `status`: "GO" | "NO_GO"  
     - `gates`: resumo com id e status de cada gate  
     - `critical_risks`: lista de riscos P0/P1 ainda abertos (se houver)  
     - `owners`: pessoa(s) responsáveis pela decisão  
     - `ci_run_sha`: opcional, SHA do commit validado em CI.

4. Opcionalmente, escrever um resumo em texto simples:  
   - `out/evidence/S28_G7_go_no_go/summary.txt` com o "veredito" humano.

Erros a evitar:
- Forçar status GO no JSON mesmo com gates FAIL (isso quebra o contrato de confiança com o futuro).  
- Deixar G7 depender de inputs manuais dentro do script — as decisões humanas devem ser refletidas **antes**, nos scorecards.

---

#### 4.4.5 Execução local consolidada — comandos-chave

Para quem está na máquina local, o caminho completo de execução da S28 pode ser resumido em blocos.

##### 4.4.5.1 Backend — setup e testes

```bash
# Na raiz do repo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Migrations
alembic upgrade head

# Testes de domínio, API e integração
pytest tests/domain/test_sources_model_invariants.py
pytest tests/api/test_admin_sources_crud_onoff.py
pytest tests/integration/test_sources_ingestion_onoff.py
```

##### 4.4.5.2 Frontend — setup e testes

```bash
cd frontend/inspectah-ui
npm install
npm run build
npm test  # ou comando equivalente configurado (ex.: npm run test:sources)
```

##### 4.4.5.3 Rodar todos os gates da S28

Na raiz do repo:

```bash
bin/s28_g0_scope_and_baseline.sh
bin/s28_g1_sources_model_and_schema.sh
bin/s28_g2_sources_admin_api.sh
bin/s28_g3_sources_console_front.sh
bin/s28_g4_sources_ingestion_integration.sh
bin/s28_g5_observability_and_legacy_sanity.sh
bin/s28_g6_demo_internal.sh   # após realizar a demo
bin/s28_g7_go_no_go.sh
```

Depois disso, conferir em `out/scorecards/`:
- `S28_G0_*.json`…`S28_G6_*.json`  
- `S28_overall.json`

---

#### 4.4.6 CI — Workflow s28-gates

##### 4.4.6.1 Uso no GitHub Actions

Workflow sugerido:  
- Arquivo: `.github/workflows/s28-gates.yml`

Disparos típicos:
- `workflow_dispatch` (manual) na branch da sprint.  
- Opcional: `pull_request` para PRs que unem a branch da sprint em `main`.

Passos principais do job:
1. Checkout do repositório.  
2. Setup de Python e Node (versões alinhadas).  
3. Instalação de dependências (backend e frontend).  
4. Execução sequencial dos scripts `bin/s28_g0_*.sh`…`bin/s28_g7_*.sh`.  
5. Upload de artefatos:
   - `out/evidence/**`  
   - `out/scorecards/**`

Regra de falha:
- Qualquer gate com exit code != 0 faz o job falhar.  
- O status do workflow é usado como insumo direto no ORR da sprint.

##### 4.4.6.2 Ligação com o ORR

- Ao final, o Sprint Owner deve olhar para:
  - Status do workflow s28-gates.  
  - Conteúdo de `S28_overall.json`.  
  - Logs de evidências relevantes.
- O commit (SHA) que passou no CI com S28_overall = GO é, na prática, o "build de referência" da Sprint 28.

---

#### 4.4.7 Checklist final de GO/NO_GO

Antes de declarar a Sprint 28 como GO, o Sprint Owner (com o time) deve percorrer esta lista:

1. **Gates & Scorecards**  
   - [ ] G0–G7 com `status = "PASS"`.  
   - [ ] `S28_overall.json` com `status = "GO"`.  
   - [ ] Sem gates ignorados ou pulados.

2. **Domínio & API**  
   - [ ] Modelo `Source` refletindo todos os campos e enums acordados.  
   - [ ] `/admin/sources` oferecendo CRUD & ON/OFF completo, com testes de API em PASS.  
   - [ ] Transições de estado proibidas realmente bloqueadas.

3. **Ingestão 2.0**  
   - [ ] Scheduler usando `mode` + `state` como critérios duros de elegibilidade.  
   - [ ] Testes de integração ON/OFF em PASS.  
   - [ ] Nenhum caso conhecido de fonte `DISABLED` sendo ingerida.

4. **Console de Fontes v2 & UX**  
   - [ ] Fluxos A–D utilizáveis por um operador sem intervenção de dev.  
   - [ ] Testes de UI/e2e em PASS.  
   - [ ] Demo interna realizada com notas e issues registradas.

5. **Legado & Observabilidade**  
   - [ ] Scripts críticos de S21/S22 rodando em PASS com S28 aplicada.  
   - [ ] Qualquer mudança inevitável documentada e atualizada nos scripts.  
   - [ ] Sem regressões P0/P1 abertas.

6. **Documentação & Evidências**  
   - [ ] Cap. 1–4 revisados para refletir o sistema atual (sem divergências gritantes).  
   - [ ] Evidências organizadas em `out/evidence/S28_G*/**`.  
   - [ ] Resultado do CI (s28-gates) referenciado no histórico da sprint.

Se, após esse checklist, ainda houver dúvidas ou riscos não endereçados, o estado correto é **NO_GO**, seguido de um plano de correção.  
Se tudo estiver alinhado, a Sprint 28 passa a fazer parte da história oficial do Inspectah como a sprint que consolidou **CRUD & ON/OFF de fontes** com console, API e ingestão falando a mesma língua.

---

Com este Bloco 4, o Capítulo 4 da Sprint 28 fica completamente fechado: G5–G7 detalhados, execução local/CI consolidada e um checklist objetivo para GO/NO_GO, transformando a especificação em um roteiro de execução confiável e auditável de ponta a ponta.

