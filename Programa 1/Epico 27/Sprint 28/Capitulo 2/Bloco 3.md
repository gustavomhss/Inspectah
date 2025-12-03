# Inspectah — Sprint 28
## Capítulo 2 — Bloco 3
### Gates S28_G3, S28_G4 e S28_G5 (Console, Integração ON/OFF × Ingestão e Sanidade de Legado)

---

#### 2.3.1 Gate S28_G3 — Sources Console Front (Console de Fontes v2)

**Objetivo do gate**  
Garantir que o **console de fontes v2** é um instrumento de operação real, não um protótipo frágil. Isso significa:
- front-end funcional e estável,  
- acoplado corretamente à API de admin `/admin/sources`,  
- alinhado ao Design System Admin v1 (E26),  
- com fluxos principais (casos A–D) cobertos por testes.

S28_G3 responde à pergunta: “Um operador consegue, pela UI, executar o dia a dia de fontes sem abrir terminal?”

**Script oficial**  
`bin/s28_g3_sources_console_front.sh`

**Arquivos de referência (entrada esperada)**
- **Páginas principais**  
  - `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`  
  - `frontend/inspectah-ui/src/features/sources/pages/SourceFormPage.tsx`

- **Componentes**  
  - `frontend/inspectah-ui/src/features/sources/components/SourceListTable.tsx`  
  - `frontend/inspectah-ui/src/features/sources/components/SourceStateBadge.tsx`  
  - `frontend/inspectah-ui/src/features/sources/components/SourceActionsMenu.tsx`  
  - (outros componentes auxiliares conforme filemap do Cap. 3)

- **API Client**  
  - `frontend/inspectah-ui/src/features/sources/api/adminSourcesApi.ts`

- **Testes de UI / e2e**  
  - `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`  
  - (eventuais arquivos adicionais divididos por fluxo, desde que organizados)

**Responsabilidades do script**
1. Rodar testes e build do frontend:
   - `cd frontend/inspectah-ui`  
   - `npm test` (ou `npm run test:sources` se houver target específico)  
   - `npm run build`
2. Validar convenções mínimas de Design System Admin v1:
   - checar se componentes-base vêm de `@/components/ui/...` ou padrão equivalente,  
   - garantir que não há import massivo de estilos customizados fora do padrão sem justificativa.
3. Garantir que os testes de UI cobrem fluxos principais (casos A–D, conforme Cap. 1).  
4. Gerar scorecard:  
   - `out/scorecards/S28_G3_sources_console_front.json`

**Fluxos mínimos que devem estar cobertos pelos testes de UI**
- **Fluxo 1 — Cadastro de nova fonte RSS (Caso A)**  
  - Abrir lista de fontes.  
  - Clicar em “Nova Fonte”.  
  - Preencher campos obrigatórios (tipo, domínio, categoria, URL, modo, cadência, criticidade).  
  - Submeter formulário e ver nova fonte na lista.

- **Fluxo 2 — Desativar fonte problemática (Caso B)**  
  - Localizar fonte específica na lista (ex.: busca por nome).  
  - Usar `SourceActionsMenu` para acionar “Desativar”.  
  - Confirmar mudança visual de estado (`ACTIVE` → `DISABLED`).

- **Fluxo 3 — Reativar fonte após manutenção (Caso C)**  
  - Partindo de fonte `DISABLED`, acionar “Reativar”.  
  - Ver estado voltar a `ACTIVE` e, opcionalmente, etiqueta de última mudança de estado.

- **Fluxo 4 — Editar fonte existente (Caso D)**  
  - Acessar tela de edição de fonte.  
  - Ajustar campos permitidos (ex.: cadência, descrição, domínio).  
  - Submeter e verificar persistência das alterações.

- **Fluxos de robustez**  
  - Lista vazia (nenhuma fonte cadastrada) com estado vazio amigável.  
  - Erro na API (ex.: backend indisponível) com mensagem ao usuário.

**Campos mínimos do scorecard S28_G3**
- `gate_id`: "S28_G3_sources_console_front"  
- `status`: "PASS" | "FAIL"  
- `flows_covered`: lista textual dos fluxos de UI cobertos  
- `frontend_build_ok`: boolean  
- `ds_violations`: lista de violações ao Design System (idealmente vazia ou com exceções claramente justificadas)  
- `open_ux_issues`: lista de problemas de UX não-bloqueantes, se houver

**Critérios de PASS**
- `npm test` e `npm run build` em estado PASS.  
- Fluxos A–D cobertos por testes de UI, sem falhas.  
- Console visualmente alinhado ao Design System Admin v1 (sem "ilhas" visuais estranhas).  
- Scorecard gerado e coerente.

**Critérios de FAIL**
- Falha em build ou testes de frontend.  
- Falta de automação para fluxos canônicos.  
- Console exigindo hacks (como abrir DevTools ou mexer em storage) para operar cenários comuns.  
- Uso sistemático de componentes customizados que ignoram o design system sem justificativa documentada.

**Impacto do FAIL**
- Bloqueia percepção de “operável via console”.  
- Mesmo que modelo e API estejam corretos, a sprint não pode ser declarada GO se o console de fontes não for utilizável.

---

#### 2.3.2 Gate S28_G4 — Sources × Ingestão 2.0 (ON/OFF Integration)

**Objetivo do gate**  
Demonstrar, com testes de integração, que o estado de uma fonte (`ACTIVE`/`DISABLED`) controla de forma normativa o comportamento da **Ingestão 2.0**. Nada de ambiguidades.

S28_G4 responde à pergunta: “Se eu desligar uma fonte no console/API, o motor de ingestão respeita isso sempre?”

**Script oficial**  
`bin/s28_g4_sources_ingestion_integration.sh`

**Arquivos de referência (entrada esperada)**
- **Lógica de ingestão**  
  - `app/ingestion/scheduler.py` (ou módulo equivalente onde ocorre o agendamento por fonte)  
  - qualquer serviço/helper que filtra fontes elegíveis para ingestão.

- **Testes de integração**  
  - `tests/integration/test_sources_ingestion_onoff.py`

**Responsabilidades do script**
1. Preparar ambiente de teste mínimo (por exemplo, banco em memória ou test DB).  
2. Executar `pytest tests/integration/test_sources_ingestion_onoff.py`.  
3. Coletar logs ou prints de `IngestionRun` para evidência.  
4. Gerar scorecard:  
   - `out/scorecards/S28_G4_sources_ingestion_integration.json`

**Cenários que DEVEM estar cobertos em teste**

- **Cenário 1 — Fonte ativa ingere normalmente**  
  - Criar uma fonte com estado `ACTIVE`, modo `AUTO`, tipo válido.  
  - Rodar ciclo(s) do scheduler.  
  - Verificar que pelo menos um `IngestionRun` é criado para a fonte.

- **Cenário 2 — Desativar fonte interrompe ingestão**  
  - Partindo do cenário 1, desativar a fonte via API (`/disable`).  
  - Rodar mais ciclos do scheduler.  
  - Confirmar ausência de novos `IngestionRun` para essa fonte a partir da desativação.

- **Cenário 3 — Reativar fonte retoma ingestão**  
  - Do estado `DISABLED`, reativar a fonte (`/activate`).  
  - Rodar o scheduler novamente.  
  - Confirmar que novos `IngestionRun` voltam a ser criados.

- **Cenário 4 — Fontes em modo MANUAL**  
  - Garantir que fontes `MANUAL` não sejam ingeridas automaticamente, mesmo se `ACTIVE`.  
  - (Opcional se não fizer parte de E27.1, mas desejável como teste de proteção.)

**Detalhes importantes dos testes**
- Devem usar **as mesmas rotas** de admin (`/admin/sources/...`) para criar e mudar estado de fontes, não caminhos “paralelos” ou fixtures mágicas que não representem uso real.  
- A coleta de `IngestionRun` pode acontecer via:  
  - consulta direta ao banco de teste,  
  - API interna, se existir,  
  - logs com IDs de execução.

**Campos mínimos do scorecard S28_G4**
- `gate_id`: "S28_G4_sources_ingestion_integration"  
- `status`: "PASS" | "FAIL"  
- `scenarios`: lista dos cenários executados (1–4) com flag de sucesso  
- `evidence_paths`: caminhos para logs ou arquivos auxiliares usados como evidência  
- `notes`: observações (ex.: limitações do ambiente de teste, hipóteses assumidas)

**Critérios de PASS**
- Todos os cenários essenciais (1–3) executados com sucesso; 4 executado se parte do escopo.  
- Nenhum caso em que fonte `DISABLED` seja ingerida em ciclo posterior.  
- Log/narrativa dos testes deixa clara a sequência: criar → ingerir → desativar → parar → reativar → retomar.

**Critérios de FAIL**
- Qualquer evidência de ingestão acontecendo com fonte `DISABLED`.  
- Necessidade de "mexer no ambiente" manualmente (ex.: desligar worker na unha) para que ON/OFF se comporte como esperado.  
- Ausência de cenários completos: testar só o lado “feliz” (`ACTIVE`) não é suficiente.

**Impacto do FAIL**
- Bloqueia GO da sprint: sem ON/OFF determinístico, o módulo de fontes continua oferecendo risco operacional.  
- Deve ser tratado como bug de **prioridade máxima** dentro da sprint.

---

#### 2.3.3 Gate S28_G5 — Observability & Legacy Sanity (S21/S22)

**Objetivo do gate**  
Garantir que a evolução da S28 **não quebrou** capacidades já entregues em S21 e S22 relacionadas a fontes e ingestão. A sprint não pode deixar um rastro de regressões silenciosas.

S28_G5 responde à pergunta: “Depois da S28, tudo o que já funcionava em S21/S22 continua funcionando?”

**Script oficial**  
`bin/s28_g5_observability_and_legacy_sanity.sh`

**Arquivos de referência (entrada esperada)**
- Scripts de gates anteriores:
  - `bin/s21_g1_sources_domain.sh`  
  - `bin/s21_g2_sources_api.sh`  
  - `bin/s22_g1_ingestion_core.sh`  
  - `bin/s22_g2_ingestion_metrics.sh`  
  - (ou conjunto equivalente de scripts oficiais dessas sprints)

- Eventuais configs de observabilidade (logs/metrics) que existam nas sprints anteriores.

**Responsabilidades do script**
1. Executar os gates de S21/S22 relacionados a fontes e ingestão, na versão mais recente do código (já com S28 aplicada).  
2. Coletar resultados, logs e resumos de métricas básicas, quando aplicável.  
3. Identificar regressões em:
   - comportamento funcional (ex.: endpoints que deixam de responder, mudanças quebrando contratos),  
   - mínimos acordos de observabilidade (ex.: logs essenciais sumidos).  
4. Gerar scorecard:  
   - `out/scorecards/S28_G5_observability_and_legacy_sanity.json`

**Itens que DEVEM ser verificados**
- **Scripts de S21**  
  - Modelo de fontes ainda satisfaz invariantes que S21 esperava.  
  - API antiga de fontes (se ainda existir) responde conforme contrato, ou foi deprecada de forma controlada (com docs).

- **Scripts de S22**  
  - Ingestão core continua funcional com o novo modelo de fonte.  
  - Métricas básicas de ingestão (contagem de runs, erro/sucesso) continuam sendo produzidas.

- **Observabilidade mínima**  
  - Logs referentes a ingestão por fonte não desapareceram totalmente.  
  - Se houve mudança de formato de log, ela foi documentada.

**Campos mínimos do scorecard S28_G5**
- `gate_id`: "S28_G5_observability_and_legacy_sanity"  
- `status`: "PASS" | "FAIL"  
- `legacy_gates_run`: lista com resultado de cada script S21/S22 executado  
- `regressions_detected`: lista (idealmente vazia) com descrição de cada regressão encontrada  
- `mitigation_plan`: se houver regressão, plano sucinto para correção dentro da própria sprint

**Critérios de PASS**
- Todos os scripts S21/S22 relevantes executados com `PASS`.  
- Nenhuma regressão funcional crítica detectada.  
- Alterações inevitáveis em comportamento legado (se existirem) documentadas, com justificativa e migração clara.

**Critérios de FAIL**
- Qualquer gate de S21/S22 em FAIL como consequência direta das mudanças de S28.  
- Regressões críticas não endereçadas dentro da sprint.  
- Perda de observabilidade mínima (deixar o time “cego” sobre ingestão/ fontes).

**Impacto do FAIL**
- Impede que S28 seja considerada estável: sprint que avança um módulo e destrói funcionalidades antigas não é GO.  
- Até que regressões sejam tratadas, S28_G5 deve ser mantido em FAIL e usado como sinal vermelho para a equipe.

---

Com os gates S28_G3, S28_G4 e S28_G5 detalhados, o Bloco 3 do Capítulo 2 cobre todo o eixo **UI (console)** + **comportamento do sistema (ON/OFF × ingestão)** + **proteção de legado**. O próximo bloco fecha o Capítulo 2 com:
- S28_G6 (Demo Interna & UX),  
- S28_G7 (GO/NO_GO Final),  
- métricas da sprint,  
- e a Definition of Done global consolidada.