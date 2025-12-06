# Inspectah — Programa 4 v4
## Exposição, Produtos, APIs & Uso Responsável

> Versão v4 — alinhada ao Roadmap Macro v4 (v2), DNA v2, Sprint Playbook v2 e Lessons Learned. Compatível com o estado atual do projeto (S1–S29) e construída sobre os Programas 1–3 v4 (Data Hub, Interpretação, Truth‑DB + Lógica + Memória).

---

## 0. Papel do Programa 4 no Inspectah

O Programa 4 é a **camada de interface com o mundo** do Inspectah. Tudo o que Programas 1–3 constroem internamente (dados, claims, sinais, verdade, contestação, memória) precisa ser exposto de forma:

- segura,
- explicável,
- orientada a produtos,
- governada.

Se P1 é o sistema circulatório, P2 é o córtex de interpretação e P3 é o coração jurídico‑lógico, o Programa 4 é o **sistema nervoso periférico**: UIs e APIs que conectam o Inspectah a humanos e sistemas externos — sem trair a filosofia de verdade versionada, contestável, lógica e com memória evolutiva.

---

## 1. Visão

Construir um conjunto de **consoles, APIs e produtos derivados** que permitam a diferentes perfis (operadores, analistas, jornalistas, empresas, reguladores, público) explorar:

1. **Fontes e ingestão** (do Programa 1),
2. **Narrativas, claims, entidades e sinais** (do Programa 2),
3. **Estados de verdade, contestação, decisões lógicas e memória evolutiva** (do Programa 3),

com:

- níveis de acesso diferenciados,
- trilha de auditoria de uso,
- disclaimers de incerteza e limitações,
- exposição transparente de políticas (especialmente as da Truth Policy DSL / E40.5).

O Programa 4 é onde o Inspectah deixa de ser apenas infra de dados e verdade para se tornar um **produto utilizável**.

---

## 2. Objetivos do Programa 4

1. **Integrar identidade e autorização fina**
   - Conectar o Inspectah a um IdP e definir perfis/permissões de acesso granular.

2. **Definir e expor APIs estáveis**
   - Criar APIs para exploradores de verdade, casos, sinais e memória, com contratos claros.

3. **Construir consoles internos de operação e análise**
   - Entregar UIs que permitam operar fontes, acompanhar ingestão, analisar casos e monitorar verdades.

4. **Materializar produtos derivados (Fact Cards, relatórios, dashboards)**
   - Gerar superfícies de valor imediato para usuários finais.

5. **Expor resultados do núcleo de lógica (E40.5)**
   - Mostrar claramente por que uma decisão foi tomada ou bloqueada, com indicação de políticas e invariantes.

6. **Expor, de forma governada, partes da Memória Evolutiva (P3‑E8.5)**
   - Permitir acesso a Experiências e padrões históricos, com limites fortes de privacidade e risco.

7. **Garantir uso responsável e proteção contra abuso**
   - Implementar mecanismos de salvaguarda, logging de acesso, disclaimers e limites de exposição.

---

## 3. Escopo macro do Programa 4

O Programa 4 cobre:

1. **Identidade, autenticação e autorização de negócio**
2. **Gateways de API, contratos, quotas e observabilidade de uso**
3. **Consoles internos de operação e análise (Fontes, Casos, Verdade)**
4. **APIs principais (Truth Twin, Explore, casos/verdades/sinais)**
5. **Produtos derivados (Fact Cards, relatórios, dashboards)**
6. **Explicabilidade de decisões e exposição do logic‑checker (E40.5)**
7. **Exposição governada da Memória Evolutiva (P3‑E8.5)**
8. **Uso responsável, salvaguardas e política de exposição**

Ficam **fora do escopo** do Programa 4:

- ingestão de dados (P1),
- interpretação e ClaimGraph/sinais (P2),
- Truth‑DB, contestação, lógica e memória em si (P3),
- qualquer mecanismo interno de governança de verdade (políticas, conselhos). P4 consome o que P3 decidir.

---

## 4. Macro‑épicos do Programa 4

Usamos rótulos locais `P4‑E#`. A numeração global de épicos é gerida no roadmap.

### P4‑E1 — Identidade, autenticação & autorização fina

Objetivo: integrar o Inspectah a um Identity Provider (IdP) e definir a camada de autorização de negócio.

Entregas principais:

1. Integração com IdP
   - SSO, MFA, recuperação de senha, tokens de acesso/refresh.

2. Modelo de perfis e papéis
   - operadores de ingestão,
   - analistas internos,
   - revisores/guardião humano,
   - administradores de políticas,
   - clientes externos (por organização),
   - perfis de leitura pública/semipública.

3. Autorização de negócio
   - mapeamento de papéis → permissões (ex.: ler apenas sinais agregados, ver detalhes de contestação, ver ou não entidades sensíveis, editar fontes).

4. Auditoria de acesso
   - logs de quem acessou o quê, quando, em qual contexto.

Critérios de pronto:

- UIs e APIs protegidas por IdP;
- perfis e permissões funcionam em casos reais;
- logs de acesso disponíveis para auditoria.

---

### P4‑E2 — Gateways de API & contratos

Objetivo: definir o "corredor oficial" de entrada/saída para APIs do Inspectah.

Entregas principais:

1. Integração com API Gateway
   - roteamento, quotas, rate limits, autenticação/autorização integrada com IdP.

2. Contratos de API
   - convenções de path, versionamento (v1, v2, ...), formatos (JSON, etc.), paginação, filtros, erros.

3. Observabilidade de APIs
   - métricas: latência, taxa de erro, uso por cliente, payloads médios;
   - logs de requisição/resposta com mascaramento de campos sensíveis.

Critérios de pronto:

- APIs principais (internas ou externas) passam pelo gateway;
- há documentação clara e consultável dos contratos;
- uso é monitorado em dashboards.

---

### P4‑E3 — Cockpits internos (Fontes, Casos, Operação)

Objetivo: entregar UIs internas para operação 24/7 e análise de casos.

Entregas principais:

1. Console de Fontes (frente do Programa 1)
   - listagem, filtros, estados, erros, ações (ativar/pausar, alterar frequência, backfill, incidentes);
   - integração com observabilidade de ingestão.

2. Cockpit de Casos
   - visão por caso/tema: claims, entidades, sinais, estados de verdade, contestação, âncoras;
   - destaques (mentiras em circulação, campo de batalha, radar de silêncio).

3. Painéis de operação 24/7
   - visão geral de ingestão, interpretação, verdade/contestação, incidentes;
   - status de serviços críticos.

Critérios de pronto:

- Operadores conseguem acompanhar saúde do sistema e agir em fontes via UI;
- analistas conseguem inspecionar casos/temas prioritários em uma única tela.

---

### P4‑E4 — Truth Twin API, Explore API & APIs de casos/verdades/sinais

Objetivo: expor o núcleo do Inspectah para consumo estruturado por sistemas externos.

Entregas principais:

1. Truth Twin API
   - API para consultar estados de verdade por claim/entidade/caso/tema;
   - inclui estados (`true`, `false`, `uncertain`, etc.), versões, últimos DecisionBlocks.

2. Explore API
   - API para navegar ClaimGraph, sinais, casos/temas, relações entre narrativas;
   - filtros por domínio, período de tempo, tipo de sinal.

3. APIs de sinais e métricas de narrativa
   - acesso a mentiras em circulação, campo de batalha, radar de silêncio, densidade de espuma, etc.

Critérios de pronto:

- Clientes internos/externos conseguem consumir estados de verdade e sinais com contratos estáveis;
- há testes automatizados de contrato e exemplos de uso.

---

### P4‑E5 — Produtos derivados (Fact Cards, relatórios, dashboards)

Objetivo: transformar o núcleo de verdade e sinais em entregáveis de alto valor para diferentes perfis.

Entregas principais:

1. Fact Cards
   - cartões de fato compartilháveis, com resumo do estado de verdade, evidências principais e nível de incerteza.

2. Relatórios temáticos
   - relatórios de casos/temas, com timeline de narrativa, estados de verdade, contestação, sinais relevantes, principais fontes.

3. Dashboards
   - painéis para acompanhar temas específicos, domínios, fontes e indicadores de manipulação.

Critérios de pronto:

- Pelo menos 1–2 produtos (ex.: Fact Cards + um relatório temático) usados por usuários reais;
- feedback inicial incorporado e usado para evoluir os produtos.

---

### P4‑E6 — Uso responsável & salvaguardas

Objetivo: garantir que o uso do Inspectah não se torne uma máquina de difamação, abuso ou simplificação enganosa.

Entregas principais:

1. Níveis de exposição
   - o que é público, o que é privado, o que é restrito a parceiros/autoridades;
   - regras por domínio, tipo de entidade (pessoa, organização, cargo público, etc.).

2. Disclaimers de incerteza e limitações
   - mensagens claras sobre limites de cobertura, incerteza de sinais, versões de políticas.

3. Proteção de indivíduos
   - anonimização/mascaramento em contextos sensíveis;
   - regras específicas para pessoas físicas, vítimas, menores, etc.

4. Logs de uso e mecanismos anti‑abuso
   - monitorar padrões de uso abusivo, scraping agressivo, tentativas de exploração.

Critérios de pronto:

- Perfis sensíveis são tratados com regras específicas;
- qualquer UI/API exposta vem acompanhada de disclaimers e limites apropriados.

---

### P4‑E7 — Explicabilidade de decisões & exposição do logic‑checker (E40.5)

Objetivo: tornar visível **por que** o Inspectah tomou (ou negou) uma decisão de verdade/contestação em P3.

Entregas principais:

1. Superfícies de explicação
   - mostrar, para um DecisionBlock, quais políticas (da Truth Policy DSL) foram aplicadas;
   - exibir se a decisão passou por E40.5, quais invariantes foram checados e quais passagens falharam.

2. Versões de política
   - indicar claramente qual versão de política estava em vigor no momento da decisão;
   - histórico de mudanças de política por domínio.

3. Integração com contestação
   - permitir que revisores vejam rapidamente o racional lógico aplicado em decisões contestadas.

Critérios de pronto:

- Usuários autorizados conseguem entender "por que" uma decisão foi tomada ou bloqueada sem abrir código;
- relatórios de auditoria conseguem referenciar políticas e checks lógicos específicos.

---

### P4‑E8 — Exposição de Memória Evolutiva (P3‑E8.5)

Objetivo: expor, de forma governada, partes da Memória Evolutiva (Experiências) para uso em análise e explicabilidade.

Entregas principais:

1. Visões de Experiências
   - por caso/tema: quais Experiências semelhantes já ocorreram;
   - por tipo de narrativa: padrões recorrentes de desinformação/manipulação;
   - por fonte: histórico agregado de participação em Experiências.

2. Controles de privacidade e risco
   - limites de exposição por tipo de dado, tipo de ator e contexto de uso;
   - mecanismos para ocultar detalhes sensíveis e focar em padrões agregados.

3. APIs internas/externas
   - superfícies para ferramentas internas e parceiros consultarem Experiências de forma agregada.

Critérios de pronto:

- É possível, em domínios piloto, mostrar como o sistema "aprendeu" com casos passados;
- não há exposição indevida de dados pessoais ou contextos sensíveis.

---

## 5. Interfaces com Programas 1, 2 e 3

### 5.1 Com Programa 1 — Data Hub, Fontes, Ingestão

P4 consome de P1:

- dados de fontes (Provider/Source) e sua saúde;
- histórico de ingestão por fonte, país, idioma, tipo de conteúdo;
- incidentes de ingestão.

Isso alimenta o Console de Fontes, dashboards de operação e, eventualmente, relatórios externos sobre transparência de fonte.

### 5.2 Com Programa 2 — Interpretação, Claims, Entidades & Sinais

P4 consome de P2:

- ClaimGraph por caso/tema/entidade;
- sinais (mentiras em circulação, campo de batalha, radar de silêncio, etc.);
- logs de agentes para telas de auditoria interna.

P4 não altera ClaimGraph nem sinais; apenas os exibe e agrupa.

### 5.3 Com Programa 3 — Truth‑DB, Lógica, Contestação & Memória

P4 consome de P3:

- estados de verdade;
- blocos (Fact, Evidence, Decision, Anchor);
- fluxos e estados de contestação;
- resultados do logic‑checker (E40.5);
- Experiências (memória evolutiva, P3‑E8.5), quando habilitadas.

P4 é a "vitrine" de P3, mas não altera decisões de verdade/fato. Revisões e mudanças de estado continuam sendo responsabilidade de P3.

---

## 6. Restrições e não‑objetivos

1. P4 não decide estados de verdade — apenas exibe o que P3 decidiu.
2. P4 não executa lógica formal; apenas exibe resultados de E40.5.
3. P4 não executa contestação; apenas oferece interfaces para acionar fluxos que vivem em P3.
4. P4 não altera ingestão (P1) nem interpretação (P2).
5. P4 não substitui políticas de governança; apenas as torna visíveis e operáveis.

---

## 7. Critérios macro de "pronto" do Programa 4

Consideramos o Programa 4 "pronto" (v1 estruturante) quando:

1. UIs internas (Console de Fontes, Cockpit de Casos, painéis de operação) permitem operar o sistema sem mexer em código;
2. APIs principais (Truth Twin, Explore, sinais) estão estáveis, documentadas e observáveis;
3. Pelo menos 1–2 produtos derivados (Fact Cards, relatórios, dashboards) estão em uso por usuários reais;
4. Resultados do logic‑checker (E40.5) são expostos de forma compreensível para revisores e analistas;
5. A Memória Evolutiva (P3‑E8.5) é parcialmente explorável via UI/API em domínios piloto, com salvaguardas;
6. Há políticas claras de uso responsável, níveis de exposição, disclaimers e proteção de indivíduos, implementadas em UIs/APIs;
7. Logs de uso e mecanismos anti‑abuso estão ativos e monitorados, reduzindo risco de uso malicioso do Inspectah.

A partir daqui, evoluções futuras se concentram em refinar produtos, criar novos modos de visualização, ampliar o alcance da Memória Evolutiva para mais domínios e calibrar políticas de exposição conforme o Inspectah cresce.

