# Inspectah — Sprint 30 — Capítulo 5 — Bloco 1
## Propósito do Capítulo 5 e Mandato do Squad da Sprint 30

O Capítulo 5 existe para garantir que a Sprint 30 **não seja apenas código e scripts**, mas um pedaço estável da anatomia do Inspectah, com dono claro, decisões permanentes explícitas e encaixe limpo dentro do Épico E28.

Se os Capítulos 1 a 4 respondem:
- **Cap. 1** — o que a S30 quer tornar verdade (objetivos, escopo, riscos, cenários‑núcleo);
- **Cap. 2** — como vamos provar que isso é verdade (gates, métricas, DoD, CI/ORR);
- **Cap. 3** — onde isso mora na arquitetura e no filemap (módulos, APIs, UI, scripts, artefatos);
- **Cap. 4** — como executar e demonstrar com evidência (plano, testes, bundle, ORR);

então o **Capítulo 5** responde:

> “Quem é dono disso, o que vira lei daqui pra frente e como a Sprint 30 se encaixa, sem atrito, na linha das próximas sprints do Épico E28?”

O Bloco 1 foca em duas coisas:
1. Deixar claro o **mandato do Capítulo 5** na S30;
2. Definir com precisão o **mandato do Squad da Sprint 30 (Squad Fluxos & Cockpit)** e suas áreas de responsabilidade.

---

## 5.1 Mandato do Capítulo 5 na Sprint 30

O Capítulo 5 é o lugar onde a S30 deixa de ser “uma sprint que passou no CI” e passa a ser **infraestrutura institucionalizada** do Inspectah.

Mandatos explícitos do Capítulo 5:

1. **Dono e accountability**  
   - Nomear qual squad responde pelo que foi entregue na S30 (e por manter isso vivo);
   - Evitar a situação em que “todo mundo é responsável” (o que sempre significa “ninguém é responsável”).

2. **Decisões que viram contrato**  
   - Clarificar quais decisões da S30 são experimentais e quais passam a ser **contratos estáveis** para o Épico E28 e para o Programa 1;
   - Documentar essas decisões de forma que futuras sprints possam depender delas sem precisar reabrir discussões.

3. **Riscos estruturais e trade‑offs**  
   - Explicitar onde a S30 assumiu complexidade, acoplamento ou limites conservadores de propósito;
   - Apontar o que precisa ser monitorado de perto pós‑GO.

4. **Linha de continuidade com S31–S35**  
   - Ancorar a S30 dentro do arco maior do Épico E28 (S29–S35);
   - Deixar claro o que as próximas sprints podem assumir como “dado” e onde elas devem acoplar.

Resultado desejado: alguém lendo apenas o Capítulo 5, meses depois, consegue responder **quem manda em fluxos, o que ficou permanente e qual é o próximo passo natural em E28**.

---

## 5.2 Squad da Sprint 30 — “Squad Fluxos & Cockpit”

A Sprint 30 não é apenas uma evolução técnica, é a sprint que transforma **fluxos de agentes** em uma entidade operável e governada dentro do Inspectah. Para isso, ela roda sob responsabilidade de um squad dedicado.

### 5.2.1 Identidade e mandato do squad

**Nome de trabalho:** Squad Fluxos & Cockpit  
**Épico:** E28 — Fluxo de Agentes Configurável  
**Programa:** Programa 1 — Núcleo de ingestão, operação e cockpit do Inspectah

**Mandato da S30 para esse squad:**
- Entregar um **fluxo‑pivô de notícias** (baseado em agentes) que seja:
  - configurável via template;
  - operável via Console;
  - observável via métricas e logs;
  - auditável via scorecards e bundle de evidências;
- Entregar isso em um formato que possa ser **reutilizado e generalizado** nas S31–S35 (para outros tipos de fluxo e integração com Debunker/Truth‑DB/casos).

Em termos práticos, o Squad Fluxos & Cockpit passa a ser a **referência oficial** quando o assunto é:
- “Como um evento ingerido vira uma jornada por agentes?”;
- “Qual fluxo está recebendo notícias agora e com que política de teste?”;
- “Onde vejo se o fluxo está saudável?”;
- “Como pauso, retomo ou reprocesso itens com segurança?”

### 5.2.2 Áreas de dono dentro da Sprint 30

Para evitar “zonas cinzentas” de responsabilidade, a S30 define explicitamente as áreas de dono do squad:

1. **Domínio e dados de Fluxos**  
   Dono de:
   - definição e evolução dos modelos de fluxo em `app/flows/`;
   - semântica de estados (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`);
   - regras de transição de estado e políticas de reprocessamento;
   - forma, conteúdo e integridade das migrations de S30 relacionadas a fluxos.

2. **Engine de execução e roteamento**  
   Dono de:
   - `app/flows/execution_engine.py` (como o fluxo caminha de etapa em etapa);
   - `app/flows/routing_policy.py` (como eventos são atribuídos a fluxos);
   - contratos internos com a camada de agentes (como a engine chama intérprete, classificador, analistas, debunkers, decision maker).

3. **Console de Fluxos (backend + frontend)**  
   Dono de:
   - `app/api/flow_console_routes.py` (rotas HTTP do console de fluxos);
   - `frontend/inspectah-ui/src/features/flows/*` (UI do cockpit);
   - experiência mínima de operação: listar, ver detalhe, mudar estado, reprocessar com segurança, inspecionar execuções.

4. **Observabilidade de fluxos**  
   Dono de:
   - design das métricas `inspectah_flow_*` relacionadas a execuções e erros de fluxo;
   - formato mínimo dos logs estruturados de fluxo;
   - requisitos de painel de observabilidade para o fluxo de notícias.

5. **Gates, scorecards e bundle da S30**  
   Dono de:
   - scripts `bin/s30_g*.sh` (G0–G5);
   - `bin/s30_metrics_summary.sh` e `S30_metrics_summary.json`;
   - `bin/s30_bundle.sh` e `inspectah_s30_evidence_bundle.zip`;
   - consistência entre docs de sprint, scorecards, evidências e o que roda no CI.

Se qualquer coisa quebrar em fluxos de notícias, console de fluxos, observabilidade de fluxos ou gates da S30, a primeira pergunta é: **“O que o Squad Fluxos & Cockpit fez ou deixou de fazer?”** — esse é o nível de accountability esperado.

---

Com isso, o Bloco 1 do Capítulo 5 define claramente o papel do Capítulo 5 e o mandato do Squad da Sprint 30. Nos próximos blocos, o capítulo aprofunda:
- quais decisões da S30 viram contratos permanentes (Bloco 2);
- quais riscos e trade‑offs estruturais foram assumidos e como monitorá‑los (Bloco 3);
- como a S30 se encaixa, de forma contínua, na trajetória S31–S35 do Épico E28 (Bloco 4).