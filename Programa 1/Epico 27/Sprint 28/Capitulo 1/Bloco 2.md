# Inspectah — Sprint 28
## Capítulo 1 — Bloco 2
### Problemas, hipóteses e tentativas anteriores (E27.1 — CRUD & ON/OFF de Fonte)

---

#### 1.2.1 Mapa detalhado dos problemas

Aqui refinamos, com bisturi, os problemas que a Sprint 28 precisa atacar. Não é uma lista genérica: são dores específicas, já observadas na prática ou previsíveis a partir do desenho atual do sistema.

##### Problema 1 — CRUD desalinhado com o modelo atual de fonte

Sintomas principais:
- O modelo de `Source` evoluiu em S21–S25 (novos campos, enums mais ricos, relação mais forte com domínios, modos, criticidade), mas:
  - a API `/admin/sources` não foi completamente atualizada para refletir essa evolução,  
  - o console de fontes v1 não exibe todos os campos importantes nem aplica as regras de negócio mais recentes,  
  - existem campos que só existem "de fato" no banco, ou só são compreendidos a partir da leitura direta de código.

Consequências:
- O operador não enxerga, na UI, a mesma realidade que o backend enxerga no modelo de domínio.  
- Cadastrar ou editar uma fonte requer conhecimento de:
  - quais campos são realmente obrigatórios,  
  - quais combinações são válidas (ex.: tipo `news_rss` exige URL; algumas categorias exigem domínio específico; certos campos só fazem sentido em certos tipos).  
- A ausência de validação forte e contratos estáveis abre espaço para fontes "meio configuradas" que funcionam até certo ponto e falham de forma opaca em produção.

Raiz do problema:
- A lógica de domínio foi ficando mais sofisticada ao longo das sprints, mas o contrato de CRUD (API + console) ficou parcialmente congelado na versão "geração 1" do produto.  
- Não houve uma sprint dedicada a **reconvergir** modelo de dados, API e UI em uma visão única e operacional.

##### Problema 2 — ON/OFF pouco previsível e risco de “duas verdades”

Sintomas principais:
- Estado da fonte (`ACTIVE`, `DISABLED`, `DEPRECATED`) vive no banco, mas o comportamento real do sistema nem sempre acompanha esse estado ponto a ponto.  
- Há relatos ou riscos plausíveis de situações como:
  - fonte marcada como `DISABLED` que continua sendo agendada em ciclos de ingestão,  
  - fonte que aparece como `ACTIVE`, mas não participa de ingestão por configurações conflitantes ou caches/lógicas paralelas.

Consequências:
- Operadores não podem confiar plenamente que "desligar" uma fonte via console/DB **sempre** terá o efeito real esperado.  
- A equipe de SRE/operadores passa a depender de inspeção manual de logs, scripts ou hacks para validar o estado real de ingestão.  
- Isso viola uma premissa central do Inspectah: **não pode haver divergência estrutural entre o que os dados dizem e o que o sistema faz**.

Raiz do problema:
- O contrato entre `Source.state` e o scheduler da Ingestão 2.0 nunca foi formalizado como um conjunto de invariantes fortes, testadas e versionadas.  
- Estados foram usados de forma mais informativa do que normativa: serviam para indicar intenção, mas não necessariamente para regular comportamento do motor de ingestão.

##### Problema 3 — Console de fontes v1 é mais painel do que ferramenta de operação

Sintomas principais:
- A UI atual para fontes foi criada em um contexto em que o principal objetivo era "enxergar" fontes, não necessariamente operá-las com rigor:  
  - lista de fontes sem filtros ricos por critério operacional (domínio, criticidade, modo, estado),  
  - formulários de edição mais próximos de um formulário CRUD genérico do que de um fluxo guiado,  
  - ausência de feedback visual forte para transições de estado (ex.: desativar uma fonte não deixa tão claro o impacto e a nova condição).  
- Inconsistência com o Design System Admin v1 em gestação (E26):  
  - padrões de estados vazios, loading, erro, componentes de tabela e filtros ainda não estão harmonizados.

Consequências:
- Operadores tratam o console de fontes como um "visor com botões" pouco confiável, e não como uma ferramenta de operação principal.  
- A curva de aprendizado é maior que o necessário; fluxos simples exigem conhecimento interno ou documentação paralela.

Raiz do problema:
- O console de fontes nasceu cedo, num estágio de produto em que o foco era viabilizar o módulo de fontes, não consolidar o padrão de UX/admin.  
- A evolução posterior (Ingestão 2.0, Programa 1, E26) ainda não foi refletida nesse console.

##### Problema 4 — Dependência de scripts, terminal e conhecimento tribal

Sintomas principais:
- Para cenários fora do caminho super feliz (ex.: corrigir fonte antiga, lidar com fonte problemática, realizar manutenção planejada), operadores acabam recorrendo a:
  - comandos diretos no banco,  
  - scripts de manutenção,  
  - pedidos para alguém "que conhece bem o módulo de ingestão".

Consequências:
- Alto custo de operação e risco de erro humano em tarefas que deveriam ser triviais e repetíveis.  
- Barreira de entrada alta para novos membros da equipe operacional.  
- Dificuldade para auditar quem fez o quê, quando, e por qual motivo.

Raiz do problema:
- O sistema foi construído com foco inicial em viabilizar a ingestão e o domínio de fontes; a camada de operação (consoles como ponto único de verdade) chegou depois.  
- Ainda não houve um esforço dedicado, como esta sprint, para puxar essas operações estruturalmente para a UI.

---

#### 1.2.2 Hipóteses detalhadas da Sprint 28

A Sprint 28 se apoia em hipóteses bem explícitas, que guiam tanto a arquitetura quanto as decisões de corte de escopo.

##### Hipótese H1 — CRUD consolidado reduz incidentes e fricção

Enunciado:  
Se consolidarmos o modelo de `Source` (campos, tipos, enums, invariantes) e alinharmos a API `/admin/sources` e o console de fontes v2 com esse modelo, então:
- será mais difícil criar fontes em estado inconsistente ou parcialmente configuradas;  
- incidentes causados por configurações inválidas ou incompletas tendem a diminuir significativamente;  
- operadores conseguirão, a partir da UI, efetuar alterações seguras sem precisar de suporte de desenvolvimento.

Mecanismos de validação:
- Testes de domínio garantindo invariantes de estado e de configuração por tipo de fonte.  
- Testes de API cobrindo casos felizes e de erro (400/404/409).  
- UX que torne impossível ou muito improvável "esquecer" campos críticos.

##### Hipótese H2 — ON/OFF determinístico aumenta confiança operacional

Enunciado:  
Se transformarmos os estados `ACTIVE`, `DISABLED`, `DEPRECATED` em um contrato normativo forte entre domínio de fontes e Ingestão 2.0, então:
- operadores poderão confiar que desligar uma fonte sempre remove essa fonte do fluxo de ingestão automática, e que religar a fonte a recoloca no fluxo sem intervenção manual nos bastidores;  
- o time de SRE/operadores terá um mecanismo direto de mitigação em incidentes: desativar a fonte problemática, com efeito imediato e rastreável.

Mecanismos de validação:
- Testes de integração que exercitam cenários básicos:  
  - fonte ativa → ingestão ocorrendo,  
  - desativar via console/API → ingestão cessa,  
  - reativar → ingestão volta.  
- Logs e registros de `IngestionRun` que mostram claramente a mudança de comportamento associada à transição de estado.

##### Hipótese H3 — Console de fontes v2 reduz dependência de scripts e especialistas

Enunciado:  
Se o console de fontes v2 expuser campos essenciais (domínio, categoria, modo, criticidade, estado, cadência) de forma clara, com ações de ON/OFF acessíveis e formulários guiados, então:
- as operações típicas (criar fonte, ajustar config, desligar temporariamente, descontinuar) poderão ser feitas por operadores não-desenvolvedores,  
- haverá menos demanda por scripts ad hoc e intervenções diretas no banco,  
- o fluxo de resposta a incidentes envolvendo fontes será significativamente mais simples.

Mecanismos de validação:
- Roteiro de demo interna (G6) em que operadores executam casos canônicos (Cadastro de nova fonte, desligar fonte problemática, reativar após manutenção).  
- Feedback qualitativo da equipe operacional sobre clareza e previsibilidade do console.

##### Hipótese H4 — Sanidade de legado previne regressões silenciosas

Enunciado:  
Se mantivermos os gates críticos de S21/S22 rodando como parte da S28, então:
- evitaremos regressões silenciosas em funcionalidades de fontes/ingestão já em uso,  
- qualquer mudança no modelo ou na API que quebre contratos anteriores será detectada durante a sprint, e não meses depois em outra fase do produto.

Mecanismos de validação:
- Gate específico (G5) que roda scripts de S21/S22 relevantes para fontes e ingestão, reportando evidências.  
- Scorecards mostrando que a S28 não sacrificou capacidades anteriores em nome de evoluções locais.

---

#### 1.2.3 Tentativas anteriores e lições específicas

A Sprint 28 não nasce do zero: ela se apoia diretamente em tentativas anteriores, que funcionaram parcialmente, mas deixaram lacunas.

- **S21 — Primeira geração de fontes e console**  
  - Definiu o alicerce do domínio de fontes: tipos, estados básicos, primeiro console.  
  - Funcionou bem como MVP do módulo, mas foi desenhada num momento em que Ingestão 2.0 e Programa 1 ainda não existiam como visão consolidada.  
  - Lições:  
    - é possível evoluir o módulo de fontes incrementalmente,  
    - console sem visão clara de operação tende a virar painel técnico.

- **S22 — Ingestão 2.0**  
  - Introduziu scheduler, `IngestionRun` e uma visão mais robusta de ingestão por fonte.  
  - Porém, a relação profunda entre estado de fonte e ingestão ainda não foi tornada explícita e testada como contrato.  
  - Lições:  
    - o sistema precisa de invariantes fortes entre estados de fonte e decisão de ingestão,  
    - sem isso, ON/OFF vira um campo semi-decorativo.

- **S25 — Sanidade global e plano anti-gaps**  
  - Mostrou que, sem sanidade contínua, módulos centrais acumulam rugas e dívidas que explodem em sprints de consolidação.  
  - Lições aplicadas à S28:  
    - nunca evoluir um módulo como fontes sem rodar gates antigos relevantes,  
    - nunca assumir que "se compila e roda local, está tudo bem".

A Sprint 28 captura essas lições e as converte em critérios concretos:  
- consolidação do modelo de fonte,  
- contrato normativo forte para ON/OFF,  
- console de operação de verdade,  
- sanidade de legado como parte do escopo, não como afterthought.

---

Este Bloco 2 fecha o entendimento do **porquê** da Sprint 28 existir, quais dores exatas ela mira, quais teses ela quer validar e como ela evita repetir erros de tentativas anteriores. Nos próximos blocos, o foco passa a ser: domínios/personas/casos (Bloco 3) e cortes de escopo rigorosos (Bloco 4), mantendo o fio condutor do Programa 1 e de E27.1.

