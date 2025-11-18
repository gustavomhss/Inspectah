# Inspectah — Sprint 9  
## Capítulo 1 — Visão, Escopo, Invariantes e Critérios de Sucesso (v3)

---

### 0. One‑liner oficial da Sprint 9

> **“A Sprint 9 transforma o protótipo técnico da S8 em um produto interno v0 do Inspectah: Admin e Usuário operam consultas reais de preço, comparação e fato público, usando múltiplas fontes e um GPT especializado, com rastreabilidade forte e sinais mínimos de operação.”**

Se a **S8** provou que o pipeline funciona, a **S9** prova que ele é **usável, previsível e apresentável** como ferramenta interna — ainda com escopo limitado, mas **seguro para uso diário em cenários bem definidos**.

---

### 1. Posição da Sprint 9 no roadmap do Inspectah

- **S8 — Esqueleto funcional**  
  Pipeline multi‑fonte + GPT bundle‑only, Admin/Usuário v0, três cenários oficiais (preço médio, comparação simples, checagem factual), gates T0–T8 verdes. “Cara de laboratório”.

- **S9 — Produto interno v0 (esta sprint)**  
  Coloca **pele e músculos** no esqueleto da S8: experiências de Admin e Usuário que qualquer membro do time interno consegue usar, prompts GPT especializados por tipo de pergunta, multi‑fonte como padrão e observabilidade mínima.

- **S10–S12 (apenas referência)**  
  S10: Truth‑DB & Guardião de Blocos (pré‑blockchain).  
  S11: Blockchain & contestação (bond, disputa, ancoragem).  
  S12: Ingestão contínua & Comunidade.

A S9 é o degrau entre **“funciona”** e **“dá para usar de verdade”**. Tudo que for feito aqui deve:
1) consolidar o que a S8 entregou (sem retrabalho desnecessário),  
2) preparar o terreno para a Truth‑DB da S10,  
3) evitar decisões que atrapalhem S11/S12.

---

### 2. Problema que a Sprint 9 resolve (com exemplo concreto)

Após a S8, o Inspectah:
- **consegue**: ingerir dados de múltiplas fontes, consolidar em bundles, usar GPT bundle‑only e responder três tipos de pergunta com evidência rastreável;
- **não garante**: que um operador/usuário interno consiga fazer isso **sem ajuda de dev**, entendendo erros, ajustando fontes e confiando na resposta.

Exemplo concreto de hoje (pós‑S8):
- Um time interno quer monitorar **o preço médio de uma “cesta básica X” em dois supermercados diferentes**, e checar semanalmente se um político falou a verdade ao afirmar que “o preço caiu nos últimos 30 dias”.
- S8 tem tudo tecnicamente: fixtures, pipeline, GPT, evidências.
- Mas o operador ainda sofre para:
  - ver claramente quais fontes alimentam a cesta X,  
  - entender se houve falha de ingestão na semana,  
  - ajustar uma fonte quebrada,  
  - explicar para o time por que o Inspectah respondeu “não sei” ou “dados insuficientes”.

A **S9** resolve essa lacuna: Admin e Usuário passam a ter fluxos e feedbacks que permitam usar o Inspectah como **ferramenta real**, e não só como demo de laboratório.

---

### 3. Invariantes globais da Sprint 9 (leis invioláveis)

Estas são regras que **não podem ser quebradas** em nenhum momento da S9:

1. **Nenhuma resposta sem trilha completa de evidência.**  
   Para qualquer resposta exibida ao usuário (via User v1), deve existir um triplo consistente:  
   `QueryLog` ↔ `EvidenceBundle` ↔ `UserResponse`, com IDs cruzados e artefatos JSON persistidos.

2. **Nenhum cenário oficial usando fonte única.**  
   Em todos os cenários oficiais da S9 (preço médio, comparação simples, checagem factual simples), `meta.num_sources >= 2` é condição obrigatória. Qualquer fluxo “single source” é erro de produto.

3. **Nenhuma decisão GPT fora do bundle.**  
   O GPT **não pode** introduzir fatos que não estejam no EvidenceBundle. Se o bundle não traz a informação, a resposta deve refletir “dados insuficientes” ou incerteza, nunca inventar.

4. **Nenhum erro crítico silencioso.**  
   Falhas de ingestão, de fonte ou de pipeline que afetem cenários oficiais **devem** aparecer de forma visível para Admin (e refletir em UX de Usuário). É proibido “engolir” erro e seguir como se nada tivesse acontecido.

Estas invariantes servem como filtro: se qualquer decisão técnica as violar, ou a decisão é revista, ou este capítulo é atualizado conscientemente.

---

### 4. Objetivos inegociáveis da Sprint 9

1. **Admin v1 utilisável (produto interno)**  
   O operador consegue:
   - ver fontes agrupadas por **tipo de informação** (ex.: preço, fato público) e por cenário;
   - cadastrar, editar, ativar/desativar fontes com validações claras e mensagens de erro legíveis;
   - ver status de ingestão por fonte (último run, itens ingeridos, erros recentes) sem abrir log bruto.

2. **Usuário v1 utilisável (produto interno)**  
   O usuário consegue:
   - fazer perguntas em linguagem natural para **preço médio**, **comparação simples** e **checagem factual simples**;
   - receber respostas:
     - claras e diretas,
     - com resumo estruturado (valor, intervalo, período, nº de fontes, nível de confiança),
     - com acesso simples às evidências;
   - em casos de problema, receber mensagens explícitas (dados insuficientes, fonte com erro, pergunta fora de escopo).

3. **Motor de decisão GPT especializado por tipo**  
   - Prompts distintos para agregação, comparação e fato, alinhados ao blueprint do Inspectah;
   - uso estrito do EvidenceBundle como entrada;
   - saída sempre compatível com `UserResponse` (texto + resumo + confiança + limitações), incluindo convergência/divergência entre fontes.

4. **Multi‑fonte como padrão**  
   - Para cada tipo de pergunta suportado na S9, há **≥2 fontes reais** operando nos ambientes de demo;
   - as respostas deixam claro que múltiplas fontes foram consideradas;
   - divergências entre fontes são tratadas como sinal de produto (afetando confiança), não ruído descartável.

5. **Observabilidade mínima de produto**  
   - Métricas e evidências suficientes para responder, sem esforço desproporcional:
     - quantas consultas foram feitas por tipo de pergunta em uma janela (ex.: últimos 7 dias);
     - qual o p95 de latência de resposta por tipo;  
     - quais foram os principais erros recentes por rota (Admin/User) e por fonte.

6. **Demo de produto v0 reprodutível**  
   - Um roteiro de demo que percorre Admin → ingestão → User → evidências, usando os três cenários oficiais;  
   - qualquer dev/operador seguindo o roteiro consegue reproduzir a demo em ambiente local.

---

### 5. Não‑objetivos explícitos da Sprint 9

Para manter a sprint enxuta e protegida:

1. **Truth‑DB completa e blocos de conhecimento**  
   Modelagem detalhada de blocos, estados, versões e queries sobre blocos é trabalho da S10.

2. **Blockchain e contestação**  
   Ancoragem on‑chain, bonds e disputas são assunto da S11.

3. **Scheduler e ingestão contínua generalizada**  
   S9 pode ter jobs simples/determinísticos, mas não constrói o scheduler completo da S12.

4. **Field Designer completo e Explore avançado**  
   Ferramentas ricas de definição de campos e exploração ad‑hoc ficam para sprints futuras.

5. **Novos tipos de pergunta além dos três oficiais**  
   Projeções, séries temporais avançadas, análises complexas etc. ficam fora da S9.

6. **UI pública / app consumer / billing**  
   A S9 é totalmente focada em **uso interno**.

---

### 6. Trilhos de trabalho da Sprint 9 (escopo organizado)

#### 6.1 Trilho Admin (Operador)

Entregas:
- Lista de fontes por tipo de informação, com filtros básicos e status;
- Fluxos de criação, edição e ativação/desativação com validação e mensagens amigáveis;
- Tela/painel de status da fonte (último run, volume de itens, erros recorrentes);
- Garantia de que o operador consegue manter **≥2 fontes ativas** por tipo suportado.

Critério de aceitação de produto:
> Um operador que conhece o domínio, mas não o código, consegue manter fontes ativas, identificar uma fonte quebrada e agir (corrigir, desativar ou ajustar) usando apenas o Admin.

#### 6.2 Trilho Usuário (Consulta)

Entregas:
- Tela de pergunta com exemplos e microcopy que delimitam o escopo da S9;
- Feedback de estado (“buscando dados”, “resposta pronta”, “dados insuficientes”, “erro de fonte”);
- Tela de resposta com texto principal, quadro de resumo e acesso rápido às evidências.

Critério de aceitação:
> Para cada cenário oficial, um usuário interno não técnico consegue formular a pergunta, entender a resposta e abrir as evidências sem ajuda do time técnico.

#### 6.3 Trilho GPT & decisão multi‑fonte

Entregas:
- Prompt templates separados para agregação, comparação e fato;
- Contratos claros de entrada/saída para cada tipo, com testes cobrindo os casos de sucesso e de dados insuficientes;
- Comportamento definido para divergência entre fontes (ajuste de confiança, explicação textual).

Critério de aceitação:
> Em todos os cenários oficiais, a explicação textual do GPT e o resumo estruturado são coerentes com o bundle e as fontes; divergências são explicitadas.

#### 6.4 Trilho Observabilidade & Operação

Entregas:
- Métricas mínimas expostas/registradas para latência p50/p95, volume de consultas e taxa de erro por rota;
- Evidências S9 que permitam auditar query → bundle → resposta;
- Hooks mínimos para futuros watchers da Truth‑DB (sem implementá‑los ainda).

Critério de aceitação:
> Diante de uma reclamação (“resposta demorou” ou “resposta estranha”), o time consegue, em minutos, localizar a query, o bundle e as fontes envolvidas e dar uma explicação plausível usando apenas os artefatos padrão.

---

### 7. Critérios de sucesso (DoD) com metas numéricas

A S9 só é concluída quando **todos** os pontos abaixo forem verdadeiros (valores numéricos podem ser refinados no Cap. 2, mas a ordem de grandeza é obrigatória):

1. **Admin v1**
   - Para cada tipo de pergunta suportado, existem pelo menos **2 fontes ativas** em ambiente de demo;
   - Um fluxo de “fonte quebrada” foi executado end‑to‑end em teste manual (fonte com erro detectada via Admin, ação corretiva aplicada, cenário volta a passar nos goldens).

2. **Usuário v1**
   - Os três cenários oficiais funcionam a partir da UI, com taxa de erro (HTTP 5xx ou falhas inesperadas) **< 2%** em um conjunto de pelo menos 50 execuções de teste interno;
   - O p95 de latência de resposta para esses cenários, em ambiente de dev/CI, é **≤ 1,5 s** do ponto de vista de User API.

3. **GPT especializado e disciplinado**
   - Existem testes automatizados cobrindo pelo menos **1 caso feliz e 1 caso de dados insuficientes** por tipo de prompt;
   - Em um conjunto de 30 execuções de teste exploratório, não há nenhuma resposta que cite fatos inexistentes nos bundles (violação do “bundle‑only”).

4. **Multi‑fonte em operação**
   - Para 100% das execuções dos cenários oficiais usadas em T4/T5/T6, `meta.num_sources >= 2` é verdadeiro;
   - Qualquer violação disso faz o gate correspondente falhar.

5. **Observabilidade mínima**
   - É possível responder, via métricas e/ou evidências padrão:
     - número de consultas por tipo nos últimos 7 dias,  
     - p95 de latência por tipo nos últimos 7 dias,  
     - top 3 erros por rota no mesmo período.

6. **Gates T0–T8 em GO**
   - Todos os gates definidos no Cap. 2 estão em PASS, e T8 declara GO com base explícita nos critérios acima.

---

### 8. Dívidas técnicas assumidas conscientemente na S9

Algumas escolhas da S9 são **atalhos conscientes**, não estado final:

1. **Escopo estreito de tipos de pergunta**  
   Fica limitado a preço médio, comparação simples e fato básico. Dívida: generalizar para outros tipos (projeções, séries temporais, indicadores compostos) em S10+.

2. **UI funcional porém simples**  
   Foco em clareza e robustez, não em design refinado. Dívida: polimento visual, UX avançada e flows públicos em sprints futuras.

3. **Observabilidade “mínima suficiente”**  
   As métricas da S9 são o mínimo para operar; a malha completa de watchers/alertas é responsabilidade de S10+.

Estas dívidas devem aparecer no resumo final da S9 como input direto para o planejamento da S10–S12.

---

### 9. Handshake com os demais capítulos

- **Capítulo 2 — Gates T0–T8:** vai transformar objetivos, invariantes e metas numéricas em gates leoninos, scorecards e evidências objetivas. Nada entra em DONE sem passar por esses gates.
- **Capítulo 3 — Arquitetura & Filemap:** vai detalhar módulos, contratos, tipos de pergunta, prompts especializados e como Admin/Usuário/Observabilidade se organizam no código e nos dados.
- **Capítulo 4 — Execução:** vai decompor a sprint em fases, amarrar cada fase a um subconjunto de gates e descrever o roteiro de demo de produto v0 da S9.

Este Capítulo 1 é a **bússola de produto** da Sprint 9: se alguma decisão técnica divergir deste texto, ela deve ser revista ou o capítulo atualizado de forma consciente — nunca ignorado.

