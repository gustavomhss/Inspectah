# Inspectah — Sprint 27 (S27)
## Capítulo 5 — Bloco 2
### Entradas, Matriz de Evidências e Checklist Pré-ORR

> Arquivo-alvo sugerido no repo: `docs/s27_cap_5_2_orr_entradas_e_checklist.md`
>
> Função: definir **quais entradas são obrigatórias** para o ORR da S27, organizar essas entradas em uma **matriz de evidências** e estabelecer um **checklist objetivo** que precisa estar verde antes da sessão. Este bloco evita ORR sem lastro.

---

## 1. Visão geral das entradas do ORR

O ORR da S27 é um julgamento baseado em evidências. As entradas se agrupam em cinco blocos principais:

1. **Scorecards de Gates (G0–G6)**  
2. **Evidências de execução (out/evidence)**  
3. **Documentos de contexto e operação (Cap.1–Cap.4 + guias/runbooks)**  
4. **Bundle de evidências da S27**  
5. **Visão consolidada do Épico E26 (S26 + S27)**

O ORR **não começa** enquanto não houver, para cada um desses blocos, pelo menos o mínimo definido neste documento.

---

## 2. Bloco 1 — Scorecards de Gates (G0–G6)

### 2.1 Lista de scorecards obrigatórios

Os seguintes arquivos em `out/scorecards/` são obrigatórios para o ORR da S27:

- `out/scorecards/S27_G0_scope_and_env.json`  
- `out/scorecards/S27_G1_admin_design_system.json`  
- `out/scorecards/S27_G2_admin_flows.json`  
- `out/scorecards/S27_G3_front_quality_admin.json`  
- `out/scorecards/S27_G4_admin_contracts.json`  
- `out/scorecards/S27_G5_docs_runbooks.json`  
- `out/scorecards/S27_G6_orr_summary.json`

### 2.2 Requisitos mínimos de preenchimento

Para que um scorecard seja considerado utilizável no ORR:

- deve estar em JSON válido;  
- deve conter, no mínimo:
  - identificador da sprint (`"sprint_id": "S27"`);  
  - identificador do gate (`"gate_id": "Gx"`);  
  - um conjunto de campos booleanos ou enumerados que representem o estado do gate (ex.: `env_ok`, `lint_ok`, `e2e_ok`, `contracts_ok`, etc.);  
  - um campo `notes` com, pelo menos, uma frase explicativa (mesmo que seja "nenhuma ressalva relevante").

Scorecards sem `notes` ou com campos críticos vazios (`null`) devem ser considerados **incompletos** para efeitos de ORR.

### 2.3 Papel dos scorecards no ORR

Durante a sessão, os scorecards funcionam como:

- **mapa de calor**: mostram rapidamente quais partes da S27 estão sólidas, fracas ou em estado intermediário;  
- **ponte para evidências**: cada campo problemático ou duvidoso deve ter ligação clara com arquivos de `out/evidence/`.

Sem scorecards minimamente preenchidos, o ORR vira uma conversa no escuro.

---

## 3. Bloco 2 — Evidências em `out/evidence/`

### 3.1 Estrutura mínima esperada

Para cada gate, deve existir pelo menos uma pasta em `out/evidence/`:

- `out/evidence/S27_G0_env_repo/`  
- `out/evidence/S27_G1_admin_design_system/`  
- `out/evidence/S27_G2_admin_flows/`  
- `out/evidence/S27_G3_front_quality_admin/`  
- `out/evidence/S27_G4_admin_contracts/`  
- `out/evidence/S27_G5_docs_runbooks/`  
- `out/evidence/S27_G6_orr/`

Dentro de cada pasta, o mínimo ideal é:

- um ou mais arquivos `.log` (stdout/stderr do script do gate);  
- arquivos `.json` adicionais, se o script gerar relatórios extras;  
- quando fizer sentido, referências a arquivos de teste, relatórios HTML, etc.

### 3.2 Qualidade mínima dos logs

Para entrar no ORR, os logs devem:

- estar legíveis (sem estar corrompidos ou vazios);  
- conter, pelo menos, o comando executado e o status final (sucesso/falha);  
- em caso de falha, conter mensagem suficiente para permitir diagnóstico posterior.

Logs gigantescos podem ser mantidos, mas, se forem difíceis de ler, recomenda-se um resumo no campo `notes` do scorecard correspondente.

### 3.3 Evidência visual (opcional, mas recomendada)

O ORR da S27 pode se apoiar em screenshots das UIs admin, armazenadas, por exemplo, em:

- `docs/screenshots/s27_admin/`

Nomes sugeridos:

- `s27_admin_fontes_list.png`  
- `s27_admin_ingestao_overview.png`  
- `s27_admin_debunker_cases.png`  
- `s27_admin_flow_fontes_ingestao_debunker.png`

Durante o ORR, essas imagens ajudam a conectar o discurso com a realidade visual dos consoles.

---

## 4. Bloco 3 — Documentos de contexto e operação

### 4.1 Documentos da S27

Para o ORR, é obrigatório que estejam presentes e minimamente atualizados:

- Capítulos da S27 (visão macro):  
  - `docs/s27_cap_1_*.md` — Contexto & objetivos;  
  - `docs/s27_cap_2_*.md` — Gates & métricas;  
  - `docs/s27_cap_3_*.md` — Arquitetura & filemap;  
  - `docs/s27_cap_4_*.md` — Execução & evidências;  
  - `docs/s27_cap_5_*.md` — ORR (este capítulo);  
  - `docs/s27_cap_6_learnings_dividas_roadmap.md` — a ser preenchido após o ORR.

- Documentos de operação Admin v1:  
  - `docs/guia_consoles_admin_v1_1.md`  
  - `docs/runbook_operacao_fontes_vX.md`  
  - `docs/runbook_operacao_ingestao_vX.md`  
  - `docs/runbook_operacao_debunker_vX.md`

### 4.2 Critério de "minimamente atualizado"

Um documento é considerado minimamente atualizado se:

- suas seções principais existem conforme esperado (não está em branco);  
- não contém contradições flagrantes com o estado atual do sistema (por exemplo, referir-se a telas que não existem mais);  
- eventuais descompassos conhecidos são explicitamente marcados (por exemplo, em uma seção "Limitações atuais").

Documentos totalmente desatualizados devem ser tratados como **não presentes** para fins de ORR.

---

## 5. Bloco 4 — Bundle de evidências da S27

### 5.1 Requisitos do bundle

O bundle da S27, gerado em:

- `out/bundles/inspectah_s27_evidence_bundle.zip`

deve conter, no mínimo:

1. Todos os scorecards G0–G6 (`out/scorecards/*.json`).  
2. Subconjunto relevante de `out/evidence/S27_G*/` (ao menos os logs principais).  
3. Capítulos 1–6 da S27 (`docs/s27_cap_*.md`).  
4. Guia Admin v1.1 e runbooks de operação dos consoles de Programa 1.

### 5.2 Papel do bundle no ORR

Durante e após o ORR, o bundle funciona como:

- **snapshot congelado** do estado da sprint no momento da decisão;  
- artefato de auditoria: se alguém contestar o veredito no futuro, o bundle é a referência;  
- base para Cap.6 e para sprints futuras, que podem reaproveitar evidências relevantes.

Sugere-se registrar, neste bloco ou em G6, um checksum (por exemplo, SHA256) do bundle, para facilitar auditorias.

---

## 6. Bloco 5 — Visão consolidada do Épico E26

Embora os detalhes completos do Épico E26 possam estar em outro documento, o ORR da S27 precisa de um **resumo congelado** para leitura rápida, contendo:

- objetivo do Épico E26 em até 3 parágrafos;  
- o que foi entregue em S26 (lista sintética de estados ou features relevantes);  
- o que a S27 se propôs a completar em cima de S26;  
- critérios de sucesso do Épico (quando foi criado) e qualquer atualização posterior.

Esse resumo pode estar:

- em uma seção deste próprio Cap.5; ou  
- em `docs/epico_e26_resumo.md`, desde que referenciado de forma clara.

O importante é: durante o ORR, ninguém deve precisar caçar o que era E26 olhando n sprints antigas.

---

## 7. Matriz de evidências do ORR da S27

Abaixo, uma matriz que liga **estados-alvo** (SA-01..SA-05), **gates** e **entradas concretas** que o ORR vai consultar:

| Estado-alvo | Gate(s) principais | Entradas principais |
|------------|--------------------|---------------------|
| SA-01 — Admin v1 padrão real | G1, G3 | `S27_G1_admin_design_system.json`, `S27_G3_front_quality_admin.json`, código em `ui/admin` e `features/*`, screenshots admin |
| SA-02 — Fluxos E2E críticos | G2, G3 | `S27_G2_admin_flows.json`, logs de `S27_G2_admin_flows`, cenários E2E, demo dos consoles |
| SA-03 — Contratos estáveis | G4, G2 | `S27_G4_admin_contracts.json`, `contracts_tests.log`, testes de contrato em `tests/api/*`, efeitos em G2 |
| SA-04 — Operação documentada | G5 | `S27_G5_docs_runbooks.json`, guia Admin v1.1, runbooks, evidências de simulação |
| SA-05 — Avaliação objetiva da S27/E26 | G6 (e G0–G5) | `S27_G6_orr_summary.json`, bundle `.zip`, este Cap.5, Cap.6 |

Essa matriz deve ser usada ativamente durante o ORR: sempre que alguém levantar uma dúvida sobre um estado-alvo, o comitê deve saber **exatamente** quais arquivos consultar.

---

## 8. Checklist pré-ORR (must be green)

Antes de marcar o ORR como "valendo", o representante de Qualidade/Gates deve checar os itens abaixo (pode ser literalmente um checklist em markdown dentro deste arquivo):

- [ ] Todos os scorecards `S27_G0..G6` existem em `out/scorecards/` e foram atualizados na última rodada de gates.  
- [ ] Pastas `out/evidence/S27_G*/` existem e contêm ao menos um log relevante por gate.  
- [ ] `inspectah_s27_evidence_bundle.zip` existe em `out/bundles/` e abre sem erros.  
- [ ] Cap.1–Cap.4 da S27 estão presentes e não conflitam de forma grosseira com o estado atual.  
- [ ] Guia Admin v1.1 e runbooks de Fontes/Ingestão/Debunker existem e foram, no mínimo, folheados pelo time.  
- [ ] Resumo do Épico E26 (S26 + S27) está disponível em um único lugar de leitura rápida.  
- [ ] Ambiente de demonstração dos consoles admin está acessível para a sessão do ORR.  
- [ ] Principais participantes confirmaram presença ou delegaram representantes.

Se algum item estiver em vermelho, isso deve ser registrado: ou o ORR é adiado, ou prossegue explicitamente em modo "preliminar".

---

## 9. Resultado esperado deste bloco

Com o Bloco 2, o ORR da S27 ganha um **filtro de qualidade** antes de começar:

- evita reuniões baseadas em memória e opinião;  
- garante que todos os artefatos relevantes estão no lugar;  
- entrega uma matriz clara ligando estados-alvo a arquivos concretos;  
- define um checklist simples para o representante de Qualidade/Gates.

Os blocos seguintes do Capítulo 5 podem, então, focar em **como conduzir a sessão** (roteiro, dinâmica, critérios GO/NO_GO/GO_WITH_RISKS) e em **como registrar o veredito** em G6 e nos docs.

