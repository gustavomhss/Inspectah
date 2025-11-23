# Inspectah — Sprint 18
## Capítulo 1 — Visão, contexto e escopo do Console de Admin

> Arquivo alvo no repositório: `Sprint 18/Capitulo 1.md`  
> Domínio: Frontend — Console de Admin (Fontes, Casos/Temas, Saúde Operacional)

---

### 1. Resumo executivo

A Sprint 18 dá ao Inspectah o que ele ainda não tem: um **cockpit de operação**.

Depois de S10–S16 (motor endurecido, Truth‑DB, Debunker, Sistema de Blocos, ingestão contínua) e S17 (primeira UI de **consulta para usuário final**), o produto já responde “o que é verdade?” para quem pergunta. Mas continua praticamente **cego para quem opera**: entender se o sistema está saudável exige abrir logs, scorecards ou JSON de evidência.

A Sprint 18 entrega o **Console de Admin** — uma área dedicada da mesma SPA, focada em **leitura, diagnóstico e confiança operacional**. Ela permite que um operador responda, em segundos, às perguntas:

- “O Inspectah está saudável agora?”
- “Quais fontes estão caindo ou se comportando mal?”
- “Quais casos/temas exigem atenção hoje?”

Sem reinventar backend, sem criar caminhos de canetada e sem misturar as fronteiras da Truth‑DB. O Console de Admin é **read‑heavy, write‑light**: expõe estados já consolidados pelo motor (Truth‑DB, Debunker, Comitês, Sistema de Blocos), não inventa verdades nem altera blocos direto da UI.

No fim da Sprint 18, um operador deve ser capaz de **abrir `/admin` e, em menos de 1 minuto, entender a situação do Inspectah** sem precisar de terminal, logs ou scorecards brutos.

---

### 2. Posição da Sprint 18 no roadmap

#### 2.1 De onde viemos

- **S10–S16 (backbone do motor)**  
  - Truth‑DB e Sistema de Blocos definidos, com blocos, sub‑blocos e evidências.  
  - Debunker, Comitês e regras de contestação/estabilização funcionando em v0.  
  - Ingestão contínua, watchers e scorecards produzindo sinais de saúde.

- **S17 (Consulta)**  
  - Primeira UI para usuário final: pergunta → resposta consolidada → evidências mínimas.  
  - Stack de frontend consolidada (React + Vite + Tailwind, SPA única).  
  - Porta de entrada para o Inspectah como produto de consulta.

Hoje, temos um motor robusto e uma frente de consulta funcionando, mas **sem visão operacional de alto nível**.

#### 2.2 Para onde vamos

- **S18 (esta sprint)** — Console de Admin: visão operacional de fontes, casos/temas e saúde do sistema.  
- **S19** — Timeline & Raio‑X: mergulho profundo em blocos, sub‑blocos, decisões do Debunker/Comitês, trilhas de evidência e linha do tempo por caso/tema.  
- **S20** — Polimento & Hardening de Front: UX, responsividade, auth básica endurecida, observabilidade de frontend, estados de loading/erro bem desenhados.

S17 responde “o que está acontecendo no mundo?”.  
S18 responde “o que está acontecendo dentro do Inspectah?”.  
S19 aprofunda a explicação do “porquê”.  
S20 deixa tudo pronto para ser mostrado sem vergonha.

---

### 3. Problema e perguntas que a S18 precisa responder

Sem o Console de Admin, o time vive em modo escuro:

- Para saber se o sistema está saudável, alguém precisa **abrir scorecards, logs ou métricas cruas**.
- Para descobrir que uma fonte crítica está caindo, é preciso **perceber sintomas a posteriori** (respostas estranhas, erros em ingestão) em vez de ver um painel claro.
- Para entender quais casos/temas estão “pegando fogo” (contestação intensa, dados frágeis), é preciso **conhecimento interno do motor**, não do produto.

A Sprint 18 existe para garantir que, ao final dela, o Console de Admin responda pelo menos às perguntas:

1. **Saúde geral**  
   - Quantas fontes estão saudáveis vs degradadas/caindo?  
   - Quantos casos/temas estão em estado estável vs em atenção/contestação?  
   - Existem integrações críticas em estado de alerta?

2. **Fontes**  
   - Quais são as fontes cadastradas e seus tipos?  
   - Qual o status atual de cada fonte (ativa/inativa, saudável/degradada)?  
   - Quando foi a última execução/checagem relevante e qual o resultado?  
   - Há um histórico curto de falhas recentes visível sem abrir logs?

3. **Casos/Temas**  
   - Que casos/temas o Inspectah acompanha hoje?  
   - Qual o estado atual de cada caso (estável, em contestação, com dados frágeis, monitoramento especial)?  
   - Qual o nível agregado de risco/controvérsia (quando o backend expõe esse sinal)?  
   - Quais são as principais fontes/evidências sustentando o estado atual (visão agregada, não timeline completa)?

Se a UI não conseguir responder isso de forma direta, a Sprint 18 fracassou como produto — mesmo que o código “compile”.

---

### 4. Objetivos da Sprint 18

#### 4.1 Objetivo macro

Colocar no ar um **Console de Admin do Inspectah**, dentro da mesma SPA da S17, que permita a um operador:

- enxergar rapidamente a **saúde geral do sistema**;  
- inspecionar **fontes** e **casos/temas** com contexto suficiente para tomada de decisão;  
- fazer tudo isso **sem precisar sair da UI** para olhar artefatos técnicos.

#### 4.2 Objetivos específicos

1. Criar uma rota/tela de admin (ex.: `/admin`) com navegação clara entre **Visão Geral**, **Fontes** e **Casos/Temas**.
2. Expor, na Visão Geral, KPIs simples porém úteis de saúde (fontes saudáveis vs degradadas, casos em atenção, integrações críticas).
3. Implementar o módulo de **Fontes** (lista + detalhe) com filtros básicos e histórico curto de saúde por fonte.
4. Implementar o módulo de **Casos/Temas** (lista + detalhe) com estado atual, risco agregado e principais fontes/evidências associadas.
5. Integrar o front a **endpoints de admin** do backend (fontes, casos, health) de forma segura e alinhada aos contratos do Sistema de Blocos/Truth‑DB.
6. Reforçar a arquitetura de frontend da S17, criando uma **zona bem delimitada para admin** (páginas, componentes e camada de API própria), pronta para S19/S20 escalarem.
7. Documentar como **subir, usar e demonstrar** o Console de Admin para qualquer dev/operador do time.

---

### 5. Escopo funcional (visão de Capítulo 1)

#### 5.1 O que ENTRA na Sprint 18

1. **Rota e layout de Admin**
   - Rota dedicada (ex.: `/admin`) na mesma SPA.  
   - Estrutura de navegação com três pilares: **Visão Geral**, **Fontes**, **Casos/Temas**.  
   - Mecanismo simples de proteção (gate por ambiente/flag), já preparando o terreno para auth real em S20.

2. **Visão Geral (Health)**
   - Cards com contagens, por exemplo:  
     - Fontes ativas saudáveis vs degradadas/inativas.  
     - Casos/temas em estado estável vs em atenção/contestação.  
     - Status resumido de integrações críticas (â ncoras/chain, ingestores principais, workers).  
   - Indicação visual clara (verde/amarelo/vermelho) de estado geral do sistema.

3. **Módulo de Fontes**
   - Lista de fontes com: identificador/nome, tipo, status atual, última atualização relevante e, quando disponível, um indicador simples de confiabilidade/prioridade.  
   - Filtros por status (saudável/degradada, ativa/inativa) e, idealmente, por tipo de fonte.  
   - Tela de detalhe de fonte com:  
     - metadados principais;  
     - histórico curto das últimas execuções/checagens (timestamp + resultado);  
     - visão agregada de erros recentes (ex.: contagem nas últimas N execuções).  
   - Espaços marcados para ações futuras (reprocessar, editar, reconfigurar), **sem funcionalidade ativa** nesta sprint.

4. **Módulo de Casos/Temas**
   - Lista de casos/temas com: identificador, título, categoria/vertical, estado atual e timestamp de última atualização relevante.  
   - Exposição de um indicador agregado de risco/controvérsia, quando o backend já o fornecer.  
   - Filtros por categoria e por estado (estável / em atenção / em contestação / dados frágeis).  
   - Tela de detalhe com:  
     - resumo textual do caso/tema;  
     - estado atual e motivo principal;  
     - principais fontes/evidências associadas (ex.: top 3–5 ancoragens) em visão agregada.  
   - Indicação explícita de que a **timeline completa** e o raio‑X detalhado virão na S19.

5. **Integração com sinais de saúde do backend**
   - Consumo de endpoints equivalentes a:  
     - `GET /admin/sources` e `GET /admin/sources/{id}`;  
     - `GET /admin/cases` e `GET /admin/cases/{id}`;  
     - `GET /admin/health` ou equivalente para KPIs agregados.  
   - Tradução de sinais técnicos (watchers, scorecards, estados WARN/FAIL) em linguagem de produto (fontes em atenção, casos em contestação, etc.).

6. **Arquitetura de frontend e documentação**
   - Pastas claras para código de admin (por exemplo, `src/pages/admin/`, `src/components/admin/`, `src/api/admin/`).  
   - Reuso de componentes base (layout, tipografia, temas) da S17.  
   - Documentação mínima de arquitetura e contratos para o front de admin.

#### 5.2 O que NÃO ENTRA

1. **Edição direta de dados sensíveis**
   - Nada de CRUD completo de fontes, blocos, estados de casos, parâmetros de risco ou políticas do Debunker/Comitês.  
   - Qualquer mutação relevante continua passando pelos guard rails do backend (Anti‑canetada, Âncoras, Comitês, Sistema de Blocos).

2. **Timeline detalhada e raio‑X profundo**
   - S18 não entrega timeline por caso/tema nem drill‑down em blocos, sub‑blocos, decisões individuais do Debunker ou votos de Comitês.  
   - Esses elementos são **escopo explícito** da S19.

3. **Tuning de parâmetros de sistema pela UI**
   - Ficam fora: ajustes de thresholds, políticas de contestação, parâmetros de ingestão, configuração de watchers.  
   - A UI de admin é observacional nesta fase.

4. **Auth/autorização completa**
   - A Sprint 18 não implementa login, papéis ou perfis diferenciados.  
   - Um gate mínimo por ambiente/flag é suficiente até S20.

5. **Dashboard BI/analytics pesado**
   - Sem gráficos complexos, cruzamentos analíticos profundos ou relatórios exportáveis.  
   - O foco é **operacional**, não BI.

---

### 6. Perfis e jornadas principais

#### 6.1 Operador/Admin do Inspectah (perfil primário)

- Abre `/admin` e, na **Visão Geral**, vê em segundos se o sistema está “verde”, “amarelo” ou “vermelho”.  
- Navega para **Fontes** para investigar alertas: filtra por degradadas, abre detalhes de uma fonte problemática, enxerga histórico curto de falhas.  
- Vai para **Casos/Temas** para entender impactos: vê quais casos estão em atenção/contestação, abre um caso específico e enxerga o resumo e suas principais evidências/fontes.  
- Usa essas informações para decidir **o que acionar no backend** (incidentes, correções, pausas em ingestão, etc.).

#### 6.2 Curador/Analista

- Usa o Console de Admin para checar se fontes sensíveis (regulatórias, oficiais, datasets críticos) estão sadias.  
- Prioriza revisão humana em casos marcados como “em contestação” ou “dados frágeis”.  
- Valida, antes de publicar relatórios/insights, se o pano de fundo do sistema está confiável.

#### 6.3 PO / Engenheiro de Produto

- Usa a Visão Geral para fazer um “check pré‑demo”: o sistema está saudável? há alertas importantes?  
- Navega por Fontes e Casos para descobrir gaps óbvios (fontes que nunca atualizam, casos críticos com pouca evidência).  
- Usa o que vê no Console de Admin para alimentar decisões de roadmap (novas integrações, melhorias de ingestão, priorização de temas).

Critério de sucesso: nenhum desses perfis deveria precisar abrir um JSON de scorecard ou log para responder perguntas básicas sobre saúde e escopo do Inspectah.

---

### 7. Relação com Truth‑DB, Sistema de Blocos e DNA

A Sprint 18 **não cria um “sub‑sistema de verdade” novo**. Ela se apoia diretamente:

- na Truth‑DB como fonte única de estados consolidados (fontes, casos, blocos, sub‑blocos);  
- no Sistema de Blocos como modelo de como esses estados são construídos e endurecidos;  
- nos watchers/scorecards e gates definidos na DNA e no Sprint Playbook para health, ingestão e consistência.

O Console de Admin expõe, em linguagem de produto, o que o motor já sabe. Exemplos de princípios que o front deve respeitar:

- **Nenhuma tela de admin pode mostrar um estado que não exista no Truth‑DB**.  
- **Nenhuma ação de admin pode modificar blocos diretamente**; qualquer fluxo futuro de mutação deve passar por rotas de backend com guard rails explícitos.  
- Sinais de WARN/FAIL de watchers/gates devem ser traduzidos para “em atenção”, “degradado”, “incidente potencial” na UI — nunca ignorados.

Os detalhes de quais watchers, gates e scorecards alimentam o Console de Admin serão especificados no **Capítulo 2 (gates de validação)**, mas este capítulo fixa o princípio: S18 é **uma janela em cima do motor**, não um atalho por fora dele.

---

### 8. Entregáveis esperados da Sprint 18

Ao final da Sprint 18, esperamos ter:

1. **Console de Admin funcional no frontend**  
   - Rota `/admin` (ou equivalente) disponível no ambiente de desenvolvimento e homologação.  
   - Páginas e componentes de Visão Geral, Fontes e Casos/Temas integrados ao layout da SPA.

2. **Integrações estáveis com backend de admin**  
   - Endpoints de listagem/detalhe de fontes e casos/temas implementados ou consolidados.  
   - Endpoint (ou conjunto de endpoints) de health agregada para a Visão Geral.  
   - Contratos estabilizados o suficiente para que o front não quebre a cada refino interno.

3. **Documentação da Sprint**  
   - Este `Capitulo 1` (visão/contexto/escopo).  
   - `Capitulo 2` (gates e métricas de validação para S18, ligados à DNA).  
   - `Capitulo 3` (filemap e arquitetura de frontend/backend para admin).  
   - `Capitulo 4` (runbooks, prompts para Codex e instruções de uso/demo do Console de Admin).  
   - Um resumo executivo em `docs/sprint_18_overview.md` para leitura rápida.

4. **Suporte em CI/CD**  
   - Workflows de CI incluindo build e lint das rotas de admin.  
   - Pelo menos um teste automatizado mínimo (smoke test da rota `/admin` ou de render das páginas principais).

---

### 9. Definição de pronto (DoD macro da Sprint 18)

A Sprint 18 é considerada concluída quando, cumulativamente:

1. Um operador consegue, via `/admin`, ver uma **Visão Geral** com KPIs coerentes com o estado real do sistema (sem discrepâncias grosseiras em relação a scorecards/health do backend).
2. O operador consegue **listar fontes, filtrar por status e abrir o detalhe** de uma fonte, visualizando metadados e histórico curto de saúde sem erros.
3. O operador consegue **listar casos/temas, filtrar por estado e abrir o detalhe** de um caso, vendo resumo, estado atual, risco agregado (quando houver) e principais fontes/evidências associadas.
4. O Console de Admin não oferece nenhum caminho para **modificar blocos, estados de casos ou parâmetros sensíveis**; quaisquer mutações permanecem sob controle do backend e dos guard rails definidos na DNA.
5. A estrutura de frontend mantém e estende o padrão da S17, com módulo de admin bem isolado e documentado (pastas, componentes, camada de API). 
6. Existe documentação suficiente para que um segundo dev/operador consiga subir, usar e explicar o Console de Admin sem depender do autor original.  
7. O pipeline de CI executa build e lint do front com as páginas de admin incluídas e roda verde.

Se qualquer um desses pontos não estiver atendido, a Sprint 18 não está realmente pronta — mesmo que existam telas “bonitas”.

---

### 10. Riscos e anti‑padrões a evitar

Para não desviar o Inspectah do seu DNA, a Sprint 18 deve ativamente evitar:

- **Console decorativo**: telas que parecem um painel, mas mostram dados inconsistentes ou desconectados da Truth‑DB.  
- **Backdoor de canetada**: qualquer botão ou fluxo que permita editar estados diretamente sem passar pelos mecanismos de confiança (Debunker, Comitês, Âncoras, Sistema de Blocos).  
- **Acoplamento frágil**: UI dependendo de estruturas internas instáveis (por exemplo, lendo JSON bruto de scorecards que podem mudar a cada sprint).  
- **Scope creep de BI**: gastar tempo construindo dashboards analíticos complexos antes de garantir o básico de operação.

O capítulo 2 deve transformar esses riscos em gates mensuráveis; aqui eles estão registrados como **alertas explícitos de produto**.

---

Este Capítulo 1 foi retrabalhado em múltiplas rodadas com a “banca fixa” (produto, arquitetura, engenharia e operação) até o consenso de que não há lacunas relevantes de visão ou escopo para a S18. Ajustes futuros devem ser incrementais e localizados, sem necessidade de reabrir a direção geral aqui descrita.

