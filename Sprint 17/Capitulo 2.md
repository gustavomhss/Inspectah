# Sprint 17 — Capítulo 2 (Refatorado)
## Gates, Validação e Definition of Done da UI de Consulta

### 1. Papel deste capítulo na Sprint 17

O Capítulo 1 definiu **o porquê** da Sprint 17: entregar a primeira UI de consulta do Inspectah para qualquer pessoa conseguir perguntar algo, ver resposta, risco e um recorte de evidências.  
Este Capítulo 2 define **como sabemos que isso realmente aconteceu**.

Aqui, Bret Victor e Kent C. Dodds, junto com o restante da equipe, transformam a visão em uma **matriz de gates T0…T8**, cada um com:

- objetivo claro;
- perguntas que ele responde;
- escopo de checagens (automáticas e manuais);
- artefatos obrigatórios (scorecards, evidências, docs);
- critérios objetivos de GO/NO_GO.

Nada na Sprint 17 é considerado “pronto” se não couber em algum gate deste capítulo. Se Capítulos 1, 3 ou 4 trouxerem algo que não se encaixa em T0…T8, essa coisa está errada, fora de escopo ou mal especificada.

---

### 2. Mapa de Gates da Sprint 17

Os gates seguem a espinha dorsal T0…T8 usada no restante do projeto, mas especializados para **UI de consulta**:

- **T0 — Sanidade de ambiente de frontend**  
  Projeto existe, instala, builda e roda em ambiente limpo.

- **T1 — Contratos UI↔API e estados de UI**  
  A UI é função explícita de estados (idle/loading/success/error) e conversa com um contrato de consulta bem definido.

- **T2 — UX mínima, acessibilidade básica e estados vazios**  
  A experiência de uso e acessibilidade não são gambiarras; estados vazios e mensagens base estão corretos.

- **T3 — Integração real UI ↔ backend de consulta**  
  O front fala com o backend de verdade (ou stub oficial), lida corretamente com sucesso, incerteza e erros.

- **T4 — Golden Flows de consulta e casos de demonstração**  
  Casos canônicos (risco baixo, alto, incerteza) funcionam e são demonstráveis, sempre do mesmo jeito.

- **T5 — Performance percebida e tamanho de bundle (v1)**  
  A UI reage rápido o suficiente e o bundle inicial não é um monstro.

- **T6 — Observabilidade leve de front**  
  Erros e eventos críticos de consulta deixam rastro; ninguém fica cego quando algo quebra.

- **T7 — CI, testes e reprodutibilidade**  
  Build, lint, testes e checks da S17 rodam em pipeline confiável (local + CI).

- **T8 — Go/No-Go humano da Sprint 17**  
  Decisão explícita, com commits, scorecards e riscos documentados.

Cada gate terá:

- um script de entrada (por exemplo, `bin/s17_t2_ux_and_accessibility.sh`);
- um **scorecard** em JSON em `out/scorecards/S17_T*_*.json`;
- uma pasta de evidências em `out/evidence/S17_T*_*/*`.

O Capítulo 3 vai detalhar filemap e scripts; o Capítulo 4, o plano de execução. Aqui cravamos **o contrato de validação**.

---

### 3. Gate S17_T0 — Sanidade de ambiente e baseline de front

**Pergunta-chave:** “Temos um ambiente de frontend saudável para desenvolver, rodar e testar a UI de consulta?”

#### 3.1 Objetivo

Garantir que qualquer pessoa do time consiga, em ambiente limpo:

- instalar dependências de front;
- rodar build;
- subir o dev server;
- executar o pacote mínimo de testes de front;
- sem esbarrar em surpresas básicas (segredo faltando, path quebrado, script ausente).

#### 3.2 Escopo

- Existência do projeto de front (ex.: `frontend/inspectah-ui/`).
- Scripts básicos funcionando:
  - `npm install` / `pnpm install` / `yarn` (o que for padronizado);
  - `npm run build`;
  - `npm run dev` (ou equivalente);
  - `npm run test` (mesmo que com poucos testes no início).
- Variáveis de ambiente mínimas documentadas (`.env.example`) para apontar para o backend de consulta local.
- Nenhum segredo critico hardcoded em front.

#### 3.3 Artefatos e evidências

- Script: `bin/s17_t0_sanity.sh`.
- Scorecard: `out/scorecards/S17_T0_sanity.json` contendo:
  - status PASS/FAIL;
  - comandos executados;
  - códigos de saída;
  - links para logs em `out/evidence/S17_T0_sanity/`.
- Evidências:
  - logs de instalação, build, dev server/check;
  - captura de saída de testes básicos.

#### 3.4 Critérios de GO

- Build de front concluído com sucesso em ambiente limpo.  
- Script de sanity retorna exit 0.  
- Testes mínimos de front (mesmo se poucos) passando.  
- Não há dependência de segredos não documentados para rodar localmente.  

Falha em T0 = bloqueio total dos demais gates da S17.

---

### 4. Gate S17_T1 — Contratos UI↔API e estados de UI

**Pergunta-chave:** “A UI de consulta é uma função clara do estado, e o contrato com o backend está explícito?”

#### 4.1 Objetivo

Formalizar e testar:

- o contrato entre a UI e o endpoint de consulta do Inspectah;  
- a máquina de estados da UI (idle → loading → success/error), de forma que a tela nunca fique em “estado fantasma”.

#### 4.2 Escopo

- Definição de um tipo/shape para a resposta de consulta no front (por exemplo, `ConsultationResult`), mapeado a partir do JSON do backend (Sprints anteriores).  
- Modelagem explícita de estados de UI, por exemplo:
  - `idle` (nenhuma consulta enviada ainda);
  - `submitting` (consulta em andamento);
  - `success` (resposta com risco/evidências);
  - `error` (erro de rede/backend ou contrato inválido);
  - opcionalmente, um subtipo de “incerto” quando o backend sinaliza incerteza.
- Comportamento da UI para cada estado:
  - visual distinto e claro em idle, loading, success e error;
  - nenhum estado sem representação (ex.: loading invisível).
- Tratamento de responses malformados (contrato quebrado) com fallback controlado para `error`.

#### 4.3 Artefatos e evidências

- Script: `bin/s17_t1_contracts_and_states.sh`.
- Scorecard: `out/scorecards/S17_T1_contracts_and_states.json` com:
  - resumo dos estados definidos;
  - verificação de que os tipos/contratos existem em código;
  - resultados de testes associados.
- Evidências:
  - testes unitários/integrados (React Testing Library ou similar) exercitando estados:
    - renderização em `idle`;
    - transição para `submitting` ao enviar consulta;
    - renderização em `success` com resposta fictícia (fixture);
    - renderização em `error` com fixture de erro/response inválido;
  - docs com o contrato UI↔API (por exemplo, seção em `docs/sprint_17_overview.md`).

#### 4.4 Critérios de GO

- Estados de UI definidos explicitamente em código (não “emergentes”).
- Pelo menos um teste automatizado para cada estado principal.
- Contrato de resposta documentado, com campos usados pela UI (resposta, risco, evidências, metadados).  
- Scorecard T1 marcado como PASS, com links para fixtures e testes.

---

### 5. Gate S17_T2 — UX mínima, acessibilidade básica e estados vazios

**Pergunta-chave:** “Uma pessoa real consegue entender o que fazer, usar a tela e não se perder, mesmo sem dados?”

#### 5.1 Objetivo

Garantir que a UI não seja só “um form que envia JSON”, mas uma tela em que:

- a proposta do Inspectah é comunicada em segundos;
- a pessoa entende onde digitar e o que esperar;
- estados vazios são claros e não confusos;
- acessibilidade básica não foi ignorada.

#### 5.2 Escopo

- **Texto de orientação inicial**  
  Presença de heading e parágrafo explicando em linguagem simples o que o Inspectah faz e o que o usuário pode perguntar.

- **Formulário de consulta acessível**  
  - input com label associado e descrição opcional;  
  - botão de submit com texto claro;  
  - envio com Enter funcionando corretamente;  
  - foco de teclado respeitado (tab order previsível).

- **Estados vazios**  
  - tela inicial (nenhuma consulta realizada) com mensagem neutra e convite à ação;  
  - casos de “sem evidências exibíveis” com aviso discreto;  
  - casos de “sem dados suficientes” com mensagem honesta.

- **Acessibilidade básica**  
  - uso de HTML semântico (headings, regions, form);  
  - contraste aceitável em texto e principalmente em indicadores de risco;  
  - foco visível em elementos interativos;  
  - uso de `aria-*` apenas quando necessário (sem poluição).

#### 5.3 Artefatos e evidências

- Script: `bin/s17_t2_ux_and_accessibility.sh`.
- Scorecard: `out/scorecards/S17_T2_ux_and_accessibility.json` com:
  - checklist de UX mínimo preenchido (por exemplo, por PO + front + alguém de QA);
  - checklist de acessibilidade básica (inspirado em WCAG core simplificado);
  - referência a testes automatizados (quando existirem) para empty states.
- Evidências:
  - capturas de tela dos estados principais (idle, pós-primeira consulta, erro);
  - logs de testes de UI (RTL) para estados vazios.

#### 5.4 Critérios de GO

- Checklists de UX e acessibilidade básica marcados como “OK”, com eventuais débitos documentados e aceitos conscientemente.
- Nenhum problema grave: tela sem instrução, input sem label, foco invisível, texto completamente ilegível.
- Scorecard T2 com PASS.

---

### 6. Gate S17_T3 — Integração UI ↔ backend de consulta

**Pergunta-chave:** “A UI conversa de verdade com o backend de consulta, lidando bem com sucesso, incerteza e erros?”

#### 6.1 Objetivo

Provar que a UI de S17 não depende de mocks ou sonhos: ela chama o endpoint oficial de consulta, entende suas respostas, e sobrevive a falhas normais (erros 4xx/5xx, timeouts, payload inesperado dentro do razoável).

#### 6.2 Escopo

- Configuração de endpoint de consulta (URL base, path) para ambiente local.  
- Mapeamento do request (pergunta + contexto mínimo) para o payload esperado pelo backend.  
- Tratamento dos tipos de resposta:
  - sucesso com dados e evidências;
  - sucesso com dados escassos / incerteza (backend sinaliza risco alto ou “não sei”);
  - erro de cliente (ex.: 4xx);
  - erro de servidor (5xx);
  - falha de rede/timeout.

- Atualização da UI de acordo com o estado retornado pela API:
  - `success` com renderização de resposta + risco + recorte de evidências;
  - `error` com mensagem amigável;  
  - `incerto` (quando existir) com sinalização clara.

#### 6.3 Artefatos e evidências

- Script: `bin/s17_t3_api_integration.sh`.
- Scorecard: `out/scorecards/S17_T3_api_integration.json` com:
  - rastreio dos cenários testados (sucesso, incerteza, erro, timeout);
  - status PASS/FAIL;
  - links para fixtures de resposta (quando usados em testes).  
- Evidências:
  - testes integrados com backend stub/real (por exemplo, usando MSW ou equivalente para simular respostas);
  - logs de uma sessão real de consulta contra backend local.

#### 6.4 Critérios de GO

- Todos os cenários listados exercitados e documentados.
- Nenhum caso em que erro do backend causa página em branco ou quebrada.
- Mensagens de erro compreensíveis do ponto de vista do usuário.
- Scorecard T3 com PASS.

---

### 7. Gate S17_T4 — Golden Flows de consulta e casos de demonstração

**Pergunta-chave:** “Temos casos canônicos de consulta que funcionam sempre e contam bem a história do Inspectah?”

#### 7.1 Objetivo

Definir e consolidar **3–5 casos canônicos** que servirão como:

- demo oficial da UI de consulta;  
- base para regressão visual/funcional em sprints futuras;  
- amostra da capacidade do sistema em diferentes domínios e níveis de risco.

#### 7.2 Escopo

- Escolher, alinhado com Debunker/Comitês e com os fixtures existentes (ciencia, clima, esporte, fofoca, mandatos, politica, projetos), casos que cubram:
  - um cenário com risco baixo e evidências robustas (ex.: fato bem documentado);
  - um cenário com risco alto ou conflito (ex.: informação controversa ou muito recente);
  - um cenário de “não sei / informação insuficiente”.

- Para cada caso canônico:
  - definir texto da pergunta;  
  - documentar o que se espera, em alto nível, da resposta (tipo, risco, exemplos de evidências);
  - garantir que a UI se comporte conforme esperado.

#### 7.3 Artefatos e evidências

- Script: `bin/s17_t4_golden_flows.sh`.
- Scorecard: `out/scorecards/S17_T4_golden_flows.json` com:
  - lista dos casos canônicos;
  - status de cada caso (PASS/FAIL);
  - link para evidências (capturas, fixtures, roteiros).
- Evidências:
  - doc com roteiros de demo (passo a passo);
  - capturas de tela dos casos canônicos;
  - opcionalmente, testes automatizados que, dado fixture de resposta, checam a renderização de UI.

#### 7.4 Critérios de GO

- Pelo menos 3 casos canônicos definidos, cobrindo baixo risco, alto risco/incerteza e “não sei”.
- Todos os casos canônicos funcionando de ponta a ponta (envio de consulta → resposta na UI) em ambiente local.
- Scorecard T4 marcado como PASS, com anotações claras de quaisquer limitações.

---

### 8. Gate S17_T5 — Performance percebida e tamanho de bundle (v1)

**Pergunta-chave:** “A UI de consulta é rápida o suficiente para não parecer travada, e o bundle não é absurdo para um v1?”

#### 8.1 Objetivo

Medir e documentar o mínimo de performance:

- tempo de feedback para o usuário depois de clicar em “Consultar”;  
- tempo até resposta em casos canônicos;  
- tamanho do bundle inicial de front.

#### 8.2 Escopo

- **Feedback de loading:**  
  - tempo entre clique em “Consultar” e aparição de estado de loading deve ser curto (por exemplo, alvo: < 200 ms em ambiente local);
  - nenhum caminho em que o usuário clique e a tela pareça morta.

- **Tempo de resposta percebido:**  
  - usar os casos canônicos (T4) para medir tempo entre clique e resposta renderizada;
  - registrar valores médios em ambiente local controlado.

- **Tamanho de bundle:**  
  - medir tamanho do bundle inicial gerado pelo build;
  - identificar dependências grandes e anotar se são realmente necessárias.

#### 8.3 Artefatos e evidências

- Script: `bin/s17_t5_performance_and_bundle.sh`.
- Scorecard: `out/scorecards/S17_T5_performance_and_bundle.json` com:
  - métricas medidas (feedback de loading, tempo de resposta, tamanho de bundle);
  - comparação com limites-alvo definidos para S17;
  - status PASS/FAIL.
- Evidências:
  - logs ou relatórios simples com tempos medidos;
  - saída de ferramentas de build (tamanho de bundles).

#### 8.4 Critérios de GO

- Feedback de loading visível em tempo aceitável (sem clique “morto”).
- Tempo de resposta percebido aceitável em casos canônicos (sem travamentos evidentes).
- Bundle inicial dentro de limites acordados para S17 (mesmo que não ideais para fase futura de escala).
- Scorecard T5 com PASS e débitos de performance, se houver, documentados.

---

### 9. Gate S17_T6 — Observabilidade leve de front

**Pergunta-chave:** “Se a UI de S17 começar a se comportar mal, teremos pelo menos algum rastro para investigar?”

#### 9.1 Objetivo

Iniciar a camada de observabilidade de frontend, alinhada à visão da S16, sem antecipar toda a complexidade da S20. A ideia é:

- capturar erros críticos de UI;  
- registrar eventos de uso importantes;  
- evitar vazamento de dados sensíveis em logs.

#### 9.2 Escopo

- **Error boundaries:**  
  - presença de um error boundary em torno da área de consulta e resultado;  
  - exibição de fallback amigável quando algo quebra na renderização.

- **Logs estruturados de eventos-chave:**  
  - envio de consulta;
  - sucesso de consulta;
  - erro de consulta (network/backend/contrato);
  - opcional: eventos de “sem dados suficientes”.

- **Sinal de correlação com backend:**  
  - quando possível, uso de um id de requisição/consulta fornecido pelo backend para correlacionar logs de front e back.

- **Privacidade:**  
  - não logar conteúdo completo de respostas sensíveis;  
  - não incluir no log dados desnecessários (ex.: payload inteiro, tokens, etc.).

#### 9.3 Artefatos e evidências

- Script: `bin/s17_t6_frontend_observability.sh`.
- Scorecard: `out/scorecards/S17_T6_frontend_observability.json` com:
  - descrição dos pontos de observabilidade implementados;
  - exemplo de logs gerados em cenários de sucesso e erro;
  - verificação de que não há dados sensíveis óbvios sendo logados.
- Evidências:
  - capturas de logs reais (anônimos/sanitizados) para consultas de teste;
  - pequena anotação de como esses logs podem ser usados pelo time.

#### 9.4 Critérios de GO

- Error boundary ativo e testado (erro forçado → fallback amigável + log).  
- Eventos críticos (consulta enviada/ sucesso/ erro) gerando logs estruturados.  
- Nenhum payload sensível sendo jogado bruto em log.  
- Scorecard T6 com PASS.

---

### 10. Gate S17_T7 — CI, testes e reprodutibilidade

**Pergunta-chave:** “Conseguimos rodar os checks da S17 de forma reprodutível, local e em CI, sem depender de sorte?”

#### 10.1 Objetivo

Amarrar a S17 à disciplina do projeto: nada de front que só funciona “na máquina de alguém”.

#### 10.2 Escopo

- Workflow de CI específico (ou estendido) para frontend da S17, por exemplo:
  - `.ci/sprint_17_gates.yml` rodando T0…T5/T6 em PR/main;
  - `.ci/sprint_17_nightly.yml` podendo rodar subset de testes periodicamente.

- Execução, em CI:
  - instalação de dependências;
  - lint de front;
  - testes de front (T1, T2, T3, T4, T5 onde aplicável);
  - build de produção.

- Instruções claras para rodar os mesmos checks localmente (documentadas em `docs/sprint_17_overview.md`).

#### 10.3 Artefatos e evidências

- Script: `bin/s17_t7_ci_and_repro.sh` (pode acionar o workflow localmente ou simular steps).  
- Scorecard: `out/scorecards/S17_T7_ci_and_repro.json` com:
  - referência ao workflow de CI;
  - resultado da última execução conhecida (commit SHA);
  - status PASS/FAIL.
- Evidências:
  - logs de uma execução real de CI;
  - comandos para rodar os mesmos checks localmente.

#### 10.4 Critérios de GO

- Workflow de CI de front configurado, rodando e verde no commit alvo da S17.  
- Qualquer falha de lint/test/build em CI quebra a integração (não é ignorada).  
- Scorecard T7 com PASS, incluindo SHA de referência.

---

### 11. Gate S17_T8 — Go/No-Go humano da Sprint 17

**Pergunta-chave:** “Sabemos, como time, que é aceitável colocar esta UI de consulta na frente de outras pessoas?”

#### 11.1 Objetivo

Registrar uma decisão explícita (GO, GO_WITH_RESTRICTIONS ou NO_GO) sobre a S17, consolidando:

- estado dos gates T0…T7;  
- percepção qualitativa de UX (Bret, Kent, PO);  
- riscos conhecidos e débitos aceitos.

#### 11.2 Escopo

Ritual simples, mas obrigatório, envolvendo pelo menos:

- alguém da engenharia de backend;  
- alguém de frontend (representando Bret e Kent);  
- alguém de produto/PO.

Durante a sessão:

1. Rodar (ou revisar) `bin/s17_all_gates.sh` para garantir que T0…T7 estão verdes.  
2. Passar pelos casos canônicos de T4, ao vivo, na UI.  
3. Verificar rapidamente estados de erro e empty state (T2, T3).  
4. Revisar scorecards T0…T7.  
5. Decidir: GO, GO_WITH_RESTRICTIONS ou NO_GO.  
6. Registrar razões, riscos e próximos passos.

#### 11.3 Artefatos e evidências

- Script: `bin/s17_t8_go_no_go.sh` (agregador dos scorecards T0…T7 + decisão humana).  
- Scorecard: `out/scorecards/S17_T8_go_no_go.json` com:
  - decisão final;
  - commit SHA da S17 (frontend);
  - resumo de riscos e restrições;
  - referência aos scorecards T0…T7.
- Doc humano: `docs/sprint_17_orr_summary.md` com wrap executivo da S17:
  - objetivo da sprint;
  - resumo dos gates T0…T8;
  - decisão GO/GO_WITH_RESTRICTIONS/NO_GO;
  - próximos passos recomendados.

#### 11.4 Critérios de GO

- Todos os scorecards T0…T7 com status PASS.  
- Scorecard T8 com decisão GO ou GO_WITH_RESTRICTIONS, com restrições claramente anotadas (ex.: “apenas uso interno / alpha”).  
- `docs/sprint_17_orr_summary.md` atualizado com commit SHA e decisão.

---

### 12. Definition of Done da Sprint 17 (vista pelos gates)

A S17 só é considerada concluída quando:

1. `bin/s17_all_gates.sh` roda em ambiente limpo e todos os scorecards `S17_T0…T8` estão com PASS (T8 podendo ser GO ou GO_WITH_RESTRICTIONS).  
2. Existe uma UI de consulta onde:
   - uma pessoa não técnica entende o que pode fazer;
   - consegue perguntar, ver resposta, risco e evidências;
   - recebe mensagens claras em estados vazios e de erro.
3. O front de S17 é reprodutível (dev local + CI) e tem ao menos um nível mínimo de testes e observabilidade.  
4. Casos canônicos de consulta estão definidos, funcionando e documentados.  
5. Há um resumo humano (ORR da S17) que qualquer pessoa do time consegue ler para entender o que a Sprint 17 entregou, quais são os riscos e o que vem na S18–S20.

Este Capítulo 2 é o centro de gravidade da S17: **Capítulo 1 diz o que queremos, Capítulo 2 define como saberemos que chegamos lá.** Os Capítulos 3 e 4 existem para implementar estes gates, não o contrário.

