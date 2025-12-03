# Inspectah — Sprint 31 (E28-S3)
## Capítulo 5 — Bloco 2: Plano de ORR (Operational Readiness Review)

### 5.8 Objetivo do ORR da Sprint 31

O ORR da Sprint 31 responde, de forma explícita e documentada, à pergunta:

> **“Podemos ligar provider-first + Console de Fontes v2 para o domínio piloto, em ambiente ‘valendo’, sem perder controle de custo, qualidade ou sanidade?”**

Este bloco define **como** essa resposta será construída:

- quais **pré-requisitos** precisam estar cumpridos antes do ORR;
- quem participa e com quais **papéis**;
- que **materiais** devem estar abertos durante a revisão;
- como é estruturado o **resumo oficial de ORR** e o veredito GO / GO_WITH_WARNINGS / NO_GO.

O objetivo é que o ORR da S31 seja reproduzível: qualquer pessoa que leia este bloco consegue conduzir uma revisão honesta, sem improvisar critérios.

---

### 5.9 Pré-requisitos formais para realizar o ORR S31

A Sprint 31 **não** deve ir para ORR se algum destes itens estiver obviamente pendente. A revisão serve para decidir GO/NO-GO, não para “descobrir” que metade da sprint não foi feita.

Pré-requisitos mínimos:

1. **Gates S31-G0..G5 executados**
   - Todos os scripts:
     - `bin/s31_g0_scope_and_baseline.sh`
     - `bin/s31_g1_models_and_migrations.sh`
     - `bin/s31_g2_provider_ingestion.sh`
     - `bin/s31_g3_console_and_observability.sh`
     - `bin/s31_g4_legacy_and_compat.sh`
     - `bin/s31_g5_p2_p3_integration.sh`
   - devem ter sido executados pelo menos uma vez em ambiente relevante (dev/staging) com saída arquivada.

2. **Scorecards dos gates presentes em `out/scorecards/`**
   - Arquivos obrigatórios:
     - `out/scorecards/S31_G0_scope_and_baseline.json`
     - `out/scorecards/S31_G1_models_and_migrations.json`
     - `out/scorecards/S31_G2_provider_ingestion.json`
     - `out/scorecards/S31_G3_observabilidade.json`
     - `out/scorecards/S31_G4_legacy_and_compat.json`
     - `out/scorecards/S31_G5_p2_p3_integration.json`
   - Cada scorecard deve conter, no mínimo: `gate_id`, `status`, `summary`, `metrics` e `evidence_paths`.

3. **Cenários E2E executados pelo menos uma vez**
   - Os quatro cenários definidos no Bloco 1 (5.3–5.6) precisam ter sido rodados em dev/staging, com evidências salvas.
   - Em caso de falha parcial, isso deve aparecer nos scorecards e nas notas de evidência.

4. **Documento de ORR gerado pelo script**
   - `bin/s31_orr.sh` deve ter sido executado pelo menos uma vez, produzindo:
     - `out/scorecards/S31_ORR_overview.json` (mesmo que ainda em rascunho);
     - `out/evidence/S31_ORR/notes.md` ou arquivo equivalente com observações.

5. **Documentação da sprint no estado “espelho do branch”**
   - Capítulos 1–5 da S31 devem refletir o estado atual do branch de entrega:
     - se algo mudou no modelo, Cap.3 precisa estar atualizado;
     - se fluxos foram ajustados, Cap.4 precisa acompanhar;
     - Cap.5 precisa listar os cenários e riscos reais, não os planejados meses atrás.

Se algum dos itens acima estiver obviamente faltando, o ORR é adiado. Esse “gate antes do gate” evita reuniões que só servem para carimbar NO_GO por falta de insumos.

---

### 5.10 Papéis e participantes do ORR

Mesmo que, na prática, poucas pessoas conduzam o ORR, o modelo de decisão da S31 segue papéis claros, alinhados à estrutura de equipes do Inspectah.

Papéis esperados:

1. **Owner da Sprint 31 / Squad Provider-first**
   - Apresenta o que foi feito na sprint;  
   - conduz demos dos cenários E2E;  
   - responde dúvidas sobre implementação, filemap e comandos.

2. **Representante do Squad Verdade & Interpretação**
   - Foca na trilha Provider → Perfil → ContentItem → Claim → FactBlock;  
   - avalia se a ingestão provider-first alimenta Programas 2–3 de forma correta;  
   - opina sobre riscos de distorção de verdade/causalidade.

3. **Representante de Data/Storage (Truth-DB / Data Hub)**
   - Avalia se o modelo e as migrations da S31 são saudáveis;  
   - verifica impacto em performance, volume e manutenção do banco;  
   - checa se evidências e trilhas de origem são auditáveis.

4. **Representante de Console & Operação**
   - Avalia se o Console de Fontes v2 está utilizável;  
   - analisa UX para operadores (clareza de métricas, fluxo “Rodar agora”);  
   - garante que runbooks sejam suficientes.

5. **Spec Office / Produto (Programas 1–3)**
   - Garante que a S31 de fato entrega o que o Programa 1–3 precisava nesta altura;  
   - verifica alinhamento com roadmap macro e com os Programas já aprovados.

6. **Conselho (Jobs, Kleppmann, etc.)**
   - Olha o quadro geral;  
   - pesa riscos vs benefícios;  
   - decide veredito: GO / GO_WITH_WARNINGS / NO_GO;  
   - registra condições e recomendações explícitas.

Em termos práticos, o importante é que o documento de ORR contenha seções que reflitam essas perspectivas, mesmo que escritas por uma única pessoa apoiada pelo Codex.

---

### 5.11 Materiais obrigatórios na mesa do ORR

Na sessão de ORR (ao vivo ou assíncrona) devem estar abertos, lado a lado, pelo menos:

1. **Capítulos da Sprint 31**
   - Cap.1 — Contexto, objetivos, domínio piloto;  
   - Cap.2 — Gates, métricas, invariantes, critérios de sucesso;  
   - Cap.3 — Arquitetura & filemap;  
   - Cap.4 — Execução & evidências;  
   - Cap.5 — Cenários E2E, ORR, runbooks, riscos.

2. **Scorecards S31-G0..G5 + ORR overview**
   - Arquivos JSON dos gates;  
   - `S31_ORR_overview.json` com status agregado.

3. **Evidências dos cenários E2E**
   - Amostras de ContentItems, logs de runs, traces de caso piloto (P2–P3);  
   - comparativos legado vs provider;  
   - qualquer gráfico ou painel S31 que já exista.

4. **Runbooks relacionados**
   - Drafts de `rb_provider_ingestion_piloto_br.md`, `rb_console_fontes_operacao_basica.md`, etc.;  
   - servem para validar se alguém conseguiria operar isso amanhã.

5. **Flags & plano de rollout/rollback**
   - Lista de feature flags da S31 (Seção 5.4 no Cap.5 completo);  
   - plano de rollout por ambiente (dev → staging → produção limitada);
   - plano de rollback caso algo dê errado.

O ORR só deve começar depois que todos esses insumos estiverem disponíveis. Se, durante a leitura, for detectado que algo está muito defasado (ex.: Cap.3 descreve um modelo que já mudou), o passo correto é interromper, alinhar docs e remarcar.

---

### 5.12 Estrutura do documento de resumo de ORR

O resumo de ORR da Sprint 31 é o registro permanente do que foi decidido e por quê.

Arquivo sugerido: `docs/sprint_31_orr_summary.md`.

Estrutura mínima:

1. **Seção 1 — Resumo executivo**
   - 5–10 linhas explicando:  
     - o que a S31 tentou entregar;  
     - principais resultados;  
     - veredito final (GO / GO_WITH_WARNINGS / NO_GO) e para quais ambientes.

2. **Seção 2 — Estado dos gates**
   - Tabela com colunas: `Gate`, `Status`, `Notas`.  
   - Linhas para G0..G5 e ORR.  
   - Links para os respectivos scorecards e evidências.

3. **Seção 3 — Cenários E2E exercitados**
   - Lista dos quatro cenários da Seção 5.2/Bloco 1;  
   - para cada um: `STATUS` (OK / LIMITADO / FALHOU) + 2–3 linhas de observação;  
   - links para os arquivos de evidência em `out/evidence/`.

4. **Seção 4 — Riscos remanescentes & mitigação**
   - Extraída e consolidada a partir da Seção 5.4 do Cap.5;  
   - destacar apenas riscos relevantes para a decisão de rollout (custo, dependência de provider, cobertura, dedupe, UI vs realidade);
   - listar, ao lado de cada risco, a mitigação ativa na S31 (flags, limites de escopo, runbooks).

5. **Seção 5 — Decisão e condições**
   - **Veredito**: GO / GO_WITH_WARNINGS / NO_GO.  
   - **Âmbito**: em quais ambientes, domínios, perfis a decisão vale (ex.: apenas perfis-piloto BR em staging).  
   - **Condições**:  
     - se GO: quais flags permanecem on/off;  
     - se GO_WITH_WARNINGS: quais restrições devem ser respeitadas e o que precisa ser atacado nas próximas sprints;  
     - se NO_GO: quais problemas são bloqueadores, qual sprint/épico deve tratá-los.

Esse documento não precisa ser longo; precisa ser **claro, honesto e rastreável**. É o que vai ser reaberto daqui a 6 meses quando alguém perguntar: “por que ativamos (ou não) provider-first naquele momento?”.

---

### 5.13 Integração do ORR com o fluxo de CI e de branches

Para a S31, o ORR não é um ritual isolado da realidade do repositório. Ele se integra ao fluxo de branches e CI da seguinte forma:

1. **Branch de entrega da S31**
   - Tudo que a S31 entrega deve estar consolidado em um branch específico (ex.: `feature/s31_provider_console_v2`).
   - O ORR analisa **esse** branch, não rascunhos paralelos.

2. **Workflow de gates em CI**
   - Deve existir workflow (ex.: `.github/workflows/s31_gates.yml`) que:
     - roda G0..G5 e `s31_orr.sh` em CI;  
     - publica artifacts de `out/evidence` e `out/scorecards`.
   - O ORR usa esses artifacts como insumo preferencial.

3. **Condição de merge em `main` / branch estável**
   - Merge do branch da S31 em `main` só é permitido se:  
     - workflow S31 estiver verde;  
     - resumo de ORR (`sprint_31_orr_summary.md`) marcar veredito aceitável para o rollout planejado.

4. **Tag ou marcador da S31**
   - Após decisão GO/GO_WITH_WARNINGS, criar tag ou marcação clara (ex.: `inspectah_s31_provider_pilot_go`) associada ao commit aprovado.  
   - Isso facilita correlacionar futuras métricas/incidentes com o estado específico da S31.

---

### 5.14 Resultado esperado deste bloco

Com o Bloco 2, o Capítulo 5 da Sprint 31 ganha um **roteiro operacional de ORR**:

- sabemos quando **não** faz sentido marcar a reunião (pré-requisitos objetivos);
- sabemos quem deve opinar e a partir de quais materiais;
- sabemos qual documento precisa ser produzido para registrar o veredito;
- sabemos como o ORR conversa com CI, branches e tags.

Os blocos seguintes vão se apoiar nesse esqueleto para detalhar runbooks, riscos, feature flags e o plano de rollout/rollback pós-S31.

