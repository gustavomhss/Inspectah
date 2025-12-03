# Inspectah — Sprint 32
## Capítulo 6 — Bloco 2
### Learnings Técnicos — Truth-DB, Blocos, Estados e Contestação v1

> Este bloco consolida os **learnings técnicos** da Sprint 32 sobre o núcleo de verdade do Inspectah. A ideia é deixar registrado o que funciona, o que precisamos proteger com unhas e dentes, e quais decisões de engenharia se provaram estruturais para o futuro do Truth-DB.

---

#### 6.2.1 Modelagem do Truth-DB: blocos, estados e suas fronteiras

Um dos aprendizados mais fortes da S32 é que a modelagem do Truth-DB **não pode ser “apenas mais um schema relacional”**. Ela é, na prática, o modelo mental de como o Inspectah entende a própria noção de verdade.

A separação clara entre as entidades principais se mostrou essencial:

- `FactBlock`: captura o “núcleo duro” do enunciado factual que está sendo avaliado. É o que permanece mesmo se a interpretação e o contexto mudarem.  
- `EvidenceBlock`: registra as evidências que sustentam (ou, em versões futuras, enfraquecem) aquele fato. É o lugar da ancoragem concreta: fonte, data, documentos, trechos, medições.  
- `TruthState`: representa a situação atual daquela verdade dentro do sistema. É uma visão de leitura otimizada para responder à pergunta “como está isso agora?”.  
- `DecisionBlock`: registra decisões explícitas sobre o estado da verdade, incluindo justificativas, caminho de raciocínio e quem/que mecanismo tomou a decisão.  
- `ContestRecord`: materializa o ato de contestar. Sem ele, contestação vira um ruído nos logs; com ele, vira parte da história oficial.

A S32 mostrou que tentar “simplificar” essa estrutura leva rapidamente a problemas sérios. Por exemplo:

- misturar histórico e estado atual na mesma entidade torna difícil reconstruir a linha do tempo;  
- colapsar fato, evidência e decisão em uma única tabela deixa o sistema incapaz de responder “o que mudou, quando e por quê?”.

Learning fixo: **manter blocos, estados e decisões como entidades distintas é um requisito de arquitetura**, não um detalhe de implementação. Qualquer evolução futura deve respeitar essas fronteiras.

---

#### 6.2.2 Invariantes como contrato de segurança do núcleo de verdade

A Sprint 32 explicitou um conjunto de invariantes que, na prática, funcionam como o “cinto de segurança” do Truth-DB. Sem elas, qualquer bug vira potencialmente um desastre de confiança.

As invariantes críticas que emergiram são:

- Não existem blocos órfãos.  
  Nenhum `EvidenceBlock`, `DecisionBlock` ou `ContestRecord` pode existir sem seu `FactBlock` ou `TruthState` correspondente. Isso precisa ser garantido com FKs, validações de aplicação e testes.

- Estados finais de verdade exigem decisão explícita.  
  Se um `TruthState` assume um status final (por exemplo, “true”, “false”, “rejected”, “resolved”), deve haver sempre um `DecisionBlock` associado, registrando quem decidiu, com base em quê e quando.

- Histórico é monotônico.  
  Contestações, revisões e promoções não podem apagar blocos ou decisões anteriores. A linha do tempo precisa ser sempre crescente. Versões futuras podem introduzir compressão, snapshots ou camadas de indexação, mas **não podem reescrever o passado**.

- Contestações nunca somem sem deixar trilha.  
  Cada contestação deve gerar um `ContestRecord` persistente. Processar a contestação significa mudar o status desse registro e, possivelmente, o `TruthState`, mas nunca apagar o fato de que houve uma contestação.

Learning fixo: invariantes não podem morar só no texto dos Capítulos. Cada uma delas precisa ter:

- representação explícita em `app/truthdb/models.py` (constraints, validações, relacionamentos);  
- testes dedicados em `tests/truthdb/test_models_and_invariants.py`;  
- checagem automática em G1, G2 ou G3, com falha clara se algo for violado.

Sem isso, o Truth-DB vira um banco de dados qualquer com um nome bonito.

---

#### 6.2.3 Fluxo de promoção v1: clareza antes de esperteza

A implementação do fluxo de promoção na S32 ensinou uma lição simples e dura: **é muito fácil tentar ser inteligente demais, cedo demais**.

Quando o time tentou antecipar todos os casos futuros (vários tipos de claims, múltiplos níveis de verdade, heurísticas complexas), o resultado foi:

- explosão de ramificações de código difíceis de testar;  
- dificuldade em explicar a lógica para o conselho em ORR;  
- maior chance de efeitos colaterais inesperados.

Ao focar em uma v1 com escopo mais estreito, alguns princípios emergiram:

- Cada claim passa por um adaptador claro (`claims/adapters_truthdb.py`) que responde:  
  “qual é o fato que estamos tentando cristalizar aqui?” e “quais evidências mínimas acompanham esse fato?”.  
- O `PromotionService` faz uma coisa muito bem definida:  
  dado um `claim_id` válido e suportado, ele cria/atualiza blocos e o estado correspondente, seguindo as invariantes.  
- Erros são tratados como cidadãos de primeira classe:  
  claims inválidas, incompletas ou de tipo não suportado resultam em falhas claras e métricas de erro, não em estados parcialmente corrompidos.

Learning fixo: **v1 de promoção deve ser brutalmente clara, previsível e fácil de demonstrar**. A sofisticação vem depois, em camadas, nunca no primeiro passo.

---

#### 6.2.4 Fluxo de contestação v1: contestar é parte do modelo, não um “if extra”

Na contestação, o principal learning foi perceber que **“contestar” não pode ser só um if no código**.

A S32 estabeleceu que contestação é um fluxo completo, com entidades e responsabilidades próprias:

- `ContestationService.register_contestation(...)` registra a intenção de contestar e cria um `ContestRecord` consistente.  
- `ContestationService.process_contestation(...)` analisa o estado, aplica a lógica v1 de reação (marcar como contestado, criar um novo `DecisionBlock`, ajustar status do `TruthState`) e preserva o histórico.

O que se aprendeu ao longo da implementação:

- Se a contestação não deixa uma entidade persistida (ContestRecord), rapidamente se perde visibilidade sobre “quem contestou o quê e quando”.  
- Se a contestação atualiza diretamente o `TruthState` sem passar por um `DecisionBlock`, a história da decisão fica truncada.  
- Se a contestação não é coberta por testes de fluxo (`test_contestation_flows.py`), qualquer ajuste na lógica pode quebrar relações finas entre contestação, decisão e estado.

Learning fixo: o ato de contestar **é parte da semântica central do sistema**, não um adendo. Por isso, sempre que o Truth-DB evoluir, contestação precisa evoluir junto, com o mesmo nível de rigor de modelagem, teste e métricas.

---

#### 6.2.5 Métricas específicas do Truth-DB: sem elas, tudo vira suposição

Outro learning crítico da S32: **sem métricas específicas, o Truth-DB vira uma caixa-preta elegante, porém inútil do ponto de vista operacional**.

Métricas genéricas de API e infraestrutura (latência de endpoint, HTTP 5xx, CPU, memória) não respondem à pergunta: 

> “o núcleo de verdade está se comportando de forma saudável?”

As métricas que emergiram como mínimas e obrigatórias são, por exemplo:

- `truthdb_promotion_success_rate`: quantas promoções deram certo vs totais.  
- `truthdb_contestation_rate`: com que frequência o sistema vê contestações (por tipo, por tema, por período).  
- `truthdb_flow_error_rate`: quantos erros ocorrem nos fluxos principais de promoção/contestação.  
- `truthdb_flow_latency_p95`: o quão lentos estão esses fluxos sob carga real.

Learning fixo:

- Toda evolução do Truth-DB precisa vir acompanhada de **métricas de domínio**, não apenas de métricas de infra.  
- ORRs futuros devem exigir, como pré-requisito, evidência de que essas métricas estão sendo coletadas e entendidas pela equipe.

---

#### 6.2.6 Reexecução, bundles e “estado de verdade reprodutível”

Por fim, a S32 mostrou que o valor real do Truth-DB não está só em responder “o que é verdade agora?”, mas também em permitir reconstruir **“como chegamos a essa verdade”**.

O mecanismo que viabiliza isso, na prática, são os bundles de sprint:

- scorecards G0–G4;  
- evidências de migrações, testes de invariantes, fluxos de promoção e contestação;  
- README com instruções de replay.

Learning fixo:

- Um estado de verdade só é realmente confiável se for, dentro do possível, **reprodutível** a partir de evidências objetivas;  
- Bundles são parte fundamental dessa reprodutibilidade: permitem reexecutar gates, reanalisar fluxos e auditar decisões mesmo muito tempo depois da sprint.

---

#### 6.2.7 Síntese do Bloco 2

Do ponto de vista técnico, a Sprint 32 deixou claro que:

- O Truth-DB não é um “banco qualquer”: é um modelo explícito de como o Inspectah entende fatos, evidências, estados e decisões.  
- Invariantes fortes são tão importantes quanto as tabelas em si; sem elas, qualquer bug vira risco de colapso de confiança.  
- Fluxos de promoção e contestação precisam ser simples, previsíveis e auditáveis na v1 — e ir ganhando complexidade só quando a base estiver sólida.  
- Métricas específicas de domínio e bundles reexecutáveis são parte essencial do pacote; sem elas, não há como falar em “verdade” com seriedade operacional.

Os próximos blocos do Capítulo 6 vão pegar esses learnings técnicos e conectá-los a **learnings de processo, governança e cultura de evidência**, para que o que foi descoberto na S32 não se perca quando o sistema ficar muito maior e mais complexo.