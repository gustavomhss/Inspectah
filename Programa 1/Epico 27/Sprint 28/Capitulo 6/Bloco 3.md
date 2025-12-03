# Inspectah — Sprint 28
## Capítulo 6 — Bloco 3
### Dívidas Técnicas — Visão Consolidada, Priorização e Estratégia de Tratamento

---

### 6.3.1 Propósito deste bloco

Cap.5 Bloco 3 já fez o inventário detalhado de dívidas técnicas da Sprint 28 (`D-28-*`).  
Este Bloco 3 do Capítulo 6 tem outro foco:

1. **Consolidar** essas dívidas em uma visão sintetizada e legível em 5–10 minutos.  
2. **Priorizar** o que é inegociável para E27.2/E27.3 versus o que pode ser tratado de forma incremental.  
3. **Vincular** cada grupo de dívida a riscos práticos e à estratégia de mitigação.  
4. **Sugerir** formatos de execução (sprint dedicada, waves dentro de uma sprint, refactors contínuos, etc.).

A ideia é que alguém planejando E27.2/E27.3 possa, só com este bloco, entender "onde dói mais" e "o que não pode escapar".

---

### 6.3.2 Mapa geral dos eixos de dívida da S28

Relembrando os eixos principais de dívida técnica gerados pela Sprint 28:

1. **Auditoria de operações em fonte**  
   - Falta de uma entidade de log (`SourceActionLog`).  
   - Ausência de timeline de ações no console.

2. **Validações profundas e UX por tipo de fonte**  
   - Validações ainda genéricas, pouco sensíveis ao tipo (`news_rss`, `api_json`, etc.).  
   - Ausência de wizards/guias para fontes mais complexas.

3. **Observabilidade orientada a fonte**  
   - Falta de métricas dedicadas por fonte/estado/mode.  
   - Ausência de dashboards específicos de operação de fontes.

4. **Governança de fontes críticas**  
   - Ausência de mecanismos sistêmicos de aprovação ("duas chaves") para ações em fontes de alta criticidade.

5. **Refinamentos estruturais de domínio e migrations**  
   - Risco de migrations pesadas em tabelas de fontes futuras.  
   - Necessidade de evitar divergência entre invariantes de domínio e lógica da API.

A prioridade não é tratar tudo de uma vez, e sim **orquestrar** essa dívida ao longo de E27.2/E27.3 e de sprints seguintes.

---

### 6.3.3 Top 5 dívidas técnicas inegociáveis (prioridade máxima)

Estas são as cinco dívidas que **não podem escapar** do horizonte E27.2/E27.3 sem gerar acúmulo perigoso de risco.

#### 6.3.3.1 D-28-AUD-1 — Ausência de `SourceActionLog`

- **Essência da dívida**:  
  Hoje, mudanças em fontes são visíveis apenas pelos campos da própria `Source` (`state`, `state_changed_at`, `state_reason`). Não há uma trilha de ações estruturada.

- **Por que é inegociável**:  
  - Sem log de ações, qualquer incidente em fontes exige investigação manual e pouco confiável.  
  - Impossível construir governança séria sem saber quem fez o quê, quando e como.

- **Janelas e formato sugerido**:  
  - **E27.2**:  
    - Modelagem, migration e implementação básica de `SourceActionLog`.  
    - Gravação das principais ações via Admin API.  
    - Endpoint simples de leitura (timeline crua).  
  - **E27.3**:  
    - Refinos, índices, possíveis integrações com Sistema de Blocos.

- **Formato de execução recomendado**:  
  - Wave dedicado dentro de E27.2, com escopo bem fechado, pois afeta modelo, API e, no futuro, UI.

---

#### 6.3.3.2 D-28-VAL-1 — Validações por tipo de fonte ausentes

- **Essência da dívida**:  
  Validações hoje são genéricas (obrigatoriedade, formato básico), sem inteligência específica por tipo de fonte.

- **Por que é inegociável**:  
  - Erros que poderiam ser detectados no formulário/API só aparecem na ingestão.  
  - Operadores pagam o preço em tentativas, erros e debugging.

- **Janelas e formato sugerido**:  
  - **E27.2**:  
    - Definir contrato de "validador por tipo" no backend.  
    - Implementar para tipos mais críticos (ex.: RSS de notícias, 1 API central).  
  - **E27.3+**:  
    - Expandir para mais tipos, com base em uso real.

- **Formato de execução recomendado**:  
  - Wave técnico dentro de E27.2, com forte parceria entre backend, ingestão e PO.

---

#### 6.3.3.3 D-28-OBS-1 — Métricas por fonte/estado/mode inexistentes

- **Essência da dívida**:  
  A ingestão 2.0 opera corretamente, mas carece de métricas específicas por fonte em um formato útil para observabilidade.

- **Por que é inegociável**:  
  - Sem métricas, o time de operação fica cego sobre quais fontes dão mais problema.  
  - Não há base numérica para priorizar melhorias em fontes.

- **Janelas e formato sugerido**:  
  - **E27.2**: instrumentação de métricas principais:  
    - ingestões bem-sucedidas por fonte,  
    - falhas por fonte,  
    - tempo desde última ingestão bem-sucedida, etc.  
  - **E27.3**: dashboards, alertas e watchers.

- **Formato de execução recomendado**:  
  - Trabalho conjunto Ingestão + Observabilidade, com desenvolvimento iterativo (começar pequeno e expandir).

---

#### 6.3.3.4 D-28-VAL-2 — Wizards inexistentes para fontes complexas

- **Essência da dívida**:  
  Interfaces de criação/edição são formulários planos; fontes mais complexas (APIs com autenticação, parâmetros, etc.) seriam muito melhor atendidas por wizards guiados.

- **Por que é prioritária (pós-VAL-1)**:  
  - Reduz drasticamente o atrito para operadores menos técnicos.  
  - Diminui a probabilidade de configuração incorreta em fontes críticas.

- **Janelas e formato sugerido**:  
  - **E27.3**:  
    - Após D-28-VAL-1 estar em boa forma, escolher 1–2 fontes estratégicas e criar wizards específicos.

- **Formato de execução recomendado**:  
  - Wave de UX/Frontend com apoio de backend (para testes de conexão e validações inline).

---

#### 6.3.3.5 D-28-GOV-1 — Falta de mecanismos sistêmicos de aprovação para fontes críticas

- **Essência da dívida**:  
  Decisões críticas (como desativar fontes de alta criticidade) ainda dependem apenas de processo humano e disciplina, sem apoio sistêmico.

- **Por que é prioritária no médio prazo**:  
  - Em ambientes de alta criticidade, confiar apenas em políticas informais é arriscado.  
  - Governança de verdade/fato exige que fontes críticas não possam ser desligadas de forma impulsiva.

- **Janelas e formato sugerido**:  
  - **E27.3+**:  
    - Definir política mínima (ex.: papéis com permissão específica).  
    - Evoluir depois para fluxos de aprovação com múltiplos aprovadores.

- **Formato de execução recomendado**:  
  - Trabalho conjunto Produto + Governança + Backend, talvez com participação do squad Verdade & Interpretação.

---

### 6.3.4 Dívidas adequadas a tratamento incremental (refinamentos contínuos)

Nem toda dívida exige um "mini-épico". Algumas podem (e devem) ser atacadas no fluxo normal de evolução.

#### 6.3.4.1 D-28-T2 — Risco de divergência entre invariantes de domínio e API

- **Natureza**:  
  Essa dívida aparece sempre que novos fluxos manipulam `Source` diretamente na API sem reutilizar invariantes e serviços de domínio.

- **Estratégia de tratamento**:  
  - Toda vez que uma nova funcionalidade tocar `Source`, revisar se está usando as funções de domínio corretas.  
  - Incluir checagens no code review e, idealmente, checklists para PRs.

#### 6.3.4.2 D-28-T3 — Migrações futuras pesadas em tabela de fontes

- **Natureza**:  
  É uma dívida de natureza "preventiva": o problema só se manifesta quando o volume de fontes for alto e mudanças de schema forem necessárias.

- **Estratégia de tratamento**:  
  - Formalizar guidelines de migrations para `Source` (evitar alterações destrutivas, considerar backfills assíncronos).  
  - Validar novas migrations em ambientes com volume de dados representativo.

#### 6.3.4.3 D-28-OBS-2 — Dashboards específicos de operação de fontes

- **Natureza**:  
  Depende diretamente de D-28-OBS-1 (sem métricas, não há painel).  

- **Estratégia de tratamento**:  
  - À medida que as métricas forem entrando em E27.2, ir montando painéis mínimos (até mesmo em estágios alpha) antes de consolidar "o" painel oficial em E27.3.

---

### 6.3.5 Estratégia de encaixe no planejamento de E27.2/E27.3

A partir da priorização acima, uma estratégia coerente de encaixe poderia ser:

- **E27.2 (Sprint 29)** — foco em **fundação de auditabilidade, validade e visibilidade**:  
  - D-28-AUD-1: `SourceActionLog` (versão básica).  
  - D-28-VAL-1: validações por tipo (fase 1).  
  - D-28-OBS-1: métricas por fonte/estado/mode.  
  - Começo de guidelines para D-28-T2/D-28-T3.

- **E27.3 (Sprint 30)** — foco em **experiência de operação e governança mínima**:  
  - D-28-AUD-2: timeline de ações no console.  
  - D-28-VAL-2: wizards para fontes complexas (pelo menos um caso crítico).  
  - D-28-OBS-2: dashboards de operação de fontes.  
  - D-28-GOV-1: primeira camada sistêmica de regras para fontes críticas.

Esse encaixe mantém um equilíbrio saudável entre trabalho estruturante (E27.2) e polimento orientado a usuários e governança (E27.3).

---

### 6.3.6 Como usar este bloco na prática

- **Para planejamento**:  
  - Usar a lista de Top 5 dívidas como base para definir objetivos de E27.2/E27.3.  
  - Estampar os IDs (`D-28-*`) em tickets e boards, garantindo rastreabilidade.

- **Para ORR e revisões futuras**:  
  - Revisitar este bloco ao final de E27.2/E27.3 para checar quais dívidas foram de fato quitadas.  
  - Se alguma dívida inegociável permanecer aberta, registrá-la explicitamente nos próximos Cap.5/6.

- **Para comunicação interna**:  
  - Este bloco é um artefato de transparência: mostra para o restante da organização que S28 não "escondeu" os pontos não resolvidos — apenas os organizou e posicionou no tempo.

---

Com este Bloco 3, o Capítulo 6 oferece uma visão consolidada, priorizada e acionável das dívidas técnicas de S28, servindo como ponte direta entre o inventário de Cap.5 e o planejamento concreto de E27.2/E27.3 e sprints seguintes.