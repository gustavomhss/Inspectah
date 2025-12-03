# Inspectah — Sprint 30 — Capítulo 2 — Bloco 2
## Definição Detalhada dos Gates G0–G5 (Objetivo, Escopo, Evidências)

Este bloco define, gate a gate, o que a Sprint 30 precisa provar para ser considerada saudável do ponto de vista de E28. Cada gate tem:
- um objetivo claro;
- o risco que está protegendo;
- entradas esperadas;
- checagens que devem ser automatizadas;
- artefatos de saída (scorecards e evidências).

A filosofia é simples: se não está coberto por um gate, não está realmente protegido.

---

### G0 — Grounding de S30: Escopo, Alinhamento com E28 e Integridade dos Docs

**Objetivo**  
Garantir que a Sprint 30 está, de fato, alinhada com o Épico E28 e que o planejamento não tem buracos: sem TODOs, sem seções vazias, sem ambiguidade sobre o que a sprint quer tornar verdade.

**Risco que protege**  
- S30 sair do trilho de E28 (por exemplo, gastar a sprint com features aleatórias de console que não reforçam fluxo de agentes).
- Capítulos de sprint incompletos gerarem decisões ad hoc durante o desenvolvimento.

**Entradas esperadas**  
- Capítulo 1 da S30 (todos os blocos) em `docs/sprint_30_cap_1_*`.
- Capítulo 2 da S30 (este capítulo) em `docs/sprint_30_cap_2_*`.
- Capítulos 3 e 4 em rascunho avançado (mínimo viável definido) em `docs/sprint_30_cap_3_*` e `docs/sprint_30_cap_4_*`.
- Documento do Épico E28 em `docs/epics/e28_fluxos_de_agentes.md`.

**Checagens automatizadas**  
- Verificar que todos os arquivos obrigatórios de Capítulos 1–4 existem.
- Varredura de TODO, FIXME, "TBD", trechos marcados como `...` ou placeholders equivalentes.
- Checagem de links: referências a E28 e a outros docs da sprint apontam para caminhos existentes.
- Verificação de que Capítulo 1 menciona explicitamente:
  - fluxo de notícias como fluxo‑pivô;
  - contrato central da S30;
  - relação com estados de fluxo (`draft`, `em_teste`, `ativo`, `pausado`).

**Saídas**  
- Script: `bin/s30_g0_scope_and_alignment.sh`.
- Scorecard: `out/scorecards/S30_G0_scope_and_alignment.json`.
- Evidências: `out/evidence/S30_G0_scope_and_alignment/` (logs de varredura, lista de arquivos checados, referência cruzada com E28).

**Critério de PASS**  
- `status == "PASS"` no scorecard.
- Zero ocorrências de TODO/FIXME/TBD em Capítulos 1–4.
- Nenhuma referência quebrada a docs do Épico E28 e da sprint.

---

### G1 — Modelo de Fluxo & Templates: Fluxo v1.5 consistente e instanciável

**Objetivo**  
Assegurar que o modelo de Fluxo de Agentes v1 foi refinado para v1.5, suportando operação diária e templates, sem quebra de compatibilidade, e que existem templates canonizados (especialmente o de notícias) válidos e instanciáveis.

**Risco que protege**  
- Esquema de fluxos divergente entre código, banco e documentos.
- Templates existindo apenas como YAML decorativo, não validados contra o modelo real.
- Topologias inválidas (loops não intencionais, fluxos sem decisão final, etapas órfãs).

**Entradas esperadas**  
- Models em `app/flows/models.py` (ou módulo equivalente) com entidades: Fluxo, Etapa, Nó/Agente, Execução de Fluxo, Execução de Etapa.
- Migrations de S30 em `migrations/versions/0030_s30_flow_model_v15.py` (nome exato a ajustar no Capítulo 3).
- Templates de fluxo em `app/flows/templates/*.yaml` (ou `.json` equivalente).

**Checagens automatizadas**  
- Aplicar migrations em banco de teste e verificar sucesso.
- Validar todos os templates contra o schema de Fluxo v1.5:
  - campos obrigatórios presentes;
  - estados permitidos identificados;
  - ligação consistente com tipos de entrada (ex.: `tipo_entrada: noticia_texto`).
- Rodar um validador de topologia que rejeita:
  - ciclos sem marcação explícita;
  - fluxos sem etapa de decisão final;
  - etapas que nunca são alcançadas a partir do início;
  - fan-out extremo sem limites definidos.

**Saídas**  
- Script: `bin/s30_g1_flow_model_and_templates.sh`.
- Scorecard: `out/scorecards/S30_G1_flow_model_and_templates.json`.
- Evidências: `out/evidence/S30_G1_flow_model_and_templates/` (logs de migrations, dumps de templates aprovados, relatório de topologias).

**Critério de PASS**  
- Todas as migrations aplicam em banco limpo e em banco migrado de versões anteriores.
- Todos os templates obrigatórios (incluindo `Fluxo_Noticias_Geral_v1`) são considerados válidos.
- Nenhuma topologia proibida é detectada.

---

### G2 — Console de Fluxos: Operabilidade Básica (Criar, Ver, Entender)

**Objetivo**  
Garantir que o Console de Fluxos atingiu o nível mínimo de operabilidade definido para S30: listar fluxos, mostrar estados, permitir inspeção de estrutura e execuções recentes com UX coerente com o Console/Admin global.

**Risco que protege**  
- Console servir apenas como vitrine de dados, sem condições de ser cockpit.
- Divergência de linguagem visual e de interação em relação a E26 (Admin & Consoles).

**Entradas esperadas**  
- Código de frontend em `frontend/inspectah-ui/src/features/flows/*`.
- Rotas de API do console em `app/api/flow_console_routes.py` (ou equivalente).
- Design system e componentes compartilhados (para garantir consistência visual).

**Checagens automatizadas**  
- Lint e build do frontend (no mínimo, sobre o módulo de fluxos).
- Testes de componente e/ou integração cobrindo:
  - listagem de fluxos;
  - visualização de detalhes de um fluxo;
  - exibição de estados (`draft`, `em_teste`, `ativo`, `pausado`);
  - exibição resumida de execuções recentes.
- Snapshot tests (ou equivalentes) para garantir que a representação textual do diagrama de fluxo não degrada silenciosamente.
- Testes de API exercitando rotas principais do console (listar fluxos, obter detalhe, listar execuções).

**Saídas**  
- Script: `bin/s30_g2_flow_console_ops.sh`.
- Scorecard: `out/scorecards/S30_G2_flow_console_ops.json`.
- Evidências: `out/evidence/S30_G2_flow_console_ops/` (logs de testes front, snapshots salvos, curls das rotas principais).

**Critério de PASS**  
- Todos os testes relacionados ao Console de Fluxos passam.
- Pelo menos os fluxos de notícias em escopo da S30 aparecem no console com estados corretos e execuções registradas em ambiente de teste.

---

### G3 — Operações Seguras: Pausar, Retomar, Reprocessar Sem Caos

**Objetivo**  
Assegurar que operações críticas de controle de fluxo (pausar, retomar, marcar `em_teste`/`ativo`, reprocessar itens) são implementadas de forma segura, com limites de volume, proteção contra loops e trilha de auditoria.

**Risco que protege**  
- Operador, via console, disparar um reprocessamento descontrolado e gerar tempestade de chamadas a agentes.
- Pausar um fluxo sem que o sistema realmente pare de roteá-lo.
- Ausência de logs estruturados para reconstruir "quem fez o quê" em operações delicadas.

**Entradas esperadas**  
- Serviços de backend que implementam operações de fluxo (ex.: `app/flows/service.py`).
- Configuração de limites (ex.: `config/flows_limits.yaml`).

**Checagens automatizadas**  
- Testes de API que tentam:
  - reprocessar toda a história de um fluxo sem limites → operação deve falhar com erro controlado;
  - reprocessar um lote dentro de limites permitidos → operação deve ser aceita e registrada;
  - pausar fluxo e verificar que nenhum novo evento entra nesse fluxo.
- Verificação de que todas as operações críticas geram logs estruturados contendo, no mínimo: `fluxo_id`, `usuario`, `operacao`, `timestamp`, `resultado`.
- Checagem de que políticas de retry não causam loops infinitos (limites de tentativas, backoff, flags de "não reprocessar novamente").

**Saídas**  
- Script: `bin/s30_g3_flow_operations_safety.sh`.
- Scorecard: `out/scorecards/S30_G3_flow_operations_safety.json`.
- Evidências: `out/evidence/S30_G3_flow_operations_safety/` (logs de testes, prints de logs estruturados, dumps de configuração de limites).

**Critério de PASS**  
- Todos os testes de operações críticas passam.
- Não há caminho conhecido para disparar reprocessamentos massivos sem limite.
- Logs de operação estão presentes e corretos para os casos de teste.

---

### G4 — Observabilidade por Fluxo: Métricas e Logs Estruturados

**Objetivo**  
Confirmar que fluxos (especialmente o de notícias‑pivô) são visíveis como entidades de primeira classe na camada de observabilidade: métricas, logs correlacionáveis, possibilidade de painel.

**Risco que protege**  
- Fluxos ficarem invisíveis na telemetria, obrigando o squad a inferir sua saúde a partir de métricas genéricas.
- Impossibilidade de responder, com dados, se o fluxo de notícias está saudável.

**Entradas esperadas**  
- Código de instrumentação (ex.: `app/flows/instrumentation.py`).
- Configuração de export de métricas (OTel/Prometheus/etc.).

**Checagens automatizadas**  
- Scrape automatizado de métricas em ambiente de teste verificando a presença de, no mínimo:
  - `fluxo_execucoes_total`;
  - `fluxo_execucoes_sucesso_total`;
  - `fluxo_execucoes_falha_total`;
  - `fluxo_latencia_p95` ou equivalente;
  - labels como `fluxo_id`, `tipo_entrada`, `status`.
- Verificação de que logs de execução contêm IDs de correlação (`exec_fluxo_id`, `exec_etapa_id`) desde o início até o fim da jornada de uma notícia.
- Export estático (arquivo) de um painel ou consulta que mostra as métricas do fluxo de notícias‑pivô.

**Saídas**  
- Script: `bin/s30_g4_flow_observability.sh`.
- Scorecard: `out/scorecards/S30_G4_flow_observability.json`.
- Evidências: `out/evidence/S30_G4_flow_observability/` (dump de métricas, exemplos de logs correlacionados, export de painel/consulta).

**Critério de PASS**  
- Todas as métricas mínimas aparecem com valores não nulos quando fluxos são exercitados.
- É possível reconstruir a execução de um fluxo de notícias usando apenas logs estruturados.

---

### G5 — Cenário End-to-End: Fluxo de Notícias Canônico em Operação de Teste

**Objetivo**  
Validar, de ponta a ponta, um cenário completo de fluxo de notícias — da ingestão até a decisão final — utilizando apenas fluxos, console e APIs oficiais, com rastreabilidade e observabilidade ativas.

**Risco que protege**  
- S30 entregar peças isoladas (modelo, console, observabilidade) que nunca foram testadas juntas em um cenário real.
- O fluxo de notícias depender de gambiarras fora do que o Console e as APIs expõem.

**Entradas esperadas**  
- Ambiente de teste com:
  - fontes de notícia mínimas configuradas (ex.: algumas feeds RSS);
  - fluxo‑pivô de notícias criado a partir do template oficial e marcado como candidato a `ativo`;
  - Console de Fluxos e painel de métricas operacionais.

**Checagens automatizadas**  
- Injetar (via script) um conjunto de notícias sintéticas ou capturadas de fontes reais.
- Verificar que:
  - a ingestão atribui o tipo de entrada adequado;
  - o fluxo de notícias correto é selecionado;
  - todas as etapas do fluxo executam com sucesso para a maioria dos casos;
  - erros são tratados de forma controlada para casos problemáticos.
- Confirmar que:
  - as execuções aparecem no Console de Fluxos (lista + detalhe);
  - as métricas incrementam de forma consistente;
  - logs estruturados registram a jornada de cada notícia.

**Saídas**  
- Script: `bin/s30_g5_e2e_canonical_flow.sh`.
- Scorecard: `out/scorecards/S30_G5_e2e_canonical_flow.json`.
- Evidências: `out/evidence/S30_G5_e2e_canonical_flow/` (inputs de teste, capturas do console, queries de métricas, trechos de logs).

**Critério de PASS**  
- Pelo menos um fluxo canônico de notícias roda E2E com 100% de sucesso para o conjunto de testes principal.
- Toda a trilha (ingestão → fluxo → decisão → observabilidade) é reconstruível apenas com ferramentas oficiais.

---

Com estes seis gates detalhados, o Capítulo 2 estabelece a malha mínima aceitável de proteção para a Sprint 30. Os próximos blocos do capítulo vão:
- amarrar essas execuções a métricas agregadas de sprint;
- definir a Definition of Done (DoD) e o workflow de CI/ORR que garante que nada disso fique só no papel.

