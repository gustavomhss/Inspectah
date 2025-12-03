# Inspectah — Sprint 27 (S27)
## Capítulo 2 — Bloco 4
### Gate G5 & Gate G6 — Documentação, Runbooks, ORR & Bundle de Evidências

> Arquivo-alvo no repo: `docs/s27_cap_2_4_g5_g6_orr_e_docs.md`
>
> Função: especificar em nível operacional os gates **G5 (documentação & runbooks)** e **G6 (ORR & bundle de evidências)** da S27. Este bloco fecha o sistema de verificação da sprint e define como o Épico E26 é declarado encerrado do ponto de vista de UI/Admin.

---

## 1. Gate G5 — Documentação & Runbooks de Operação

### 1.1 Objetivo refinado

G5 garante que a consolidação do Admin v1 em Fontes, Ingestão e Debunker não fica apenas no código: ela é refletida em **documentação operável**.

Ele responde:

1) Existem guias e runbooks atualizados para todos os consoles admin críticos (Fontes, Ingestão, Debunker) sob Admin v1?  
2) Esses documentos usam um **idioma comum** de componentes, ações e estados (mesmo vocabulário, mesmas referências visuais)?  
3) Esses runbooks foram efetivamente usados em ORR/simulações, ou só existem como arquivo morto?

### 1.2 Escopo exato

G5 cobre, no mínimo, os seguintes artefatos:

1) **Guia de Consoles Admin v1.1**  
   - Arquivo base sugerido: `docs/guia_consoles_admin_v1_1.md` (nome exato pode variar, mas deve ser único e referenciado em Cap.3/Cap.5).  
   - Conteúdo: princípios, padrões, anti-padrões e exemplos concretos de Fontes, Ingestão e Debunker.

2) **Runbooks de operação**  
   - `docs/runbook_operacao_fontes_vX.md`  
   - `docs/runbook_operacao_ingestao_vX.md`  
   - `docs/runbook_operacao_debunker_vX.md`

3) **Referências cruzadas**  
   - Cap.1, Cap.3 e Cap.5 da S27 devem apontar explicitamente para esses docs.  
   - O ORR (Cap.5) deve registrar o uso de runbooks durante as simulações.

### 1.3 Estrutura mínima esperada dos runbooks

Cada runbook deve, no mínimo, ter seções para:

- Objetivo do console (o que ele governa).  
- Personas principais (quem usa).  
- Fluxos críticos de operação (passo a passo, com referências de UI).  
- Tratamento de incidentes típicos ("se X acontecer, faça Y").  
- Tabela de estados importantes e o que significam na tela (cores, ícones, labels).  
- Referências a outros consoles (como chegar a Ingestão a partir de Fontes, etc.).

G5 não exige perfeição literária, mas exige **completude mínima e aderência à realidade**.

### 1.4 Script de gate sugerido

- Script: `bin/s27_g5_docs_runbooks.sh`

Responsabilidades sugeridas:

1) Verificar presença dos arquivos obrigatórios (guia + runbooks).  
2) Opcionalmente, checar estrutura mínima dos runbooks (por regex simples, headings obrigatórios).  
3) Gerar scorecard e logs.

### 1.5 Modelo de scorecard G5

Arquivo: `out/scorecards/S27_G5_docs_runbooks.json`

Estrutura sugerida:

```json
{
  "guides_present": true,
  "runbook_fontes_present": true,
  "runbook_ingestao_present": true,
  "runbook_debunker_present": true,
  "runbooks_min_structure_ok": true,
  "runbooks_reviewed_in_orr": true,
  "notes": "observações sobre gaps de docs, melhorias sugeridas, etc."
}
```

### 1.6 Evidências de G5

- Diretório: `out/evidence/S27_G5_docs_runbooks/`
  - `presence_check.log` — resultado da verificação de arquivos;  
  - `structure_check.log` — saída da checagem de headings;  
  - opcionalmente, link ou referência à ata de ORR destacando uso dos runbooks.

### 1.7 Critérios de GO/NO-GO para G5

- **GO**:  
  - todos os runbooks e o guia v1.1 existem,  
  - `runbooks_min_structure_ok == true`,  
  - `runbooks_reviewed_in_orr == true` (houve pelo menos uma rodada real de uso/teste).

- **GO com ressalvas**:  
  - runbooks presentes, mas algumas melhorias de estrutura apontadas;  
  - desde que registradas em Cap.6 como dívidas de documentação.

- **NO-GO**:  
  - ausência de qualquer runbook crítico ou do guia;  
  - runbooks desatualizados a ponto de não refletirem a UI/Admin pós-S27.

G5 é o gate que traduz código em **capacidade operacional real**.

---

## 2. Gate G6 — ORR & Bundle de Evidências da S27

### 2.1 Objetivo refinado

G6 é o gate de **síntese e decisão**.

Ele responde:

1) Dado tudo o que os gates G0–G5 mostram, a S27 pode ser considerada **GO** para merge e uso?  
2) O Épico E26 pode ser declarado **encerrado** do ponto de vista de UI/Admin (Admin v1 em Fontes, Ingestão, Debunker)?  
3) O bundle de evidências da S27 está completo, organizado e reprodutível?

### 2.2 Escopo exato

G6 cobre:

- Consolidação de scorecards G0–G5.  
- Execução de uma ou mais rodadas de ORR local/remoto, com participação de owners de Admin/Fontes/Ingestão/Debunker.  
- Geração de:
  - scorecard de ORR (S27_G6),  
  - documento de ORR (Cap.5 da S27),  
  - bundle de evidências `.zip` com artefatos da sprint.

### 2.3 Estrutura mínima do ORR da S27

O ORR da S27 deve conter, no mínimo:

- Lista de participantes e papéis (Admin lead, Ingestão, Debunker, Ops).  
- Resumo dos resultados de G0–G5 (com links para scorecards).  
- Execução de cenários E2E-chave (por exemplo, fluxo Fontes → Ingestão → Debunker).  
- Lista de riscos remanescentes, classificados por severidade.  
- Decisão final (GO | NO_GO | GO_WITH_RISKS) e condições associadas.

### 2.4 Script de gate sugerido

- Script: `bin/s27_g6_orr_bundle.sh`

Responsabilidades sugeridas:

1) Verificar a presença de todos os scorecards G0–G5 em `out/scorecards/`.  
2) Verificar a presença do documento de ORR da S27 (Cap.5), ex.: `docs/s27_cap_5_orr_local_summary.md`.  
3) Opcionalmente, verificar consistência básica do scorecard G6 (se já existir).  
4) Gerar/atualizar o bundle de evidências:  
   - `out/bundles/inspectah_s27_evidence_bundle.zip`,  
   - contendo:  
     - `out/scorecards/S27_*.json`,  
     - `out/evidence/S27_G*/**/*`,  
     - subset relevante de docs (`docs/s27_cap_*.md`, guia v1.1, runbooks).
5) Gerar scorecard G6.

### 2.5 Modelo de scorecard G6

Arquivo: `out/scorecards/S27_G6_orr_summary.json`

Estrutura sugerida:

```json
{
  "overall_status": "GO",
  "gates_failed": [],
  "gates_with_ressalvas": [],
  "major_risks": [],
  "bundle_created": true,
  "bundle_path": "out/bundles/inspectah_s27_evidence_bundle.zip",
  "notes": "comentários sobre condições de GO, follow-ups obrigatórios, etc."
}
```

- `overall_status` ∈ {"GO", "NO_GO", "GO_WITH_RISKS"}.  
- `gates_failed` lista gates G0–G5 que não atingiram critério de GO.  
- `gates_with_ressalvas` lista gates com GO parcial/condicional.  
- `major_risks` descreve riscos relevantes para operação/roadmap.

### 2.6 Critérios de GO/NO-GO para G6

- **GO**:  
  - `overall_status == "GO"`,  
  - nenhum gate crítico (G1, G2, G3, G5) em `gates_failed`,  
  - `bundle_created == true` com `bundle_path` válido.

- **GO_WITH_RISKS**:  
  - `overall_status == "GO_WITH_RISKS"`,  
  - riscos destacados em `major_risks` e refletidos em Cap.6 (dívidas/roadmap).  
  - Aceitável somente se todos os participantes do ORR concordarem explicitamente.

- **NO-GO**:  
  - `overall_status == "NO_GO"`,  
  - ou qualquer gate crítico falhando sem plano aceitável.

G6 é o último filtro antes de declarar E26 encerrado em UI/Admin.

---

## 3. Como G5 & G6 fecham o ciclo da S27

- G5 garante que o conhecimento de como operar os consoles admin pós-S27 está registrado e usável.  
- G6 garante que há um julgamento deliberado, baseado em evidências, sobre a qualidade da sprint e o encerramento do Épico E26.

Do ponto de vista de ciclo completo:

1) Cap.1 define o problema e os estados-alvo.  
2) Cap.2 (com os quatro blocos) traduz isso em gates, métricas e ORR.  
3) Cap.3 liga gates e estados a arquivos, módulos e rotas reais (filemap/arquitetura).  
4) Cap.4 vira plano de execução (tasks S27-T-XXX) ancorado em gates.  
5) Cap.5 documenta o ORR (G6).  
6) Cap.6 registra o que restou: learnings, dívidas e ajustes de roadmap.

G5 e G6 são, portanto, os gates que **fecham a porta**: se eles não passarem, a S27 não está pronta e E26 não está concluído.

