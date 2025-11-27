# Sprint 24 – Debunker v0 & Humano-no-Loop
## Capítulo 2.4 – Plano de validação manual dos gates de qualidade

### 1. Objetivo deste subcapítulo

Este subcapítulo descreve, em nível operacional e auditável, **como validar manualmente** todos os gates de qualidade definidos para a Sprint 24 (listados e detalhados em 2.1, 2.2 e 2.3), garantindo que:

- As verificações automáticas (testes, scorecards, métricas) estejam corretamente configuradas, interpretadas e confiáveis.
- O comportamento real do sistema Debunker v0 + humano-no-loop, observado via UI e Truth-DB, esteja alinhado com os critérios de GO/NOGO definidos para cada gate.
- Cada execução de gate relevante possa ser **reproduzida** (mesmo ambiente, mesmos dados, mesmos passos) e **auditada** (evidências claras, armazenadas em locais conhecidos e estruturados).

O escopo aqui é exclusivamente **procedimental**: o que o time faz, em qual ordem, usando quais comandos/telas, produzindo quais evidências mínimas para considerar o gate como "validado manualmente".

---

### 2. Pré-requisitos gerais de validação

Antes de executar qualquer roteiro específico, o time deve validar que as seguintes condições globais estão satisfeitas:

1. **Ambiente e serviços**
   - Backend Inspectah instalado via `pip install -e .` ou equivalente, com `python-multipart` e demais dependências já resolvidas (conforme pyproject.toml).  
   - Virtualenv ativo (`source .venv/bin/activate`) e `PYTHONPATH=.` exportado na raiz do repositório Inspectah.  
   - Serviços necessários executando:
     - API principal (`uvicorn inspectah.api:app ...`) ou equivalente usado nos testes de S24.  
     - Banco de dados configurado e migrado (scripts de migração da S24 executados).  
   - Frontend `inspectah-ui` com dependências instaladas (`npm ci`) e build executável (`npm run build`) sem erros.

2. **Dados de teste mínimos para Debunker v0**
   - Conjunto de **cases de teste** cobrindo, no mínimo, os seguintes tipos (podem ser gerados via seeds da S23/S24 ou scripts de cenário):
     - Claims factuais simples (ex.: "Número de habitantes de país X em ano Y").  
     - Claims políticos controversos com múltiplas fontes conflitantes.  
     - Claims com evidência fraca/ambígua que devem disparar "dados insuficientes".  
     - Claims claramente falsos com evidências sólidas em sentido contrário.  
   - Para cada case de teste, existir um identificador estável (ex.: `case_id = noticia:2025-123-fake`, `claim_id = claim:12345`) para facilitar rastreio na UI e no Truth-DB.

3. **Acesso às ferramentas de observabilidade**
   - Acesso ao painel de logs/métricas definido na S19/S20 (ou equivalente) para inspecionar:
     - Eventos de DebunkIssue (criação, atualização, fechamento).  
     - Eventos de DebunkDecision (estado anterior, estado novo, analista, rationale, evidências ligadas).  
   - Acesso a consultas no banco (SQL ou abstração do Truth-DB) para verificar a persistência correta de TruthRecords/TruthChangeEvents ligados aos casos da S24.

4. **Papel e responsabilidades durante a validação**
   - Pelo menos 3 papéis explícitos durante a execução dos roteiros:
     - **Executor técnico**: roda scripts, comandos, CI local, coleta logs.  
     - **Analista Debunker**: exerce o papel do humano-no-loop na UI, toma decisões e escreve rationales.  
     - **Auditor de qualidade**: verifica se as evidências geradas atendem aos critérios dos gates (2.2) e se os scorecards estão consistentes (2.3).

---

### 3. Roteiro manual por tipo de gate

Nesta seção descrevemos, em alto nível mas de forma operacional, como validar manualmente cada família de gates da S24. Os nomes/IDs exatos dos gates são os definidos em 2.1; aqui usamos rótulos genéricos para não duplicar especificação.

#### 3.1 Gates de integridade de ingestão e triagem para Debunker (Gates T0/T1)

Objetivo: garantir que **da ingestão até a criação das DebunkIssues** tudo funciona conforme as regras da S23/S24.

Passos manuais típicos:

1. **Preparar cenário controlado**
   - Popular o ambiente com um conjunto pequeno (5–10) de casos de teste, misturando os tipos de claims listados em 2.2 (fáceis, ambíguos, controversos, claramente falsos).  
   - Garantir que o pipeline de ingestão da S23 esteja ativo (ou simulado via scripts) para gerar os claims e eventuais flags de incerteza.

2. **Rodar o gate automatizado**
   - Executar o script/gate correspondente (ex.: `bash bin/s24_g0_...` ou similar definido em 2.1).  
   - Verificar saída do script e scorecard em `out/scorecards/S24_G0_*.json` ou equivalente.

3. **Verificação manual via UI (triagem)**
   - Acessar a tela de DebunkIssues (desenhada em S24 Cap. 1 e detalhada em 24_macro_v2).  
   - Confirmar, para cada caso de teste, que:
     - Existe uma DebunkIssue criada quando deveria existir.  
     - Issues não são criadas para casos que não atendem aos critérios (evitar over-flag).  
     - Campos obrigatórios (estado inicial, prioridade, origem, reason) estão preenchidos conforme regras de 2.2.

4. **Verificação via banco/Truth-DB**
   - Rodar consultas que listem DebunkIssues criadas no intervalo de tempo da validação.  
   - Verificar se as issues correspondem 1:1 aos eventos esperados do pipeline de ingestão (sem duplicidade, sem perda).

5. **Evidências mínimas a capturar**
   - Screenshot ou gravação de tela mostrando a lista de DebunkIssues para o conjunto de testes, com filtros aplicados.  
   - Dump textual (SQL ou API) das issues criadas, anexado em `out/evidence/S24_G0_*`.  
   - Comentário curto do Auditor explicitando se o comportamento observado está aderente às regras definidas (ou registrando divergências).

#### 3.2 Gates de fluxo de trabalho humano-no-loop (Gates T2/T3)

Objetivo: validar que o **ciclo completo de trabalho do analista** (abrir issue, ler evidências, decidir, registrar rationale e outcome) funciona sem ruídos, e que as transições de estado estão corretas.

Passos manuais típicos:

1. **Seleção de casos para validação**
   - Escolher pelo menos um case de cada tipo de cenário mapeado em 2.2 (fácil, difícil, ambíguo, falso óbvio).  
   - Garantir que todos estejam presentes como DebunkIssues nas filas da UI.

2. **Execução do fluxo na UI (por analista Debunker)**
   - Para cada caso de teste:
     - Abrir a issue na UI de Debunker.  
     - Navegar pelas evidências associadas (links, documentos, snippets, sinais de ingestão).  
     - Tomar uma decisão explícita (ex.: CONFIRMED_TRUE, CONFIRMED_FALSE, INSUFFICIENT_EVIDENCE, NEEDS_MORE_RESEARCH), escrevendo um rationale claro.  
     - Checar se a UI exige ligação entre a decisão e pelo menos uma evidência (como projetado na S24 macro).

3. **Verificação via logs e métricas**
   - Confirmar que eventos de `DebunkDecision` aparecem nos logs com:
     - `issue_id`, `decision_type`, `analyst_id`, `timestamp`.  
     - Referência a claims/evidências (IDs) quando exigido.  
   - Conferir painel de métricas de S24 para ver contadores de decisões por tipo e fila de backlog.

4. **Verificação via Truth-DB**
   - Para cada decisão registrada, verificar se:
     - Foi gerado um `TruthChangeEvent` com o estado correto (e.g., de UNDER_REVIEW → ESTABLISHED_FACT ou UNDER_DISPUTE).  
     - O `TruthRecord` mais recente reflete a decisão humana tomada (sem delay ou somente com o delay previsto em 2.3).  
   - Garantir que **nenhuma** decisão humana fique "pendurada" sem refletir em Truth-DB.

5. **Evidências mínimas a capturar**
   - Screenshot ou gravação de tela do fluxo completo de uma issue complexa (abrir → ler → decidir → salvar).  
   - Export de logs contendo os eventos de DebunkDecision correspondentes.  
   - Dump do estado de TruthRecords/TruthChangeEvents antes/depois da decisão para pelo menos 2 casos complexos.

#### 3.3 Gates de consistência entre Debunker, Timeline e XRay (Gates T4/T5)

Objetivo: garantir que as decisões do Debunker se **propaguem corretamente** para as timelines e visões XRay do Inspectah, sem inconsistências visuais ou semânticas.

Passos manuais típicos:

1. **Preparação de um caso com múltiplos eventos**
   - Escolher um caso de timeline rico (ex.: obra pública com vários marcos, ou cronologia de um político).  
   - Garantir que existam claims associados a múltiplos eventos dessa timeline, com estados de verdade distintos (factual, controverso, em disputa).

2. **Aplicar decisões Debunker**
   - A partir das DebunkIssues correspondentes, tomar decisões variadas (confirmar, negar, marcar como insuficiente, reabrir disputa) sobre 3–5 claims da mesma timeline.

3. **Verificar Timeline UI**
   - Abrir a timeline do caso e checar se:
     - Os eventos impactados pelo Debunker mudaram de cor/estado/sinalização conforme o design definido na S19/S24.  
     - Os tooltips ou painéis de detalhes exibem o estado de verdade atual, com indicação de que houve decisão humana (vs apenas LLM).  
     - Em nenhum ponto a timeline mostra estado contraditório (ex.: card dizendo "confirmado" mas painel lateral indicando "em disputa").

4. **Verificar XRay UI**
   - Abrir a visão XRay para o mesmo caso.  
   - Confirmar que a visão "profunda" (incluindo ligações com evidências e decisões) está alinhada com o que foi visto na timeline e no Truth-DB.  
   - Verificar que as decisões antigas permanecem auditáveis (histórico de mudanças), e que a decisão atual está claramente destacada.

5. **Evidências mínimas a capturar**
   - Screenshots comparativos da timeline antes/depois das decisões Debunker.  
   - Screenshot do XRay mostrando a mesma decisão humana refletida no grafo/visão detalhada.  
   - Dump do estado de Truth-DB para os claims envolvidos, demonstrando coerência entre camadas.

#### 3.4 Gates de resiliência, erro humano e auditoria (Gates T6/T7/T8)

Objetivo: testar cenários de **erro humano, rollback, disputa e auditoria**, validando que o Debunker v0 não permite corrupção fácil de estados de verdade.

Passos manuais típicos:

1. **Simular decisões contraditórias**
   - Criar cenário onde dois analistas diferentes tomam decisões conflitantes para o mesmo claim (em momentos distintos).  
   - Verificar na UI se o sistema:
     - Registra ambas as decisões no histórico.  
     - Destaca qual é a decisão vigente.  
     - Sinaliza a existência de conflito/revisão (ex.: badge "revisado", "decisão alterada").

2. **Simular erro e correção**
   - Analista 1 toma uma decisão claramente errada (em acordo com o PO, apenas para teste).  
   - Analista 2 entra posteriormente, reabre ou corrige a decisão com rationale detalhado.  
   - Validar que:
     - A correção não apaga o registro anterior; apenas adiciona novo TruthChangeEvent.  
     - O estado final de Truth-DB reflete a decisão corrigida.  
     - Logs e métricas registram esse ciclo de erro/correção.

3. **Auditoria de trilha completa**
   - Escolher um caso complexo e tentar reconstruir a história de decisões Debunker apenas a partir de:
     - Logs de eventos.  
     - Truth-DB (TruthRecords/TruthChangeEvents).  
     - UI (timeline/XRay/DebunkIssues).  
   - Validar se é possível responder, de forma inequívoca:
     - Quem decidiu o quê, quando, com base em quais evidências.  
     - Qual era o estado de verdade antes e depois de cada decisão.  
     - Se houve disputas e como foram resolvidas.

4. **Evidências mínimas a capturar**
   - Relato textual estruturado (em markdown) reconstituindo a linha do tempo de decisões de um caso complexo, anexado em `out/evidence/S24_G7_*`.  
   - Export de logs + snapshot de Truth-DB usados para essa reconstrução.  
   - Anotação do Auditor indicando se algum ponto da trilha foi ambíguo ou impossível de reconstruir (insumo para melhorias de S25).

---

### 4. Check-list final de validação manual da S24

Para considerar a Sprint 24 **GO** do ponto de vista de validação manual dos gates, o time deve conseguir marcar todos os itens abaixo como verdadeiros, com evidências guardadas:

1. Todos os gates definidos em 2.1 têm **roteiro manual mínimo** descrito ou referenciado neste subcapítulo.  
2. Para cada tipo de gate (ingestão/triagem, workflow humano, consistência com timeline/XRay, resiliência/auditoria), existe pelo menos um **cenário completo executado** em ambiente de validação.  
3. Os scorecards mencionados em 2.3 foram lidos e interpretados em conjunto com as evidências manuais, e não existe divergência entre o que a automação diz e o que a equipe observou na prática.  
4. Todos os materiais de evidência (screenshots, dumps de logs, exports de Truth-DB, relatos de auditoria) estão armazenados nas pastas padrão `out/evidence/S24_G*` e são facilmente reexecutáveis ou reproduzíveis.  
5. A equipe de produto, o Squad Verdade & Interpretação e o Conselho (quando acionado) concordam que:
   - O Debunker v0 + humano-no-loop se comporta, na prática, de acordo com o modelo de verdade definido por Judea Pearl.  
   - A camada de armazenamento e consulta (Stonebraker + Norvig) suporta a auditoria e a explicabilidade necessárias.  
   - Os comitês e agentes (Percy) estão devidamente cercados por trilhas de evidência e mecanismos de correção de erro humano.

Somente quando este check-list estiver **integralmente atendido** e devidamente evidenciado é que a Sprint 24 pode ser considerada **GO** do ponto de vista de validação manual dos gates de qualidade.

