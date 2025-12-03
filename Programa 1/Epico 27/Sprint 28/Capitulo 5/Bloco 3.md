# Inspectah — Sprint 28
## Capítulo 5 — Bloco 3
### Dívida Técnica Assumida Conscientemente (Mapa Estruturado)

---

#### 5.3.1 Convenções deste bloco

Este bloco pega a ideia geral de "dívida técnica" da S28 e a transforma em um **quadro estruturado**, que possa ser:

- rastreado em backlog,  
- usado como insumo direto para planejamento de E27.2/E27.3,  
- consultado por ORR/Conselho quando precisar entender **o que foi conscientemente deixado para depois**.

Cada item de dívida é descrito com:

- **ID**: identificador curto (ex.: `D-28-AUD-1`).  
- **Eixo**: Auditoria, Validações por Tipo, Observabilidade, etc.  
- **Descrição**: o que falta / o que foi simplificado demais.  
- **Motivo de postergação**: por que não coube em S28.  
- **Risco associado**: ponte para riscos mapeados em 5.2.  
- **Custo estimado**: Baixo / Médio / Alto (heurístico, relativo a uma sprint).  
- **Janela alvo**: sugestão de encaixe (E27.2, E27.3, etc.).  
- **Notas de implementação**: pistas para quem for puxar a tarefa no futuro.

---

#### 5.3.2 Eixo 1 — Auditoria de Operações em Fonte


##### D-28-AUD-1 — Ausência de entidade dedicada de auditoria (`SourceActionLog`)

- **ID**: D-28-AUD-1  
- **Eixo**: Auditoria de operações  
- **Descrição**:  
  A Sprint 28 registra mudanças diretamente na entidade `Source` (`state`, `state_changed_at`, `state_reason`), mas não modela uma entidade explícita para registrar ações do operador, como `SourceActionLog`.

  Uma entidade desse tipo capturaria:
  - `id`  
  - `source_id`  
  - `action_type` (CREATE, UPDATE, ACTIVATE, DISABLE, DEPRECATE, etc.)  
  - `performed_by` (identidade do operador)  
  - `performed_at`  
  - `origin` (UI, script interno, API client específico)  
  - `metadata` (JSON com detalhes relevantes da ação)

- **Motivo de postergação**:  
  - Introduzir um log de auditoria completo traz decisões de modelo, privacidade, retenção e futuro acoplamento ao Truth-DB/Sistema de Blocos.  
  - Para S28, a prioridade era consolidar o fluxo CRUD & ON/OFF com ingestão obediente, sem abrir ainda a "caixa de governança" completa.

- **Risco associado**:  
  - Conecta diretamente a **R-28-P2** (trilha de auditoria insuficiente) e **R-28-O1/O3** (operações fora de política / decisões críticas sem rastreio fino).  

- **Custo estimado**:  
  - **Médio**: envolve modelo, migrations, ajustes em Admin API, testes e decisões mínimas de política de retenção.

- **Janela alvo**:  
  - **E27.2** para versão básica (entidade + gravação sistemática).  
  - Evoluções em **E27.3+** para integração com UI e Truth-DB.

- **Notas de implementação**:  
  - Começar pequeno: modelar a entidade e registrar ações em pontos centrais da Admin API.  
  - Evitar, no primeiro momento, expor endpoints públicos de consulta avançada; pode começar com consulta simples por `source_id`.  
  - Pensar desde já na extensibilidade para no futuro ancorar certos eventos no Sistema de Blocos.

---

##### D-28-AUD-2 — Falta de exposição de timeline de ações no console

- **ID**: D-28-AUD-2  
- **Eixo**: Auditoria de operações  
- **Descrição**:  
  Mesmo que `SourceActionLog` venha a existir, S28 não inclui ainda nenhuma tela que mostre ao operador uma **linha do tempo de ações por fonte** (quem criou, quem desativou, quem reativou, etc.).

- **Motivo de postergação**:  
  - Sem o próprio log estruturado (D-28-AUD-1), a timeline seria apenas um "wrapper" de campos da própria `Source`.  
  - Time optou por não construir uma UI sobre uma base de auditoria incompleta.

- **Risco associado**:  
  - Complementa **R-28-P2** (falta de trilha visível) e **R-28-O3** (decisões críticas sem review fácil).  

- **Custo estimado**:  
  - **Baixo/Médio**: assim que o log existir, a timeline é basicamente frontend + endpoints de leitura.

- **Janela alvo**:  
  - **E27.3** (depois que a fundação de auditoria estiver estável em E27.2).

- **Notas de implementação**:  
  - Reaproveitar componentes de lista e timeline já existentes no Design System Admin v1 (se houver).  
  - Incluir filtros por tipo de ação e período de tempo.  
  - Permitir que a timeline seja base para investigações de incidentes e, futuramente, para verificação cruzada com fatos registrados no Truth-DB.

---

#### 5.3.3 Eixo 2 — Validações Profundas e UX por Tipo de Fonte

##### D-28-VAL-1 — Validações genéricas em vez de validações por tipo

- **ID**: D-28-VAL-1  
- **Eixo**: Validações por tipo de fonte  
- **Descrição**:  
  A S28 trata validações como algo principalmente genérico (campos obrigatórios, formatos básicos). Não há, ainda, validações especializadas por tipo de fonte, como:
  - para RSS: verificação de URL acessível, parsing inicial, presença de campos-chave;  
  - para APIs JSON: teste de endpoint, headers, autenticação, formato do payload;  
  - para outros tipos futuros (CSV em storage, streams, etc.): checagens específicas.

- **Motivo de postergação**:  
  - Escopo de S28 foi definido para consolidar **núcleo** (modelo + API + console + ingestão obediente).  
  - Colocar todas as validações específicas de tipo nesta sprint poderia explodir o escopo e atrasar E27.1.

- **Risco associado**:  
  - Relacionado a **R-28-P3** (UX de formulários básica) e **R-28-I3** (observabilidade limitada, pois algumas falhas seriam evitáveis já no cadastro).  

- **Custo estimado**:  
  - **Médio** (por tipo de fonte dominado).  
  - Alto se tentarmos cobrir muitos tipos de uma vez.

- **Janela alvo**:  
  - **E27.2**: tipos principais (RSS de notícias, API JSON).  
  - **E27.3+**: cobrir tipos adicionais.

- **Notas de implementação**:  
  - Definir uma interface clara de "validador por tipo" no backend, permitindo adicionar novos tipos incrementalmente.  
  - Reaproveitar resultados de validação para UX (exibir mensagens específicas, sugerir correções).  
  - Garantir que as validações sejam reaplicáveis no futuro (por exemplo, ao editar config).

---

##### D-28-VAL-2 — Ausência de wizards/guias de configuração para fontes complexas

- **ID**: D-28-VAL-2  
- **Eixo**: Validações por tipo de fonte / UX  
- **Descrição**:  
  A criação de fontes em S28 é baseada em formulários "flat". Para fontes mais complexas (APIs com autenticação, múltiplos parâmetros, etc.), seria ideal ter wizards passo-a-passo.

- **Motivo de postergação**:  
  - Sem ainda ter validações de tipo consolidadas, construir wizards poderia resultar em flows frágeis e difíceis de manter.  
  - O time optou por primeiro firmar o contrato técnico; depois, construir experiência guiada.

- **Risco associado**:  
  - Também ligado a **R-28-P3** (UX básica) e, indiretamente, a riscos de operação (erros de configuração).  

- **Custo estimado**:  
  - **Médio/Alto**, dependendo da sofisticação desejada nos wizards.  

- **Janela alvo**:  
  - **E27.3**: após E27.2 ter criado base sólida de validações por tipo.

- **Notas de implementação**:  
  - Começar com 1–2 wizards de alto impacto (ex.: principal fonte de notícias via RSS, principal API de dados econômicos).  
  - Integrar teste de conexão dentro do wizard.  
  - Reaproveitar componentes do Design System para manter consistência.

---

#### 5.3.4 Eixo 3 — Observabilidade Orientada a Fonte

##### D-28-OBS-1 — Ausência de métricas dedicadas por fonte/estado/mode

- **ID**: D-28-OBS-1  
- **Eixo**: Observabilidade por fonte  
- **Descrição**:  
  S28 não define ainda métricas específicas como:
  - número de ingestões por `source_id` x período,  
  - taxa de erro por fonte,  
  - histogramas de latência de ingestão por fonte,  
  - tempo desde a última ingestão bem-sucedida por fonte.

- **Motivo de postergação**:  
  - O foco foi garantir comportamento correto de ON/OFF, não ainda medir em profundidade o desempenho individual das fontes.  
  - Definir métricas sem observar uso real poderia levar a dashboards ruidosos.

- **Risco associado**:  
  - Relacionado a **R-28-I3** (observabilidade limitada) e, indiretamente, a riscos operacionais de diagnóstico lento.  

- **Custo estimado**:  
  - **Médio**: envolve instrumentação, storage de métricas e ajustes em painéis.

- **Janela alvo**:  
  - **E27.2**: instrumentação e métricas iniciais.  
  - Ajustes e refinamentos em **E27.3**.

- **Notas de implementação**:  
  - Usar naming consistente com a stack atual (ex.: Prometheus).  
  - Garantir cardinalidade controlada (não criar explosão de séries).  
  - Priorizar métricas úteis para operações diárias.

---

##### D-28-OBS-2 — Falta de dashboards específicos de operação de fontes

- **ID**: D-28-OBS-2  
- **Eixo**: Observabilidade por fonte / Cockpit  
- **Descrição**:  
  Ainda não há um painel dedicado para operação de fontes, mostrando, por exemplo:
  - distribuição de fontes por estado/mode/criticidade,  
  - fontes mais falhas nos últimos X dias,  
  - fontes desativadas há muito tempo.

- **Motivo de postergação**:  
  - Sem métricas dedicadas (D-28-OBS-1), qualquer dashboard seria baseado em consultas ad-hoc de logs ou banco.  
  - Time optou por postergar até que a camada de métricas estivesse minimamente estável.

- **Risco associado**:  
  - Complementa **R-28-I3** e **R-28-O2** (piora a capacidade de treinar e acompanhar operação).  

- **Custo estimado**:  
  - **Baixo/Médio** uma vez que as métricas existam.  

- **Janela alvo**:  
  - **E27.3**: construir painéis com base nas métricas criadas em E27.2.

- **Notas de implementação**:  
  - Pensar desde o início em uso diário pelo time de operações.  
  - Evitar dashboards "bonitos, porém inúteis"; focar em perguntas concretas do dia-a-dia.

---

#### 5.3.5 Eixo 4 — Governança e Fluxos de Aprovação para Fontes Críticas

##### D-28-GOV-1 — Ausência de mecanismos sistêmicos de aprovação para ações críticas

- **ID**: D-28-GOV-1  
- **Eixo**: Governança / Fluxos de aprovação  
- **Descrição**:  
  S28 não implementa, em código, mecanismos como "duas chaves" ou fluxos de aprovação para ações em fontes com `criticality` alta (por exemplo, desativar fonte que alimenta pipelines estratégicos).

- **Motivo de postergação**:  
  - Implica decisões organizacionais (quem aprova o quê, em que contexto) que extrapolam o escopo puramente técnico de E27.1.  
  - Exigir fluxo de aprovação já em S28 poderia travar a adoção inicial do console.

- **Risco associado**:  
  - Fortemente ligado a **R-28-O3** (decisões críticas sem política sistêmica).  

- **Custo estimado**:  
  - **Médio/Alto**: envolve modelo de permissões, UI para aprovação, trilha de auditoria e testes.  

- **Janela alvo**:  
  - Após maturidade inicial de uso do console, em **E27.3+**.  

- **Notas de implementação**:  
  - Começar com políticas simples (ex.: certas ações exigem usuário com papel mais alto).  
  - Evoluir depois para fluxos explícitos de aprovação com múltiplos aprovadores.  
  - Amarrar essas decisões com auditoria (D-28-AUD-1/D-28-AUD-2).

---

#### 5.3.6 Como esta dívida deve ser usada no planejamento futuro

Este bloco não é um "muro de lamentações"; é uma **lista intencional de investimentos futuros**.

Recomendações para uso prático:

1. **Planejamento de E27.2/E27.3**  
   - Ao abrir o planejamento de E27.2, usar os itens `D-28-AUD-*`, `D-28-VAL-*` e `D-28-OBS-*` como candidatos prioritários.  
   - Em E27.3, revisar `D-28-GOV-*` e o que sobrar dos demais e decidir o que vira sprint agora vs. backlog de longo prazo.

2. **ORR e revisão de riscos**  
   - Em revisões futuras, cruzar esta lista de dívidas com os riscos 5.2.  
   - Se algum risco aumentar em probabilidade/severidade, antecipar a quitação da dívida associada.

3. **Comunicação com stakeholders**  
   - Usar esta seção como explicação clara de que "não foi esquecido" — foi adiado com intenção e amarrado a planos futuros.

---

Com este Bloco 3, o Capítulo 5 da Sprint 28 transforma a noção de dívida técnica em um inventário estruturado, com IDs, eixos, motivos, riscos associados e janelas-alvo. O próximo bloco conecta essa dívida e os riscos a um **backlog de continuidade organizado por sprint (E27.2, E27.3 e além)**, além de rotinas de monitoração pós-sprint.

