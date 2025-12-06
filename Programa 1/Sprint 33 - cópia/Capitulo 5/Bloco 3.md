# Sprint 33 — Capítulo 5

## Bloco 3 — O que o Inspectah faz de diferente: operar verdade, não só infraestrutura

Este bloco aprofunda a seção 5.3 do capítulo, detalhando **como o Inspectah se afasta do padrão tradicional de operação de sistemas**. Em vez de operar apenas infraestrutura (CPU, memória, latência de request), a Sprint 33 começa a estruturar o que significa **operar um sistema de verdade** – um organismo que ingere, interpreta, contesta e consolida alegações sobre o mundo.

Enquanto boa parte do estado da arte de SRE/observabilidade se concentra na pergunta "o serviço está saudável?", o Inspectah, via S33, começa a responder perguntas do tipo:

- "a cadeia que leva alegações a fatos está íntegra e atual?";
- "o que acontece com a verdade do sistema quando uma fonte crítica falha?";
- "quão rápido o sistema reage a nova evidência forte?".

O OracleOps v1 é o primeiro instrumento da plataforma desenhado explicitamente para esse tipo de operação.

---

### 5.3.1 Componentes operacionais alinhados à jornada da informação

Em sistemas tradicionais, componentes operacionais costumam ser coisas como "serviço A", "banco B", "fila C" – objetos técnicos sem semântica própria além de sua função infraestrutural.

Na S33, o `components_map` não é uma lista de serviços abstratos; ele é um reflexo da **jornada da informação** dentro do Inspectah:

- fontes (RSS, APIs, bases oficiais, etc.);
- pipelines de ingestão e normalização;
- etapas de interpretação, classificação e enriquecimento de claims;
- passos de consolidação no Truth‑DB e no Sistema de Blocos;
- APIs e superfícies de consulta que expõem verdades e estados de casos.

Cada `component_id` mapeado pode ser lido como um degrau explícito na escada "do mundo para o fato". Operar esses componentes significa operar essa escada.

Isso tem duas consequências importantes:

1. **Quando um componente falha, não é só um serviço que cai:** é um pedaço identificável da jornada da informação que fica comprometido (por exemplo, ingestão de uma fonte crítica, atualização de um bloco de verdade, sincronização de contestação).
2. **Quando o cockpit mostra o estado de um componente, está mostrando o estado de uma parte da cadeia de verdade:** o operador sabe o que aquele componente representa na história maior, não só um hostname.

A S33 planta essa visão na arquitetura de operação: componentes como "primeira classe semântica", não só técnica.

---

### 5.3.2 SLOs que protegem integridade informacional, não apenas uptime

Na maioria dos sistemas, SLOs giram em torno de disponibilidade e latência técnica. No Inspectah, esses aspectos continuam importantes, mas não são suficientes. Um sistema pode estar "100% UP" e, ainda assim, servir informações antigas, incompletas ou desatualizadas a ponto de induzir usuários ao erro.

A S33 abre caminho para uma categoria diferente de SLOs, que vão além do técnico:

- **SLOs de recência de fonte:** tempo máximo aceitável entre uma atualização em uma fonte crítica (por exemplo, IBGE, diário oficial) e a incorporação dessa atualização no Data Hub.

- **SLOs de latência de promoção de alegações a fatos:** tempo máximo entre a chegada de uma alegação forte (ou evidência decisiva) e a atualização correspondente no Truth‑DB.

- **SLOs de resposta a contestação:** tempo máximo para avaliar uma contestação bem fundamentada sobre um fato importante.

- **SLOs de coerência de caso:** indicadores de que casos de alto impacto não ficaram "congelados" por longos períodos sem considerar novos dados relevantes.

Na S33, nem todos esses SLOs são implementados de forma plena – isso seria trabalho para várias sprints –, mas a arquitetura (`ops_slos`, `ops_slo_evaluator`, cockpit) é propositalmente desenhada para suportar esse tipo de meta. O recorte escolhido para a sprint pode focar em recência de ingestão e saúde de pipelines, mas a forma é geral: SLO como guarda‑chuva da integridade informacional, não só da infraestrutura.

Isso é um desvio real em relação ao mainstream: **o foco deixa de ser apenas "o serviço respondeu" e passa a incluir "a verdade está atual, consistente e bem suportada"**.

---

### 5.3.3 Bundles de incidentes como cápsulas de verdade operacional

Postmortems tradicionais registram o que aconteceu durante um incidente: timeline, causa raiz, impacto, ações de mitigação. Eles já são valiosos. No Inspectah, esse conceito é estendido.

Os bundles produzidos em `out/evidence/S33_G4_incidents/` reúnem, para cada incidente exercitado na S33:

- timeline textual;
- prints do cockpit em diferentes momentos;
- recortes de logs e métricas;
- contexto de SLOs na época do incidente (quais estavam em risco, violados ou ok);
- runbook usado, com notas sobre o que funcionou ou não.

Esses bundles funcionam como **cápsulas de verdade operacional**:

- contam a história factual de um problema (o que aconteceu, quando, o que se viu, o que se fez);
- podem ser revisados e reutilizados em treinamentos e simulações futuras;
- podem, em versões futuras, ser conectados ao próprio Truth‑DB como evidências sobre a confiabilidade interna do sistema.

Em um sistema comprometido com verdade e auditabilidade, é natural que a própria operação também se torne objeto de observação e registro. A S33 dá o primeiro passo nessa direção, estruturando a forma como incidentes operacionais são embalados e preservados.

---

### 5.3.4 ORR focada em "operar verdades" e não apenas em "subir serviço"

Operações clássicas de ORR normalmente verificam se:

- o serviço sobe em ambiente de produção;
- existem métricas e alertas mínimos;
- runbooks básicos estão escritos;
- integrações críticas não quebram nada óbvio.

Na S33, a ORR vai além:

- ela verifica se o operador convidado consegue entender **o que o sistema sabe sobre um recorte de mundo** (por exemplo: fontes ativas, casos em foco, pipelines críticos);
- se é possível seguir do sintoma (algo está vermelho no cockpit) até as evidências e runbooks relevantes;
- se a interface e os SLOs ajudam o operador a responder perguntas como:
  - "isso é um problema urgente?";
  - "isso afeta a qualidade da verdade que o Inspectah está expondo?";
  - "quais casos, fontes ou APIs podem estar entregando desinformação ou dados velhos por causa disso?".

A ORR da S33 avalia, portanto, a **operabilidade da camada de verdade**, não só a disponibilidade técnica das peças. É uma mudança de eixo: o sucesso é medido em termos de capacidade de cuidar da integridade do conhecimento do sistema.

---

### 5.3.5 OracleOps como sistema nervoso da plataforma de verdade

Num organismo vivo, o sistema nervoso é o que permite perceber o ambiente, reagir a estímulos, coordenar respostas, aprender com experiências. O OracleOps v1, como desenhado na S33, é o embrião de um sistema nervoso para o Inspectah.

- Os componentes operacionais são os "órgãos" que captam, transformam e exponham informação.
- Os SLOs funcionam como sensores que disparam dor quando alguma parte se afasta demais do funcionamento esperado.
- Os incidentes são os eventos em que algo deu errado o suficiente para merecer atenção consciente.
- Os runbooks são os reflexos condicionados: sequências de ação que o sistema aprendeu para lidar com problemas recorrentes.
- Os bundles de incidentes são a memória de longo prazo: registros estruturados de experiências passadas.
- O cockpit é o painel onde um "sistema nervoso central" humano/operador observa tudo isso e intervém.

Ao tratar esses elementos como **domínio explícito** e não apenas como ferramentas auxiliares, a S33 cria uma fundação para que, em sprints futuras, esse sistema nervoso se torne mais sofisticado:

- detecção precoce de anomalias na cadeia de verdade;
- priorização automática de incidentes com impacto epistemológico maior;
- sugestões de mitigação com base em experiências passadas;
- integração entre "veracidade do mundo" (Truth‑DB) e "veracidade interna" (saúde da própria plataforma).

---

### 5.3.6 Síntese: do estado da arte técnico ao estado da arte epistemológico

O diferencial da S33 não é apenas implementar boas práticas técnicas (que já são, por si, uma evolução importante). O diferencial está em **como essas práticas são recontextualizadas** para um sistema de verdade:

- componentes deixam de ser apenas serviços para virar etapas nomeadas da narrativa "do mundo ao fato";
- SLOs deixam de medir só disponibilidade e passam a ter vocabulário para recência, integridade e tempo de resposta epistemológica;
- incidentes e runbooks deixam de ser exclusivos da infraestrutura e passam a capturar falhas e respostas na cadeia de informação;
- ORR deixa de perguntar apenas "o serviço sobe?" e passa a perguntar "a verdade que o serviço entrega faz sentido e reage bem a mudanças?".

Este Bloco 3 registra esse "twist" conceitual. A partir da S33, operar o Inspectah significa, cada vez mais, **operar a qualidade e a confiabilidade do seu retrato do mundo**, e não apenas garantir que processos técnicos estejam rodando.