# Inspectah — Sprint 32
## Capítulo 1 — Bloco 4
### Síntese Executiva, Fronteira com Outros Docs e Ligações com Próximos Capítulos

#### 1.10 Síntese executiva do Capítulo 1 (em 5 frases duras)

1. A Sprint 32 é o momento em que o **Truth‑DB + Sistema de Blocos** deixam de ser blueprint e passam a operar, de forma enxuta, porém real, em modo **24/7** para pelo menos **um tipo de claim prioritário**.
2. O foco da S32 é montar um **fluxo completo e auditável** de claim (Programa 2) → blocos (Programa 3) → estado de verdade → contestação → novo estado, com invariantes em código e evidências registradas.
3. Observabilidade deixa de ser opcional: métricas mínimas de promoção, contestação, erros e latência p95 precisam estar plugadas na stack do Programa 1 para que a sprint seja considerada GO.
4. Contestação ganha uma **v1 funcional**: registrar, processar e registrar o resultado de contestações passa a ser algo que o Inspectah sabe fazer, com trilha de blocos e estados de verdade que nunca apagam o passado.
5. O sucesso da S32 é medido não pela quantidade de features, mas pela capacidade de **reexecutar, auditar e falsificar** decisões de verdade usando o bundle `inspectah_s32_evidence_bundle.zip` e os scorecards dos gates S32_G0–G4.

Esta é a “mensagem de elevador” da sprint: se alguém perguntar o que a S32 fez, é isso que deve sair da boca (ou do README) sem gaguejar.

---

#### 1.11 Fronteira da S32 com sprints anteriores e posteriores

**Com o que a S32 assume como base pronta (sprints anteriores):**
- Ingestão de fontes prioritárias está funcional, com console e saúde básica (Programa 1, S29–S31).  
- Claims, entidades e sinais são produzidos pelo Programa 2 com um nível mínimo de estrutura e logs.  
- O blueprint do Sistema de Blocos v2 e o Programa 3 v3 já existem como referência conceitual, mas nunca foram executados de ponta a ponta.

**O que a S32 deixa preparado para sprints seguintes (S33–S35):**
- Um Truth‑DB **vivo**, com estado de verdade e contestação funcionando para um tipo de claim, pronto para ser generalizado a outros tipos.  
- Interfaces claras para que o Programa 4 construa UIs, painéis e produtos em cima de estados de verdade e trilhas de contestação.  
- Uma base de invariantes, métricas e bundle de evidência que permite detectar regressões e crescer sem perder sanidade.

**Limite explícito:**  
S33–S35 não devem gastar energia refazendo o núcleo da S32; o objetivo é que possam **partir deste alicerce** para:
- suportar mais tipos de claims;
- enriquecer a lógica de contestação;
- construir battlefield de narrativas, Fact Cards, painéis “quem ganha com isso?” e demais produtos do pacote de ideias estáveis.

---

#### 1.12 Ligações do Capítulo 1 com os próximos capítulos da especificação

O Capítulo 1 estabelece o **porquê** e o **recorte** da S32. A partir daqui, os próximos capítulos derivam diretamente deste contrato:

- **Capítulo 2 — Estados‑alvo, Gates, Métricas & Invariantes**  
  - Traduz o que foi descrito aqui em **SA32_x**, `S32_Gx_*`, métricas e invariantes explícitas.  
  - A pergunta é: “Como medimos, em JSON e em testes, que o que o Capítulo 1 prometeu está de fato acontecendo?”

- **Capítulo 3 — Arquitetura & Filemap**  
  - Concretiza quais **módulos, serviços, modelos, migrações, testes e scripts** vão materializar o fluxo claim → verdade → contestação e os artefatos da S32.  
  - Aqui o foco é: “Onde, em termos de código e arquivos, cada pedaço do Capítulo 1 vai morar?”

- **Capítulo 4 — Execução, Evidências & Linha do Tempo**  
  - Define como o squad vai **fatiar o trabalho ao longo da sprint**, quais fases existem e como cada gate será acionado.  
  - Também estabelece quais evidências vão sendo produzidas em cada fase e como elas alimentam o bundle final.

- **Capítulo 5 — ORR & Operação Pós‑Sprint**  
  - Diz como o conselho e a operação 24/7 vão **julgar a sprint**: critérios de GO/NO‑GO, runbooks mínimos, plano de rollback e checagem dos gates históricos.  
  - Garante que o Truth‑DB não é só uma coisa “bonita no dev”, mas algo que consegue sobreviver na vida real.

- **Capítulo 6 — Learnings & Anti‑gaps**  
  - Conecta o que a S32 descobrir com o histórico de lessons learned do projeto e com o roadmap futuro.  
  - Aqui entram explicitamente os **gaps que decidimos não fechar** agora e as proteções para que não sejam esquecidos.

- **Capítulo 7 — Tasks**  
  - Fatiamento prático em tasks/PRs, com mapeamento dos estados‑alvo e gates.  
  - Serve como “ponte direta” entre a especificação e a execução diária (issues, branches, PRs).

Cada um desses capítulos precisa olhar de volta para o Capítulo 1 e responder à pergunta:  
> “Este pedaço ajuda a cumprir a promessa da S32 ou está tentando resolver outro problema?”

Se a resposta for “outro problema”, esse item deve ser tratado como **fora de escopo** da S32 e, no máximo, registrado como input para as próximas sprints.

---

#### 1.13 Como este Capítulo 1 deve ser usado na prática

- Como **contrato de intenção** da S32: qualquer discussão de escopo, trade‑off ou priorização deve ser referenciada aqui.  
- Como **filtro de tarefas**: tasks que não conectam claramente com os objetivos, problemas e definição de sucesso descritos aqui devem ser adiadas ou cortadas.  
- Como **referência para o ORR**: ao julgar a sprint, o conselho deve comparar o que está escrito aqui com o que foi realmente entregue em código, evidências e operação.

Se houver divergência grande entre o Capítulo 1 e o resto da documentação da S32, o default é considerar o Capítulo 1 como fonte de verdade para intenção de escopo – e ajustar os demais capítulos ou, se for o caso, registrar conscientemente que houve uma alteração de plano (com justificativa) ao longo da sprint.

Com este Bloco 4, o Capítulo 1 da Sprint 32 fica fechado: temos contexto, problemas, escopo, squad, riscos, decisões e síntese executiva que alinham todos os próximos capítulos ao objetivo real da sprint.