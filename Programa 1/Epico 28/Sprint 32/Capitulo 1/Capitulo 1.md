# Inspectah — Sprint 32
## Capítulo 1 — Contexto, Intenção e Problemas a Resolver

### 1.1 Contexto macro da Sprint 32 dentro do Épico E28

A Sprint 32 vive dentro do **Épico E28** (S29–S35), que tem como missão tirar o Inspectah do modo “plataforma promissora em construção” e colocá‑lo em um estado de **operação 24/7 confiável**, onde o ciclo completo

> **fonte → ingestão → interpretação → verdade/contestação → exposição**

funciona de ponta a ponta, com trilha de evidências, observabilidade e defesas contra besteira (erros honestos, viés, manipulação e “criatividade” de modelos).

Na linha do tempo até aqui (visão macro):

- **S29**: consolidou visão, cortes de escopo e o papel do Épico E28 como guarda‑chuva do modo 24/7 “verdade & casos”.
- **S30**: reforçou o pipeline 24/7, consolidou o modelo de operação contínua (ingestão + manutenção) e organizou os fluxos em torno dos Programas 1–4.
- **S31**: aprofundou o lado de ingestão/admin/manutenção e alinhou o Console/Operação com o novo modelo de programas.

A **S32** entra como sprint em que o foco se desloca de “ingestão + operação geral” para o **coração do Inspectah**:

- **Truth‑DB + Sistema de Blocos** deixam de ser só blueprint e passam a operar em modo realista (ainda que com escopo enxuto) 24/7.
- **Promoção de claims para estados de verdade** passa a ser um fluxo executável, testável e auditável.
- **Contestação** deixa de ser “uma ideia para depois” e vira **v1 funcional**: já dá para contestar um estado, disparar uma reavaliação mínima e registrar o rastro no Truth‑DB.

A S32 é, portanto, a sprint em que o Inspectah passa de:

> “Temos ingestão legal e um blueprint bonito de Truth‑DB”

para:

> “Temos um **esqueleto vivo de verdade e contestação 24/7**, com fluxos mínimos, scripts, evidências e ORR para bater em cima”.

### 1.2 Relação com os Programas 1–4

Conectando com o **Roadmap Macro v3** dos Programas:

- **Programa 1 — Data Hub & Operação 24/7**
  - Já entregou o básico: ingestão estável das fontes prioritárias, console de fontes e pilares de observabilidade.
  - Na S32, Programa 1 entra como **infraestrutura de operação**: garantir que os novos fluxos do Truth‑DB e contestação rodem 24/7 com logs/metrics encaixados.

- **Programa 2 — Interpretação, Claims & Entidades**
  - Já transforma conteúdo em **claims estruturadas, entidades e sinais**, com logs mínimos e trilha inicial de decisões.
  - Na S32, Programa 2 é o **alimentador oficial** do Truth‑DB: define quais tipos de claims entram no escopo da sprint e garante que o formato está sólido.

- **Programa 3 — Truth‑DB, Sistema de Blocos & Contestação**
  - É o protagonista da S32.
  - Pega as claims vindas do Programa 2 e transforma isso em blocos, estados de verdade e trilhas de contestação, respeitando o blueprint do Sistema de Blocos.

- **Programa 4 — Exposição, Produtos & Uso Responsável**
  - Por enquanto fica principalmente **escutando**.
  - A S32 prepara o “motor de verdade” que os produtos do Programa 4 vão consumir depois (Fact Cards, battlefield de narrativas, etc.), mas sem ainda entregar essas UIs ricas.

A S32 está, portanto, no ponto de interseção entre **Programa 2 (claims)** e **Programa 3 (verdade/contestação)**, com suporte de **Programa 1 (operação/observabilidade)** e preparando o terreno para **Programa 4 (produtos)**.

### 1.3 Squad responsável e papéis principais

A S32 é tocada principalmente pelo **Squad Verdade & Interpretação**, reforçado pelo núcleo de dados/armazenamento e observabilidade. Em termos de “conselho virtual” e papéis conceituais:

- **Judea Pearl** — Chief Truth & Causality Architect
  - Garante que o modelo de estados de verdade e contestação respeita causalidade mínima, não apaga histórico e não inventa mágica.

- **Michael Stonebraker** — Chief Truth‑DB & Storage Architect
  - Dono do modelo de dados, migrações, integridade do Truth‑DB e eficiência de consultas básicas.

- **Peter Norvig** — Chief Knowledge & Retrieval Architect
  - Cuida para que o Truth‑DB seja consultável e útil, não apenas “correto no papel”.

- **Percy Liang** — Chief Agents & Committees Architect
  - Garante que os fluxos de promoção/contestação tenham interfaces claras para agentes/comitês e que não haja buracos de decisão.

- **Andy Grove** — Chief Execution & Scope Surgeon
  - Cirurgia de escopo: corta exageros, garante que a S32 termina algo concreto.

- **Gerald Weinberg** — Chief Quality & Testing Architect
  - Puxa a barra de testes, invariantes e ORR.

- **Karl Popper** — Chief Falsification & Evidence Architect
  - Puxa o lado de contestação, falsificação e rigor da evidência.

Na prática da sprint, isso se traduz em:

- Devs & engenheiros focados em **modelos, serviços de promoção/contestação e scripts de gates**.
- Time de dados/observabilidade garantindo **métricas, logs e bundling de evidências**.
- Product/PO mantendo a linha: o objetivo é **verdade + contestação 24/7 enxutos e testáveis**, não um zoológico de features.

### 1.4 Problemas concretos que a S32 precisa resolver

1. **Fluxo claim → blocos → estado de verdade ainda é teórico.**
   - Hoje, temos claims estruturadas e um blueprint de blocos, mas não um fluxo real, com código, scripts e testes, que execute essa promoção em produção.

2. **Contestação não existe como fluxo executável.**
   - Há ideias de contestação (bonds, versões, battlefield etc.), mas não um caminho mínimo operacional para: registrar uma contestação, reavaliar a claim e registrar o novo estado com trilha de decisão.

3. **Truth‑DB e Sistema de Blocos carecem de invariantes operacionais explícitos.**
   - Não basta ter um modelo de dados: precisamos de **invariantes formais** (em testes, asserts, contratos) garantindo que:
     - blocos não perdem vínculo com evidências;
     - estados de verdade não “voltam no tempo” sem trilha de decisão;
     - contestações nunca apagam histórico.

4. **Falta acoplamento com observabilidade 24/7.**
   - O Truth‑DB ainda não expõe métricas claras de promoção/contestação, erros por tipo, latências e saúde.
   - Precisamos ligar esse motor na infra de métricas/logs definida no Programa 1.

5. **Não existe bundle de evidências dedicado à S32.**
   - Sem um bundle `inspectah_s32_evidence_bundle.zip`, não há como um conselho/ORR auditar a sprint com replays, logs e scorecards consistentes.

### 1.5 Escopo positivo da S32 (o que entra)

Entram na S32:

- Pelo menos **um tipo de claim prioritário** (ex.: “afirmação factual simples baseada em notícia”) com fluxo completo:
  - claim do Programa 2 → criação de blocos → estado de verdade → possibilidade de contestação e reavaliação.

- **Truth‑DB operacional v1**:
  - modelos ajustados;
  - migrações aplicáveis em ambiente real;
  - serviços de promoção/contestação implementados;
  - testes de invariantes e cenários principais.

- **Contestação v1 (fluxo mínimo, porém real):**
  - registrar uma contestação;
  - disparar um fluxo de análise mínimo (automaticamente ou via stub de comitê);
  - registrar o resultado na forma de novos blocos/estados.

- **Gates S32 e scorecards JSON:**
  - G0: escopo & baseline;
  - G1: modelos & invariantes;
  - G2: fluxos de promoção;
  - G3: fluxos de contestação;
  - G4: ORR & bundle.

- **Observabilidade mínima do Truth‑DB:**
  - métricas de promoção, contestação, erro e latência p95 expostas na stack padrão de observabilidade.

- **Bundle de evidências S32:**
  - scorecards, logs e amostras de blocos/estados empacotados para revisão.

### 1.6 Fora de escopo (para proteger a sprint)

Explicitamente fora da S32 (jogado para S33–S35 e outros épicos):

- UIs avançadas de casos: battlefield de narrativas, mapa de argumentos pró/contra, painéis “quem ganha com isso?”, “mentiras em circulação agora”, etc.
- Governança humana complexa (workflow multi‑nível, SLAs contratuais, votação ponderada por reputação, etc.).
- Integração pesada com blockchain (além de um lacre mínimo/prova de conceito, se couber em segurança) para ancoragem on‑chain.
- Otimizações de performance ou tuning fino de queries para grandes volumes.
- Suporte a dezenas de tipos de claims diferentes; a S32 foca em **1 tipo bem feito**, com invariantes, testes e evidências.

Esses itens podem aparecer no Capítulo 6 como **gaps assumidos** e seeds para S33+.

### 1.7 Riscos principais e mitigação

1. **Escopo explode em “sistema perfeito de verdade do mundo”.**
   - Mitigação: trancar o foco em 1 tipo de claim prioritário + fluxo mínimo de contestação.
   - Tudo extra é logado como dívida/gap, não implementado às pressas.

2. **Invariantes ficam vagas ou só em documento.**
   - Mitigação: invariantes precisam existir como **testes ou asserts** ligados aos gates G1–G3.

3. **Contestação v1 vira um stub simbólico sem valor.**
   - Mitigação: exigir que pelo menos um cenário completo de contestação funcione, com mudança de estado de verdade rastreável.

4. **Observabilidade é empurrada para “depois”.**
   - Mitigação: métrica mínima de promoção/contestação/erros/latência precisa existir para a sprint ser GO.

5. **Bundle de evidências incompleto.**
   - Mitigação: G4 falha se o bundle não estiver completo e reexecutável.

### 1.8 Definição de sucesso da Sprint 32 (visão PO)

A S32 é considerada **bem‑sucedida** se, ao final da sprint, for verdade dizer:

> “Para um tipo de claim prioritário, o Inspectah consegue **promover afirmações a estados de verdade, contestá‑las, reavaliá‑las e registrar todo o rastro** no Truth‑DB, com invariantes claras, métricas básicas e um bundle de evidências que qualquer pessoa técnica do conselho consegue usar para reexecutar os cenários em ambiente de revisão.”

Se essa frase não for verdadeira, a S32 vira **NO‑GO conceitual**, independentemente de quantas linhas de código foram escritas.

Este Capítulo 1 funciona como **contrato de intenção** da Sprint 32: tudo o que vier nos Capítulos 2–7 (gates, filemap, execução, ORR, learnings e tasks) deriva daqui e deve ser cobrado contra este contexto.

