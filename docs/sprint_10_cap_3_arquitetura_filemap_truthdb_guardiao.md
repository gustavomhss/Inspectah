# Sprint 10 — Capítulo 3 — Arquitetura, Filemap e Contratos Estruturais (Truth-DB & Guardião de Blocos) (v4)

Versão v4 — refinada em conjunto com a “banca” (Jobs, Lamport, Vitalik, Knuth, Kay, Kleppmann, Pérez, Meyer) a partir do Cap. 1 v3 (Visão), Cap. 2 v3 (Gates), DNA/Leassons e do Cap. 3 v3. Este capítulo é **exclusivamente estrutural**: define arquitetura, filemap e contratos internos da S10. Toda a parte de **execução, scripts, comandos e runbook** fica para o Capítulo 4.

---

## 0) TL;DR — o esqueleto está aqui, o movimento é no Cap. 4

- Cap. 1 diz o **porquê/o quê** da Truth-DB & Guardião.  
- Cap. 2 diz **como ela é julgada** (gates, SLIs/SLOs, DoD).  
- Este Cap. 3 diz **onde cada coisa mora e como elas se encaixam entre si**, em termos de:
  - arquitetura de componentes (Truth-DB, Guardião, engine, pipelines, exports);
  - filemap (docs, código, configs, schemas, migrations);
  - contratos estruturais (dados, estados, ações, integrações e exports).

Qualquer coisa que envolva “rodar algo, script, pipeline, CI, PASS/WARN/FAIL” pertence ao Cap. 4.

---

## 1) Objetivos do Capítulo 3

1. Definir a **arquitetura de alto nível** da S10 (componentes e fronteiras) para Truth-DB & Guardião de Blocos.  
2. Especificar o **filemap canônico** da S10: onde ficam docs, código-fonte, configs, schemas, migrations e ferramentas de inspeção.  
3. Formalizar os **contratos estruturais** que amarram o sistema:
   - contrato de dados (Truth-DB);
   - contrato de estados (máquina de estados de fatos);
   - contrato de ações do Guardião;
   - contrato de integração com pipelines de domínio;
   - contrato de exports para S11/S12.
4. Amarrar **gates do Cap. 2 → artefatos estruturais** deste capítulo, garantindo que toda a S10 seja desenvolvida para encaixar nesses gates.

---

## 2) Arquitetura de alto nível da S10

A S10 se organiza em cinco blocos arquiteturais principais:

1. **Truth-DB Core**  
   - papel: ser a base canônica de blocos, fatos, complementos, versões e estados;  
   - inclui modelo de dados, máquina de estados, invariantes estruturais e exports;  
   - gates mais ligados: G1 (modelo), G2 (estados), G7 (auditabilidade/futuro).

2. **Guardião de Blocos (GPT + camada de ações)**  
   - papel: receber contexto + evidências e propor ações estruturadas sobre a Truth-DB;  
   - exposto via contrato de ações, schemas e prompts (Cap. 4 detalha prompts);  
   - gates mais ligados: G3 (contrato), G4 (engine mecânica).

3. **Engine Mecânica de Aplicação**  
   - papel: receber ações JSON, validar contrato + estados + invariantes e aplicar/rejeitar na Truth-DB;  
   - funciona como “firewall” entre qualquer agente (GPT, pipelines, operadores) e a Truth-DB;  
   - gates mais ligados: G2 (estados), G3 (contrato), G4 (engine).

4. **Pipelines de Domínio (A e B)**  
   - papel: transformar eventos de domínio (obras públicas, preços, etc.) em blocos/fatos/complementos e acionar o Guardião/engine;  
   - gates mais ligados: G5 (domínio A), G6 (domínio B).

5. **Camada de Inspeção & Exports (Auditability & Future)**  
   - papel: tornar a Truth-DB auditável (linha do tempo, estados, eventos) e pronta para consumo de S11/S12 (blockchain, Explorer, etc.);  
   - gates mais ligados: G7 (auditabilidade/futuro) e insumo central para G8 (GO/NO-GO).

O Cap. 4 vai dizer **como** esses blocos são acionados (scripts, comandos, CI). Aqui definimos apenas **quem é quem** e **onde vive o quê**.

---

## 3) Filemap canônico da Sprint 10

Este filemap destaca **novos artefatos** ou artefatos existentes que passam a ter papel central na S10. Ele complementa o filemap global do projeto.

### 3.1 Documentos

- `docs/`
  - `DNA/`  
    Fonte suprema de verdade (não modificada pela S10, mas sempre referenciada).
  - `sprint_10_cap_1_visao_truthdb_guardiao.md`  
    Cap. 1 v3 — visão da Truth-DB & Guardião de Blocos.
  - `sprint_10_cap_2_gates_truthdb_guardiao.md`  
    Cap. 2 v3 — gates, SLIs/SLOs, DoD.
  - `sprint_10_cap_3_arquitetura_filemap_truthdb_guardiao.md`  
    Este capítulo (arquitetura + filemap + contratos estruturais).
  - `sprint_10_cap_4_execucao_codex_guardiao_de_blocos.md`  
    Cap. 4 — execução, scripts, runbook, integração Codex/CI.
  - `sprint_10_cenarios_e2e.md`  
    Catálogo de cenários E2E da S10 (sem comandos, apenas descrição estrutural de caminhos e casos de uso).
  - `sprint_10_state_machine.md` (opcional)  
    Diagrama textual da máquina de estados (espelho humano do contrato de estados).
  - `sprint_10_contrato_acoes_guardiao.md`  
    Documento canônico do contrato de ações do Guardião (sem lógica de execução).
  - `sprint_10_summary.md`  
    Resumo humano da S10, consumido pelo G8.

### 3.2 Truth-DB Core

Assumindo um namespace `inspectah/` (adaptar ao repo real, mantendo a estrutura conceitual):

- `inspectah/truthdb/`
  - `__init__.py`
  - `models.py`  
    Define entidades canônicas da S10: `BlocoTema`, `FatoRegistravel`, `Complemento`, `VersaoFato`, `EstadoFato`.
  - `state_machine.py`  
    Define a máquina de estados de fatos (contrato de estados em forma executável).
  - `invariants.py` (opcional)  
    Centraliza invariantes estruturais (integridade de IDs, relações obrigatórias, etc.).
  - `actions_contract.py`  
    Tipos de ação, mapeamento para schemas, convenções de nomes de ações (lado código).
  - `engine.py`  
    Interface da engine mecânica (sem detalhar como será chamada nem por quem).
  - `exports.py`  
    Estruturas de saída para blocos/fatos e linhas do tempo (base para S11/S12).

### 3.3 Pipelines de domínio

- `inspectah/pipelines/`
  - `s10_domain_a_obras.py`  
    Lado estrutural da pipeline do domínio A (nomes de entrypoints, tipos de dados internos, estrutura de fatos/blocos). Detalhes de execução ficam no Cap. 4.
  - `s10_domain_b_precos.py`  
    Lado estrutural da pipeline do domínio B.

### 3.4 Configurações

- `config/`
  - `s10_truthdb_domains.yml`  
    Declara domínios A e B: tipos de fatos, fontes de dados lógicas, mapeamentos eventos→fatos/blocos.
  - `s10_state_machine.yml` (opcional)  
    Versão declarativa da máquina de estados (contrato de estados em formato de config).
  - `s10_exports.yml`  
    Define quais campos entram nos exports voltados a S11/S12 (IDs, hashes, metadados mínimos, etc.).

### 3.5 Migrations / Banco de Dados

- `migrations/versions/`
  - `XXXX_s10_truthdb_core.py`  
    Migration que introduz/ajusta tabelas da Truth-DB segundo o contrato deste capítulo (nome exato a definir no Cap. 4).

### 3.6 Schemas do contrato de ações

- `schema/` (ou `resources/schema/`)
  - `s10_guardian_actions.schema.json`  
    Schemas JSON de payload para cada ação do Guardião, em total alinhamento com `sprint_10_contrato_acoes_guardiao.md` e `actions_contract.py`.

### 3.7 Ferramentas de inspeção e exports

- `scripts/`
  - `truthdb_inspect.py`  
    Interface estrutural de CLI para inspecionar blocos/fatos/estados (Cap. 4 define comandos exatos).
  - `truthdb_export_demo.py`  
    Ponto de entrada conceitual para gerar exports exemplares (A e B).

### 3.8 Scorecards e evidências (estrutura de pastas)

Mesmo que a lógica de preenchimento seja Cap. 4, a **estrutura** pertence a este capítulo:

- `out/scorecards/`
  - `S10_G0_sanity.json`
  - `S10_G1_truthdb_model.json`
  - `S10_G2_state_machine.json`
  - `S10_G3_guardian_contract.json`
  - `S10_G4_mechanical_engine.json`
  - `S10_G5_e2e_domain_A.json`
  - `S10_G6_e2e_domain_B.json`
  - `S10_G7_audit_and_future.json`
  - `S10_G8_go_no_go.json`

- `out/evidence/`
  - `S10_G0/…`
  - `S10_G1/…`
  - `S10_G2/…`
  - `S10_G3/…`
  - `S10_G4/…`
  - `S10_G5/…`
  - `S10_G6/…`
  - `S10_G7/…`
  - `S10_G8/…`

O Cap. 4 vai especificar como esses scorecards são preenchidos e quais comandos os produzem.

---

## 4) Contratos estruturais da S10

### 4.1 Contrato de dados — Truth-DB

A Truth-DB é o **contrato de dados canônico** da S10. Em termos estruturais:

- Toda informação consolidável na S10 deve ser representável como combinação de:
  - `BlocoTema` — agrupador lógico (tema, assunto, caso, processo);
  - `FatoRegistravel` — fato principal que pode ser rastreado e versionado;
  - `Complemento` — elementos adicionais (documentos, trechos, evidências textuais) vinculados ao fato/bloco;
  - `VersaoFato` — “fotografia” de um fato em um momento (conteúdo, contexto, referências);
  - `EstadoFato` — estado atual dentro da máquina de estados.
- Invariantes de alto nível (expressos em `models.py` + `invariants.py`):
  - nenhum `FatoRegistravel` sem `BlocoTema` associado;
  - nenhuma `VersaoFato` órfã (sempre ligada a um `FatoRegistravel`);
  - estados sempre pertencem ao conjunto permitido da máquina de estados;
  - chaves primárias/estrangeiras consistentes e não nulas onde obrigatório.

Esse contrato de dados é a base do G1 (modelo consistente) e da parte estrutural de G7 (auditar/exportar).

### 4.2 Contrato de estados — Máquina de estados de fatos

A máquina de estados define **quais estados um fato pode assumir** e **quais transições são permitidas**, independentemente de implementação:

- Estados típicos (exemplo estrutural): `planejado`, `confirmado`, `concluido`, `nao_confirmado`, `adiado`, `cancelado`, `incerto` (o conjunto final está no Cap. 1/2 e em `state_machine.py`).
- O contrato exige que:
  - exista uma lista explícita de estados permitidos em `state_machine.py` e/ou `s10_state_machine.yml`;
  - exista uma representação clara das transições válidas/proibidas (ex.: matriz origem→destino ou lista de pares permitidos);
  - todas as mudanças de estado de um `FatoRegistravel` passem por essa definição (direta ou indiretamente via engine).

Esse contrato é a base estrutural do G2 (máquina de estados) e influencia a engine (G4) e pipelines (G5/G6).

### 4.3 Contrato de ações — Guardião de Blocos

O Guardião de Blocos interage com o sistema **exclusivamente** via um conjunto pequeno e estável de ações, definidas em:

- `docs/sprint_10_contrato_acoes_guardiao.md` (texto humano);
- `schema/s10_guardian_actions.schema.json` (schemas JSON);
- `inspectah/truthdb/actions_contract.py` (tipos e funções de validação).

Em termos estruturais, o contrato exige:

- um conjunto finito e explícito de ações, com nomes estáveis (exemplos):
  - `criar_bloco_tema`;
  - `criar_fato_registravel`;
  - `anexar_complemento`;
  - `criar_versao_fato`;
  - `atualizar_estado_fato`;
  - `promover_complemento_a_fato` (se utilizada);
- para cada ação:
  - campos obrigatórios definidos (IDs, payload, metadados mínimos);
  - relação clara com o modelo da Truth-DB (quais entidades afeta);
  - vínculo com a máquina de estados, quando aplicável (ex.: mudança de estado);
- nenhuma ação “fantasma”: tudo que o código/engine reconhece como ação deve estar definido no contrato textual e no schema.

Esse contrato é o núcleo estrutural de G3 (contrato de ações) e um dos pilares de G4 (engine).

### 4.4 Contrato de integração — Pipelines de domínio ↔ Truth-DB & Guardião

Os pipelines de domínio (A e B) não podem falar “qualquer coisa” com a Truth-DB; eles seguem um contrato claro:

- Entrada de pipeline: eventos de domínio (ex.: dados de obras, dados de preços) em formatos próprios de ingestão (vindos da S9 ou equivalentes).  
- Saída estrutural de pipeline:
  - criação/atualização de `BlocoTema` e `FatoRegistravel` via ações do Guardião;
  - anexação de `Complemento` e criação de `VersaoFato` segundo o contrato de ações;
  - atualização do `EstadoFato` apenas via ações e máquina de estados.
- Nenhum pipeline escreve diretamente na Truth-DB “por fora” da engine e do contrato de ações (isso é parte da invariância estrutural da arquitetura).

Esse contrato sustenta G5 e G6 em nível estrutural.

### 4.5 Contrato de exports — Truth-DB → S11/S12

Exports definem como a Truth-DB se apresenta para o “mundo externo” da S10 (pelo menos S11 e S12):

- `inspectah/truthdb/exports.py` define estruturas padrão de export para:
  - blocos (incluindo metadados essenciais);
  - fatos (incluindo versões, estados e vínculos a blocos/complementos);
  - linhas do tempo (sequência de eventos/ações/estados);
- `config/s10_exports.yml` define quais campos mínimos **devem** aparecer em qualquer export “oficial” voltado a S11/S12:
  - IDs estáveis;
  - hashes/referências imutáveis relevantes;
  - referências mínimas a evidências;
  - marcação do domínio e do tipo de fato.

Esse contrato dá base estrutural ao G7 (auditabilidade/futuro) e garante que S11/S12 não precisem “adivinhar” formato.

---

## 5) Mapa gate → artefatos estruturais

Esta tabela amarra, **sem falar de execução**, os gates do Cap. 2 aos artefatos estruturais deste capítulo.

| Gate | Foco (Cap. 2)                       | Artefatos estruturais principais                                                      |
|------|-------------------------------------|----------------------------------------------------------------------------------------|
| G0   | Sanidade de ambiente/repo/DNA      | estrutura de `docs/` (Cap.1–4, contrato de ações), layout de `out/`, configs básicas |
| G1   | Modelo de dados — Truth-DB         | `truthdb/models.py`, `migrations/XXXX_s10_truthdb_core.py`, invariantes de dados      |
| G2   | Máquina de estados de fatos        | `truthdb/state_machine.py`, `config/s10_state_machine.yml`, `sprint_10_state_machine.md` |
| G3   | Contrato de ações do Guardião      | `sprint_10_contrato_acoes_guardiao.md`, `schema/s10_guardian_actions.schema.json`, `actions_contract.py` |
| G4   | Engine mecânica de validação       | `truthdb/engine.py`, `truthdb/invariants.py`, uso centralizado do contrato de ações   |
| G5   | E2E — Domínio A                    | `pipelines/s10_domain_a_obras.py`, `config/s10_truthdb_domains.yml`, Truth-DB core   |
| G6   | E2E — Domínio B                    | `pipelines/s10_domain_b_precos.py`, `config/s10_truthdb_domains.yml`, Truth-DB core  |
| G7   | Auditabilidade & futuro (S11/S12)  | `truthdb/exports.py`, `config/s10_exports.yml`, estrutura de `scripts/truthdb_inspect.py` |
| G8   | GO/NO-GO da Sprint 10              | `out/scorecards/S10_G*.json` (estrutura), `sprint_10_summary.md`                      |

O Cap. 4 vai dizer **como** cada gate é verificado usando esses artefatos (scripts, testes, comandos de CI). Aqui o compromisso é estrutural: se um gate existe no Cap. 2, seus artefatos canônicos estão mapeados no Cap. 3.

---

## 6) Papel deste capítulo para o Codex e para futuras sprints

Para o agente Codex (engenheiro) e para qualquer humano desenvolvendo a S10, este Cap. 3 funciona como:

- **mapa estático**: quais módulos, arquivos e diretórios são considerados “oficiais” para Truth-DB & Guardião;  
- **contrato de fronteiras**: o que pode e o que não pode ser feito diretamente contra a Truth-DB (sempre via engine/ações);  
- **contrato de formato**: como ações, estados e exports são representados em código, configs e schemas;  
- **ponte com os gates**: mostra quais artefatos cada gate depende para existir.

Qualquer mudança estrutural relevante (mexer em nomes de entidades, estados, ações, exports) deve ser refletida aqui e, se afetar gates ou SLOs, acompanhada de ADR e atualização do Cap. 2.

---

## 7) Relação com Capítulos 1, 2 e 4

- **Cap. 1 — Visão**  
  Define o *porquê* e o *o quê* da Truth-DB & Guardião de Blocos.

- **Cap. 2 — Gates, SLIs/SLOs**  
  Define *como a S10 será julgada* (gates, SLIs/SLOs, DoD, GO/NO-GO).

- **Cap. 3 — Arquitetura, Filemap e Contratos Estruturais (este)**  
  Define *onde* cada conceito vive no repo e *quais contratos estáveis* ligam dados, estados, ações, pipelines e exports.

- **Cap. 4 — Execução e Automação (a ser escrito)**  
  Vai definir *como* tudo isso é executado na prática: scripts, comandos, runbook, integração com Codex e CI, lógica de preenchimento de scorecards e evidências.

Com essa divisão, a S10 fica limpa: Cap. 3 cuida do esqueleto e dos contratos estruturais; Cap. 4 cuida do movimento (execução) — sem misturar responsabilidades.

