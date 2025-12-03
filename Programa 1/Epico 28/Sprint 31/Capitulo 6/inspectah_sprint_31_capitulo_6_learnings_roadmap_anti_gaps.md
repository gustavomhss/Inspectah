# Inspectah — Sprint 31 (E28-S3)
## Capítulo 6 — Learnings, Roadmap & Anti-gaps

### 6.1 Lessons Learned

#### 6.1.1 Técnicas

1. Provider-first é viável como pilar estrutural, desde que tratado como sistema de produção, não script de ETL. A combinação client → normalizer → dedupe → ContentItem → métricas funcionou bem como esqueleto, e deve ser reaproveitada em próximos domínios.

2. O uso de `IngestionProfile` como unidade de configuração se mostrou correto. Ter um objeto único que concentra provider, filtros, janelas, budget e status facilita tanto gate técnico quanto operação via Console. Fica claro que perfis são a “moeda de controle” da ingestão.

3. Métricas por perfil não podem ser adorno. A S31 mostrou que sem métricas mínimas por perfil (calls, itens brutos, ContentItems, erros, uso de budget) é impossível discutir custo, sanidade e cobertura com seriedade. O modelo adotado (contadores agregados + snapshot por run) é um bom baseline, mas precisa ser aprofundado nas próximas sprints.

4. Dedupe e normalização precisam ser explicitamente parametrizáveis por domínio. As heurísticas usadas para notícias BR funcionam razoavelmente bem, mas a S31 deixou claro que não existe “dedupe universal”. O desenho com serviço dedicado de dedupe e chaves configuráveis é um acerto, e deve ser elevado a padrão de arquitetura.

5. O acoplamento leve entre Console v2 e o backend (UI consumindo apenas APIs estáveis de Console) se mostrou saudável. A S31 conseguiu evoluir o Console sem enfiar lógica de ingestão na UI, o que facilita futuras refatorações e mudanças de providers.

6. A integração provider-first → Programas 2–3 funciona melhor quando há um caso piloto real guiando o desenho. Trabalhar com um caso concreto de notícia/caso político ajudou a validar a trilha de proveniência e a evitar abstrações vazias na camada de verdade.

#### 6.1.2 Processuais

7. Ancorar a Sprint 31 explicitamente nos Programas 1–3 foi essencial para evitar que provider-first virasse um subprojeto paralelo. A disciplina de sempre perguntar “onde isso toca P1, P2 e P3?” blindou a sprint contra escopo decorativo.

8. O modelo de gates G0..G5 específico da S31 (models, provider ingestion, Console, legado, P2–P3) funcionou como “esqueleto mental” compartilhado entre squads. Todo mundo sabia que G2 e G3 eram o coração técnico da sprint, e que G5 era o cheque de verdade.

9. O uso do Sprint Playbook v3, com Capítulos 1–6 e blocos fixos, reduziu ambiguidades de documentação. A S31 reforça que manter Cap.3 e Cap.4 alinhados ao código não é luxo; é requisito para qualquer ORR decente.

10. A decisão de introduzir runbooks ainda dentro da sprint, em vez de deixar para “depois”, se provou extremamente valiosa. As simulações controladas de incidente (provider caindo, custo explodindo) revelaram lacunas que não apareceriam em testes puramente automatizados.

11. A separação entre “piloto BR” e “mundo inteiro” foi um aprendizado importante. Sempre que a conversa escorregou para ingestão global, a S31 trouxe a discussão de volta para o domínio piloto, o que evitou over-design e expectativas irreais.

#### 6.1.3 Produto, custo e estratégia

12. Provider-first muda a curva de custo e de velocidade ao mesmo tempo. A S31 mostrou, na prática, que é possível reduzir complexidade de scraping e ampliar cobertura, ao custo de depender de contratos e métricas de uso muito mais explícitos. O projeto só faz sentido se custo, cobertura e verdade forem discutidos juntos.

13. O Console de Fontes v2, mesmo em versão inicial, já se mostrou um instrumento de produto, não só de operação. A forma como perfis e métricas são expostos sugere um futuro em que “curadoria de perfis” é uma capacidade de produto central, inclusive para negociar qualidade e custo com parceiros externos.

14. A S31 reforça a importância de pilotos “altamente opinados”: escolher notícias BR (política/economia + um perfil social) como primeira arena foi acertado. O domínio é ruidoso, politicamente carregado e sensível a viés, o que obriga o desenho a ser sério desde cedo.

15. Finalmente, a sprint mostrou que é perigoso subestimar o tempo necessário para fechar o ciclo até Programas 2–3. Alimentar a camada de verdade a partir de providers demanda mais do que “puxar dados”; exige trilha de proveniência, contratos claros de ContentItem e disciplina de caso piloto.

---

### 6.2 Dívidas técnicas (S31-DT-*)

Abaixo, as principais dívidas técnicas da Sprint 31. Todas têm id, descrição, risco e sugestão de onde/ quando atacar.

1. S31-DT-001 — Observabilidade de scheduler de perfis
   Descrição: hoje o scheduler de perfis ainda não tem painel dedicado nem logs consolidados por perfil. Risco: dificuldade em ver claramente quais perfis estão rodando, com que frequência e com que taxa de erro, especialmente em ambientes com muitos perfis ativos. Sugestão: tratar em sprint de observabilidade de ingestão (provavelmente no próprio Épico E28), criando painéis e logs estruturados orientados a perfil.

2. S31-DT-002 — Testes de carga e stress específicos de provider-first
   Descrição: a S31 focou em casos piloto e cargas moderadas. Ainda não existem testes sistemáticos de carga para perfis “pesados” ou cenários de burst. Risco: comportamento imprevisível sob picos de volume; possíveis surpresas de custo ou latência. Sugestão: introduzir suites de load-tests focadas em ingestão provider-first em uma sprint posterior do E28, com cenários de volume e frequência mais agressivos.

3. S31-DT-003 — Políticas de dedupe por domínio
   Descrição: dedupe hoje está configurado de forma adequada ao domínio de notícias BR, mas ainda não há um mecanismo uniforme para parametrizar políticas de dedupe por domínio/tema/fonte. Risco: ao expandir para outros domínios (ex.: dados econômicos, social global), heurísticas atuais podem falhar ou gerar distorções. Sugestão: evoluir o serviço de dedupe para aceitar políticas declarativas e criar uma matriz de “políticas por domínio” em docs.

4. S31-DT-004 — UI de Console v2 para múltiplos providers
   Descrição: a UI foi desenhada em torno de um provedor de news principal e poucos perfis. Falta validar como a experiência escala para múltiplos providers e dezenas de perfis. Risco: Console se torna confuso ou pouco navegável conforme a quantidade de perfis cresce. Sugestão: em sprint futura de UX, introduzir filtros mais ricos, agrupamentos por domínio/tema e paginação/segmentação mais sofisticada.

5. S31-DT-005 — Automação de alertas de custo e erro
   Descrição: embora existam métricas e runbooks, alertas automáticos ainda são rudimentares ou inexistentes. Risco: incidentes de custo ou falhas de provider podem passar despercebidos até que alguém olhe manualmente os painéis. Sugestão: sprint específica de alerting, integrando métricas da ingestão provider-first com sistema de alertas (limites de calls, taxa de erro, ausência de dados em janelas esperadas).

6. S31-DT-006 — Hardening da trilha Provider → P2–P3
   Descrição: a integração providers → Programas 2–3 foi provada via caso piloto, mas ainda não há um conjunto robusto de testes automatizados cobrindo a trilha completa (inclusive casos de erro). Risco: regressões silenciosas ao evoluir modelos ou pipelines de P2–P3. Sugestão: introduzir testes de integração de ponta a ponta, com fixtures de ContentItems provider-first alimentando P2–P3 e asserts sobre a trilha de proveniência.

7. S31-DT-007 — Coverage e bias-check automatizado por provider
   Descrição: hoje a análise de cobertura e viés por provider é essencialmente manual. Risco: dependência de julgamento subjetivo e risco de enviesar a base de fatos sem perceber. Sugestão: em sprints posteriores do Épico E28, introduzir jobs periódicos de análise de cobertura/bias (por país, tema, espectro político), integrados a relatórios internos.

8. S31-DT-008 — Estrutura formal de “planos de ingestão” por domínio
   Descrição: a S31 focou no plano de ingestão BR, mas o conceito de “plano de ingestão por domínio” ainda não está formalizado em modelos e docs. Risco: expansão ad-hoc para novos domínios, sem critérios claros de custo, cobertura e verdade. Sugestão: criar um artefato padrão de “plano de ingestão” que seja pré-requisito para ligar provider-first em qualquer novo domínio.

---

### 6.3 Impacto da Sprint 31 no roadmap

1. Consolidação de provider-first como trilha principal de ingestão de notícias
   A S31 eleva provider-first de hipótese a trilha oficial de ingestão para notícias no Épico E28. Programas 1–3 passam a assumir que, para domínios semelhantes, a rota preferencial é via providers, e não scraping puro, desde que contratos e métricas sejam aceitáveis.

2. Repriorização de esforços de scraping
   A sprint reforça que o esforço pesado em scrapers customizados para grandes portais deve ser reavaliado. Em muitos casos, o investimento faz mais sentido em negociação/integração de providers do que em manutenção de scrapers frágeis. O roadmap deve refletir essa mudança de foco.

3. Introdução de um trilho explícito de “Provider Ops & Observabilidade”
   Ficou claro que provider-first traz um novo tipo de operação (contratos, limites, custo, cobertura) que merece um trilho próprio no roadmap. Próximas sprints do E28 devem incluir temas como observabilidade de providers, alertas, relatórios de cobertura e bias.

4. Aceleração da integração com Programas 2–3
   A prova de conceito com caso piloto sugere que é seguro antecipar algumas integrações de Programas 2–3 com providers em sprints seguintes, desde que sob escopo controlado. O roadmap pode puxar parte desse trabalho um pouco mais cedo dentro do próprio Épico E28.

5. Escopo revisitado para sprints seguintes do Épico E28
   A partir da S31, sprints posteriores de E28 podem ter escopos mais nítidos: uma sprint focando em ampliação de domínios (novos perfis), outra em observabilidade/alertas, outra em fairness/bias, e assim por diante. O capítulo de Programas 1–4 já foi atualizado para refletir essa granularidade.

6. Insumo direto para futuras sprints de governança e verdade
   A experiência com notícias BR via providers gerou insumos concretos para os squads de Verdade & Interpretação: exemplos de casos, padrões de viés de cobertura, necessidade de explicitar “mix de fontes” para cada caso. O roadmap de sprints focadas em governança de verdade deve incorporar esses aprendizados.

---

### 6.4 Anti-gaps & recomendações

A Sprint 31, além de entregar provider-first + Console v2 para o domínio piloto, expôs alguns buracos conceituais e operacionais que precisam ser cobertos.

1. Gap: ausência de um “Manifesto de Providers”
   Hoje, a decisão de usar ou não um provider ainda é muito implícita. Falta um documento central por domínio que explicite por que aquele provider faz sentido (cobertura, custo, TOS, viés conhecido), qual mix de fontes complementa o quadro e quais limites éticos/operacionais se aplicam. Recomendação: criar um “Manifesto de Providers” por domínio, como anexo aos Programas.

2. Gap: falta de definição formal de “plano de ingestão por domínio”
   A S31 tratou bem o piloto BR, mas o conceito de plano de ingestão ainda mora disperso em Cap.1, Cap.3 e anotações. Recomendação: formalizar um template único de plano, incluindo: domínios, fontes, providers, escopo, custos esperados, métricas de sucesso, riscos específicos.

3. Gap: critérios de fairness e cobertura ainda implícitos
   A discussão sobre viés e cobertura ficou, em grande parte, na esfera intuitiva. Recomendação: definir métricas e critérios mínimos de fairness/cobertura por domínio (mesmo que simples no início), além de um processo para revisá-los periodicamente.

4. Gap: ausência de “modo de simulação” de custo
   Embora a S31 tenha desenhado métricas e runbooks para custo, ainda falta um modo claro de simulação (“quanto custaria ligar estes perfis em produção por X meses?”). Recomendação: introduzir ferramentas simples de projeção de custo, usando métricas coletadas pelos perfis pilotos.

5. Gap: documentação de limites de uso (contract aware)
   A forma como limites de uso (rate limits, quotas mensais, restrições de TOS) são documentados ainda é dispersa. Recomendação: criar uma seção padrão de “limites e obrigações contratuais” por provider, referenciada tanto no Cap.3 quanto nos runbooks de incidente.

6. Gap: trilha de auditoria de decisões de rollout
   As decisões de ligar ou não certos perfis em ambientes específicos ainda não possuem uma trilha de auditoria consolidada. Recomendação: atrelar decisões de rollout/rollback sempre a registros formais (tags, entradas em ORR summary, notas em runbooks) e, no futuro, a um painel de governança operacional.

7. Gap: ligação explícita entre provider-first e políticas de verdade
   A S31 tocou em verdade apenas via caso piloto, mas não formalizou como o fato de uma informação ter vindo de provider X, Y ou Z influencia a política de promoção a “verdade” no Inspectah. Recomendação: sprints futuras de governança devem tratar explicitamente de peso de fontes, mix por caso, e como exibir isso para o usuário final.

Em conjunto, estas recomendações formam o pacote de Anti-gaps da Sprint 31. Elas não diminuem o valor da sprint; pelo contrário, transformam seus aprendizados em agenda concreta para as próximas sprints do Épico E28 e para o amadurecimento geral do Inspectah como plataforma de ingestão e verdade baseada em providers.

