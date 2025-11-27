# 6 – Lições Aprendidas, Riscos & Próximos Passos (Verdade & Interpretação / Casos Inspectah) – v2 extremo

Este Capítulo 6 fecha o ciclo desta sprint para o Squad **Verdade & Interpretação**, com foco no eixo **Casos Inspectah + Coleções + Camada de Produto** descrito no Cap. 5.

Ele tem cinco objetivos explícitos:

1. Registrar, sem maquiagem, o que **funcionou bem** ao transformar a Truth‑DB e os comitês em produto (Casos Inspectah, coleções, cockpit mínimo).  
2. Explicitar o que **doeu ou ficou frágil** – tanto técnica quanto conceitualmente – e que precisa ser tratado como risco ou débito visível.  
3. Assumir, por escrito, quais decisões desta sprint passam a ser **fundação estável** para as próximas (o que não pode mais ser quebrado sem grande motivo).  
4. Traduzir as observações em um conjunto concreto de **recomendações e próximos passos** para S23–S25 e para a Fase 2 (Sistema de Blocos completo, reputação, comunidade, on‑chain).  
5. Amarrar o Cap. 5 à visão macro do Inspectah: não é só “um cockpit bonitinho”, é o primeiro rosto da camada de Verdade & Interpretação perante o mundo.

---

## 6.1 – Lições aprendidas

### 6.1.1 – O que funcionou (pontos fortes da sprint)

**(1) Caso Inspectah como view estruturada em cima da Truth‑DB**  
A decisão de modelar o **Caso Inspectah** como uma *view estruturada* sobre Claims, TruthRecords, TruthChangeEvents, decisões de comitê e evidências foi um acerto forte:

- Impediu a criação de uma “base paralela de casos” desconectada da Truth‑DB.  
- Garantiu que cada caso canônico possa ser rastreado até as entidades de verdade (sem copiar/colar texto).  
- Permitiu que `docs/cases/case_*.yaml` funcione como **camada editorial versionada**, e não como duplicação de dados.

Na prática, o modelo case_yaml + resolver em `app/cases/` criou uma ponte clara entre **mundo editorial** (como contamos a história) e **mundo de dados** (como o sistema provou/aferiu a verdade).

**(2) Case Layer (`app/cases/`) como contrato de produto**  
Centralizar casos e coleções em `app/cases/` (domain + repository + resolver + schemas + routes) evitou uma série de problemas clássicos:

- Não há mais "endpoint de produto" falando direto com a Truth‑DB; tudo passa pelo resolver.  
- A API de produto (casos/coleções) tornou‑se um **contrato explícito** que o frontend e futuras integrações podem depender.  
- Mudanças internas na Truth‑DB podem, em tese, ser absorvidas pela Case Layer sem quebrar a superfície de produto.

Isso reduz a entropia: a equipe sabe que qualquer coisa relacionada a “caso” ou “coleção temática” vive atrás de `app/cases/`.

**(3) Cockpit mínimo focado em personas A/B**  
Mesmo com UI deliberadamente enxuta, o recorte `/cases`, `/cases/:id`, `/collections`, `/collections/:id` demonstrou que:

- Persona A (analista/jornalista) consegue, de fato, sair de uma afirmação ou tema e chegar em uma visão consolidada do caso + evidências.  
- Persona B (cidadão curioso) consegue navegar por temas (coleções) e entender, ao menos de forma básica, “qual é a posição do Inspectah” em relação a certas narrativas.

Esse cockpit mínimo mostrou que **não é necessário uma UI gigantesca** para tornar a Truth‑DB visível; bastam poucos pontos de entrada bem definidos.

**(4) Scripts, evidências e CI de produto alinhados ao padrão do projeto**  
Tratar scripts de check/metrics/demo de casos/coleções como cidadãos de primeira classe em `bin/` e evidências em `out/evidence/` foi importante para:

- impedir que a camada de produto virasse “remember-me da demo”;  
- manter a mesma disciplina de reproducibilidade aplicada às sprints anteriores (gates Sx_Gy, bundles, scorecards).  

Resultado: demos, métricas e artefatos de produto são reexecutáveis, auditáveis e versionados junto com o código.

**(5) GP0–GP4 como ponte entre visão de produto e gates técnicos**  
Ter definido GP0–GP4 (enquadramento, caso, página de caso, coleções, curadoria+métricas) e ligado esses gates ao ORR/GO deixou claro que:

- a sprint não entrega “produto” se só G0–G6 estiverem verdes;  
- a camada de Verdade & Interpretação precisa ser julgada também por **valor prático** para A/B/C, não só por elegância técnica.

---

### 6.1.2 – O que doeu / pontos de fricção

**(1) Curadoria ainda muito manual e dependente de especialistas**  
Criar ou ajustar casos canônicos ainda é um processo custoso:

- Exige que o curador entenda bem o modelo interno (Claims, TruthRecords, comitês, debunker).  
- Envolve leitura de múltiplas fontes, decisões editoriais finas e preenchimento manual de `case_*.yaml`.  
- Qualquer mudança relevante na Truth‑DB pode tornar um caso desatualizado sem nenhum alerta automático.

Hoje, a curadoria funciona, mas é **artesanal**. Isso é aceitável no estágio atual, mas não escala.

**(2) Timeline de truth é útil, mas ainda “2D” para casos realmente complexos**  
A timeline que aparece nos casos canônicos cumpre seu papel para um arco simples (afirmação → comitê → verdade atual), mas:

- fica rapidamente densa em cenários com muitas mudanças, múltiplas fontes ou longos períodos de contestação;  
- não diferencia bem “tipos de evento” (ex.: atualização de dado oficial vs decisão de comitê vs correção de erro factual);  
- ainda não representa “camadas de narrativa” (discurso político vs dado técnico vs imprensa, etc.).

A estrutura atual é suficiente para MVP de produto, mas limitada para casos “épicos”.

**(3) Métricas de produto ainda embrionárias**  
As métricas introduzidas nesta sprint – como `N_casos_canonicos`, `coverage_casos_em_colecoes`, distribuição de estados de truth e `click_distance_A` – são importantes como primeira camada, porém:

- não capturam percepção subjetiva de clareza/confiança;  
- não medem tempo/esforço de curadoria de ponta a ponta;  
- não estão ainda conectadas a um painel contínuo (a leitura ainda é manual, via `metrics.json`).

Precisam evoluir de “foto” para “série temporal de produto”.

**(4) Gap entre casos canônicos e o fluxo contínuo de ingestão**  
Nesta sprint, casos canônicos foram escolhidos com forte componente manual (casos bons de demo). Isso é útil, mas revela um risco:

- o sistema ainda não propõe automaticamente “candidatos a caso” com base no fluxo de ingestão, volume de menções ou conflitos;  
- há risco de desconexão entre o que é relevante “no mundo real” e o que está sendo curado como caso.

**(5) Ausência de reputação, comunidade e trilha pública de contestação**  
Por decisão consciente de escopo, a sprint não tocou em:

- reputação de fontes/atores/curadores;  
- contestação pública estruturada (ex.: usuários contestando casos);  
- ancoragem on‑chain ou em Sistema de Blocos completo.

O resultado é um produto forte em verdade interna, mas ainda **monástico**: a verdade é discutida por comitês internos, com pouca visibilidade de conflito público.

---

## 6.2 – Riscos mapeados

### 6.2.1 – Riscos técnicos

**Risco T1 – "Case drift": casos descolados da Truth‑DB**  
Quando Claims, TruthRecords ou decisões de comitê mudam, um Caso Inspectah pode ficar desatualizado ou incoerente.

Impacto:
- casos exibirem estado de truth que não bate mais com a Truth‑DB;  
- coleções temáticas apresentarem narrativas que já foram revisitadas.

Mitigações recomendadas:
- tornar `sXX_cases_check` parte de rotinas periódicas (cron/CI) em staging/produção;  
- introduzir um campo de “última reconciliação” no modelo de caso resolvido;  
- planejar, em sprints futuras, um job `reconcile_cases` que sinalize casos com divergências relevantes.

**Risco T2 – Acoplamento forte da Case Layer ao modelo atual da Truth‑DB**  
A Case Layer depende de certas invariantes da Truth‑DB (ex.: um único FACT ativo por claim, tipos de estado, estrutura de eventos). Se esses invariantes mudam sem coordenação, a Case Layer quebra.

Mitigações recomendadas:
- manter `app/cases/resolver.py` como o único lugar onde a Truth‑DB é “interpretada” em termos de casos;  
- documentar explicitamente, em anexo técnico, quais invariantes de Truth‑DB a Case Layer assume;  
- criar testes de contrato entre Truth‑DB e Case Layer, rodando em gates de S23–S25.

**Risco T3 – Falta de observabilidade dedicada à Case Layer**  
Hoje, logs/métricas são focados no pipeline de ingestão, comitês, Debunker, etc. A Case Layer pode sofrer com:

- endpoints lentos;  
- erros de resolução;  
- payloads excessivamente grandes;

sem que isso seja monitorado.

Mitigações recomendadas:
- introduzir métricas específicas para endpoints `/api/cases*` e `/api/collections*` (latência, taxa de erro, tamanho médio de payload);  
- instrumentar logs de resolução de casos (ex.: quantas entidades são carregadas por caso, número de eventos em timeline) para detectar casos extremos.

### 6.2.2 – Riscos de produto/UX

**Risco P1 – Expectativa equivocada de "verdade absoluta" a partir dos casos**  
Se o usuário interpretar o Caso Inspectah como “versão final e eterna da verdade”, perde-se a noção de **estado temporal e revisabilidade**.

Mitigações recomendadas:
- sempre mostrar timestamp de última atualização da verdade do caso;  
- deixar visível que o caso é um recorte da Truth‑DB em um ponto no tempo, não um oráculo imutável;  
- introduzir, em UI futura, uma forma simples de ver “histórico de revisões” do caso.

**Risco P2 – Sobrecarga cognitiva em casos excessivamente complexos**  
Casos com muitos eventos, múltiplas entidades e longos períodos de contestação tendem a produzir telas difíceis de ler.

Mitigações recomendadas:
- quebrar casos gigantes em sub‑casos temáticos quando fizer sentido;  
- planejar visualizações específicas (segmentação de timeline, filtros de evento, views focadas por entidade);  
- evitar misturar “todas as narrativas possíveis” em um único caso.

**Risco P3 – Desalinhamento entre casos canônicos e principais dores reais**  
Se o conjunto de casos não acompanhar as narrativas que mais impactam a sociedade, o Inspectah pode ser percebido como “legal, mas irrelevante”.

Mitigações recomendadas:
- usar sinais do pipeline de ingestão (frequência de temas, entidades, conflitos) para priorizar casos;  
- estabelecer metas por sprint para casos ligados a assuntos de alta relevância pública.

**Risco P4 – Curadoria interna como gargalo operacional**  
Se apenas poucas pessoas dominam fluxo e critérios de `docs/cases/`, a capacidade de criar/atualizar casos fica limitada.

Mitigações recomendadas:
- simplificar ainda mais o modelo de caso onde for possível, mantendo lastro na Truth‑DB;  
- criar templates mais guiados para casos comuns (ex.: “dado oficial vs declaração X”);  
- introduzir ferramentas de apoio (assistentes/LLMs internos) para sugerir estrutura de casos, mantendo o humano no laço para validação.

---

## 6.3 – Débitos assumidos (técnicos e de produto)

### 6.3.1 – Débitos técnicos

1. **Console de curador inexistente (tudo via arquivos + CLI)**  
   Hoje o curador trabalha em arquivos YAML e scripts. Funciona, mas não é amigável para um usuário menos técnico.

2. **Ausência de suíte robusta de testes para a Case Layer**  
   Existem checks e scripts, mas falta uma suíte focada em:
   - resolução de casos complexos;  
   - integridade da timeline sob diferentes cenários;  
   - comportamento da API de casos/coleções em cenários limite.

3. **Métricas de produto confinadas a arquivos locais**  
   `metrics.json` ainda não foi integrado a um stack de observabilidade; depende de leitura manual.

4. **Observabilidade de endpoints de casos/coleções ainda genérica**  
   A camada de produto não tem dashboards próprios; compartilha a infraestrutura genérica do backend.

### 6.3.2 – Débitos de produto/UX

1. **Visualizações especializadas para conflito ainda ausentes**  
   Nada como timelines segmentadas, gráficos de confiança, ou views dedicadas a “versões concorrentes da narrativa” foi implementado nesta sprint.

2. **Onboarding e explicação in‑product mínimos**  
   A UI atual assume um usuário relativamente instruído; falta contexto inline (tooltips, seções “como ler este caso”, exemplos guiados).

3. **Fluxos de feedback do usuário inexistentes**  
   Não há um canal nativo onde o usuário possa contestar, comentar ou sugerir melhorias diretamente a partir de um caso.

4. **Integração explícita com Sistema de Blocos/on‑chain postergada**  
   Casos não expõem, ainda, sinais de imutabilidade ou âncoras externas; isso foi conscientemente empurrado para a Fase 2.

Esses débitos não são bugs; são **pedaços do mapa** que a sprint escolheu não percorrer agora para preservar a sanidade e o foco.

---

## 6.4 – Decisões fundacionais desta sprint (o que passa a ser “Lei”)

O squad recomenda tratar as seguintes decisões como **fundação estável** para sprints futuras. Mudar isso exige forte justificativa e replanejamento:

1. **Caso Inspectah continua sendo uma view sobre Truth‑DB, não uma base paralela**  
   Qualquer tentação de replicar dados da Truth‑DB em outro store para “facilitar” casos deve ser tratada como exceção extrema.

2. **`app/cases/` é o boundary oficial de produto para casos/coleções**  
   Nada que queira expor um “caso” ou uma “coleção” pode ignorar esse módulo.

3. **`docs/cases/` é o repositório único de configurações editoriais de casos e coleções**  
   Não se aceita YAML paralelo, planilha secreta etc. Tudo converte para esse formato.

4. **Scripts de check e métricas de produto passam a ser gates efetivos**  
   O projeto assume que `sXX_cases_check` e `sXX_cases_metrics` continuarão existindo, evoluindo e sendo cobrados em ORR.

5. **GP0–GP4 entram no “contrato psicológico” da sprint**  
   Novas sprints de Verdade & Interpretação são julgadas não apenas pelo motor interno, mas também pela camada de produto/experiência que apresentam.

---

## 6.5 – Próximos passos recomendados (S23–S25)

### 6.5.1 – Evolução da Case Layer e dos Casos Inspectah

1. **Amadurecer a API de `app/cases/` como contrato formal**  
   - Especificar contratos (schemas, tipos de erro) em doc separado;  
   - Adicionar testes de contrato que garantam estabilidade entre sprints.

2. **Aumentar o número e a diversidade de casos canônicos**  
   - Definir metas de casos por sprint (por tema, por tipo de narrativa);  
   - Garantir pelo menos alguns casos “quentes” por sprint, alinhados com narrativas atuais.

3. **Introduzir um mecanismo leve de “drift alert”**  
   - Começar com um script que compara, periodicamente, estados de truth em casos vs Truth‑DB;  
   - sinalizar casos que passaram de certo “tempo máximo sem reconciliação”.

### 6.5.2 – Curadoria & Ferramentas

1. **Criar um “Case Builder” interno (mesmo que simples)**  
   - Uma UI de formulário minimalista que preenche/edita `case_*.yaml` por trás;  
   - Integração com buscas de Claims/TruthRecords para reduzir o atrito.

2. **Explorar uso de agentes/LLMs como auxiliares de curadoria**  
   - agente sugere estrutura inicial de caso com base em Claims/Events e textos de fontes;  
   - curador humano edita/valida antes de publicação.

3. **Documentar mais exemplos de casos “bem resolvidos”**  
   - uma galeria interna de bons casos, com antes/depois, ajuda a padronizar qualidade.

### 6.5.3 – Métricas de produto & observabilidade

1. **Promover métricas de produto ao stack de observabilidade**  
   - exportar valores de `metrics.json` para o sistema de métricas (Prometheus, etc.);  
   - construir painel com evolução de número de casos, cobertura por tema, distribuição de estados de truth.

2. **Medir custo de curadoria**  
   - criar uma métrica aproximada (tempo/passo) para criar/editar caso;  
   - usar isso para dimensionar investimento em ferramentas de curadoria.

3. **Instrumentar endpoints de casos/coleções**  
   - métricas de latência, erro, tamanho de payload;  
   - alertas para endpoints com comportamento degradado.

---

## 6.6 – Ponte para Fase 2 (Sistema de Blocos, reputação, comunidade, on‑chain)

As decisões e aprendizados desta sprint são insumo direto para a Fase 2. O Cap. 6 recomenda:

1. **Mapear Casos Inspectah → Sistema de Blocos**  
   - definir como um caso corresponde a blocos/sub-blocos/anchors;  
   - planejar que eventos (mudanças de truth, decisões de comitê, contestação forte) devem ser “elevados” a blocos imutáveis.

2. **Começar a pensar reputação na superfície de casos**  
   - desenhar como scores de fontes/atores/curadores poderiam aparecer em Casos Inspectah;  
   - garantir que qualquer score seja explicável (o que compôs a nota?).

3. **Especificar um modelo de contestação pública controlada**  
   - permitir que usuários levantem dúvidas, anexem novas evidências, sugiram revisões;  
   - integrar esse fluxo com Debunker v0/v1 e com comitês, mantendo triple redundancy.

4. **Planejar visualizações avançadas para conflitos prolongados**  
   - views que mostrem “camadas de narrativa” (político, imprensa, dado oficial);  
   - timelines densas com filtro por tipo de evento.

---

## 6.7 – Fechamento

Esta sprint conseguiu dar ao Inspectah um **primeiro rosto consistente** da camada de Verdade & Interpretação:

- Casos Inspectah viraram uma unidade concreta de produto, rastreada até a Truth‑DB;  
- coleções temáticas começaram a organizar o caos informacional em prateleiras compreensíveis;  
- o cockpit mínimo mostrou que já é possível navegar verdade, não só logs.

Ao mesmo tempo, o Cap. 6 deixa claro que essa face ainda é **controlada, interna e contida**: curadoria é artesanal, métricas são iniciais, visualizações são simples e a sociedade ainda não entrou no ringue (sem reputação, sem contestação pública, sem on‑chain).

O papel das próximas sprints – e da Fase 2 – é, justamente, pegar essa fundação sólida e começar a abrir o sistema, com cuidado, para um mundo onde a verdade é disputada, contestada e, ainda assim, precisa ser tratada com o mesmo rigor civilizatório que o Inspectah quer praticar desde o dia 0.

