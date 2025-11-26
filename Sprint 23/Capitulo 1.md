# Inspectah — Sprint 23
## Capítulo 1 — Contexto, Objetivos e Escopo

### 1. Contexto geral

Até a Sprint 22, o Inspectah já possui:

- Console de fontes e ontologia de fontes amadurecida (S21 / S21.2), com cadastros ricos, tipos de fonte claros e campos alinhados à visão de produto.
- Ingestão 2.0 funcional (S22): console de ingestão com lista de fontes, detalhe, histórico de runs, toggle Manual/Automático, barra de progresso e execução inline sem "RUNNING eterno".
- Pipeline técnico consistente (watchers, normalizer, indexer, evidence vault, Truth-DB em blueprint) e ORR disciplinado por sprints.

O próximo gargalo não é mais "trazer dados para dentro", mas sim **interpretar, classificar e organizar informação com rigor absurdo**, de forma transparente, auditável e resistente a erros humanos e alucinações de modelos de IA.

A Sprint 23 entra exatamente aqui: **criar a primeira versão sólida da camada de agentes de interpretação, classificação, organização e debunk**, com redundância tripla e governança clara.

### 2. Problema que a Sprint 23 resolve

Hoje, mesmo com ingestão funcionando, ainda faltam peças críticas:

1. **Não existe um console unificado de agentes** onde o admin consiga ver, criar, ajustar e versionar as “mentes” que interpretam e classificam o mundo dentro do Inspectah.
2. **Diretrizes de agentes estão implícitas**, dispersas em código, prompts soltos ou mental models. Não há lugar único para:
   - Nome, descrição, instruções e política de comportamento de cada agente.
   - Configuração de modelo, temperatura, contexto máximo, limites de uso e guardrails.
   - Conjuntos de arquivos/KBS anexos a cada agente.
3. **Não existe a estrutura explícita de redundância tripla por camada**:
   - Dois agentes céticos (debunkers) trabalhando de forma independente.
   - Um agente mediador que recebe os dois relatórios, confronta divergências e decide o veredito.
4. **Atualização de modelos é opaca e frágil**:
   - Não há um mecanismo central para dizer “todos os agentes agora usam o modelo GPT mais recente do plano Plus” com buffer de tempo e rollback.
5. **Decisões de agentes não são expostas como "reports" estruturados e auditáveis**:
   - Precisamos que cada camada produza bundles estruturados (JSON, schemas) com: entradas, raciocínios resumidos, conclusões, scores de confiança e links para evidências, sempre versionados e reproduzíveis.

Sprint 23 existe para transformar esse cenário em uma **plataforma de agentes** com cara de produto, não um aglomerado de prompts.

### 3. Visão da Sprint 23 em uma frase

> Entregar a **primeira versão do Console de Agentes do Inspectah**, com perfis de agentes (interpretação, classificação, debunk, mediação) configuráveis como "GPTs customizados", trilha de auditoria clara e redundância tripla para todas as decisões críticas.

### 4. Objetivos principais da Sprint 23

1. **Modelar o domínio de agentes e suas camadas**
   - Definir o modelo de dados de `AgentProfile`, `AgentRole`, `AgentLayer`, `AgentBundle` e `AgentPolicy` (incluindo consenso triplo).
   - Especificar como os agentes se encaixam nas etapas do pipeline (ex.: pós-ingestão, pré-Truth-DB, classificação de risco, organização por casos/temas).

2. **Criar o Console Admin de Agentes (v1)**
   - Inspirado diretamente no fluxo de criação de GPTs customizados:
     - Nome do agente.
     - Descrição (o que faz, para quem existe).
     - Instruções (comportamento, tom, o que evitar, limitações).
     - Modelo recomendado (e possibilidade de override pelo admin).
     - Área para upload/gestão de arquivos de conhecimento (KBs) específicos daquele agente.
   - Listagens claras por camada/função; fácil de entender quem faz o quê.

3. **Definir e registrar a redundância tripla por camada**
   - Para cada camada crítica (ex.: interpretação de texto, classificação/organização, debunk, mediação):
     - Dois agentes céticos (Debunker A/B) com diretrizes específicas para investigar, checar, cruzar evidências e questionar.
     - Um agente Mediador que recebe os relatórios dos dois, compara, aponta conflitos e emite decisão final GO/NO_GO (ou classes/fatos finais) com justificativa.
   - Padronizar o formato do "report" de cada agente e do resultado final da camada.

4. **Desenhar o mecanismo de upgrade de modelos de IA**
   - Criar o conceito de política global de modelo: “usar sempre o modelo mais atual disponível no plano Plus”, com opção de buffer (ex.: ativar novo modelo em 15 dias) e override por agente.
   - Especificar como as mudanças são auditáveis (quem mudou o quê, quando, de qual modelo para qual modelo) e como isso aparece para o admin.

5. **Tornar transparentes e auditáveis as diretrizes de todos os agentes**
   - Definir como o usuário (admin e, quando fizer sentido, o usuário final) consegue ver:
     - A arquitetura de agentes que participaram de uma decisão.
     - As instruções fundamentais de cada agente.
     - O fluxo de consenso triplo que levou àquele veredito.
   - Garantir que isso seja tão simples quanto “abrir a ficha técnica” de um GPT.

### 5. Escopo detalhado da Sprint 23

A Sprint 23 foca em **especificação e camada de gestão/configuração**, com alguns elementos executáveis mínimos para validar o modelo. O escopo se organiza em quatro blocos:

1. **Domínio e contratos de agentes**
   - Modelos de dados:
     - `AgentProfile`: id, nome, descrição, camada, função (ex.: interprete, classificador, debunker, mediador), modelo default, parâmetros (temperature, top_p, etc.), flags de segurança.
     - `AgentKnowledge`: ligação entre agente e KBs (arquivos, coleções de documentos, links para o Truth-DB, etc.).
     - `AgentPolicy`: regras de uso, limites, modelos permitidos, versões.
     - `AgentConsensus`: estrutura para registrar outputs de Debunker A, Debunker B e decisão do Mediador em cada camada.
   - APIs de CRUD para perfis de agentes (admin): criar, listar, atualizar, versionar e desativar.

2. **Console de Agentes (frontend admin)**
   - Lista de agentes com filtros por camada, função e status.
   - Tela de detalhe de um agente, com seções análogas ao ChatGPT "criar GPT":
     - Nome, descrição, instruções.
     - Modelo e parâmetros atuais.
     - Seção de KBs anexados (com visualização dos arquivos principais, tamanho, tipo).
     - Histórico de versões de instrução/modelo.
   - Tela de "camadas" mostrando, para cada camada:
     - Quem são os dois debunkers.
     - Quem é o mediador.
     - Como o consenso é formado.

3. **Política global de modelos e buffer de upgrades**
   - Entidade/configuração global (ex.: `ModelPolicy`):
     - Modelo base recomendado (ex.: `gpt-4.1-mini`, `gpt-5.1-thinking`, etc.).
     - Flag "usar sempre o mais atual".
     - Campo de buffer (dias até o novo modelo ser adotado por padrão).
   - Interface admin para:
     - Ver o modelo atual em uso global.
     - Ver o próximo modelo disponível.
     - Configurar o buffer (ex.: 15 dias) ou aplicar imediatamente.
     - Ver histórico de alterações.

4. **Bundles de decisão e trilha de auditoria**
   - Desenho do formato de "information bundle" produzido pelos agentes:
     - Entrada bruta (texto, evento, fonte).
     - Normalização/parse inicial.
     - Outputs dos debunkers (cada um com sua visão, checks executados, flags de dúvida).
     - Decisão do mediador: classificação final, risco, tags, links para evidências.
     - Metadados: versões dos agentes usados, modelos, timestamps, IDs de run.
   - Definição de como isso é guardado (Truth-DB / Evidence Vault) e como é lido depois (UI e APIs).

### 6. Fora de escopo (explícito)

Para manter a Sprint 23 focada e viável, ficam **fora de escopo**, mesmo que já estejam no roadmap:

- Implementar o Debunker v0 completo, com UI de contestação pública, staking ou bonds on-chain.
- Qualquer integração com blockchain, reputação comunitária, sistema de blocos completo ou arbitragem entre humanos.
- UI de usuário final para explorar todos os detalhes dos bundles de decisão (nesta sprint, focamos na visão admin e nos contratos de dados; a experiência completa para usuário final entra em sprints futuras).
- Execução massiva de agentes em produção; aqui o foco é arquitetura, console, contratos e provas de conceito controladas.

### 7. Stakeholders, squad e papéis

**Squad 3 — Agentes de Interpretação e Classificação (Sprint 23)**

- **PO / Visão de Produto**: Gustavo.
- **Arquitetura e domínio de agentes**: Percy Liang (líder de LLMs e lógica de decisão), Martin Kleppmann (persistência, auditoria, trilhas de eventos), Donald Knuth (rigor de especificação e invariantes).
- **Experiência de admin (console)**: Bret Victor (clareza visual e narrativa do sistema), Steve Jobs (simplicidade radical do console e foco na experiência do admin).
- **Governança e redundância tripla**: Leslie Lamport (modelos de consenso, estados e provas), Vitalik Buterin (modelos de confiança e lógica de "debate" entre agentes e mediador).

A equipe inteira entra como conselho para revisar e blindar o capítulo 1 (este documento) e os demais capítulos da Sprint 23.

### 8. Critérios de sucesso da Sprint 23

A Sprint 23 será considerada **GO** se, ao final, tivermos:

1. **Especificação de domínio e contratos completa** para agentes, camadas e consenso triplo, sem lacunas e com invariantes claros.
2. **Console de Agentes (admin) implementado em v1**, com:
   - CRUD de perfis de agentes.
   - Tela de detalhe com instruções, modelo, KBs e histórico de versões.
   - Visualização clara da composição das camadas de redundância (Debunker A/B + Mediador) para pelo menos um fluxo completo de caso.
3. **Política global de modelos especificada e implementada** em nível mínimo funcional:
   - Configuração global de modelo atual.
   - Buffer de upgrade configurável.
   - Override por agente suportado no domínio (mesmo que com UI simples).
4. **Formato de information bundles definido e prototipado** para pelo menos um fluxo exemplo (ex.: notícia política ou evento climático), com trilha de auditoria completa no papel e, idealmente, com um caminho executável mínimo.
5. **Documentação da Sprint 23 completa**, incluindo:
   - Este Capítulo 1 (contexto, objetivos, escopo).
   - Capítulo 2 (gates e critérios de validação).
   - Capítulo 3 (filemap e arquitetura detalhada).
   - Capítulo 4 (plano de execução e runbook de testes).

### 9. Definição de pronto (DoD) para o Capítulo 1

Este Capítulo 1 é considerado pronto quando:

- Descreve claramente **por que** a Sprint 23 existe e qual lacuna ela fecha na evolução do Inspectah.
- Define objetivos concretos e mensuráveis para o domínio de agentes, console admin, consenso triplo e política de modelos.
- Explicita escopo e fora de escopo, evitando distorções nas próximas fases.
- Alinha os papéis do squad e deixa claro que a camada de agentes será tratada como **produto**, não apenas como prompts soltos.
- Serve de base coerente e sem lacunas para os Capítulos 2, 3 e 4 da Sprint 23.

