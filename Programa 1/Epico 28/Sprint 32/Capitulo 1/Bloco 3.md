# Inspectah — Sprint 32
## Capítulo 1 — Bloco 3
### Squad, Riscos, Decisões Pré-tomadas e Definição de Sucesso

#### 1.6 Squad responsável e papéis (versão operacional)

A Sprint 32 é conduzida pelo **Squad Verdade & Interpretação**, reforçado por dados/armazenamento e observabilidade. O conselho “all‑stars” funciona como bússola conceitual, mas aqui traduzimos isso em papéis operacionais mais concretos.

**Arquitetura de Verdade & Causalidade**  
- *Owner conceitual:* Judea Pearl (Chief Truth & Causality Architect).  
- *Responsabilidades práticas na sprint:*  
  - Definir, junto com o time, o modelo de estados de verdade (e.g., `pending`, `provisionally_true`, `true`, `contested`, `rejected`, etc.) para o tipo de claim prioritário.  
  - Ajudar a cravar regras de transição entre estados (o que pode mudar, quando e com base em quê).  
  - Garantir que contestações são tratadas como **tentativas de falsificação** e não como “mudanças de humor”.

**Modelo de Dados & Storage do Truth‑DB**  
- *Owner conceitual:* Michael Stonebraker (Chief Truth‑DB & Storage Architect).  
- *Responsabilidades práticas:*  
  - Liderar o desenho final dos modelos `FactBlock`, `EvidenceBlock`, `DecisionBlock`, `AnchorBlock` e estados de verdade.  
  - Definir migrações necessárias para suportar o escopo da S32, sem quebrar o que veio antes.  
  - Garantir integridade referencial e performance mínima aceitável para consultas básicas.

**Conhecimento & Recuperação (Consultabilidade)**  
- *Owner conceitual:* Peter Norvig (Chief Knowledge & Retrieval Architect).  
- *Responsabilidades práticas:*  
  - Garantir que o Truth‑DB não seja apenas “correto”, mas também **consultável**: queries chave para casos, estados de verdade e contestações precisam ser claras e eficientes.  
  - Ajudar a definir índices, visões ou endpoints internos que o Programa 4 usará no futuro.  
  - Assegurar que blocos e estados sejam representados de forma amigável para agentes e UIs.

**Agentes, Comitês & Fluxos de Decisão**  
- *Owner conceitual:* Percy Liang (Chief Agents & Committees Architect).  
- *Responsabilidades práticas:*  
  - Definir interfaces mínimas para que agentes/comitês possam interagir com fluxos de promoção e contestação.  
  - Especificar como o resultado dessas decisões é materializado em `DecisionBlocks`.  
  - Garantir que o fluxo v1 de contestação tenha ganchos claros para versões futuras mais sofisticadas.

**Execução, Escopo & Prioridade**  
- *Owner conceitual:* Andy Grove (Chief Execution & Scope Surgeon).  
- *Responsabilidades práticas:*  
  - Proteger a sprint contra escopo inflado; cortar sem dó tudo que não for crítico para o “esqueleto vivo” da S32.  
  - Ajudar a quebrar em milestones: modelos/migrações → promoção → contestação → ORR & bundle.  
  - Garantir que haja sempre algo **terminado** ao fim de cada fase.

**Qualidade, Testes & ORR**  
- *Owner conceitual:* Gerald Weinberg (Chief Quality & Testing Architect).  
- *Responsabilidades práticas:*  
  - Puxar a definição de invariantes e testabilidade desde o início (não como afterthought).  
  - Ancorar os gates G1–G3 em cenários que realmente estressam promoção/contestação.  
  - Definir quais evidências e logs entram no bundle da S32 para que o ORR seja de fato reprodutível.

**Falsificação & Evidência**  
- *Owner conceitual:* Karl Popper (Chief Falsification & Evidence Architect).  
- *Responsabilidades práticas:*  
  - Garantir que o design de contestação trate hipóteses como falsificáveis, não como dogmas.  
  - Ajudar a estruturar o vínculo entre claims, evidências e os critérios que justificam mudar um estado de verdade.  
  - Definir, junto com Norvig/Stonebraker, a forma como evidências são armazenadas e referenciadas nos blocos.

Na prática, o squad da sprint se organiza em três “sub‑frentes” de trabalho:

1. **Núcleo de dados & modelos** — donos de `models.py`, migrações, invariantes estruturais e consultas básicas.  
2. **Núcleo de fluxos & serviços** — donos de `PromotionService`, `ContestationService`, scripts de gates e cenários de teste.  
3. **Núcleo de observabilidade & evidências** — donos das métricas, logs, diretórios `out/evidence`, scorecards e bundle S32.

Essa divisão não é rígida, mas serve para garantir que ninguém tente “abraçar tudo” e que não falte dono para o pedaço mais chato: evidências e métricas.

---

#### 1.7 Riscos principais e como a S32 pretende mitigá‑los

**Risco 1 — Escopo “verdade do mundo” explode e mata a sprint.**  
- *Sintoma:* o time tenta cobrir muitos tipos de claim, muitos estados de verdade, uma contestação ultra‑complexa e várias UIs.  
- *Mitigação:*  
  - Fixar explicitamente **um tipo de claim prioritário** para a S32.  
  - Qualquer outro tipo de claim vira “seed” para S33+ (registrado no Capítulo 6).  
  - Gates e estados‑alvo vinculados a esse tipo de claim apenas (SA32_1, SA32_2, etc.).

**Risco 2 — Invariantes ficam bonitas no doc, mas não aparecem em código.**  
- *Sintoma:* documentos descrevem regras lindas, mas nada falha quando são violadas.  
- *Mitigação:*  
  - Para cada invariante crítica, exigir ao menos:  
    - um teste automatizado em `tests/truthdb/*`; ou  
    - um assert/checagem explícita em código, coberta por testes de integração.  
  - Vincular essas invariantes ao gate `S32_G1_models_and_invariants`. Se um teste que representa uma invariante falhar, **G1 é NO‑GO**, e a sprint não fecha.

**Risco 3 — Contestação v1 vira apenas um stub cosmético.**  
- *Sintoma:* rota de contestação existe, mas não muda nada relevante no Truth‑DB; não há novos blocos; estados de verdade não mudam.  
- *Mitigação:*  
  - Exigir pelo menos **um cenário end‑to‑end** de contestação que:  
    - consuma um estado de verdade existente;  
    - registre uma contestação;  
    - processe a contestação (ainda que via fluxo simples ou stub de comitê);  
    - gere novos blocos e atualize o estado de verdade;  
    - deixe trilha clara no bundle S32 (logs + dumps de blocos).  
  - Esse cenário deve ser obrigatório no gate `S32_G3_contestation_flows`.

**Risco 4 — Observabilidade é relegada a “coisa para a próxima sprint”.**  
- *Sintoma:* código do Truth‑DB funciona “no vácuo”, mas não gera métricas nem logs minimamente úteis.  
- *Mitigação:*  
  - Definir um conjunto mínimo de métricas obrigatórias (promoção, contestação, erros, latência p95) no Capítulo 2.  
  - Garantir que `S32_G2_promotion_flows` e `S32_G3_contestation_flows` validem não só o comportamento funcional, mas também a existência das métricas.  
  - Tornar impossível considerar a sprint **GO** sem essas métricas expostas (Capítulo 5: critérios de GO/NO‑GO).

**Risco 5 — Bundle de evidências incompleto ou inútil.**  
- *Sintoma:* o bundle existe, mas não contém scorecards completos, logs relevantes ou instruções de replay.  
- *Mitigação:*  
  - Especificar, já no Capítulo 3/4, a estrutura esperada do bundle `inspectah_s32_evidence_bundle.zip`.  
  - Vincular a checagem do bundle ao gate `S32_G4_orr_and_bundle`.  
  - Tratar qualquer ausência de scorecard ou logs essenciais como falha de G4.

**Risco 6 — Regressões silenciosas no pipeline anterior (ingestão/claims).**  
- *Sintoma:* tudo lindo em Truth‑DB, mas alguma mudança de modelo/migração quebra ingestão ou geração de claims.  
- *Mitigação:*  
  - Executar, como parte da rotina da S32, gates críticos de sprints anteriores ligados a ingestão e claims (ao menos em modo sanidade).  
  - Exigir no ORR da S32 (Capítulo 5) um item explícito: “status dos gates históricos críticos”.

---

#### 1.8 Decisões pré-tomadas que a S32 assume como dado

1. **Truth‑DB continua sendo o lugar canônico da verdade do Inspectah.**  
   Não há “atalhos” fora dele: qualquer estado de verdade ou resultado de contestação relevante precisa estar materializado em blocos/estados dentro do Truth‑DB.

2. **Sistema de Blocos segue o blueprint v2 como referência primária.**  
   - FactBlock, EvidenceBlock, DecisionBlock e outros tipos seguem o desenho do documento de Sistema de Blocos v2.  
   - Divergências necessárias na S32 devem ser documentadas explicitamente (Capítulo 3 e Capítulo 6).

3. **Contestação é sempre aditiva, nunca destrutiva.**  
   - Estados não são apagados ou sobreescritos sem rastro.  
   - Toda mudança relevante em um estado de verdade é acompanhada de um DecisionBlock que a explique.

4. **A S32 não redesenha o mundo: refina e concretiza.**  
   - O objetivo é tirar do papel o que já está decidido no Programa 3 v3 e no Roadmap Macro v3, não reinventar o modelo de verdade a cada commit.

5. **Gates e scorecards são parte do produto, não “infra lateral”.**  
   - Scripts em `bin/` e scorecards JSON em `out/scorecards/` são tratados como artefatos de primeira classe.  
   - Sem gates verdes e bundle coerente, a sprint não é GO, ainda que o código “pareça pronto”.

---

#### 1.9 Definição de sucesso da Sprint 32 (statement oficial)

A Sprint 32 é considerada **bem-sucedida** se, ao final, a seguinte afirmação for verdadeira sem malabarismo semântico:

> Para um tipo de claim prioritário, o Inspectah consegue **promover afirmações a estados de verdade, contestá‑las, reavaliá‑las e registrar todo o rastro** no Truth‑DB, com invariantes claras, métricas básicas expostas e um bundle de evidências (S32) suficiente para reexecutar os cenários de promoção/contestação em ambiente de revisão.

Essa frase se desdobra em critérios concretos:

- Há pelo menos um tipo de claim com fluxo completo claim → blocos → estado de verdade → contestação → novo estado.  
- Invariantes críticas do Truth‑DB estão codificadas e testadas, não apenas descritas.  
- Métricas de promoção, contestação, erros e latência p95 estão integradas à observabilidade.  
- Gates S32_G0–G4 estão verdes, com scorecards JSON consistentes.  
- O bundle `inspectah_s32_evidence_bundle.zip` existe, é completo e permite replays úteis.

Se qualquer uma dessas perninhas falhar de forma séria, a S32 deve ser tratada como **NO‑GO conceitual**, independentemente da quantidade de código entregue. O foco é construir um alicerce de verdade/contestação 24/7 confiável, não apenas “entregar features”.

Este Bloco 3 fecha a visão de squad, riscos, decisões pré-tomadas e definição de sucesso, concluindo o Capítulo 1 da Sprint 32 em nível adequado ao padrão de excelência do projeto.

