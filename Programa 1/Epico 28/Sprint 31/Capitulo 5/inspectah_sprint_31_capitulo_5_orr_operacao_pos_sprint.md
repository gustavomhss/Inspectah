# Inspectah — Sprint 31 (E28-S3)
## Capítulo 5 — ORR & Operação Pós-sprint

### 5.0 Função deste capítulo

O Capítulo 5 garante que a Sprint 31 não termine em “demo bonito”, e sim em **capacidade operacional real**, com critérios claros de GO/NO-GO, cenários end-to-end, runbooks e plano de rollback.

Ele responde a quatro perguntas:

1. Em quais **cenários end-to-end** vamos provar que S31 funciona de verdade?  
2. Como será conduzido o **ORR** (Operational Readiness Review) da sprint?  
3. O que precisa existir de **runbooks** para operar provider-first e Console v2 sem adivinhação?  
4. Quais **riscos e feature flags** ficam ativos pós-sprint, e como desligar tudo sem quebrar o resto do Inspectah?

---

### 5.1 Cenários end-to-end de validação (S31)

Os cenários E2E da Sprint 31 são recortes concretos que exercitam o estado-alvo da sprint no domínio piloto (notícias BR — política/economia + um perfil social). Eles conectam:

> Provider → IngestionProfile → ContentItem → Console v2 → (Programa 2) → (Programa 3, caso piloto)

Abaixo, 4 cenários mínimos, cada um com passos, gates e evidências esperadas.

#### Cenário 1 — Ingestão piloto BR_PT_HARD_NEWS via provider

**Objetivo:** provar que um perfil de news BR/PT (ex.: `BR_PT_HARD_NEWS`) roda via provider, gera ContentItems com proveniência completa e fica visível no Console.

Passos:

1. Garantir que migrations S31 foram aplicadas e configs mínimas estão carregadas (`Provider` + `IngestionProfile` BR_PT_HARD_NEWS).
2. Rodar `profile_runner.run_profile` para o perfil em ambiente de desenvolvimento ou staging, usando janela controlada (ex.: últimas 2h).
3. Confirmar no banco que foram criados `ContentItem` com:
   - `provider_id`, `ingestion_profile_id`, `external_id` (quando houver), `source_domain`, `ingested_at` preenchidos;
   - campos de conteúdo coerentes (título, URL, published_at).
4. Abrir o Console de Fontes v2 (`/console/ingestion-profiles`), localizar o perfil BR_PT_HARD_NEWS e abrir a tela de detalhe.
5. Ver último run refletido na UI (horário, volume, status, uso de budget).

Gates que exercitam:

- **G2** (`s31_g2_provider_ingestion.sh`) — ingestão e dedupe piloto.
- **G3** (`s31_g3_console_and_observability.sh`) — exibição dos runs e métricas básicas na UI.

Evidências propostas:

- `out/evidence/S31_G2_provider_ingestion/contentitems_sample.json` (amostra de itens BR_PT_HARD_NEWS).  
- `out/evidence/S31_G3_console/e2e_run.log` (log do fluxo completo).  
- Screenshot ou dump da tela de detalhe do perfil (opcional, mas desejável).

#### Cenário 2 — Fluxo "Rodar agora" via Console para perfil de news

**Objetivo:** provar que o Console v2 não é painel morto: operador consegue disparar ingestão e ver o efeito.

Passos:

1. Abrir `/console/ingestion-profiles` e filtrar até encontrar o perfil BR_PT_HARD_NEWS.
2. Abrir detalhe do perfil.
3. Clicar em **"Rodar agora"**.
4. Confirmar na UI que o pedido foi aceito (mensagem de sucesso ou status de run em progresso).
5. Aguardar a conclusão do job, depois:
   - atualizar a tela;  
   - ver novo run listado (timestamp > anterior);  
   - conferir contagens de calls, itens brutos, ContentItems criados e erros.
6. Validar que métricas internas (`provider_calls_total`, `items_ingested_total`, etc.) foram incrementadas.

Gates que exercitam:

- **G3** (Console & observabilidade) — fluxo run-now + atualização de execução.

Evidências:

- `out/evidence/S31_G3_console/front_tests.log` com teste E2E desse fluxo.  
- `out/evidence/S31_G3_console/api_tests.log` mostrando chamada ao endpoint `run-now` e job enfileirado.

#### Cenário 3 — Conteúdo provider-first chegando em Programa 2–3 (caso piloto)

**Objetivo:** provar que os ContentItems vindos de providers entram na trilha de interpretação e verdade (Programas 2–3) para pelo menos um **caso piloto**.

Passos:

1. Selecionar um evento/caso real no domínio piloto (ex.: decisão relevante no Senado, medida provisória, fato econômico marcante) que esteja coberto pelo provider.
2. Garantir que:
   - o perfil BR_PT_HARD_NEWS (ou outro perfil BR adequado) está ativo e capturou notícias sobre o caso;  
   - existem `ContentItem` com `provider_id` ligados a esse caso (por título/URL/entidade).
3. Rodar pipeline de Programa 2 para consumir esses ContentItems e gerar:
   - Claims (declarações, números, promessas etc.) com referência ao ContentItem de origem.
4. Rodar pipeline de Programa 3 para montar pelo menos um FactBlock/caso estrutural com:
   - trilha de origem: Provider → Perfil → ContentItem → Claim → FactBlock.
5. Verificar que o caso pode ser consultado e auditado no mínimo pela CLI/console interno (UI dedicada pode vir em sprint seguinte, mas a trilha lógica precisa existir).

Gates que exercitam:

- **G5** (`s31_g5_p2_p3_integration.sh`) — integração S31 com Programas 2–3.

Evidências:

- `out/evidence/S31_G5_p2_p3/case_pilot_trace.json` com a trilha de origem completa.  
- `out/evidence/S31_G5_p2_p3/pipeline_run.log` (execução das pipelines P2/P3 para o caso piloto).

#### Cenário 4 — Sanity de legado vs provider (não-regressão)

**Objetivo:** garantir que a entrada de providers não quebrou ingestão legada crítica e que, para um recorte simples, as duas rotas captam o mesmo universo de fatos relevantes.

Passos:

1. Escolher um feed legado crítico (ex.: RSS de um grande portal BR) que esteja previsto no `legacy_adapter` da S31.
2. Rodar ingestão desse feed via fluxo legado (por script/gate apropriado).
3. Rodar ingestão de um perfil provider-first que teoricamente cobre o mesmo recorte (mesmo tema/região/idioma) na mesma janela de tempo.
4. Comparar resultados em alto nível:
   - contagem total de itens;  
   - existência/ausência de notícias importantes em um vs outro;  
   - consistência básica de timestamps.
5. Registrar diferenças relevantes e, se necessário, ajustar filtros/perfis.

Gates que exercitam:

- **G4** (`s31_g4_legacy_and_compat.sh`) — compatibilidade com legado e plano de migração.

Evidências:

- `out/evidence/S31_G4_legacy/legacy_jobs.log` (runs legados).  
- `out/evidence/S31_G4_legacy/migration_plan.md` (plano de migração com notas sobre comparações legado vs provider).  
- Amostra comparativa de itens (pode ser um JSON sintético, não texto integral).

---

### 5.2 Plano de ORR (Operational Readiness Review) da Sprint 31

O ORR da S31 é o momento em que o Conselho e o Squad responsável respondem, de forma formal:

> “Podemos ligar provider-first + Console v2 para o domínio piloto em ambiente ‘valendo’ sem passar vergonha ou queimar dinheiro à toa?”

#### 5.2.1 Pré-requisitos de ORR

Antes da reunião de ORR, devem estar **necessariamente** em estado aceitável:

- Todos os gates S31-G0..G5 executados com scorecards em `out/scorecards/`:
  - G0 — Scope & baseline;  
  - G1 — Models & migrations;  
  - G2 — Provider ingestion;  
  - G3 — Console & observabilidade;  
  - G4 — Legacy & compatibilidade;  
  - G5 — Integração Programas 2–3.
- `out/scorecards/S31_ORR_overview.json` gerado via `bin/s31_orr.sh` (mesmo que ainda em rascunho).
- Evidências mínimas para cada gate (capítulos 3 e 4 detalham) presentes e referenciadas nos scorecards.
- Pelo menos **um caso piloto** de Programa 3 com trilha completa Provider → Perfil → ContentItem → Claim → FactBlock.

Se qualquer gate crítico estiver em FAIL sem plano aceitável de correção ou mitigação, o ORR não deve ser realizado (ou deve terminar em NO_GO quase automaticamente).

#### 5.2.2 Quem participa do ORR S31

Participantes esperados (virtuais, seguindo o modelo de equipe do Inspectah):

- Representação do **Squad Verdade & Interpretação** (Pearl, Stonebraker, Norvig, Percy) — foco na trilha de verdade e armazenamento.
- Representação do **Squad Console & Operação** — foco em UI, operação diária e UX de operador.
- Representação do **Spec Office** — garante aderência ao Programa 1–3 e roadmap.
- **Conselho** (Jobs, Kleppmann, etc.) — arbitra o veredito final GO / GO_WITH_WARNINGS / NO_GO.

Na prática, basta que o documento de ORR reflita as perspectivas desses papéis, mesmo que quem esteja tocando seja um único humano + Codex.

#### 5.2.3 Material aberto durante o ORR

Na reunião de ORR (real ou assíncrona) devem estar abertos, pelo menos:

- Cap.1–5 da Sprint 31 (especialmente Cap.2, Cap.3 e este Cap.5).  
- Scorecards S31-G0..G5 + `S31_ORR_overview.json`.  
- Evidências dos cenários E2E (Seção 5.1).  
- Logs/charts de ingestão piloto (painel S31 de ingestão, se já existir).

#### 5.2.4 Estrutura do resumo de ORR

Arquivo alvo: `docs/sprint_31_orr_summary.md`.

Seções mínimas:

1. **Resumo executivo**  
   - 5–10 linhas explicando o que a S31 tentou fazer e qual o veredito (GO / GO_WITH_WARNINGS / NO_GO).

2. **Estado dos gates**  
   - tabela com S31-G0..G5 + status + observações.

3. **Cenários E2E exercitados**  
   - lista dos cenários da Seção 5.1, com observação se passaram ou tiveram limitações.

4. **Riscos remanescentes & mitigação**  
   - link para Seção 5.4; destacar apenas os mais críticos.

5. **Decisão e condições**  
   - GO: em que ambientes e sob quais feature flags;  
   - GO_WITH_WARNINGS: quais restrições ou observações;  
   - NO_GO: o que precisa ser corrigido e em qual sprint/épico.

Este resumo é o documento oficial para qualquer discussão futura sobre “por que provider-first foi (ou não) colocado em produção para o domínio piloto na S31”.

---

### 5.3 Runbooks & operação pós-Sprint 31

A S31 introduz uma nova peça operacional: ingestão provider-first + Console de Fontes v2. Para isso não virar caixa-preta, alguns runbooks precisam existir (nem que em versão v0) ao final da sprint.

#### 5.3.1 Runbooks mínimos a criar/atualizar

Arquivos sugeridos em `docs/runbooks/`:

1. `docs/runbooks/rb_provider_ingestion_piloto_br.md`
   - Como monitorar os perfis-piloto BR (news + social).  
   - Quais métricas olhar diariamente (calls, items, errors, budget_usage).  
   - Como pausar um perfil problemático via Console.

2. `docs/runbooks/rb_console_fontes_operacao_basica.md`
   - Passo a passo para: listar perfis, inspecionar detalhes, usar "Rodar agora" com segurança.  
   - Boas práticas de criação/edição de perfis (escopo, budget, flags de experimental).

3. `docs/runbooks/rb_incidente_provider_api.md`
   - Como reagir a instabilidade ou mudança de comportamento do provider (erros 5xx, rate limit, payload quebrado).  
   - Contatos/suporte do provider (quando aplicável).  
   - Critérios para fallback para ingestão legada.

4. `docs/runbooks/rb_custo_explodindo_ingestao.md`
   - O que fazer se métricas de calls/budget indicarem custo fora do previsto.  
   - Como reduzir frequência ou escopo de perfis.  
   - Como desligar temporariamente ingestão provider-first mantendo legado.

Cada runbook deve seguir uma estrutura mínima: **Contexto**, **Sinais/alertas**, **Passos de diagnóstico**, **Ações**, **Critérios de encerramento**.

#### 5.3.2 Relação com Truth Ops / On-call

Mesmo que o modelo formal de on-call ainda esteja sendo montado, a S31 deve:

- deixar claro **quem** (que papel) é responsável por acompanhar ingestão provider-first no dia a dia;  
- indicar, nos runbooks, quando escalar incidentes para Truth Ops / liderança técnica;  
- garantir que qualquer pessoa assumindo plantão consiga, lendo os runbooks, operar sem improviso.

#### 5.3.3 Testando runbooks

Antes de considerar o Cap.5 pronto, é desejável:

- simular ao menos um incidente pequeno (ex.: forçar erro de provider controlado) e seguir o runbook de incidente;  
- ajustar o runbook com base na experiência (passos faltando, comandos pouco claros, etc.).

---

### 5.4 Riscos, rollback & feature flags

Mesmo com todos os gates verdes, a S31 deixa riscos remanescentes. Eles precisam ser nomeados e acoplados a mecanismos concretos de controle: rollback e feature flags.

#### 5.4.1 Riscos principais pós-S31

1. **Dependência de provider externo**  
   - Mudanças de contrato, TOS, limites de uso ou estabilidade podem afetar ingestão.

2. **Custo maior que o previsto**  
   - Perfis mal configurados ou aumento súbito de volume podem aumentar uso de tokens e chamadas.

3. **Cobertura enviesada ou incompleta**  
   - Provider pode ter gaps por país/tema, gerando visão parcial do mundo.

4. **Bugs de dedupe ou normalização**  
   - Podem causar explosão de duplicatas, ou, pior, fusão de conteúdos distintos.

5. **Desalinhamento UI ↔ realidade**  
   - Console pode mostrar status “saudável” apesar de problemas reais (lag de métricas, bugs de exibição).

Cada risco deve aparecer tanto no resumo de ORR quanto em um quadro de riscos vivo para programas futuros.

#### 5.4.2 Plano de rollback S31

Rollback aqui não é “apagar a sprint”, e sim ter **rotas de saída seguras**:

1. **Desligar ingestão provider-first mantendo legado**  
   - Pausar todos os `IngestionProfile` provider-first (status → PAUSED) para o domínio piloto.  
   - Desativar scheduler de provider para esses perfis (ou feature flag global de scheduler).  
   - Garantir que fluxos legados críticos seguem rodando (validar com G4 ou scripts derivados).

2. **Desligar Console v2 parcialmente**  
   - Manter páginas de leitura (lista/detalhe) e desabilitar ações destrutivas (edição, run-now) via feature flag.  
   - Exibir aviso claro na UI quando uma ação estiver temporariamente indisponível.

3. **Reverter migrations (em último caso)**  
   - Só considerado se migrations da S31 introduzirem bug grave sem correção simples.  
   - Requer playbook próprio (fora do escopo desta sprint) e deve ser evitado; preferir correção forward.

#### 5.4.3 Feature flags propostos

Flags mínimas para controlar ativação da S31 por ambiente e escopo:

1. `s31_provider_ingestion_enabled`
   - Nível: ambiente (dev/staging/prod).  
   - Efeito: habilita/desabilita scheduler + jobs de provider-first.

2. `s31_console_v2_enabled`
   - Nível: ambiente/role de usuário.  
   - Efeito: mostra ou esconde o Console de Fontes v2 (ou partes dele).

3. `s31_provider_pilot_profiles_only`
   - Nível: ambiente.  
   - Efeito: restringe ingestão provider-first a um conjunto fechado de perfis-piloto (ex.: BR_PT_HARD_NEWS + 1 social), prevenindo escala prematura.

4. `s31_p2_p3_provider_sources_allowed`
   - Nível: ambiente.  
   - Efeito: controla se Programas 2–3 podem consumir ContentItems com `provider_id` em ambientes mais sensíveis.

Essas flags devem ser descritas em:

- docs da sprint (Cap.3 e Cap.5);  
- runbooks relevantes (como desligar/ligar);  
- se possível, em um arquivo central de flags do projeto.

#### 5.4.4 Matriz de decisão GO / GO_WITH_WARNINGS / NO_GO

No fim do ORR, a Sprint 31 recebe um veredito, atrelado às flags acima:

- **GO**  
  - Todos os gates G0..G5 em PASS (ou WARN muito bem justificado).  
  - Cenários E2E 1–4 executados com sucesso aceitável.  
  - Flags podem ser ligadas em staging e, gradualmente, em produção para o domínio piloto.

- **GO_WITH_WARNINGS**  
  - Algum risco relevante permanece, mas com mitigação clara.  
  - S31 entra em operação apenas com `s31_provider_pilot_profiles_only` ativa e possivelmente `s31_console_v2_enabled` restrita a poucos operadores.  
  - Próxima sprint deve trazer melhorias pontuais (performance, custo, cobertura, UX).

- **NO_GO**  
  - Gate crítico em FAIL (ex.: G2 ou G5), ou casos E2E falhando de forma grave.  
  - Flags permanecem desligadas em produção; provider-first continua limitado a dev/staging.  
  - Um mini-épico ou sprint seguinte deve ser aberto especificamente para corrigir os problemas.

---

### 5.5 Fecho do Capítulo 5

Com este capítulo, a Sprint 31 ganha:

- cenários E2E claros para provar que provider-first + Console v2 não é teoria;  
- um plano formal de ORR conectado aos gates e às evidências;  
- runbooks mínimos para operar a nova capacidade com segurança;  
- riscos nomeados, com rotas de rollback e feature flags bem definidas.

É esse conjunto que transforma a S31 de “mais uma sprint de código” em um passo controlado na operação real do Inspectah para o domínio piloto de notícias BR, pronto para ser expandido nas próximas sprints do Épico E28.