# Inspectah — Sprint 28
## Capítulo 4 — Bloco 3
### Plano Detalhado por Gate (G3, G4) — Frontend & Integração ON/OFF × Ingestão

---

#### 4.3.1 Objetivo deste bloco

Este bloco mergulha no plano de execução dos gates intermediários da Sprint 28:

- **S28_G3 — Sources Console Front**  
- **S28_G4 — Sources Ingestion Integration (ON/OFF × Ingestão 2.0)**

Aqui, a pergunta é: **como sair de um repositório com backend pronto (G1+G2) para um console utilizável e uma ingestão obediente ao ON/OFF, com tudo provado por testes?**

A resposta vem em forma de:
- tarefas concretas,  
- ordem de ataque recomendada,  
- comandos típicos,  
- estrutura de evidências,  
- riscos específicos de cada gate.

---

#### 4.3.2 Gate S28_G3 — Sources Console Front

**Pergunta que G3 responde:**
> “O Console de Fontes v2 entrega, de forma estável e testada, os fluxos principais de operação de fontes (CRUD & ON/OFF), usando a Admin API como fonte de verdade?”

G3 valida que o frontend não é só uma camada decorativa, mas sim uma ferramenta operacional real.

---

##### 4.3.2.1 Escopo funcional de G3

Fluxos mínimos que o console precisa cobrir, alinhados aos casos A–D da sprint:

1. **Cadastro de nova fonte (Caso A)**  
   - Abrir página de lista (`SourcesListPage`).  
   - Navegar para formulário (`SourceFormPage`).  
   - Preencher dados básicos + config mínima.  
   - Salvar e ver a nova fonte aparecer na lista.

2. **Desativar fonte problemática (Caso B)**  
   - A partir da lista, usar `SourceActionsMenu` para desativar fonte `ACTIVE`.  
   - Ver `SourceStateBadge` mudar para `DISABLED`.

3. **Reativar fonte após manutenção (Caso C)**  
   - A partir de fonte `DISABLED`, usar `SourceActionsMenu` para reativar.  
   - Ver estado voltar para `ACTIVE`.

4. **Editar fonte (Caso D)**  
   - Abrir detalhe/edição de uma fonte existente.  
   - Atualizar campos de operação (ex.: cadência, criticidade, descrição).  
   - Salvar e verificar mudança na listagem e/ou detalhe.

5. **Estados extremos de UI**  
   - Lista vazia (nenhuma fonte cadastrada).  
   - Erro de API (ex.: backend off) tratado com mensagem amigável.

---

##### 4.3.2.2 Tarefas concretas para G3 (por camada do front)

1. **Páginas**
   - `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`
     - Conectar com `adminSourcesApi.listSources`.  
     - Receber filtros (type, state, domain, mode, criticality) e enviar para API.  
     - Montar tabela com `SourceListTable`.  
     - Tratar estados: loading, erro, vazio.

   - `frontend/inspectah-ui/src/features/sources/pages/SourceFormPage.tsx`
     - Suportar modo criação e edição (ex.: via param de rota `sourceId`).  
     - Na criação: usar `adminSourcesApi.createSource`.  
     - Na edição: buscar dados com `adminSourcesApi.getSource` e salvar via `updateSource`.  
     - Validar campos obrigatórios (nome, tipo, mode, config mínima).  
     - Exibir erros por campo e toasts de sucesso/erro.

2. **Componentes**
   - `SourceListTable.tsx`
     - Receber lista de fontes tipada (`SourceListItem[]`).  
     - Renderizar colunas: Nome, Tipo, Domínio, Modo, Estado, Criticidade, Última alteração, Ações.  
     - Integrar `SourceStateBadge` e `SourceActionsMenu` em colunas apropriadas.

   - `SourceStateBadge.tsx`
     - Receber `state` (`ACTIVE`, `DISABLED`, `DEPRECATED`).  
     - Mapear para rótulos e estilos (usando Design System Admin v1).  
     - Manter lógica visual simples e declarativa.

   - `SourceActionsMenu.tsx`
     - Receber callbacks para ações: ver, editar, ativar, desativar, deprecar.  
     - Exibir/ocultar ações de acordo com estado atual (ex.: não oferecer “Ativar” se já está `ACTIVE`).  
     - Tratar confirmação para ações destrutivas (ex.: `confirm('Deseja realmente desativar?')`).  
     - Disparar loading/disabled enquanto requisição está em andamento.

3. **Cliente de API**
   - `frontend/inspectah-ui/src/features/sources/api/adminSourcesApi.ts`
     - Implementar funções:
       - `listSources(filters)`,  
       - `getSource(id)`,  
       - `createSource(payload)`,  
       - `updateSource(id, payload)`,  
       - `activateSource(id)`,  
       - `disableSource(id)`,  
       - `deprecateSource(id)`.  
     - Garantir que os tipos usados aqui batem com os DTOs do backend (`SourceListItem`, `SourceDetail`, etc.).  
     - Tratar erros e traduzi-los para exceções ou objetos que o front consiga exibir.

4. **Integração com rotas globais**
   - Adicionar entradas de rota no app principal do frontend, ex.:
     - `/admin/sources` → `SourcesListPage`.  
     - `/admin/sources/new` → `SourceFormPage` (criação).  
     - `/admin/sources/:sourceId` → `SourceFormPage` (edição).

---

##### 4.3.2.3 Testes de UI / e2e para G3

Arquivo central:
- `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`

Cenários recomendados:

1. **Happy path de criação**
   - Navegar para `/admin/sources`.  
   - Clicar em "Nova Fonte".  
   - Preencher formulário com dados válidos.  
   - Ver novo item aparecer na tabela com estado `ACTIVE`.

2. **Desativar fonte**
   - Partindo de fonte `ACTIVE`.  
   - Abrir `SourceActionsMenu`, clicar em “Desativar”.  
   - Confirmar ação.  
   - Ver `SourceStateBadge` mostrar `DISABLED`.

3. **Reativar fonte**
   - Partindo de fonte `DISABLED`.  
   - Usar ação “Ativar”.  
   - Ver estado voltar a `ACTIVE`.

4. **Editar fonte**
   - Entrar na tela de edição.  
   - Alterar, por exemplo, `criticality` e `description`.  
   - Salvar e verificar alteração na UI.

5. **Erros & lista vazia**
   - Simular retorno vazio da API e verificar mensagem adequada.  
   - Simular erro 500 e verificar mensagem de falha amigável.

Esses testes podem usar mocks da API ou backend real, conforme padrão do projeto, mas precisam rodar dentro do script de gate.

---

##### 4.3.2.4 Script, comandos e evidências de G3

Script oficial:
- `bin/s28_g3_sources_console_front.sh`

Comportamento esperado (conceitual):

1. **Preparar ambiente**
   - Garantir que dependências do front estão instaladas:  
     - `cd frontend/inspectah-ui`  
     - `npm install` (pode ser assumido já feito em passo anterior, mas o script deve ser idempotente).

2. **Rodar testes e build**
   - `npm test` (ou comando customizado para testes de UI/e2e).  
   - `npm run build` para garantir que o console compila.

3. **Registrar evidências**
   - Redirecionar logs de testes e build para:  
     - `out/evidence/S28_G3_sources_console_front/test.log`  
     - `out/evidence/S28_G3_sources_console_front/build.log`

4. **Gerar scorecard**
   - `out/scorecards/S28_G3_sources_console_front.json` com campos como:
     - `gate_id`,  
     - `status`,  
     - `tests_run`,  
     - `build_ok`,  
     - `known_ui_issues`.

Erros comuns a evitar:
- Testes muito frágeis (quebrando por detalhes irrelevantes de layout).  
- Deixar o console “funcionar” manualmente, mas sem validação automatizada de flows A–D.  
- Esquecer de atualizar rotas globais, deixando o console inacessível via navegação normal.

---

#### 4.3.3 Gate S28_G4 — Sources Ingestion Integration (ON/OFF × Ingestão 2.0)

**Pergunta que G4 responde:**
> “Quando o operador liga ou desliga uma fonte no console/API, a Ingestão 2.0 obedece essa decisão de forma determinística e comprovada?”

G4 é o teste de realidade da Sprint 28: ON/OFF não é só um botão bonito, é um comando que muda o comportamento da ingestão.

---

##### 4.3.3.1 Escopo funcional de G4

Cenários mínimos que devem ser verdade no sistema (também detalhados em Cap. 2 e Cap. 3):

1. **Fonte AUTO+ACTIVE é ingerida automaticamente**  
   - Fonte criada com `mode = AUTO` e `state = ACTIVE`.  
   - Scheduler roda → pelo menos um `IngestionRun` é criado para essa fonte.

2. **Fonte DESATIVADA deixa de ser ingerida**  
   - Fonte `ACTIVE` é desativada (`state = DISABLED`).  
   - Scheduler roda → nenhum novo `IngestionRun` é criado a partir da desativação.

3. **Fonte reativada volta a ser ingerida**  
   - Fonte `DISABLED` é reativada (`state = ACTIVE`).  
   - Scheduler roda → `IngestionRun` volta a ser criado.

4. **Fonte MANUAL nunca entra na ingestão automática**  
   - Fonte `mode = MANUAL`, `state = ACTIVE`.  
   - Scheduler roda → essa fonte não entra na lista de elegíveis para ingestão automática.

---

##### 4.3.3.2 Tarefas concretas para G4 (backend)

1. **Atualizar scheduler para respeitar `mode` + `state`**
   - Arquivo principal: `app/ingestion/scheduler.py` (ou serviço equivalente).  
   - Implementar função clara para selecionar fontes elegíveis, ex.:

```python
# pseudo-código conceitual

def get_auto_eligible_sources(db_session):
    return (
        db_session.query(Source)
        .filter(Source.mode == SourceMode.AUTO)
        .filter(Source.state == SourceState.ACTIVE)
        # + filtros herdados de S22, se existirem
        .all()
    )
```

   - Garantir que essa função seja o único ponto de verdade para seleção de fontes automáticas.

2. **Integrar com criação de `IngestionRun`**
   - Arquivo(s): `app/ingestion/models.py` (para `IngestionRun`), eventualmente `app/ingestion/services.py`.  
   - Para cada fonte elegível, criar `IngestionRun` com:
     - `source_id`,  
     - `status` inicial (`PENDING`/`QUEUED`),  
     - timestamps adequados.

3. **Evitar atalhos que bypassam o domínio**
   - Scheduler não deve alterar `Source.state`.  
   - Scheduler não deve ignorar `state` por conveniência (ex.: “rodar ignore state para debug” dentro do código de produção).

---

##### 4.3.3.3 Testes de integração para G4

Arquivo central:
- `tests/integration/test_sources_ingestion_onoff.py`

Aspectos fundamentais dos testes:

1. **Usar a Admin API para criar/mutar fontes**
   - Não setar `Source` diretamente no banco.  
   - Criar fontes via `/admin/sources` (POST).  
   - Mudar estado via rotas de ON/OFF (`/activate`, `/disable`, `/deprecate`).

2. **Controlar o scheduler explicitamente**
   - Expor, em modo teste, uma função do tipo `run_scheduler_cycle(db_session)` para rodar um ciclo de ingestão sob demanda.  
   - Evitar depender de cron real ou workers externos nos testes.

3. **Verificar `IngestionRun` antes e depois de cada ação**
   - Ao criar fonte `ACTIVE+AUTO`, rodar scheduler e checar ao menos um `IngestionRun` para aquele `source_id`.  
   - Ao desativar fonte, rodar scheduler e verificar que **nenhum novo** `IngestionRun` surgiu após o timestamp de desativação.  
   - Ao reativar fonte, verificar que novos `IngestionRun` passam a ser criados.  
   - Para fonte `MANUAL`, verificar que nenhum `IngestionRun` é criado em ciclos normais.

4. **Isolamento entre cenários**
   - Cada cenário de teste deve usar banco limpo (fixtures).  
   - Evitar compartilhamento de estado que possa poluir resultados.

---

##### 4.3.3.4 Script, comandos e evidências de G4

Script oficial:
- `bin/s28_g4_sources_ingestion_integration.sh`

Comportamento esperado (conceitual):

1. **Preparar ambiente**
   - Ativar venv e configurar `PYTHONPATH=.`.  
   - Garantir que o banco de desenvolvimento/teste esteja migrado (`alembic upgrade head`).

2. **Rodar testes de integração**
   - Comando típico:

```bash
pytest tests/integration/test_sources_ingestion_onoff.py
```

3. **Registrar evidências**
   - Logs completos de pytest →  
     - `out/evidence/S28_G4_sources_ingestion_integration/tests.log`
   - Opcionalmente, dumps auxiliares (ex.: conteúdo de tabela `IngestionRun` para cenário de demo).

4. **Gerar scorecard**
   - Arquivo: `out/scorecards/S28_G4_sources_ingestion_integration.json`
   - Campos sugeridos:
     - `gate_id`: "S28_G4_sources_ingestion_integration"  
     - `status`: "PASS" | "FAIL"  
     - `scenarios_covered`: ["AUTO_ACTIVE", "DISABLED_STOP", "REACTIVATE_RESUME", "MANUAL_IGNORED"]  
     - `regressions_detected`: lista ou vazia.

Erros comuns a evitar:
- Rodar testes de integração criando/mutando fontes direto no banco, sem passar pela API.  
- Deixar o scheduler usar filtros inconsistentes com o modelo (`state` usado em um lugar, ignorado em outro).  
- Testes que passam apenas em ambiente muito específico (ex.: dependendo de ordem exata de logs ou de delays).

---

#### 4.3.4 Relação entre G3 e G4 na execução da sprint

Embora G3 (frontend) e G4 (integração ON/OFF × ingestão) possam ser trabalhados em paralelo por squads diferentes, existe uma ordem lógica para estabilização:

1. Backend (G1+G2) precisa estar minimamente estável antes de testes sérios de UI e ingestão.  
2. G4 depende de G2 para criar/mutar fontes via API; por isso, G2 deve chegar em PASS ou quase-PASS antes de considerar G4 pronto.  
3. G3 precisa de G2 estável para que o console não vire fonte de erros falsos.

Uma sequência prática é:

- Backend consolida G1 e G2.  
- Em paralelo, frontend inicia implementação de telas usando mocks de API.  
- Assim que G2 estabiliza, G3 e G4 passam a usar a mesma Admin API real.  
- No fim, G3 e G4 andam juntos:  
  - G3 prova que o operador tem como ligar/desligar.  
  - G4 prova que a ingestão obedece.

---

Com este Bloco 3, o Capítulo 4 da Sprint 28 detalha a execução dos gates **S28_G3** (console de fontes v2) e **S28_G4** (integração ON/OFF × ingestão 2.0), transformando arquitetura em passos de implementação, testes, scripts e evidências. O Bloco 4 fecha o capítulo cobrindo G5–G7, execução local/CI e o checklist final de GO/NO_GO da sprint.

