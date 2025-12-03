# Inspectah — Sprint 32
## Capítulo 1 — Bloco 2
### Problemas concretos, Escopo Positivo e Fora de Escopo

#### 1.3 Problemas concretos que a Sprint 32 precisa atacar

A) Fluxo claim → blocos → estado de verdade ainda é teórico

Hoje o Inspectah já consegue:
- Ingerir conteúdo de múltiplas fontes (Programa 1).
- Interpretar esse conteúdo em forma de claims, entidades e sinais (Programa 2).
- Descrever, em documentos e blueprints, como o Truth‑DB e o Sistema de Blocos deveriam funcionar (Programa 3).

O que ainda **não existe** de forma sólida é um fluxo operacional, reprodutível e auditável que faça, na prática:

`claim (P2) → blocos (P3) → estado de verdade (P3)`

com as seguintes propriedades:
- implementado em código (serviços, modelos, scripts);
- coberto por testes (unidade + integração mínima);
- com gates e scorecards específicos da sprint (S32_G1, S32_G2);
- com evidências armazenadas de forma organizada em `out/evidence`.

Esse é o primeiro problema central da S32: transformar o **modelo mental** em um **fluxo executável e verificável**.

B) Contestação ainda não existe como fluxo executável

A ideia de contestação já existe no projeto: contestar um estado de verdade, reavaliar evidências, eventualmente reclassificar uma claim. Porém, isso está mais no plano conceitual (Programas, Épicos, Sistema de Blocos) do que em código.

Hoje não há um caminho mínimo que faça, de ponta a ponta:

1. Registrar formalmente uma contestação (quem contesta, com base em quê, contra qual estado/claim).
2. Disparar um fluxo de análise (ainda que simples, possivelmente automatizado e com stubs de comitê/agente).
3. Gerar um novo DecisionBlock que explique o resultado da contestação.
4. Atualizar o estado de verdade associado, sem apagar o histórico anterior.

A Sprint 32 precisa, portanto, entregar uma **Contestação v1 funcional**:
- focada em um tipo de claim;
- com fluxo mínimo, mas completo;
- testável via gates e replays de evidências;
- com trilha de auditoria de ponta a ponta.

C) Invariantes de Truth‑DB e Sistema de Blocos ainda não foram brutalmente explicitadas

O projeto já tem uma visão rica sobre blocos, estados e verdade. Porém, para operar 24/7 sem virar caos epistemológico, o Truth‑DB precisa de **invariantes claras em código**, por exemplo:
- nenhum bloco pode ficar “solto” (sem vínculo com claim/entidade e evidência relevante);
- nenhum estado de verdade pode ser alterado sem um DecisionBlock associado;
- contestações nunca apagam blocos anteriores, apenas acrescentam novos;
- referências entre blocos e evidências não podem se quebrar silenciosamente.

Hoje, várias dessas regras existem de forma dispersa em texto. A S32 precisa:
- consolidar quais invariantes são obrigatórios para v1;
- implementá‑las como testes/contratos ligados a `S32_G1_models_and_invariants`;
- garantir que qualquer violação derrube o gate e apareça no scorecard.

D) Falta acoplamento real com observabilidade 24/7

Não basta o Truth‑DB ser correto “em teoria”. Para operar em produção, o sistema precisa expor:
- métricas de promoções bem‑sucedidas vs tentativas;
- taxa de contestações registradas;
- erros por tipo de operação (promoção, contestação, gravação de blocos, migração etc.);
- latência p95 de um fluxo claim → estado de verdade.

Atualmente, o núcleo de observabilidade do Programa 1 já existe, mas o Truth‑DB ainda não está devidamente “plugado” nele. A S32 precisa ligar o motor de verdade nesses dutos:
- definindo métricas mínimas;
- publicando‑as na mesma stack do resto da plataforma;
- garantindo que os gates G2/G3 validem que essas métricas estão saindo.

E) Inexistência de um bundle de evidências dedicado à S32

Sem um bundle `inspectah_s32_evidence_bundle.zip`, faltam condições para:
- reexecutar cenários de promoção/contestação em ambiente de revisão (ORR);
- auditar regressões vs sprints futuras;
- demonstrar, de maneira objetiva, o que a sprint deixou pronto.

A S32 precisa instituir esse bundle como **artefato obrigatório**, incluindo:
- scorecards G0–G4;
- logs dos scripts de gates;
- snapshots/amostras de blocos e estados de verdade antes/depois de contestações;
- instruções mínimas de replay.

#### 1.4 Escopo positivo (o que entra de forma explícita na S32)

O escopo positivo da S32 é intencionalmente focado, mas não raso. Entram, de forma explícita:

1) Um tipo de claim prioritário com fluxo completo

Escolheremos (no Capítulo 2/3) **um tipo de claim prioritário** – por exemplo, “afirmação factual simples baseada em notícia” – como trilho principal da sprint. Para esse tipo de claim, a S32 deve entregar:
- mapping claro de claim → blocos (FactBlock, EvidenceBlock, DecisionBlock);
- fluxo de promoção implementado em serviço dedicado (`PromotionService` ou equivalente);
- testes de integração que façam o caminho completo claim → estado de verdade;
- cenários cobridos pelos gates `S32_G2_promotion_flows`.

2) Truth‑DB operacional v1

O Truth‑DB precisa chegar ao final da S32 com:
- modelos ajustados e migrações aplicáveis em ambiente real;
- invariantes mínimas implementadas (testes/asserts);
- consultas básicas viáveis para consumo posterior (Programa 4);
- ausência de regressões graves nos fluxos de ingestão/claims.

3) Contestação v1 funcional

A S32 entrega uma **primeira versão funcional de contestação**, com as seguintes propriedades:
- é possível registrar uma contestação contra um estado de verdade;
- existe um fluxo (ainda que simples) que processa essa contestação e chega a uma nova decisão;
- o resultado da contestação é registrado em blocos adicionais e atualiza o estado de verdade sem apagar a história anterior;
- cenários-chave são validados via `S32_G3_contestation_flows`.

4) Gates S32 + scorecards JSON

Serão implementados, no mínimo:
- `S32_G0_scope_and_baseline` — checagem de docs, filemap e preparação;
- `S32_G1_models_and_invariants` — sanidade do modelo e invariantes;
- `S32_G2_promotion_flows` — fluxos de promoção;
- `S32_G3_contestation_flows` — fluxos de contestação;
- `S32_G4_orr_and_bundle` — verificação final e bundle.

Cada gate gera um scorecard JSON em `out/scorecards/`, com campos padronizados para o conselho.

5) Observabilidade mínima do Truth‑DB

Pelo menos as seguintes métricas devem existir e estar integradas à stack padrão:
- taxa de promoções bem‑sucedidas;
- taxa de contestações registradas;
- erros por tipo de operação;
- latência p95 de um fluxo claim → estado de verdade (em cenário controlado).

6) Bundle de evidências S32

Criação do bundle `out/bundles/inspectah_s32_evidence_bundle.zip`, contendo:
- scorecards G0–G4;
- logs principais de execução dos gates;
- amostras de blocos e estados de verdade pré e pós‑contestação;
- instruções mínimas de replay.

#### 1.5 Fora de escopo (proteções explícitas da S32)

Para manter a sprint finita e executável, ficam explicitamente fora do escopo da S32:

- UIs avançadas de casos e narrativas (battlefield, mapas de argumentos, “quem ganha com isso?”, “mentiras em circulação agora” etc.).
- Governança humana complexa (workflows multi‑nível, votos ponderados por reputação, contratos B2B, SLAs e assim por diante).
- Integração profunda com blockchain para ancoragem dos blocos (além, no máximo, de um lacre mínimo/prova de conceito se não puser a sprint em risco).
- Otimizações pesadas de performance, sharding, multi‑região e tuning fino de consultas.
- Suporte amplo a múltiplos tipos de claims complexas; a S32 foca em **um tipo de claim bem resolvido** e deixa os demais para S33–S35.

Esses itens devem aparecer como **gaps assumidos** no Capítulo 6 (learnings & anti‑gaps) e alimentar o planejamento das próximas sprints, sem contaminar a execução da S32.

Este Bloco 2 fecha o recorte de problemas, escopo positivo e fora de escopo da Sprint 32, servindo como base para os estados‑alvo, gates, arquitetura e plano de execução que virão nos próximos capítulos.

