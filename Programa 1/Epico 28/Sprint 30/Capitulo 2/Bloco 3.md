# Inspectah — Sprint 30 — Capítulo 2 — Bloco 3
## Métricas Agregadas da Sprint 30 e Ligação Direta com o Contrato de E28

Este bloco amarra os gates G0–G5 em um conjunto pequeno, porém decisivo, de **métricas agregadas de sprint**. A ideia é simples:

- gates dizem “cada peça isolada está saudável”;  
- métricas de sprint dizem “o conjunto cumpre o contrato do épico”.

Se todas as métricas deste bloco forem verdade, a Sprint 30 está, na prática, honrando o papel que lhe foi dado dentro de E28.

---

### 1. Eixo 1 — Fluxo‑pivô de notícias realmente operável

**Pergunta central:** o fluxo de notícias‑pivô se comporta como um cidadão de primeira classe, operável via Console, ou ainda depende de atalhos em código e scripts?

Métrica S30-E1.1 — Criação e promoção via Console
- Definição: número de ciclos completos "criar → testar → promover" de um fluxo de notícias, executados exclusivamente via Console (e APIs oficiais), em ambiente de teste de S30.
- Alvo mínimo: **N ≥ 3** ciclos registrados.
- Evidência:
  - logs de operação (quem criou, quem promoveu, timestamps);
  - prints/capturas do Console mostrando estados mudando de `draft` → `em_teste` → `ativo`.
- Interpretação:
  - N < 3 indica que o fluxo‑pivô ainda não foi exercitado o suficiente para ser considerado confiável;
  - N ≥ 3, com evidências consistentes, indica que o caminho operacional padrão foi realmente usado, e não só demonstrado uma vez.

Métrica S30-E1.2 — Operações de pausa/retomada testadas na prática
- Definição: número de operações de pausa/retomada de fluxo de notícias realizadas via Console, com verificação de impacto real no roteamento.
- Alvo mínimo: **N ≥ 3** ciclos pausa→retomada.
- Evidência:
  - logs estruturados de operação;
  - testes de roteamento antes/depois (ex.: notícias que deixaram de entrar no fluxo pausado e passaram a seguir o fallback planejado).
- Interpretação:
  - Se o fluxo não for pausado/retomado algumas vezes em ambiente de teste, a sprint não provou que a cerca elétrica de operação funciona.

Métrica S30-E1.3 — Troca de agente crítico sem tocar em código
- Definição: número de trocas bem-sucedidas de agente em etapa crítica (por exemplo, classificador de tipo de notícia) realizadas via Console.
- Alvo mínimo: **N ≥ 2** trocas, com efeito observável em execuções posteriores.
- Evidência:
  - diffs de configuração de fluxo (antes/depois);
  - logs de execuções mostrando o novo agente em uso;
  - registro em trilha de auditoria.
- Interpretação:
  - Se ainda é “mais fácil” pedir para alguém editar código para trocar um agente, S30 falhou em um dos objetivos centrais.

---

### 2. Eixo 2 — Estados de fluxo como lei, não sugestão

**Pergunta central:** os estados `draft`, `em_teste`, `ativo` e `pausado` estão realmente mandando no sistema, ou continuam decorativos?

Métrica S30-E2.1 — Consistência de roteamento por estado
- Definição: proporção de eventos de notícia roteados em conformidade com a política declarada de estados, em cenários de teste desenhados pela sprint.
- Cenários mínimos:
  - Cenário A: apenas um fluxo `ativo` para o tipo de entrada → 100% dos eventos vão para esse fluxo.
  - Cenário B: um fluxo `ativo` e um `em_teste` com fração configurada de tráfego (ex.: 10%).
  - Cenário C: fluxo `pausado` → 0% de novos eventos direcionados a ele.
- Alvo mínimo:
  - Em cada cenário, **≥ 99%** dos eventos roteados em conformidade com a política; desvios precisam ser explicados como casos de teste específicos.
- Evidência:
  - logs de roteamento anotados com estado do fluxo e decisão tomada;
  - relatórios gerados pelo script de teste de roteamento (parte de G3/G5).

Métrica S30-E2.2 — Tempo para aplicar uma mudança crítica de estado
- Definição: tempo decorrido entre a ação no Console (ex.: pausar um fluxo) e a primeira evidência de que novos eventos passaram a seguir a regra nova (ex.: deixando de usar o fluxo pausado).
- Alvo mínimo:
  - **T ≤ 5 minutos** em ambiente de teste (considerando filas internas e caches razoáveis).
- Evidência:
  - timestamps de logs de operação de pausa;
  - timestamps de logs de roteamento mostrando mudança de comportamento.
- Interpretação:
  - Se o sistema demora demais para responder a um comando crítico, a eficácia prática de estados como ferramenta de operação cai muito.

---

### 3. Eixo 3 — Rastreabilidade e observabilidade de fluxo

**Pergunta central:** o squad consegue observar e entender o que o fluxo de notícias está fazendo, sem abrir mão de telemetria estruturada?

Métrica S30-E3.1 — Cobertura de logs estruturados por jornada de notícia
- Definição: proporção de execuções de fluxo de notícias em que existe uma trilha completa de logs estruturados cobrindo todas as etapas de execução (do início à decisão final), correlacionadas por `exec_fluxo_id` e `exec_etapa_id`.
- Alvo mínimo:
  - **≥ 95%** das execuções de teste do fluxo‑pivô com trilha completa.
- Evidência:
  - consultas a logs estruturados mostrando a cadeia completa para amostras de notícias.

Métrica S30-E3.2 — Métricas mínimas por fluxo não nulas
- Definição: verificação de que, após exercícios de carga da S30, as métricas mínimas definidas para fluxos (pelo menos `fluxo_execucoes_total`, `fluxo_execucoes_sucesso_total`, `fluxo_execucoes_falha_total`, `fluxo_latencia_p95`) apresentam valores não nulos para o fluxo‑pivô de notícias.
- Alvo mínimo:
  - Todas as métricas com valor > 0 ao final da bateria de testes.
- Evidência:
  - scrapes/export de métricas salvos em `out/evidence/S30_G4_flow_observability/`.

Métrica S30-E3.3 — Uso real do painel de fluxo na revisão da sprint
- Definição: demonstração, durante a revisão da sprint, de que o painel/consulta de fluxo de notícias é usado pelo squad para responder perguntas sobre saúde e performance (não apenas “mostrado rapidamente”).
- Alvo mínimo:
  - Squad é capaz, em sessão registrada, de responder, usando apenas o painel/consulta:
    - se o fluxo está saudável;
    - qual a taxa de erro aproximada;
    - se há sinais de aumento de latência ou backlog.
- Evidência:
  - notas da revisão;
  - prints/screencaps de painel;
  - eventualmente, um resumo em texto em `out/evidence/S30_G4_flow_observability/usage_notes.md`.

---

### 4. Eixo 4 — Autonomia operacional do squad (sem atalhos escondidos)

**Pergunta central:** o squad realmente opera o fluxo via mecanismos oficiais, ou continua dependendo de “atalhos mágicos” em código/banco?

Métrica S30-E4.1 — Zero uso de caminhos fora de Console + APIs oficiais para casos normais
- Definição: para os cenários de teste da S30 (criação, teste, promoção, pausa, retomada, reprocessamento limitado), nenhuma operação crítica é executada via:
  - acesso direto ao banco;
  - scripts não embrulhados em APIs oficiais;
  - modificações de configuração manual fora do fluxo de deploy/CI.
- Alvo mínimo:
  - **0** ocorrências de operações críticas realizadas “por fora” em ambiente de teste.
- Evidência:
  - checklist do squad;
  - ausência de comandos manuais registrados no diário da sprint para esses casos.

Métrica S30-E4.2 — Percepção de cockpit ≥ 9.9/10
- Definição: avaliação subjetiva de cada membro do Squad Fluxos & Orquestração sobre a afirmação:
  > “Para o caso de notícias, o Console de Fluxos é hoje, de fato, o cockpit operacional; eu consigo operar o fluxo sem mexer em código.”
- Alvo mínimo:
  - Nota mínima individual: **9.9/10**;
  - Nota média: idealmente 10/10; qualquer valor abaixo de 9.9 aciona discussão formal de gap.
- Evidência:
  - registro de notas (por pessoa) em `out/evidence/S30_squad_review/console_cockpit_scores.json`.

---

### 5. Scorecard agregado de sprint e relação com GO/NO-GO

Todas as métricas acima devem ser consolidadas em um **scorecard agregado** da Sprint 30, produzido automaticamente a partir das saídas dos gates e de scripts auxiliares.

- Script: `bin/s30_metrics_summary.sh`.
- Saída: `out/scorecards/S30_metrics_summary.json`.

Campos mínimos esperados no JSON:
- `epic`: `"E28_Fluxo_de_Agentes_Config_v1"`;
- `sprint`: `"S30"`;
- `axes`: lista com objetos descrevendo cada eixo (E1–E4) e suas métricas;
- `status`: `"PASS"` ou `"FAIL"`;
- `reasons`: lista textual de justificativas em caso de `FAIL`.

A Sprint 30 só pode ser marcada como GO se:
- `status == "PASS"` em **todos** os scorecards de gates `S30_G*_*.json`;
- `status == "PASS"` em `S30_metrics_summary.json`.

Se qualquer métrica deste bloco falhar, a S30 não cumpriu completamente seu contrato com E28. O squad pode decidir, em conjunto com o conselho, se:
- reabre a sprint até atingir os alvos; ou
- registra explicitamente as falhas como dívidas de épico, impedindo que o E28 seja considerado completo até que sejam endereçadas.

Este Bloco 3, portanto, funciona como a "tabela verdade" da Sprint 30: ele não substitui os gates, mas amarra tudo o que foi definido em G0–G5 ao contrato maior de E28, tornando claro o que significa, na prática, dizer que a S30 foi um sucesso.

