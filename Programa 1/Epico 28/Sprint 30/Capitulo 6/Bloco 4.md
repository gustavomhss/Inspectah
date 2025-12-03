# Inspectah — Sprint 30 — Capítulo 6 — Bloco 4
## Tasks de Governança, ORR, Backlog Pós‑S30 e Checklist Final de GO (Eixo Gv)

Este bloco fecha o Capítulo 6 e, na prática, **fecha a Sprint 30**: aqui vivem as tasks que garantem que a S30 não seja apenas código e pipelines, mas uma unidade de evolução **governada, auditável e bem encaixada no Épico E28**.

O Eixo Gv cobre quatro frentes:
1. Consolidação de documentação da sprint;
2. Execução do ORR e registro da decisão GO/NO‑GO;
3. Registro do backlog imediato para S31–S35;
4. Checklist final de GO da S30.

---

## 6.10 Tasks de Consolidação de Documentação — Eixo Gv

Estas tasks garantem que os Capítulos 1–6 da S30 estão **coerentes entre si, atualizados e livres de lixo** (TODO/FIXME, restos de versões antigas, contradições).

### Gv1 — Revisar e congelar Capítulos 1–3 da Sprint 30

**Descrição**  
Realizar uma revisão final dos Capítulos 1, 2 e 3 (Contexto/Objetivos, Gates & Métricas, Arquitetura & Filemap), garantindo que refletem exatamente o que foi implementado.

**Inclui**
- verificar se o escopo final (incluindo ajustes durante a sprint) está refletido no Cap. 1;
- validar que todos os gates descritos no Cap. 2 existem como scripts em `bin/s30_g*.sh` e geram scorecards correspondentes;
- garantir que o filemap do Cap. 3 corresponde ao estado real do repo (sem caminhos mortos, sem módulos fantasmas);
- remover TODO/FIXME e notas internas que ficaram obsoletas.

**Dependências**
- F1–F6, C1–C5, O1–O10 concluídos ou em estado final;
- Cap. 1–3 escritos e iterados.

**Relação com gates**
- G0 — escopo e alinhamento.

---

### Gv2 — Revisar e alinhar Capítulos 4 e 5 com o que foi entregue

**Descrição**  
Garantir que Cap. 4 (Execução & Evidências) e Cap. 5 (Governança & Continuidade) descrevem fielmente o que foi realizado.

**Inclui**
- conferir se o plano de execução descrito no Cap. 4 está sincronizado com os scripts de gates, E2E, metrics summary e bundle;
- verificar se o cenário E2E narrado no Cap. 4 bate com o que `bin/s30_g5_e2e_canonical_flow.sh` faz na prática;
- ajustar o Cap. 5 para refletir qualquer nuance final de decisões permanentes, riscos e continuidade (por exemplo, se alguma decisão foi ligeiramente reescopada durante a implementação).

**Dependências**
- O5–O10 concluídos;
- Cap. 4 e 5 em versão quase final.

**Relação com gates**
- G0 — docs alinhados;
- G5 — E2E descrito com fidelidade.

---

### Gv3 — Revisar Capítulo 6 (este) e alinhar tasks com estado real

**Descrição**  
Garantir que a lista de tasks deste capítulo corresponde ao que foi realmente implementado, sem tasks fantasmas ou tasks fora da spec.

**Inclui**
- marcar explicitamente tasks que foram:
  - concluídas integralmente;
  - parcialmente concluídas (com observações para backlog);
  - descopadas conscientemente (justificativa);
- atualizar dependências, se o caminho real tiver sido diferente do planejado;
- garantir que o checklist final de GO (seção 6.13) corresponde à realidade.

**Dependências**
- execução prática da sprint já avançada;
- sincronização com board de tasks (Jira/Linear/etc.).

**Relação com gates**
- G0 — coerência entre spec e execução.

---

## 6.11 Tasks de ORR (Operational Readiness Review) — Eixo Gv

Estas tasks formalizam o rito de **ORR da S30**, conectando CI, scorecards, evidências e percepção qualitativa do squad e do conselho.

### Gv4 — Preparar material para ORR da Sprint 30

**Descrição**  
Organizar o material necessário para uma sessão de ORR objetiva, sem caça ao tesouro.

**Inclui**
- garantir que a última execução do workflow `.github/workflows/s30-gates.yml` está verde ou claramente falha, com logs recentes;
- verificar que `inspectah_s30_evidence_bundle.zip` está disponível e contém:
  - `S30_G*.json`;
  - `S30_metrics_summary.json`;
  - `out/evidence/S30_G*/`;
- separar links ou caminhos para:
  - Console de Fluxos rodando em ambiente de review (dev/stage/local reprodutível);
  - dashboards de telemetria relevantes.

**Dependências**
- O7–O10 concluídos;
- bundle gerado pelo menos uma vez.

**Relação com gates**
- pré‑requisito logístico para ORR.

---

### Gv5 — Conduzir sessão de ORR da Sprint 30

**Descrição**  
Executar a ORR como rito formal de prontidão operacional da S30.

**Inclui (mínimo recomendável)**
- participantes: representantes do Squad Fluxos & Cockpit +, idealmente, alguém de Observabilidade e alguém de Verdade & Interpretação (pela interdependência futura);
- agenda:
  1. Revisão rápida de objetivos da S30 (Cap. 1);
  2. Revisão de `S30_metrics_summary.json` e principais scorecards (`S30_G*`);
  3. Navegação guiada pelo Console de Fluxos (listar fluxos, ver fluxo‑pivô, rodar uma operação simples);
  4. Inspeção de métricas e logs de uma execução recente do fluxo de notícias;
  5. Verificação da execução bem‑sucedida do cenário E2E (ou reexecução ao vivo);
  6. Discussão de riscos residuais (Cap. 5.3) e planos de monitoração.

**Saída esperada**
- consenso (ou maioria qualificada) sobre GO/NO‑GO para o escopo da S30;
- lista de observações e recomendações para backlog.

**Dependências**
- Gv4 concluída;
- CI e bundle em estado estável.

**Relação com gates**
- ORR é gate humano complementar aos gates automatizados.

---

### Gv6 — Registrar decisão de ORR e resumo em `S30_ORR_summary.txt`

**Descrição**  
Registrar oficialmente o resultado da ORR em arquivo de texto dentro de `out/evidence/`.

**Inclui**
- GO/NO‑GO explícito, com eventual escopo parcial (se algum subcomponente ficar fora);
- principais evidências mencionadas (referência a scorecards, logs, dashboards, prints);
- riscos residuais aceitos e plano de monitoração (link para Cap. 5.3 e ajustes, se houver);
- backlog imediato derivado da ORR (linkado a Gv8).

**Arquivos principais**
- `out/evidence/S30_ORR_summary.txt`

**Dependências**
- Gv5 concluída.

**Relação com gates**
- insumo obrigatório para o bundle O9;
- âncora histórica da sprint.

---

## 6.12 Tasks de Backlog Pós‑S30 — Eixo Gv

Estas tasks não são trabalho técnico imediato, mas garantem que **aprendizados e lacunas** da S30 não se percam entre uma sprint e outra.

### Gv7 — Consolidar backlog técnico imediato para S31–S35

**Descrição**  
Converter limitações conscientes, atalhos tomados e ideias de evolução em itens de backlog claros para sprints futuras do Épico E28.

**Inclui**
- recopilar, a partir de Cap. 1–5 + ORR:
  - ajustes desejados no modelo de fluxo (ex.: novos campos, melhor indexação);
  - melhorias desejadas no Console de Fluxos (UX, filtros, comparações);
  - refinamentos de limites de reprocessamento (depois de uso real);
  - extensões desejadas da telemetria (novas métricas/labels);
- abrir itens de backlog com:
  - contexto curto (por que importa);
  - relação explícita com a S30 (qual dor foi percebida aqui).

**Saída**
- conjunto de tickets/epics/sprints futuras identificadas claramente como “derivadas da S30”.

**Dependências**
- Gv1–Gv3 (docs consolidados);
- Gv5–Gv6 (ORR realizada e registrada).

**Relação com gates**
- não bloqueia GO técnico, mas bloqueia um fechamento elegante da S30 como fundação do E28.

---

### Gv8 — Registrar backlog de produto e de experiência de operação

**Descrição**  
Olhar para o impacto da S30 do ponto de vista de produto e operação (não só de infraestrutura de fluxo).

**Inclui**
- identificar, junto com pessoas de operação/usuários internos:
  - dores na experiência de operar fluxos de notícias;
  - melhorias desejadas em termos de visibilidade, alertas, relatórios;
- registrar isso como backlog de produto, separado do backlog puramente técnico.

**Dependências**
- Gv5 (ORR com gente de operação envolvida, se possível).

**Relação com gates**
- não bloqueia GO, mas alimenta o roadmap do Programa 1.

---

## 6.13 Checklist Final de GO da Sprint 30

Para fins práticos, a S30 só é considerada **GO** quando todas as condições abaixo forem verdadeiras. Este checklist deve ser usado tanto localmente quanto na revisão de CI/ORR.

### 6.13.1 Checklist técnico

- [ ] **Fundação de Fluxos (Eixo F)**
  - [ ] F1 — modelos v1.5 implementados em `app/flows/models.py`;
  - [ ] F2 — migration `0030_s30_flow_model_v15.py` aplicada com sucesso em ambiente de teste;
  - [ ] F3 — template canônico de fluxo de notícias criado e validado;
  - [ ] F4 — serviço de fluxos (`service.py`) implementado (create, state, replace, route, reprocess);
  - [ ] F5 — política de roteamento (`routing_policy.py`) operando para `noticia_texto`;
  - [ ] F6 — engine de execução (`execution_engine.py`) orquestrando etapas e registrando execuções.

- [ ] **Console de Fluxos (Eixo C)**
  - [ ] C1 — schemas de fluxo definidos em `app/flows/schemas.py`;
  - [ ] C2 — rotas `flow_console_routes.py` implementadas e testadas;
  - [ ] C3 — telas principais do console construídas (lista, detalhe, execuções, criação);
  - [ ] C4 — hooks de API implementados e integrados à UI;
  - [ ] C5 — testes de frontend rodando verdes para flows.

- [ ] **Observabilidade, E2E e Gates (Eixo O/G)**
  - [ ] O1 — instrumentação de fluxos implementada;
  - [ ] O2 — engine integrada à instrumentação;
  - [ ] O3 — naming de métricas e labels documentado/testado;
  - [ ] O4 — dataset sintético de notícias pronto;
  - [ ] O5 — script E2E `bin/s30_g5_e2e_canonical_flow.sh` executando com sucesso;
  - [ ] O6 — cenário E2E documentado;
  - [ ] O7 — scripts de gates G0–G4 implementados e rodando;
  - [ ] O8 — `bin/s30_metrics_summary.sh` gerando `S30_metrics_summary.json`;
  - [ ] O9 — `bin/s30_bundle.sh` gerando `inspectah_s30_evidence_bundle.zip`;
  - [ ] O10 — workflow `.github/workflows/s30-gates.yml` passando verde.

### 6.13.2 Checklist de governança e continuidade

- [ ] Gv1 — Cap. 1–3 revisados e alinhados com o que foi implementado;
- [ ] Gv2 — Cap. 4–5 atualizados com execução real, decisões e riscos finais;
- [ ] Gv3 — Cap. 6 ajustado para refletir o estado final das tasks;
- [ ] Gv4 — material de ORR preparado (CI, bundle, console, dashboards);
- [ ] Gv5 — ORR realizada com decisão explícita de GO/NO‑GO;
- [ ] Gv6 — `S30_ORR_summary.txt` preenchido e incluído no bundle;
- [ ] Gv7 — backlog técnico imediato para S31–S35 registrado;
- [ ] Gv8 — backlog de produto/experiência de operação registrado.

Quando todos os itens acima forem verdadeiros, a Sprint 30 não é só “mergeada”: ela é **promovida** como parte sólida da fundação do Épico E28 e do Programa 1, com evidência, governança e caminho claro para as próximas sprints.

