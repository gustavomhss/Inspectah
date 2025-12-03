# Sprint 29 — Capítulo 6
## Bloco 1 — Papel do Capítulo 6 e foco em riscos, débitos e long tail

Os Capítulos 1 a 5 da Sprint 29 já responderam às perguntas clássicas de uma sprint de alto rigor:

- **Capítulo 1** — Por que esta sprint existe? Qual problema resolve? O que é sucesso?  
- **Capítulo 2** — Como decidimos se ela passou ou falhou? Quais gates, métricas e scorecards são obrigatórios?  
- **Capítulo 3** — Onde cada peça vive na árvore de arquivos, no backend, no frontend e na infraestrutura?  
- **Capítulo 4** — Como executar, em waves, até produzir evidências concretas e gates em PASS?  
- **Capítulo 5** — O que isso significa para o produto, para o ORR, para o Épico E28 e para o Programa 1?

O Capítulo 6 entra como a camada final de honestidade e disciplina: ele existe para impedir que a Sprint 29 pareça mais "resolvida" do que realmente está. Em vez de vender apenas o que foi conquistado, o Capítulo 6 registra, de forma explícita e organizada:

- riscos que acompanham a introdução de fluxos de agentes configuráveis;  
- débitos técnicos conscientemente assumidos para caber no recorte da S29;  
- plano de mitigação e follow-up (o que fazer com esses riscos e débitos, em que horizonte);  
- critérios para monitorar o comportamento do sistema depois da sprint, incluindo quando recuar (rollback) e quando expandir o escopo;  
- o "long tail" da S29 — isto é, quais artefatos, decisões e aprendizados precisam ser carregados para as próximas sprints, especialmente dentro do Épico E28 e das sprints de Verdade/Debunker/Comitês (S23–S25).

Em outras palavras, se o Capítulo 5 responde "onde chegamos", o Capítulo 6 responde "qual o preço, quais riscos e o que não podemos esquecer daqui para frente".

---

### 1.1. Por que um capítulo inteiro só para riscos e long tail

Num projeto como o Inspectah, em que o objetivo é lidar com verdade, evidência e governança em domínios sensíveis, o risco de autoengano técnico é alto. É muito fácil:

- comemorar a UI nova de fluxo de agentes;  
- ficar satisfeito com os gates em PASS;  
- e esquecer que uma mudança de fluxo em domínio sensível pode alterar decisões reais sobre fatos.

O Capítulo 6 existe para **blindar a S29 contra esse tipo de amnésia estrutural**. Ele transforma riscos e dívidas em entidades nomeadas, em vez de deixá-los escondidos em comentários de PR ou na cabeça de quem implementou.

Este bloco, em particular, define o papel do capítulo e estabelece algumas regras de jogo:

1. Nenhum risco relevante deve ficar implícito. Se alguém na equipe consegue formular um receio concreto sobre fluxos configuráveis, esse receio merece pelo menos ser avaliado e registrado.  
2. Todo débito técnico que possa impactar E28.x, S23–S25 ou a operação deve aparecer de forma tratável (com descrição, impacto e sugestão de follow-up).  
3. Monitoramento pós-sprint e critérios de rollback/expansão não são opcionais: são parte da definição de "sprint saudável" quando o assunto toca fluxo de decisão e verdade.

---

### 1.2. Quatro eixos de atenção do Capítulo 6

Para manter o Capítulo 6 estruturado e útil, ele organiza o pensamento em quatro eixos principais:

1. **Riscos**  
   - Técnicos (modelo de fluxo, catálogo de papéis, performance, consistência back/front);  
   - de produto e governança (quem altera fluxos, impacto em decisões de verdade, entendimento dos operadores);  
   - operacionais (fallbacks, janelas de inconsistência, efeitos em pipelines em produção);  
   - de programa/roadmap (E28 ficar "travado" na v1, desalinhamento com sprints de Verdade/Debunker/Comitês).

2. **Débitos técnicos**  
   - Aspectos conscientemente simplificados na S29 (UX básica, instrumentação mínima, catálogo de papéis simplificado, cobertura parcial de testes de limites);  
   - pontos em que o time decidiu priorizar entrega de fundação sobre refinamento total.

3. **Mitigação e follow-up**  
   - Ações concretas de curto prazo (governança mínima de quem pode mexer em fluxos, monitoramento de fallback, comunicação interna de limitações);  
   - candidatos óbvios de escopo para E28.2, E28.3, E28.4.

4. **Long tail**  
   - O que não pode ser esquecido quando novas sprints mexerem com fluxo, verdade, debunking e comitês;  
   - quais artefatos de S29 viram referência obrigatória (ORR, bundle de evidências, capítulos 3–6);  
   - quais decisões da S29 devem ser tratadas como fundação e só reabertas com forte justificativa.

---

### 1.3. Objetivo de qualidade para este capítulo

O Capítulo 6 só atinge o nível de excelência esperado da Sprint 29 se, ao final da leitura, for possível afirmar que:

- ninguém da equipe consegue apontar um risco importante sobre fluxos configuráveis que não esteja pelo menos mencionado aqui;  
- débitos técnicos relevantes estão mapeados com clareza suficiente para alguém retomá-los em E28.x sem precisar "caçar" contexto em PRs antigos;  
- existe um quadro mental compartilhado sobre quando expandir o uso de fluxos configuráveis e quando optar por rollback ou contenção;  
- o conhecimento acumulado da S29 está preparado para ser reaproveitado por squads futuros, sem depender da memória de indivíduos.

Este Bloco 1, portanto, funciona como a "capa conceitual" do Capítulo 6: ele explica por que este capítulo existe, qual é o padrão de rigor que ele precisa seguir e quais eixos organizarão o conteúdo dos blocos seguintes (mapa de riscos, débitos, plano de mitigação, monitoramento e long tail).

