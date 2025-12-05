# Sprint 33 — Capítulo 2

## Bloco 4 — Gate G4, Gate G5 e DoD operacional da Sprint 33

Este bloco detalha, em nível executável, os dois últimos gates da Sprint 33 — **G4 (Runbooks, bundles de evidência e fluxo de aprendizado)** e **G5 (ORR operacional de integração)** — e explicita como eles se combinam para formar o **DoD operacional** da sprint. Se os blocos anteriores definiram o vocabulário (G0/G1) e a superfície operável (G2/G3), aqui definimos a musculatura de resposta a incidentes e o ritual que prova, de ponta a ponta, que a S33 cumpriu aquilo que prometeu.

---

### 2.4.1 G4 — Runbooks, bundles de evidência e fluxo de aprendizado (detalhado)

**Pergunta que G4 responde:**
> "Quando algo dá errado no recorte da S33, existe um caminho padrão para reagir, registrar o que aconteceu e transformar isso em aprendizado reutilizável?"

G4 garante que a resposta a incidentes não depende de improviso. Ele exige:
- runbooks claros para cenários prioritários;
- evidência consolidada de pelo menos um incidente percorrido de ponta a ponta;
- um fio condutor entre incidentes, runbooks, bundles e backlog.

#### Artefatos formais de G4

G4 se ancora nos seguintes artefatos:

1. **Catálogo de runbooks da S33** (ex.: `docs/s33/runbooks/`):
   - Arquivos de runbook em formato textual simples (Markdown ou equivalente), um por cenário; por exemplo:
     - `rb_s33_fonte_critica_falhando.md`;
     - `rb_s33_fila_ingestao_saturada.md`;
     - `rb_s33_truthdb_pipeline_atrasado.md`;
     - `rb_s33_api_ops_indisponivel.md`.
   - Cada runbook deve conter, no mínimo:
     - contexto (quando usar);
     - pré‑condições e sinais típicos;
     - passos de diagnóstico;
     - passos de mitigação/correção;
     - critérios explícitos de sucesso/falha;
     - relação com SLOs e componentes (IDs).

2. **Integração de runbooks com o cockpit**:
   - Links contextuais na UI do OracleOps Cockpit para os runbooks relevantes, por exemplo:
     - na tela de detalhe de uma fonte crítica em estado "falhando";
     - na tela de incidente (link para o runbook que guia a resposta);
   - Nome dos runbooks consistente entre repositório e UI.

3. **Bundles de evidência de incidentes** (ex.: `out/evidence/S33_G4_incidents/`):
   - Pelo menos um bundle completo referente a um incidente real ou simulado de forma realista, contendo:
     - export ou captura de dashboards relevantes;
     - recortes de logs (ou links estáveis para eles);
     - timeline do incidente (estados, timestamps, atores);
     - referência ao SLO violado (se aplicável);
     - cópia ou referência ao runbook utilizado;
     - pós‑mortem minimalista (hipótese de causa raiz, ações definitivas, débitos técnicos).

4. **Mapa de aprendizados e backlog**:
   - Documento de síntese (ex.: `docs/s33/s33_incidents_learnings.md`) relacionando incidentes da sprint com:
     - ajustes feitos (SLO, alerta, UI, métrica);
     - itens de backlog criados (refatorações, melhorias de observabilidade, novos runbooks);
   - Referências cruzadas para IDs de incidentes e runbooks.

5. **Scorecard de G4** (ex.: `out/scorecards/S33_G4_runbooks_and_evidence.json`).

#### Invariantes de G4

Para que G4 seja "PASS", as seguintes invariantes precisam ser verdade:

- **Inv‑G4‑1 — Cobertura mínima de cenários prioritários.**  
  Existe pelo menos um runbook para cada cenário de incidente prioritário definido no Capítulo 1 / G0 (por exemplo: falha em fonte oficial crítica, saturação de fila de ingestão, atraso em pipeline de Truth‑DB, indisponibilidade de API interna do cockpit).

- **Inv‑G4‑2 — Runbooks executáveis, não decorativos.**  
  Os runbooks têm nível de detalhe suficiente para que alguém com acesso às ferramentas, mas sem ser autor do código, consiga seguir os passos. "Verificar sistema" ou "checar logs" sem dizer como/onde são considerados insuficientes.

- **Inv‑G4‑3 — Integração de runbooks na rotina.**  
  Pelo menos em um cenário testado, o runbook é acessado a partir do cockpit durante o fluxo de operação (não apenas abrindo o arquivo direto no repositório).

- **Inv‑G4‑4 — Bundle de evidência completo.**  
  O bundle de incidente selecionado contém todas as peças descritas nos artefatos formais, e alguém consegue, a partir apenas desse bundle, reconstruir a narrativa do incidente sem depender da memória de quem participou.

- **Inv‑G4‑5 — Aprendizados endereçados.**  
  Pelo menos um aprendizado relevante se materializou em ação concreta: ajuste de SLO, melhoria de alerta, refinamento de UI, novo runbook ou melhoria de runbook existente.

#### Execução de G4 (script + simulação guiada)

G4 combina verificação automatizada com uma simulação semi‑manual:

1. **Script de sanity de runbooks e evidência** (ex.: `bin/s33_g4_runbooks_and_evidence.sh`):
   - Verifica a presença de runbooks nos caminhos esperados;
   - Checa, de forma simples, se cada runbook contém seções mínimas (contexto, passos, critérios);
   - Lista os bundles presentes em `out/evidence/S33_G4_incidents/` e verifica arquivos obrigatórios;
   - Gera relatório para `S33_G4_runbooks_and_evidence.json`.

2. **Simulação guiada de incidente**:
   - Escolhe‑se um incidente do recorte (real ou simulado) associado a um componente e, se possível, a um SLO;
   - Um operador segue o runbook correspondente, a partir do cockpit, até mitigar ou resolver o incidente;
   - A cada passo, verifica‑se se a informação necessária está de fato disponível (logs, dashboards, comandos);
   - Atualiza‑se o bundle de evidência com o que foi observado na simulação.

**Critério de aceite para G4:**

- G4 é "PASS" se o script confirmar a existência e estrutura mínima dos artefatos e se, na simulação, o operador conseguir percorrer o incidente de ponta a ponta com apoio real dos runbooks e do cockpit, deixando um bundle de evidência compreensível para terceiros.

---

### 2.4.2 G5 — ORR operacional da Sprint 33 (integração)

**Pergunta que G5 responde:**
> "A combinação de todos os entregáveis da S33 — cockpit, incidents, SLOs, runbooks, evidência — permite que alguém de fora da implementação opere o recorte da sprint de forma coerente?"

G5 é o gate de integração: ele não introduz novos requisitos funcionais, mas testa se os requisitos já definidos se comportam como um sistema único na mão de um operador. É aqui que a S33 prova que deixou de ser um conjunto de boas ideias e se tornou uma camada de operação real.

#### Roteiro de ORR operacional

A ORR operacional da S33 deve ser conduzida como um pequeno exercício encenado, com papéis claros:

- **Facilitador**: alguém que conhece a especificação da S33 e o estado atual do sistema;
- **Operador convidado**: pessoa que não implementou diretamente o cockpit nem o modelo de Incident (idealmente alguém de Ops ou Engenharia que não acompanhou o dia a dia da sprint);
- **Observador**: registra tempos, dificuldades, pontos de confusão e oportunidades de melhoria.

O roteiro mínimo de ORR inclui:

1. **Inspeção de saúde inicial**:
   - O facilitador dá acesso ao cockpit e pede ao operador: "me diga se o recorte da S33 está saudável agora";
   - O operador deve usar apenas o cockpit para responder, eventualmente abrindo links de observabilidade oferecidos ali.

2. **Exploração de componentes do recorte**:
   - O facilitador escolhe uma fonte crítica e um pipeline representativo;
   - Pede ao operador para encontrar, no cockpit, o estado atual, histórico recente e qualquer incidente relacionado a esses componentes.

3. **Cenário de incidente guiado**:
   - Um incidente (real ou simulado) é apresentado ao sistema (por exemplo, alteração de dados de teste, desligamento controlado de um job, simulação via flags);
   - O operador deve perceber o incidente via sinais do cockpit/SLOs/alertas;
   - Abrir ou localizar o incidente correspondente;
   - Seguir o runbook relevante;
   - Levar o incidente até um estado resolvido/estável.

4. **Consulta a SLOs**:
   - O facilitador escolhe 2–3 SLOs da lista da S33;
   - Pede ao operador para mostrar, usando cockpit + ferramentas ligadas, se esses SLOs estão sendo cumpridos;
   - Se algum estiver violado, discutir como isso apareceria/ apareceu na rotina.

5. **Análise de evidência e aprendizado**:
   - O operador e o observador revisitam o bundle de evidência gerado para o incidente;
   - Confirmam se a narrativa é compreensível e se os aprendizados foram registrados como backlog ou ajustes concretos.

#### Invariantes de G5

G5 será considerado "PASS" se:

- **Inv‑G5‑1 — Independência relativa de autores.**  
  O operador convidado consegue cumprir o roteiro sem precisar, a todo momento, perguntar aos autores "onde está X" ou "o que significa Y". Perguntas pontuais são aceitáveis; dependência crônica não.

- **Inv‑G5‑2 — Uso real dos artefatos da S33.**  
  Durante a ORR, são efetivamente utilizados:
   - cockpit (overview + drill‑down);
   - modelo de Incident (criação/atualização de incidente);
   - SLOs instrumentados (consultas, estado no cockpit);
   - runbooks;
   - bundle de evidência.
  Se a operação real precisar pular consistentemente esses artefatos para "ir direto na base", o gate falha.

- **Inv‑G5‑3 — Tempo de resposta razoável.**  
  O tempo para detectar, enquadrar e conduzir o incidente dentro do roteiro é razoável para o recorte da S33. Não há longos períodos de "cego" sem saber onde procurar.

- **Inv‑G5‑4 — Feedback concreto para próximos ciclos.**  
  A ORR gera uma lista clara de pontos de melhoria (UI, métricas, runbooks, fluxo), que alimenta diretamente o backlog, mostrando que o sistema não é só operável, mas também evolutivo.

#### Scorecard de G5

O resultado da ORR é consolidado em um scorecard (ex.: `out/scorecards/S33_G5_orr_operacional.json`), contendo:

- status global (PASS/NO_GO);
- tempos aproximados de cada etapa do roteiro;
- avaliações qualitativas do operador e do facilitador;
- lista de issues/backlog gerados;
- referência aos bundles de evidência usados.

---

### 2.4.3 DoD operacional da Sprint 33

Embora o Capítulo 2 já apresente um DoD global, este bloco enfatiza o **DoD operacional**, isto é, a linha de chegada mínima para considerar que a camada OracleOps v1 está "viva" no sentido operacional:

A Sprint 33 é considerada **operacionalmente DONE/GO** quando, simultaneamente:

1. **G0–G4 estão com scorecards PASS**, com evidência armazenada nas pastas padrão (`out/evidence/S33_G*/`, `out/scorecards/`).
2. **Pelo menos uma ORR operacional completa (G5) foi realizada**, com scorecard PASS e feedbacks incorporados ao backlog.
3. **Existe um operador não‑autor capaz de:**
   - usar o cockpit para inspecionar o recorte da S33;
   - identificar problemas visíveis (componentes degradados, SLOs violados, incidentes abertos);
   - seguir runbooks para um cenário crítico do recorte;
   - localizar e interpretar o bundle de evidência de pelo menos um incidente.
4. **Todos os artefatos citados neste capítulo (docs, scripts, scorecards, bundles, runbooks)** existem, foram versionados no repositório e estão referenciados de forma consistente (sem caminhos quebrados ou documentos órfãos).

Se qualquer uma dessas condições não estiver satisfeita, a S33 pode até ter entregado código de valor, mas ainda não terá cumprido sua promessa central: tornar operável, de forma minimamente madura, o recorte escolhido do Inspectah. Nesse caso, o resultado correto é **NO_GO operacional**, com ajustes e reforço de escopo para a sprint seguinte.

