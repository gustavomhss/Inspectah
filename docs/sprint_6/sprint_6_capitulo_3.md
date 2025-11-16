# Sprint 6 — Capítulo 3

Inspectah Data Hub Alpha — Filemap Oficial da Sprint 6

---

## 0) Papel deste capítulo

Este Capítulo 3 é dedicado **exclusivamente** ao **filemap oficial da Sprint 6**.

Ele define, de forma precisa e estável:

- quais diretórios, arquivos e scripts existem no Inspectah ao final da Sprint 6;
- como eles se relacionam com os pilares P1–P5 do Capítulo 1;
- como eles se relacionam com os gates S6‑G0…S6‑G8 do Capítulo 2;
- quais nomes e caminhos passam a ser tratados como **contrato** para sprints futuras.

Capítulo 3 **não** descreve a execução nem a cronologia da sprint. O "como executar" (trilhas, checkpoints, plano de trabalho) é responsabilidade do **Capítulo 4**. Este capítulo responde apenas à pergunta:

> "Onde vive cada coisa da Sprint 6, como ela se chama e qual papel ela cumpre no Inspectah Data Hub Alpha?"

---

## 1) Princípios do filemap

### 1.1. Fonte única de verdade

O filemap da Sprint 6 é a **fonte única de verdade** para a estrutura do Inspectah até o nível de arquivos relevantes. Se um artefato é importante para o Inspectah Data Hub Alpha, ele deve aparecer aqui ou ser explicitamente marcado como fora de escopo.

### 1.2. Estabilidade de nomes

Nomes e caminhos definidos neste capítulo são tratados como **estáveis** a partir do final da Sprint 6. Sprints futuras podem:

- adicionar novos arquivos, diretórios e scripts;
- estender estruturas já existentes;
- introduzir novas versões de artefatos (v2, v3…).

Mas não podem, sem plano explícito de migração:

- renomear ou mover silenciosamente os artefatos que são contratos da Sprint 6;
- alterar o significado sem atualizar o filemap e os contratos do Capítulo 1.

### 1.3. Alinhamento com contratos e gates

Cada entrada do filemap é traçada com três perguntas:

1. **Que pilar P1–P5 ela serve?** (Capítulo 1)
2. **Que gate S6‑G0…S6‑G8 depende dela?** (Capítulo 2)
3. **Que tipo de artefato ela é?** (configuração, script operacional, script de gate, scorecard, evidência, bundle, doc etc.)

Este capítulo organiza o filemap seguindo essa lógica.

---

## 2) Visão geral da árvore da Sprint 6

Estrutura macro (somente pastas relevantes para a Sprint 6):

- `docs/`
  - `sprint_6/`
- `config/`
  - `sources/`
  - `fields/`
- `bin/`
- `out/`
  - `scorecards/`
  - `evidence/`
  - `queries/`
  - `s6_bundle/`

As próximas seções detalham cada uma dessas áreas.

---

## 3) Documentação da Sprint 6 (`docs/sprint_6/`)

### 3.1. Arquivos obrigatórios

- `docs/sprint_6/sprint_6_capitulo_1.md`
  - Conteúdo: objetivo único, pilares P1–P5, contratos, DoR/DoD, filme do operador.
  - Papel: documento de intenção e escopo da Sprint 6.
  - Relacionamento: pré‑requisito de S6‑G0.

- `docs/sprint_6/sprint_6_capitulo_2.md`
  - Conteúdo: definição dos gates S6‑G0…S6‑G8, scripts, scorecards, lógica GO/NO‑GO.
  - Papel: especificação do funil de validação.
  - Relacionamento: base de todos os scripts de gate.

- `docs/sprint_6/sprint_6_capitulo_3.md`
  - Conteúdo: este filemap oficial da Sprint 6.
  - Papel: contrato de estrutura de arquivos.
  - Relacionamento: referência cruzada por gates e por sprints futuras.

- `docs/sprint_6/sprint_6_capitulo_4.md`
  - Conteúdo: plano de execução, cronologia, trilhas, checkpoints e wrap final.
  - Papel: descreve **como** a Sprint 6 foi executada (não coberto aqui).
  - Relacionamento: referenciado pelos gates finais e pelo bundle S6.

- `docs/sprint_6/dominio_piloto.md`
  - Conteúdo: descrição detalhada do domínio piloto (tipo de informação, fontes candidatas, formatos, URLs exemplo, restrições de uso).
  - Papel: ancora P1 (Sources) e P2 (Field Designer).
  - Relacionamento: entrada direta de S6‑G0 e S6‑G1.

- `docs/sprint_6/sprint_6_resultados.md`
  - Conteúdo: resumo executivo da Sprint 6, SLOs medidos, estado final dos gates, decisões GO/NO‑GO.
  - Papel: wrap final humano.
  - Relacionamento: referenciado por S6‑G8.

### 3.2. Contrato de documentação

- Todos os capítulos 1–4 da Sprint 6 devem existir.
- Qualquer alteração estrutural em domínios, gates ou filemap exige atualização neste diretório.

---

## 4) Configuração de fontes e campos (`config/`)

### 4.1. Sources (`config/sources/`)

- `config/sources/fonte_a.yaml`
- `config/sources/fonte_b.yaml`
- `config/sources/fonte_c.yaml`
- (opcional) `config/sources/fonte_*.yaml` adicionais

Papel:

- Descrevem o **Source Registry v0** do domínio piloto (P1).
- Cada arquivo define: identificador da fonte, tipo (`rss`, `api_json`, `html_plain` v0…), endpoints, parâmetros fixos, política de polling, chave(s) de dedupe, referências ao modelo canônico.

Relacionamento:

- Gates: S6‑G1 (validação de fontes), S6‑G3 (coleta), S6‑G2 (ao mapear campos).
- Contratos: não podem ser renomeados sem atualização explícita em Capítulo 1 e Capítulo 2.

### 4.2. Fields (`config/fields/`)

- `config/fields/dominio_piloto.yaml`

Papel:

- Define o **modelo canônico** do domínio piloto (P2):
  - lista de campos canônicos (nome, tipo, descrição);
  - obrigatoriedade (obrigatório/opcional);
  - fonte de cada campo por tipo de fonte (JSONPath, XPath, chave, seletor);
  - transformações simples (parsing de datas, normalização, truncamento).

Relacionamento:

- Gates: S6‑G2 (Field Designer), S6‑G3 (coleta canônica), S6‑G4 (consulta), S6‑G6 (reprodutibilidade).
- Contratos: nomes e semântica dos campos aqui descritos são parte do contrato de estabilidade da Sprint 6.

---

## 5) Scripts operacionais do Inspectah Alpha (`bin/inspectah_*.sh`)

Scripts que o operador e o guard usam no dia a dia, independentes de gates específicos.

- `bin/inspectah_sources_validate.sh`
  - Papel: valida sintaxe e semântica dos YAML de fonte; executa dry‑run para obter amostras.
  - Relacionamento: base de S6‑G1, usado também em desenvolvimento diário.

- `bin/inspectah_fields_preview.sh`
  - Papel: aplica o Field Designer v0 em amostras; mostra registros canônicos e erros de parsing.
  - Relacionamento: base de S6‑G2.

- `bin/inspectah_collect_once.sh`
  - Papel: roda um ciclo completo de coleta para o domínio piloto (todas as fontes relevantes).
  - Relacionamento: base de S6‑G3; também usado em rodadas manuais de coleta.

- `bin/inspectah_query.sh`
  - Papel: executa consultas consolidadas sobre o domínio piloto (filtros, paginação, export JSON/CSV).
  - Relacionamento: base de S6‑G4; uso diário pelo operador.

- `bin/inspectah_show_evidence.sh`
  - Papel: dado um `item_id`, mostra manifesto e ponte para raw.* da evidência.
  - Relacionamento: base de S6‑G4; implementa a navegação consulta → evidência.

- `bin/inspectah_metrics_snapshot.sh`
  - Papel: captura snapshot de métricas essenciais (latência, volume, falhas, frescor) para o domínio piloto.
  - Relacionamento: base de S6‑G5.

- `bin/inspectah_s6_build_bundle.sh`
  - Papel: constrói o bundle S6 (artefatos, evidências, configs, exports e docs) em `out/s6_bundle/`.
  - Relacionamento: base de S6‑G6.

- `bin/inspectah_s6_verify_bundle.sh`
  - Papel: valida que o bundle S6 é suficiente para reexecutar um mini fluxo (pelo menos validação de fontes + consulta simples).
  - Relacionamento: base de S6‑G6.

- `bin/inspectah_s6_guard.sh`
  - Papel: guard automatizado da Sprint 6; encadeia a execução dos gates essenciais (G1…G4) em um único comando.
  - Relacionamento: base de S6‑G7 e de qualquer integração com CI.

Contratos:

- Os nomes acima são fixos; scripts futuros podem envolver wrappers, mas estes são os entrypoints canônicos da S6.

---

## 6) Scripts de gates S6‑G0…S6‑G8 (`bin/s6_g*.sh`)

Scripts responsáveis por materializar os gates definidos no Capítulo 2.

- `bin/s6_g0_domain_setup.sh`
  - Gate: S6‑G0 (Domínio & Setup / DoR).
  - Entrada: docs da sprint, `dominio_piloto.md`, estado do repo.
  - Saída: `out/scorecards/S6_G0_domain_setup.json`, `out/evidence/S6_G0_domain_setup/`.

- `bin/s6_g1_sources_registry.sh`
  - Gate: S6‑G1 (Source Registry v0).
  - Entrada: `config/sources/*.yaml`, `inspectah_sources_validate.sh`.
  - Saída: `out/scorecards/S6_G1_sources_registry.json`, `out/evidence/S6_G1_sources_registry/`.

- `bin/s6_g2_field_designer.sh`
  - Gate: S6‑G2 (Field Designer v0).
  - Entrada: `config/fields/dominio_piloto.yaml`, fontes.
  - Saída: `out/scorecards/S6_G2_field_designer.json`, `out/evidence/S6_G2_field_designer/`.

- `bin/s6_g3_collect_evidence.sh`
  - Gate: S6‑G3 (Coleta & Evidence Vault).
  - Entrada: configs, scripts de coleta.
  - Saída: `out/scorecards/S6_G3_collect_evidence.json`, `out/evidence/S6_G3_collect_evidence/`.

- `bin/s6_g4_explore_verify.sh`
  - Gate: S6‑G4 (Consulta Consolidada & Jornada do Operador).
  - Entrada: dados canônicos e de evidência, scripts de consulta.
  - Saída: `out/scorecards/S6_G4_explore_verify.json`, `out/evidence/S6_G4_explore_verify/`.

- `bin/s6_g5_metrics_obs.sh`
  - Gate: S6‑G5 (Métricas & Observabilidade).
  - Entrada: endpoint/arquivo de métricas, snapshot.
  - Saída: `out/scorecards/S6_G5_metrics_obs.json`, `out/evidence/S6_G5_metrics_obs/`.

- `bin/s6_g6_bundle_repro.sh`
  - Gate: S6‑G6 (Bundle & Reprodutibilidade).
  - Entrada: scripts de build/verify de bundle, artefatos de S6.
  - Saída: `out/scorecards/S6_G6_bundle_repro.json`, `out/evidence/S6_G6_bundle_repro/`.

- `bin/s6_g7_guard_automation.sh`
  - Gate: S6‑G7 (Guards Automatizados).
  - Entrada: `inspectah_s6_guard.sh` e scripts S6‑G1…S6‑G4.
  - Saída: `out/scorecards/S6_G7_guard_automation.json`, `out/evidence/S6_G7_guard_automation/`.

- `bin/s6_g8_sprint_go_no_go.sh`
  - Gate: S6‑G8 (GO/NO‑GO da Sprint 6).
  - Entrada: todos os scorecards S6‑G0…S6‑G7.
  - Saída: `out/scorecards/S6_G8_sprint_go_no_go.json`, `out/evidence/S6_G8_sprint_go_no_go/summary.md`.

Contratos:

- Esses scripts são a implementação canônica dos gates; qualquer mudança em nomes ou caminhos precisa ser refletida no Capítulo 2 e aqui.

---

## 7) Scorecards da Sprint 6 (`out/scorecards/`)

Diretório responsável por armazenar o estado consolidado de cada gate.

Arquivos obrigatórios:

- `out/scorecards/S6_G0_domain_setup.json`
- `out/scorecards/S6_G1_sources_registry.json`
- `out/scorecards/S6_G2_field_designer.json`
- `out/scorecards/S6_G3_collect_evidence.json`
- `out/scorecards/S6_G4_explore_verify.json`
- `out/scorecards/S6_G5_metrics_obs.json`
- `out/scorecards/S6_G6_bundle_repro.json`
- `out/scorecards/S6_G7_guard_automation.json`
- `out/scorecards/S6_G8_sprint_go_no_go.json`

Cada arquivo contém, no mínimo:

- `gate`: identificador do gate (ex.: "S6_G3");
- `status`: `PASS`, `WARN`, `FAIL` (ou `GO`/`NO_GO` no caso de S6‑G8);
- métricas e detalhes relevantes para diagnóstico.

Contratos:

- Scorecard sem diretório de evidência correspondente em `out/evidence/` é considerado inválido.

---

## 8) Evidências da Sprint 6 (`out/evidence/`)

### 8.1. Evidência por gate

Subdiretórios por gate:

- `out/evidence/S6_G0_domain_setup/`
- `out/evidence/S6_G1_sources_registry/`
- `out/evidence/S6_G2_field_designer/`
- `out/evidence/S6_G3_collect_evidence/`
- `out/evidence/S6_G4_explore_verify/`
- `out/evidence/S6_G5_metrics_obs/`
- `out/evidence/S6_G6_bundle_repro/`
- `out/evidence/S6_G7_guard_automation/`
- `out/evidence/S6_G8_sprint_go_no_go/`

Papel:

- Guardar logs, amostras de saída, manifests auxiliares, snapshots e resumos humanos que sustentam cada scorecard.

### 8.2. Evidência operacional do domínio piloto

- `out/evidence/dominio_piloto/{fonte}/{YYYY}/{MM}/{DD}/{item_id}/`
  - `raw.*` — conteúdo bruto (HTML, JSON, XML etc.).
  - `text.txt` — texto extraído, quando aplicável.
  - `manifest.json` — metadados, hash(s), origem da informação, timestamps.
  - `hash.txt` — hash forte do conteúdo bruto, se não estiver dentro do manifest.

Papel:

- Materializar o **contrato de evidência** da Sprint 6: nenhum registro canônico existe sem um pacote de evidência correspondente.

Contratos:

- Pacotes são imutáveis após criados.
- Reexecutar coleta não sobrescreve evidências antigas; no máximo adiciona novas.

---

## 9) Consultas e exports (`out/queries/`)

- `out/queries/dominio_piloto_*.json`
- `out/queries/dominio_piloto_*.csv`

Papel:

- Guardar resultados de consultas consolidadas (Explore & Verify v0).
- Fornecer exemplos concretos de uso do `inspectah_query.sh`.

Relacionamento:

- Produzidos tanto durante o uso normal quanto durante S6‑G4.

---

## 10) Bundle da Sprint 6 (`out/s6_bundle/`)

- `out/s6_bundle/inspectah_s6_bundle.tar.gz` (nome exato pode ser fixado no script de build).
- `out/s6_bundle/SHA256SUMS` — hashes do bundle e componentes relevantes.
- `out/s6_bundle/README.md` — instruções curtas de como usar `inspectah_s6_verify_bundle.sh`.

Papel:

- Representar um snapshot autocontido da Sprint 6 (estado Alpha) para recuperação, diagnóstico e demonstrações.

Relacionamento:

- Construído por `bin/inspectah_s6_build_bundle.sh`.
- Validado por `bin/inspectah_s6_verify_bundle.sh`.
- Gate S6‑G6 depende da existência e integridade deste diretório.

---

## 11) Relação Filemap ↔ Pilares ↔ Gates

Resumo conceitual:

- P1 — **Registro de fontes**
  - `config/sources/`, `inspectah_sources_validate.sh`, S6‑G1.
- P2 — **Field Designer v0**
  - `config/fields/dominio_piloto.yaml`, `inspectah_fields_preview.sh`, S6‑G2.
- P3 — **Watchers + Evidence Vault v0**
  - `inspectah_collect_once.sh`, `out/evidence/dominio_piloto/...`, S6‑G3.
- P4 — **Explore & Verify v0**
  - `inspectah_query.sh`, `inspectah_show_evidence.sh`, `out/queries/`, S6‑G4.
- P5 — **Observabilidade + Bundle S6**
  - `inspectah_metrics_snapshot.sh`, `inspectah_s6_build_bundle.sh`, `inspectah_s6_verify_bundle.sh`, `out/s6_bundle/`, S6‑G5 e S6‑G6.

Gates S6‑G0…S6‑G8 são implementados pelos `bin/s6_g*.sh` e persistem seu estado em `out/scorecards/` + `out/evidence/S6_G*/`.

---

## 12) Mapa resumido: caminho → tipo → pilar → gate

| Caminho raiz                          | Tipo de artefato            | Pilar(es) P1–P5        | Gate(s) S6‑G* principais                      | Comentário operacional                                  |
|---------------------------------------|-----------------------------|------------------------|-----------------------------------------------|---------------------------------------------------------|
| `docs/sprint_6/`                      | Documentação de sprint      | Todos                 | S6‑G0, S6‑G8                                  | Norte conceitual da S6 (escopo, gates, filemap, wrap). |
| `config/sources/`                     | Configuração de fontes      | P1                     | S6‑G1, S6‑G3                                  | Descreve o Source Registry v0 do domínio piloto.       |
| `config/fields/dominio_piloto.yaml`   | Modelo canônico             | P2                     | S6‑G2, S6‑G3, S6‑G4, S6‑G6                    | Define campos canônicos e mapeamento fonte → campo.    |
| `bin/inspectah_*.sh`                  | Scripts operacionais        | P1–P5                  | S6‑G1…S6‑G6, S6‑G7                            | Entrada de uso diário do operador e do guard.          |
| `bin/s6_g*.sh`                        | Scripts de gate             | Todos                 | S6‑G0…S6‑G8                                   | Implementam o funil de validação da S6.                |
| `out/scorecards/`                     | Estado dos gates            | Todos                 | S6‑G0…S6‑G8                                   | Registro formal de PASS/WARN/FAIL/GO/NO_GO.            |
| `out/evidence/S6_G*/`                 | Evidência por gate          | Todos                 | S6‑G0…S6‑G8                                   | Logs, amostras e manifests que sustentam scorecards.   |
| `out/evidence/dominio_piloto/...`     | Evidência operacional       | P3, P4                 | S6‑G3, S6‑G4                                  | Pacotes de evidência (manifest + raw) por item.        |
| `out/queries/`                        | Resultados de consulta      | P4                     | S6‑G4                                        | Exports JSON/CSV gerados por Explore & Verify.         |
| `out/s6_bundle/`                      | Bundle Alpha da Sprint 6    | P5                     | S6‑G6                                        | Snapshot autocontido da S6 para reexecução/diagnóstico.|

Este quadro é a vista "30 segundos" do Inspectah Alpha: em uma única página, alguém entende onde mora cada peça crítica da Sprint 6.

---

## 13) Invariantes do filemap como contrato

As seguintes invariantes são **obrigatórias** a partir do final da Sprint 6:

1. **Contratos de diretórios**
   - É proibido mover ou renomear as pastas‑raiz `docs/sprint_6/`, `config/sources/`, `config/fields/`, `bin/`, `out/scorecards/`, `out/evidence/`, `out/queries/` e `out/s6_bundle/` sem atualização explícita deste Capítulo 3 e do Capítulo 1.

2. **Contratos de scripts canônicos**
   - Scripts `bin/inspectah_*.sh` e `bin/s6_g*.sh` são entrypoints canônicos da S6. Wrappers podem ser adicionados, mas estes nomes **não podem** ser trocados ou removidos sem plano de migração formal.

3. **Scorecards ↔ evidência**
   - Nenhum `out/scorecards/S6_G*.json` é considerado válido se não existir o diretório correspondente `out/evidence/S6_G*/` com evidência mínima.

4. **Registros ↔ evidência operacional**
   - Qualquer registro retornado por `inspectah_query.sh` deve corresponder a um pacote de evidência em `out/evidence/dominio_piloto/...`. Se isso não for verdadeiro, há violação do contrato de evidência da S6.

5. **Bundle S6 como snapshot estável**
   - `out/s6_bundle/` deve sempre permitir reexecutar o mini fluxo definido em `inspectah_s6_verify_bundle.sh`. Se evoluções futuras tornarem o bundle inútil, deve existir um plano de migração claro documentado.

Qualquer mudança que viole essas invariantes **quebra o contrato da Sprint 6** e deve ser tratada como regressão grave.

---

## 14) Exemplo de navegação prática usando o filemap

Exemplo minimalista de como um operador (ou revisor) enxerga o Inspectah Alpha apenas com o filemap:

1. Começa em `docs/sprint_6/` e lê `sprint_6_capitulo_1.md` + `sprint_6_capitulo_2.md` para entender objetivo e gates.
2. Abre `docs/sprint_6/dominio_piloto.md` para ver quais fontes importam e que informação está sendo rastreada.
3. Navega para `config/sources/` e inspeciona `fonte_a.yaml`, `fonte_b.yaml`, `fonte_c.yaml` para ver como essas fontes estão configuradas.
4. Abre `config/fields/dominio_piloto.yaml` para ver quais campos canônicos existem e como são extraídos.
5. Roda `bin/inspectah_collect_once.sh` e observa novos pacotes em `out/evidence/dominio_piloto/...`.
6. Roda `bin/inspectah_query.sh` e vê resultados em tela + exports em `out/queries/`.
7. Escolhe um `item_id`, roda `bin/inspectah_show_evidence.sh` e navega até o pacote correspondente em `out/evidence/dominio_piloto/...`.
8. Por fim, olha `out/scorecards/` e `out/evidence/S6_G*/` para conferir o estado dos gates, e `out/s6_bundle/` para verificar se o snapshot Alpha está íntegro.

Esse fluxo não descreve a cronologia da sprint (tema do Capítulo 4), mas mostra que **todo o sistema é navegável apenas com nomes de arquivos e pastas** descritos aqui.

---

## 15) Guia para sprints futuras (S7, S8, ...)

A partir da Sprint 7, este filemap passa a funcionar como contrato de compatibilidade:

- É **seguro**:
  - adicionar novos scripts em `bin/`, mantendo os existentes;
  - criar novos subdiretórios bem nomeados dentro de `out/evidence/` (por exemplo, para novos domínios);
  - estender `config/fields/dominio_piloto.yaml` com novos campos opcionais, mantendo os existentes.

- Exige **migração formal** documentada:
  - qualquer mudança em nomes/caminhos de `bin/inspectah_*.sh` e `bin/s6_g*.sh`;
  - remoção ou renomeação de arquivos centrais em `config/sources/` ou `config/fields/`;
  - mudanças que tornem `out/s6_bundle/` inutilizável como snapshot da S6.

- É **fortemente desencorajado**:
  - criar artefatos relevantes fora das pastas mapeadas neste capítulo sem, em seguida, atualizar o filemap;
  - manter arquivos "órfãos" (não mencionados aqui) que sejam necessários para o funcionamento do Alpha.

Sprints futuras devem pensar: “O que estou fazendo se encaixa no filemap (estendo) ou o modifica (migro)?” — nunca deixar o estado real divergir silenciosamente deste capítulo.

---

## 16) Como este capítulo deve ser usado

- **Durante a implementação**: o filemap é um check‑list estrutural. Qualquer arquivo importante criado pela S6 deve ser confirmadamente mapeado aqui; se não estiver, ou é lixo ou o filemap está desatualizado.
- **Na revisão da sprint**: revisores usam este capítulo como roteiro de auditoria: conferem se cada caminho descrito existe, se cumpre o papel indicado e se os scorecards têm evidência correspondente.
- **Em sprints futuras**: este capítulo é o contrato de estrutura do Inspectah Alpha. Mudanças profundas exigem discussão explícita, atualização deste documento e, se necessário, migrações controladas.

Com este Capítulo 3 refinado, o Inspectah Data Hub Alpha ganha um **mapa estrutural completo, simétrico e navegável**: em poucos segundos, qualquer integrante do time entende onde cada peça vive, como ela se chama, que contratos cumpre e como se conecta aos pilares P1–P5 e aos gates S6‑G0…S6‑G8. O Capítulo 4 passa a poder assumir todo esse mapa como base estável para descrever a execução da Sprint 6.