# Inspectah — Sprint 21 — Capítulo 4 (v2)
## Plano de Execução da Sprint 21 (Console de Fontes)

### 1. Papel deste capítulo

Os Capítulos 1, 2 e 3 definem o **porquê**, o **como validar** e o **onde vive cada artefato** da Sprint 21. Este Capítulo 4 responde à pergunta operacional:

> "Qual é a sequência concreta de trabalho que o Squad 1 e o Codex devem seguir para entregar o Console de Fontes no nível exigido pelos gates S21_G0…S21_G8?"

O objetivo é que este documento permita rodar a Sprint 21 quase como um script humano: seguir fases, atualizar arquivos, rodar testes, executar scripts de gate e chegar a uma decisão GO/NO-GO baseada em evidências. Cada fase traz: entradas, saídas, arquivos tocados, gates alimentados e notas de paralelização.

---

### 2. Pré-condições e contexto de execução

Antes de iniciar a execução da Sprint 21, assumimos:

- Sprints 1–20 estão estáveis, com branch `main` limpo e ORR das sprints críticas já rodando.
- O repositório está sincronizado com o remoto (sem commits locais pendentes).
- Os documentos abaixo existem em `docs/` e são considerados base estável:
  - `docs/sprint_21_capitulo_1.md` (Capítulo 1 — contexto e objetivos).
  - `docs/sprint_21_capitulo_2_gates.md` (Capítulo 2 — gates e validação, v2).
  - `docs/sprint_21_capitulo_3_filemap.md` (Capítulo 3 — arquitetura e filemap, v2).
- Convenções de repositório, `bin/`, `out/scorecards/` e `out/evidence/` seguem o padrão das sprints anteriores.

Com isso garantido, a Sprint 21 será executada em **fases numeradas e parcialmente paralelizáveis**, sempre respeitando dependências de modelo de dados e docs.

---

### 3. Estratégia geral de execução

A Sprint 21 é dividida em dez blocos de trabalho:

- Fase 0 — Preparação de ambiente e branch.
- Fase 1 — Consolidação dos documentos conceituais (ontologia, modelo, ciclo de vida, fluxos, ganchos).
- Fase 2 — Modelo de dados e migrations.
- Fase 3 — Serviços, validações e API de admin.
- Fase 4 — UI mínima do Console de Fontes.
- Fase 5 — Testes do módulo de fontes.
- Fase 6 — Seeds e cenários de uso.
- Fase 7 — Contratos com S22–S25 e scorecard.
- Fase 8 — Scripts de gates, scorecards JSON e evidências.
- Fase 9 — Wrap final, GO/NO-GO e merge.

Dependência principal: **Fase 1 → Fase 2 → Fase 3**. As fases de UI, testes, cenários e contratos podem ser parcialmente paralelizadas depois que modelo de dados e serviços atingirem um mínimo de estabilidade.

---

### 4. Fase 0 — Preparação de ambiente e branch

**Objetivo**: isolar o trabalho da Sprint 21 em um branch próprio, com ambiente repetível.

Entradas:
- Branch `main` atualizado.
- Ambiente Python/venv previamente configurado.

Saídas:
- Branch de feature criado e ativo.
- Ambiente pronto para rodar testes e migrations.

Arquivos/pastas tocados:
- Nenhum arquivo lógico da Sprint 21 ainda; apenas configuração local.

Passos de alto nível:
- Atualizar `main` a partir do remoto.
- Criar branch, por exemplo: `feature/s21_console_fontes`.
- Ativar o virtualenv (`.venv`) e garantir que dependências do projeto estão instaladas.

Gates alimentados:
- Nenhum gate é concluído aqui, mas esta fase é pré-condição para todas as demais.

---

### 5. Fase 1 — Consolidação dos documentos conceituais

**Objetivo**: materializar a parte conceitual da Sprint 21 em `docs/`, de forma coerente com os Capítulos 1–3 e com os gates S21_G0…S21_G4.

Entradas:
- Capítulos 1, 2 e 3 em `docs/`.

Saídas:
- Documentos conceituais de ontologia, modelo de dados, ciclo de vida, fluxos admin e ganchos Debunker completos e consistentes.

Arquivos envolvidos (`docs/`):
- `docs/sprint_21_ontologia_fontes.md`
- `docs/sprint_21_modelo_dados_fontes.md`
- `docs/sprint_21_ciclo_vida_fontes.md`
- `docs/sprint_21_fluxos_admin_fontes.md`
- `docs/sprint_21_ganchos_debunker_fontes.md`

Passos macro:

1. Revisar Capítulos 1–3
- Confirmar que o escopo da Sprint 21 está claro e que o filemap do Capítulo 3 cobre todas as áreas necessárias.

2. Escrever/ajustar `sprint_21_ontologia_fontes.md`
- Definir tipos de fonte da Fase 1.
- Especificar atributos obrigatórios/opcionais por tipo.
- Incluir exemplos concretos por domínio (política, fofoca, esportes, clima, mandatos, projetos, ciência).

3. Escrever/ajustar `sprint_21_modelo_dados_fontes.md`
- Descrever entidades: `Source`, `SourceType`, `SourceCategory`, `SourceStateHistory`, `SourceHealthCheck`.
- Definir campos, relacionamentos, chaves, índices relevantes e campos de auditoria.

4. Escrever/ajustar `sprint_21_ciclo_vida_fontes.md`
- Definir estados da fonte.
- Definir transições permitidas, pré-condições e pós-condições.

5. Escrever/ajustar `sprint_21_fluxos_admin_fontes.md`
- Descrever fluxos: criação, edição, marcação como suspeita, abertura de revisão, desativação temporária, desativação permanente, reativação.

6. Escrever/ajustar `sprint_21_ganchos_debunker_fontes.md`
- Especificar campos adicionais no modelo para conflito, contestação e flags Debunker.
- Explicar como esses campos se encaixam no ciclo de vida.

Revisões:
- Revisão interna pelo Squad 1 para consistência e clareza.
- Revisão externa de pelo menos um representante do Squad 3 (ontologia) e um do Squad 4 (ganchos Debunker).

Gates alimentados:
- S21_G0 (escopo e contexto, referenciado).
- S21_G1 (ontologia).
- S21_G2 (modelo de dados e ciclo de vida).
- S21_G3 (fluxos admin).
- S21_G4 (ganchos Debunker).

---

### 6. Fase 2 — Modelo de dados e migrations

**Objetivo**: traduzir o modelo conceitual em modelos persistidos e migrations aplicáveis.

Entradas:
- `docs/sprint_21_modelo_dados_fontes.md`
- `docs/sprint_21_ciclo_vida_fontes.md`

Saídas:
- Modelos de dados implementados.
- Migration de schema criada e aplicada em ambiente local.

Arquivos envolvidos:
- `app/sources/models.py`
- `migrations/versions/<hash>_s21_sources_schema.py`

Passos macro:

1. Implementar modelos em `app/sources/models.py`
- Criar classes de modelo correspondentes às entidades definidas nos docs.
- Implementar campos de auditoria e enums de estado conforme ciclo de vida.

2. Gerar migration de schema
- Criar arquivo de migration em `migrations/versions/` com criação/alteração das tabelas de fontes.
- Comentar no cabeçalho referência aos docs da Sprint 21.

3. Aplicar migrations em ambiente de desenvolvimento
- Garantir que o banco é atualizado sem erros.
- Realizar um sanity check criando alguns registros simples via ORM ou shell.

Gates alimentados:
- S21_G2 (modelo de dados e ciclo de vida implementáveis).

Fases paralelizáveis após esta:
- Início dos testes de domínio.
- Esboço de serviços em `service.py`.

---

### 7. Fase 3 — Serviços, validações e API de admin

**Objetivo**: implementar a lógica de domínio das fontes e expô-la via API administrativa.

Entradas:
- Modelo de dados implementado (Fase 2).
- Ontologia e ciclo de vida definidos (Fase 1).

Saídas:
- Serviços de domínio prontos.
- API de admin disponível para CRUD de fontes e health-check manual.

Arquivos envolvidos:
- `app/sources/schemas.py`
- `app/sources/validators.py`
- `app/sources/service.py`
- `app/sources/healthcheck.py`
- `app/sources/routes_admin.py`

Passos macro:

1. Implementar schemas em `schemas.py`
- Criar DTOs para criação, edição, leitura e filtros de fontes.
- Definir schemas de config específicos por tipo de fonte.

2. Implementar validações em `validators.py`
- Validar config por tipo e garantir presença de atributos obrigatórios da ontologia.

3. Implementar serviços em `service.py`
- Criar funções para criar, atualizar, alterar estado, registrar health-check, listar e detalhar fontes.
- Aplicar máquina de estados de forma centralizada.

4. Implementar health-check em `healthcheck.py`
- Lógica de execução de health-check manual por tipo.
- Registro de resultados em `SourceHealthCheck`.

5. Implementar API em `routes_admin.py`
- Mapear endpoints HTTP para os serviços e schemas.

Gates alimentados:
- S21_G2 (ciclo de vida implementado na prática).
- S21_G3 (fluxos administrativos habilitados via API).
- S21_G4 (se algum gancho Debunker for usado aqui).

Após esta fase, já é possível começar a construir a UI mínima (Fase 4) e intensificar os testes (Fase 5).

---

### 8. Fase 4 — UI mínima do Console de Fontes

**Objetivo**: disponibilizar um console mínimo para admins operarem fontes via navegador, alinhado com os fluxos descritos em `docs/sprint_21_fluxos_admin_fontes.md`.

Entradas:
- API de admin estável (Fase 3).

Saídas:
- Telas mínimas de lista, detalhe e formulário de fonte, integradas à API.

Arquivos envolvidos (exemplo em stack React/Next):
- `app/admin/ui/pages/sources/index.tsx`
- `app/admin/ui/pages/sources/[id].tsx`
- `app/admin/ui/pages/sources/new.tsx`
- `app/admin/ui/components/source_health_pill.tsx`
- `app/admin/ui/components/source_state_timeline.tsx`

Passos macro:

1. Implementar lista de fontes
- Tabela com colunas básicas e filtros por tipo/categoria/estado.

2. Implementar detalhe de fonte
- Página com visão completa de uma fonte, estados recentes e histórico de health-checks.

3. Implementar formulário de criação/edição
- Formulário condicional por tipo de fonte, refletindo a ontologia.

4. Implementar componentes auxiliares
- Componente visual para estado de saúde e pequena timeline de estados.

Gates alimentados:
- S21_G3 (fluxos admin operacionalizados).
- S21_G6 (cenários de uso demonstráveis via UI).

---

### 9. Fase 5 — Testes do módulo de fontes

**Objetivo**: garantir que o módulo de fontes se comporta conforme a especificação, cobrindo domínio, serviços, API e health-checks.

Entradas:
- Modelo de dados, serviços e API implementados (Fases 2 e 3).

Saídas:
- Conjunto de testes cobrindo invariantes de domínio e fluxos principais, rodando verde.

Arquivos envolvidos:
- `tests/sources/test_domain_model.py`
- `tests/sources/test_service.py`
- `tests/sources/test_routes_admin.py`
- `tests/sources/test_healthcheck_integration.py`

Passos macro:

1. Testes de domínio (`test_domain_model.py`)
- Verificar criação e validação de entidades.
- Testar transições válidas e proibir transições inválidas de estados.

2. Testes de serviços (`test_service.py`)
- Testar operações de criação, edição, mudança de estado e registro de health-check.
- Cobrir casos de erro (config inválida, estado proibido, etc.).

3. Testes de API (`test_routes_admin.py`)
- Exercitar endpoints de CRUD e health-check.

4. Testes de health-check (`test_healthcheck_integration.py`)
- Integrar com seeds criados na Fase 6, quando disponíveis.

Gates alimentados:
- S21_G2 (robustez do modelo e ciclo de vida).
- S21_G3 (fluxos admin verificados via API).
- S21_G6 (ao usar seeds da Fase 6).

---

### 10. Fase 6 — Seeds e cenários de uso

**Objetivo**: materializar cenários de uso em dados reais e documentação, garantindo que o Console de Fontes funciona em domínios concretos.

Entradas:
- Ontologia, modelo, ciclo de vida e fluxos admin consolidados.

Saídas:
- Documento de cenários de uso preenchido.
- Migration de seeds aplicada.

Arquivos envolvidos:
- `docs/sprint_21_cenarios_uso_fontes.md`
- `migrations/versions/<hash>_s21_sources_seed_examples.py`
- `tests/sources/test_healthcheck_integration.py` (reutilizado)

Passos macro:

1. Preencher `sprint_21_cenarios_uso_fontes.md`
- Descrever cenários para cada domínio relevante, com atributos e estados percorridos.

2. Implementar migration de seeds
- Criar migration que insere fontes reais de exemplo, coerentes com os cenários.

3. Ajustar testes de health-check
- Configurar testes de integração para usar essas fontes.

Gates alimentados:
- S21_G6 (cenários de uso).

---

### 11. Fase 7 — Contratos com S22–S25 e scorecard

**Objetivo**: formalizar contratos entre S21 e sprints futuras e consolidar scorecard de qualidade/risco do Console de Fontes.

Entradas:
- Módulo de fontes implementado e testado.
- Cenários de uso documentados.

Saídas:
- Documento de contratos revisado por squads futuros.
- Scorecard de qualidade/risco preenchido.

Arquivos envolvidos:
- `docs/sprint_21_contratos_s22_s25.md`
- `docs/sprint_21_scorecard_console_fontes.md`

Passos macro:

1. Preencher `sprint_21_contratos_s22_s25.md`
- Seção para S22 (ingestão): garantias de config e estados.
- Seção para S23 (interpretação): uso da ontologia.
- Seção para S24 (Debunker): uso de ganchos de conflito/contestação.
- Seção para S25 (governança): uso de proveniência de fontes.

2. Revisão cruzada
- Cada squad futuro revisa a sua seção.

3. Criar `sprint_21_scorecard_console_fontes.md`
- Definir indicadores de cobertura, robustez e risco.
- Preencher valores com base em docs, código, testes e cenários.

Gates alimentados:
- S21_G5 (contratos S22–S25).
- S21_G7 (scorecard de qualidade/risco).

---

### 12. Fase 8 — Scripts de gates, scorecards JSON e evidências

**Objetivo**: automatizar a checagem dos gates, gerar scorecards JSON e organizar evidências em `out/`.

Entradas:
- Todos os docs e código principais da Sprint 21 criados.

Saídas:
- Scripts de gate implementados.
- Scorecards JSON criados.
- Pastas de evidência preenchidas.

Arquivos envolvidos:
- `bin/s21_g0_contexto.sh`
- `bin/s21_g1_ontologia_fontes.sh`
- `bin/s21_g2_modelo_dados.sh`
- `bin/s21_g3_fluxos_admin.sh`
- `bin/s21_g4_ganchos_debunker.sh`
- `bin/s21_g5_contratos_s22_s25.sh`
- `bin/s21_g6_cenarios_uso.sh`
- `bin/s21_g7_scorecard.sh`
- `bin/s21_g8_go_no_go.sh`
- `bin/s21_all_gates.sh` (opcional)
- `out/scorecards/S21_G*.json`
- `out/evidence/S21_G*/MANIFEST.json`

Passos macro:

1. Implementar scripts de gate
- Cada script verifica a presença e o formato de seus artefatos.
- Cada script gera/atualiza um scorecard JSON com o formato padrão (Capítulo 2 v2).

2. Criar pastas de evidência
- Para cada gate, criar `out/evidence/S21_GX_nome_gate/` com `MANIFEST.json` e arquivos relevantes.

3. Rodar gates sequencialmente
- Opcional: implementar `bin/s21_all_gates.sh` para orquestrar a execução.
- Garantir que S21_G0…S21_G7 retornem exit 0 em ambiente limpo.

Gates alimentados:
- S21_G0…S21_G7 (camada automatizada e evidências associadas).

---

### 13. Fase 9 — Wrap final, GO/NO-GO e merge

**Objetivo**: consolidar o resultado da Sprint 21, registrar decisão formal de GO/NO-GO e preparar merge para `main`.

Entradas:
- Todos os gates S21_G0…S21_G7 em estado PASS (ou PASS_WITH_RISKS justificado).

Saídas:
- Wrap final da sprint.
- Scorecard S21_G8 preenchido.
- Decisão GO/NO-GO registrada.

Arquivos envolvidos:
- `docs/sprint_21_wrap_execucao.md`
- `out/scorecards/S21_G8_go_no_go.json`
- `out/evidence/S21_G8_go_no_go/MANIFEST.json`

Passos macro:

1. Redigir `sprint_21_wrap_execucao.md`
- Resumir objetivos, entregas, status dos gates, riscos remanescentes e próximos passos.

2. Implementar e rodar `bin/s21_g8_go_no_go.sh`
- Ler scorecards S21_G0…S21_G7.
- Gerar `S21_G8_go_no_go.json` com decisão e justificativa.
- Gerar `MANIFEST.json` com evidências principais.

3. Revisão final
- Revisão interna do Squad 1.
- Revisão externa de pelo menos um membro do conselho + representantes de S22–S25.

4. Decisão de merge
- Em caso de GO: abrir PR de `feature/s21_console_fontes` para `main`, com descrição alinhada ao wrap.
- Em caso de NO_GO: registrar explicitamente o motivo e as correções necessárias, mantendo a branch viva até resolução.

Gate alimentado:
- S21_G8 (wrap e GO/NO-GO).

---

### 14. Check-list final da Sprint 21

A Sprint 21 é considerada **concluída com sucesso** quando, ao término da Fase 9:

1. Todos os arquivos descritos no Capítulo 3 existem, estão versionados e coerentes com este plano.
2. Todos os gates S21_G0…S21_G8 possuem scorecards em `out/scorecards/` com formatos válidos.
3. Todas as pastas `out/evidence/S21_G*/` possuem `MANIFEST.json` e pelo menos um arquivo de evidência relevante.
4. Testes em `tests/sources/` rodam em ambiente limpo, sem falhas.
5. O console de fontes (UI) permite operar os cenários de `docs/sprint_21_cenarios_uso_fontes.md` ponta a ponta.
6. O documento `docs/sprint_21_contratos_s22_s25.md` foi revisado e aceito pelos squads S22–S25.
7. `docs/sprint_21_wrap_execucao.md` e `out/scorecards/S21_G8_go_no_go.json` contam a mesma história (não há contradição entre narrativa e números).

Quando esses itens estiverem verdadeiros, o Console de Fontes passa a ser um módulo concreto, auditável e pronto para sustentar:
- Ingestão contínua na Sprint 22 (Ingestão 2.0).
- Agentes de interpretação e classificação na Sprint 23.
- Debunker v0 e humano-no-loop na Sprint 24.
- Governança de verdade/fato e promoção na Sprint 25.

A Sprint 21, assim, encerra entregando não apenas código, mas um **contrato operacional completo** sobre como o Inspectah enxerga, cadastra, governa e prepara fontes para todo o restante do pipeline de verdade.