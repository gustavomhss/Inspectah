# Inspectah — Sprint 31 (E28-S3)
## Capítulo 6 — Bloco 3: Impacto no Roadmap & Anti-gaps

### 6.15 Papel deste bloco

Este bloco amarra a Sprint 31 com duas perguntas bem pragmáticas:

1. **O que muda no roadmap depois da S31?**  
2. **Quais buracos conceituais/operacionais ainda ficaram abertos, e como blindar contra eles?**

Na prática:

- a Seção 6.16 fala de **impacto no roadmap** (Programas 1–4, Épico E28 e adjacências);
- a Seção 6.17 lista os **Anti-gaps** — pontos que não podem continuar implícitos se quisermos escalar provider-first sem nos sabotar.

---

### 6.16 Impacto da Sprint 31 no roadmap

#### 6.16.1 Provider-first sobe de “experimento” para “trilha oficial”

Antes da S31, provider-first era tratado como uma possibilidade forte, mas ainda hipotética. Depois da S31:

- provedores de news/social passam a ser a **rota preferencial** de ingestão para domínios semelhantes ao piloto BR;  
- scrapers customizados deixam de ser primeira escolha e viram **plano B** (para casos realmente sem provider viável ou para redundância crítica);
- Programas 1–3 passam a assumir que, sempre que houver provider decente disponível, a discussão começa por ele.

**Ajuste de roadmap:**  
Nos Programas 1–4, tudo que estava escrito como “scrapers para grandes portais de notícia” deve ser reavaliado sob a ótica “provider + complementos”, não “scraper by default”. Scrapers passam a ser item explícito de exceção, não padrão.

---

#### 6.16.2 Esforço de scraping precisa ser repriorizado

A S31 mostra que investir pesado em scrapers frágeis para grandes portais, quando já existem providers que concentram essas fontes, é má alocação de esforço:

- o custo de manutenção de scrapers é alto e recorrente;  
- mudanças de layout ou bloqueios geram retrabalho constante;  
- a qualidade dos dados muitas vezes não é superior à obtida via providers.

**Ajuste de roadmap:**

- Criar uma linha explícita de decisão:  
  1. *Existe provider que cubra esse portal/tema com qualidade aceitável e TOS compatível?*  
  2. *Se sim, usar provider-first + ajustes finos; se não, discutir scraper como exceção.*
- Reduzir a ambição de “scrapear o mundo” no curto prazo e focar em integrar bem os providers certos.

---

#### 6.16.3 Nasce um trilho próprio de “Provider Ops & Observabilidade”

Provider-first não é só ingestão; é também operação de contrato, custo e estabilidade.

A S31 evidenciou a necessidade de um trilho dedicado no roadmap para:

- observabilidade de providers (painéis por provider/perfil, histórico de runs, erros, latência);  
- alertas de custo, erro, silêncio, desequilíbrio de cobertura;  
- relatórios internos de cobertura e viés por provider/domínio.

**Ajuste de roadmap:**

- Dentro do Épico E28, reservar sprints (ou sub-sprints) focadas apenas em:  
  - métricas & painéis de provider-first;  
  - alertas paramétricos;  
  - relatórios internos de qualidade de ingestão por domínio.

---

#### 6.16.4 Integração com Programas 2–3 pode ser acelerada, mas com escopo limitado

O caso piloto da S31 mostrou que é possível ligar providers a Programas 2–3 **sem gambiarras**. Isso abre espaço para antecipar integrações mais ricas em sprints seguintes, desde que:

- o escopo permaneça controlado (casos piloto, temas críticos, domínios bem entendidos);  
- a trilha de proveniência continue clara (Provider → Perfil → ContentItem → Claim → FactBlock).

**Ajuste de roadmap:**

- Em Programas 2–3, marcar explicitamente casos/pilotos que devem ser alimentados por providers nas próximas sprints de E28;  
- Garantir que cada integração nova venha com pelo menos um caso real e trace completo, não só “capacidade abstrata”.

---

#### 6.16.5 Escopo das sprints seguintes de E28 fica mais nítido

Com a S31 concluída, o Épico E28 deixa de ser apenas “ingestão 2.0” e ganha clusters de foco mais claros:

1. **Cluster A — Expansão de domínios e perfis**  
   - novos domínios geográficos/temáticos;  
   - novos perfis dentro de domínios já abertos;  
   - definição de planos de ingestão por domínio (ver Anti-gap 3).

2. **Cluster B — Observabilidade, custo e incidentes**  
   - painéis, alertas, histórico de runs;  
   - simulações de custo, projeções;  
   - runbooks e automações para incidentes.

3. **Cluster C — Fairness, cobertura e governança de fontes**  
   - relatórios de cobertura/bias;  
   - pesos de fontes para camada de verdade;  
   - documentação e exposição transparente de “mix de fontes”.

**Ajuste de roadmap:**  
Os Programas 1–4 e o Playbook do Épico E28 devem listar essas trilhas explicitamente, em vez de tratar “ingestão” como um bloco monolítico.

---

#### 6.16.6 Input direto para futuras sprints de governança de verdade

Provider-first com notícias BR produziu:

- exemplos concretos de casos com múltiplas fontes;
- amostras de viés de cobertura (quem fala sobre o quê, com que frequência);
- claridade maior sobre o que significa “confiar mais” ou “confiar menos” em determinados conjuntos de fontes.

**Ajuste de roadmap:**

- Sprints de governança, verdade e reputação de fontes devem usar os artefatos da S31 como dados de treino: casos piloto, relatórios internos, amostras de cobertura.  
- Políticas de promoção a verdade (como o Inspectah decide o que é fato consolidado) precisam incorporar, no futuro, o “mix de sources” e seu histórico, não apenas o conteúdo textual.

---

### 6.17 Anti-gaps: o que não pode ficar implícito

Anti-gaps são os **pontos cegos identificados** que, se deixados soltos, viram bomba-relógio. A S31 expôs alguns que precisam ser tratados como requisitos, não só “boas ideias”.

#### Anti-gap 1 — Manifesto de Providers por domínio

Hoje, a escolha de providers ainda é meio implícita (“parece bom, vamos usar”). Isso não escala.

**O que falta:**

- um documento por domínio que responda:  
  - por que estes providers foram escolhidos;  
  - que parte do mundo/tema cada um cobre;  
  - quais são os limites contratuais e éticos;  
  - quais são os viéses conhecidos.

**Recomendação:**

- Criar, para cada domínio, um **Manifesto de Providers** como anexo aos Programas.  
- Tratar o Manifesto como peça obrigatória antes de ligar provider-first em produção para aquele domínio.

---

#### Anti-gap 2 — Plano de Ingestão por Domínio (PID) como artefato formal

Na prática, o plano de ingestão BR existe espalhado entre Cap.1, Cap.3, Cap.6 e Programas. Isso funciona enquanto o número de domínios é pequeno; depois vira confusão.

**O que falta:**

- um artefato único por domínio que descreva:  
  - universo de fontes (providers + legados);  
  - escopo de ingestão (o que entra, o que fica fora);  
  - custos estimados;  
  - métricas desejadas (cobertura, latência, frequência);  
  - riscos específicos daquele domínio.

**Recomendação:**

- Definir um template padrão de **Plano de Ingestão por Domínio (PID)** e usá-lo como pré-condição para abrir novos domínios em provider-first.  
- Conectar PIDs diretamente aos Programas 1–3, para garantir que ingestão não corra solta sem amarração com verdade/produto.

---

#### Anti-gap 3 — Critérios mínimos de fairness e cobertura

A discussão sobre viés e cobertura na S31 foi rica, mas ainda muito humana/intuitiva.

**O que falta:**

- critérios mínimos, ainda que simples, que definam:  
  - o que significa “cobrir razoavelmente” um domínio (por fonte, por espectro político, por região);  
  - sinais objetivos de que estamos dependendo demais de um tipo de fonte.

**Recomendação:**

- Introduzir, em sprints posteriores de E28, métricas mínimas de fairness/cobertura (mesmo que rústicas) e painéis internos que permitam ver, por domínio, se estamos caindo em monocultura de fonte.

---

#### Anti-gap 4 — Modo de simulação/projeção de custo

Hoje, o time consegue olhar custo **a posteriori** (calls, volume), mas simular “quanto custaria ligar esses perfis por X meses?” ainda é meio artesanal.

**O que falta:**

- ferramenta simples que permita responder perguntas do tipo:  
  - “Se eu duplicar a frequência deste perfil, qual o impacto estimado em calls/mês?”;  
  - “Se eu ligar estes cinco perfis piloto em produção, qual faixa de custo espero ver?”

**Recomendação:**

- Criar um modo de **simulação de custo** usando dados históricos das ingestões piloto (calls, volume por run).  
- Integrar esse modo a discussões de produto/finanças ao decidir expansão de domínios.

---

#### Anti-gap 5 — Documentação de limites e obrigações contratuais

Limites de uso (rate limits, quotas, cláusulas de TOS) hoje aparecem em conversas e anotações, não em um mapa centralizado.

**O que falta:**

- um lugar único por provider/domínio que liste:  
  - limites de chamadas por janela;  
  - tipos de uso permitidos/proibidos;  
  - obrigações específicas (ex.: exibição de créditos, restrições de redistribuição).

**Recomendação:**

- Adicionar, ao Manifesto de Providers, uma seção padrão de **limites & obrigações contratuais**.  
- Ligar essa seção diretamente aos runbooks de incidentes (para quando bater limite ou receber aviso do provider).

---

#### Anti-gap 6 — Trilha de auditoria das decisões de rollout

Hoje, decisões de “ligar/desligar” perfis e domínios ainda dependem muito de contexto oral e mensagens dispersas.

**O que falta:**

- uma trilha que diga:  
  - quando determinado perfil/domínio foi ligado ou desligado;  
  - por quem;  
  - com qual justificativa;  
  - sob quais condições (flags, ambiente, limites).

**Recomendação:**

- Atrelar toda decisão de rollout/rollback a:  
  - entradas no `sprint_XX_orr_summary.md` correspondentes;  
  - tags/labels em repositório (ex.: `provider_pilot_br_go`, `provider_pilot_br_paused`);  
  - em estágios futuros, um painel simples de governança operacional.

---

#### Anti-gap 7 — Ligação explícita entre provider-first e políticas de verdade

Provider-first muda o mix de fontes que alimentam a Truth-DB, mas isso ainda não está formalmente refletido nas políticas de promoção a verdade.

**O que falta:**

- explicitar:  
  - como o Inspectah pondera o fato de uma informação vir de provider A vs provider B;  
  - como o mix de fontes (news, dados oficiais, social) influencia o peso de uma alegação;  
  - que transparência será oferecida ao usuário final sobre essa composição.

**Recomendação:**

- As sprints de governança de verdade devem tratar provider-first como primeira classe:  
  - desenhar como “mix de fontes” entra nos comitês de verdade;  
  - definir como exibir isso (ex.: “este fato se apoia em X fontes de notícia, Y dados oficiais, Z sinais sociais”).

---

### 6.18 Resultado esperado deste bloco

Com este Bloco 3, a Sprint 31 deixa de ser uma sprint “apenas técnica” e passa a ocupar seu lugar correto:

- como ponto de virada do roadmap (provider-first sobe a trilho principal, scraping vira exceção, observabilidade de providers ganha trilho próprio);
- como detonador de uma agenda clara de Anti-gaps (Manifesto de Providers, PIDs, fairness, custo, contratos, auditoria, políticas de verdade).

A partir daqui, qualquer planejamento sério de sprints do Épico E28 e das sprints de governança/verdade precisa consultar este bloco como checklist: se algum desses Anti-gaps continuar implícito, é sinal de que ainda estamos construindo o futuro do Inspectah em terreno móvel demais.

