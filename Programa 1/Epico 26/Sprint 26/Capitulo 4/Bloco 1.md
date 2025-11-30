# Inspectah — Sprint 26 (S26)
## Capítulo 4 — Bloco 4.1
### Plano de Waves da Sprint 26

> Arquivo-alvo no repo: `docs/s26_cap_4_1_plano_de_waves.md`
>
> Função: definir **como a S26 será executada no tempo**, em waves W0–W3, ligando cada wave a objetivos claros, critérios de saída e gates S26 (G0–G6). Este plano é a espinha dorsal que orienta a Execution Matrix (Bloco 4.2), o Protocolo Codex (Bloco 4.3) e o Plano de Tasks (Bloco 4.4).

A S26 é a sprint que inaugura o **Design System Inspectah Admin v1** e consolida o **Console de Fontes v2** como primeiro cliente real desse design system. Em termos operacionais, isso exige organização em waves bem delimitadas:

- **W0 — Grounding & Sanidade**  
- **W1 — Fundação de Design System & Filemap**  
- **W2 — Console de Fontes v2 & Contratos de Fontes**  
- **W3 — Hardening, UX mínima & Evidências finais**

Cada wave abaixo é descrita com:

- objetivo em linguagem de verdade (coerente com Cap.1 e Cap.2);
- escopo típico para o Codex e para humanos;
- critérios de saída objetivos (o que precisa ser verdade para fechar a wave);
- gates S26 diretamente impactados.

---

## W0 — Grounding & Sanidade

### W0.1 Objetivo

Garantir que **ninguém está executando S26 no escuro**:

- Codex e humanos entendem o **contrato da S26** (Cap.1), os **gates e DoD** (Cap.2) e a **arquitetura/filemap** (Cap.3);
- o repositório local e o ambiente básico estão em estado utilizável para começar a mexer em Design System e Console de Fontes.

Formulação em linguagem de verdade:

> "Ao final da W0, é verdade que o time (Codex + humanos) tem um resumo sólido e coerente de S26 (Cap.1–3) e que o gate G0 pode ser rodado com previsibilidade sobre o estado atual do repo, sem surpresas grosseiras."

### W0.2 Escopo típico

- Leitura estruturada (por Codex) de:
  - Cap.1 da S26 (contexto, problema, states-of-truth);
  - Cap.2 (gates G0–G6, scorecards, mapa de evidências);
  - Cap.3 (arquitetura geral, filemap de `ui/admin` e `features/sources`, invariantes);
  - este Bloco 4.1 (plano de waves) como lente de execução.
- Inspeções não destrutivas no repo local:
  - `git status`, `ls` em pastas-chave (`frontend/inspectah-ui/src/ui/admin/`, `frontend/inspectah-ui/src/features/sources/`, `app/sources/`, `out/`, `bin/`);
  - leitura de scripts de gates S26 (`bin/s26_g0_*.sh`, `bin/s26_g1_*.sh`, etc.) se já existirem.
- Execução opcional e controlada de sanidade mínima (sem alterar arquivos):
  - smoke de `bin/ci_local.sh`, se aplicável;
  - dry-run ou execução de G0, se já implementado e estável.

### W0.3 Critérios de saída

W0 é considerada concluída quando **todas** as condições abaixo forem verdadeiras:

1. Existe um **resumo estruturado de S26**, produzido e salvo (ex.: em `docs/s26_cap_0_notas_de_grounding.md` ou similar), contendo:
   - objetivos principais da S26 (ligados aos states-of-truth do Cap.1);
   - lista de gates ativos (G0–G6) e seu papel (Cap.2.1/2.2);
   - visão da arquitetura lógica (Design System Admin v1, Console de Fontes v2, APIs de fontes) e filemap relevante (Cap.3.1–3.3);
   - visão das waves W0–W3 deste Bloco 4.1.
2. O estado atual do repo foi inspecionado e **não há surpresas estruturais** que impeçam a execução das próximas waves (quebras graves de layout de pastas, scripts inexistentes que deveriam existir, etc.).
3. Há uma decisão explícita registrada sobre o momento de rodar G0 ("G0 já pode rodar" ou "G0 só roda após tasks X de W1").

### W0.4 Gates relacionados

- **Principal:** G0 — Scope & Baseline.  
- **Indiretos:** nenhum outro gate precisa estar green ao final de W0; a wave é de entendimento e radiografia.

---

## W1 — Fundação de Design System & Filemap

### W1.1 Objetivo

Materializar a **fundação de código** para o Design System Inspectah Admin v1 e para o Console de Fontes v2, alinhando o filemap real ao desenho do Cap.3, **sem ainda exigir UX final**.

Formulação em linguagem de verdade:

> "Ao final da W1, é verdade que o Design System Admin v1 existe como árvore de código coerente (`ui/admin`), que a feature `features/sources` está esqueletrada para o Console de Fontes v2 e que G0 consegue validar essa estrutura mínima sem colapsar."

### W1.2 Escopo típico

- Criar/ajustar filemap do Design System Admin v1 conforme Cap.3.2:
  - `frontend/inspectah-ui/src/ui/admin/tokens/`;
  - `frontend/inspectah-ui/src/ui/admin/layout/`;
  - `frontend/inspectah-ui/src/ui/admin/components/`;
  - `frontend/inspectah-ui/src/ui/admin/hooks/` (se usado);
  - `frontend/inspectah-ui/src/ui/admin/index.ts`.
- Criar/ajustar filemap base do Console de Fontes v2 conforme Cap.3.3:
  - `frontend/inspectah-ui/src/features/sources/pages/`;
  - `frontend/inspectah-ui/src/features/sources/components/`;
  - `frontend/inspectah-ui/src/features/sources/api/sourcesApi.ts`;
  - `frontend/inspectah-ui/src/features/sources/types/Source.ts`;
  - `frontend/inspectah-ui/src/features/sources/index.ts`.
- Ajustar scripts mínimos de gates para enxergar a nova estrutura:
  - G0 passa a checar a existência de `ui/admin` e `features/sources`;
  - G1 se prepara para validar `ui/admin` (mesmo que com implementação parcial);
  - G3 é ajustado, se necessário, para rodar lint/build com novo filemap.

### W1.3 Critérios de saída

W1 é concluída quando:

1. O filemap previsto em Cap.3.2 (Design System Admin v1) e Cap.3.3 (Console de Fontes v2) está **materializado** no repo (pastas e arquivos-chave existem, mesmo que alguns estejam em modo "skeleton").
2. G0 roda com sucesso sobre essa nova estrutura (ou falha apenas em pontos esperados, claramente registrados como pendências específicas de W2/W3).
3. G1 e G3 conseguem ao menos executar até o fim, mesmo que reportem falhas de implementação que serão resolvidas nas waves seguintes.

### W1.4 Gates relacionados

- **Diretos:**
  - G0 — Scope & Baseline (agora validando filemap novo);
  - G1 — Design System Admin v1 (Static Integrity) — ainda em modo parcial, mas com scripts conectados à árvore `ui/admin`;
  - G3 — Front-End Quality & Regression (capaz de rodar com a nova estrutura).

- **Indiretos:**
  - G2 e G4 não precisam estar verdes, mas dependem da estrutura criada aqui.

---

## W2 — Console de Fontes v2 & Contratos de Fontes

### W2.1 Objetivo

Entregar o **núcleo funcional do Console de Fontes v2**, usando o Design System Admin v1, e garantir que os **contratos de API de fontes** estão alinhados com o que a UI espera.

Formulação em linguagem de verdade:

> "Ao final da W2, é verdade que um operador consegue, via Console de Fontes v2, listar, criar, editar e alterar o estado de fontes (ativar/desativar/arquivar) em cima do Design System Admin v1, e que os testes de API de fontes confirmam a coerência entre UI e backend (G2 e G4 verdes)."

### W2.2 Escopo típico

- Implementar fluxos principais do Console de Fontes v2:
  - `SourcesListPage` com tabela de fontes, filtros básicos e ações principais;
  - `SourceEditPage` com `SourceForm` (criação/edição) baseado em componentes de `@/ui/admin`;
  - uso de `SourceStatusBadge` e badges de status do design system.
- Implementar chamadas reais em `sourcesApi.ts` para as rotas de backend de fontes:
  - listar, obter por id, criar, atualizar;
  - ativar, desativar, arquivar.
- Ajustar e/ou criar rotas e testes de API de fontes no backend:
  - `app/sources/routes.py` (ou equivalente);
  - `tests/api/test_sources_console.py` cobrindo caminho feliz dos fluxos.
- Criar/ajustar testes automatizados ligados a G2 (fluxos do console) e G4 (contratos de API).

### W2.3 Critérios de saída

W2 é concluída quando:

1. Um operador interno consegue, em ambiente de desenvolvimento, executar **pelo menos** os fluxos básicos de fontes:
   - listar fontes;
   - criar uma fonte válida;
   - editar uma fonte existente;
   - ativar, desativar e arquivar conforme regras do domínio.
2. O gate **G2 — Console de Fontes v2 (Fluxos Básicos)** está **GREEN** (todos os testes de fluxos básicos passam).
3. O gate **G4 — API & Modelo de Dados de Fontes (Contratos)** está **GREEN** (testes de API específicos de fontes passando, sem violação de contrato).
4. G1 e G3 não possuem falhas bloqueantes relacionadas à S26 (eventuais pendências menores podem ser empurradas para W3, desde que registradas).

### W2.4 Gates relacionados

- **Diretos:**
  - G2 — Console de Fontes v2 (Fluxos Básicos);
  - G4 — API & Modelo de Dados de Fontes (Contratos).

- **Indiretos:**
  - G1 — integridade do Design System, usado intensamente pelo console;
  - G3 — saúde geral do frontend (lint/test/build com o console e o design system ativos).

---

## W3 — Hardening, UX mínima & Evidências finais

### W3.1 Objetivo

Refinar a experiência do Console de Fontes v2 em nível mínimo aceitável para uso interno, **endurecer** a solução técnica entregue em W1–W2 e fechar a sprint com documentação e evidências em ordem.

Formulação em linguagem de verdade:

> "Ao final da W3, é verdade que o Console de Fontes v2 é utilizável em contexto realista interno, que o Design System Admin v1 se comporta de forma estável sob uso real, e que todos os gates G0–G6 da S26 estão verdes, com bundle de evidências gerado e docs/runbooks publicados."

### W3.2 Escopo típico

- Ajustes de UX no Console de Fontes v2:
  - mensagens de erro e estados vazios mais claros;
  - feedback visual consistente (loading, desabilitado, sucesso, erro);
  - pequenas melhorias de usabilidade (ordenação padrão, persistência leve de filtros, etc. se couber no escopo).
- Hardening técnico:
  - tratar bordas óbvias detectadas em testes e uso interno (ex.: respostas vazias, timeouts razoáveis, erros intermitentes);
  - limpar warnings triviais de lint/build ligados à S26;
  - garantir que o design system não quebre em casos simples de composição.
- Documentação & evidências:
  - finalizar guia do Design System Admin v1;
  - finalizar runbook de operação de fontes;
  - garantir que todas as pastas `out/evidence/S26_G*/` estejam preenchidas;
  - gerar o bundle `inspectah_s26_evidence_bundle.zip`.

### W3.3 Critérios de saída

W3 é concluída quando:

1. Os gates **G0–G6** estão **GREEN**, respeitando thresholds definidos no Cap.2 (sem edições manuais de scorecards).
2. Existe documentação utilizável para:
   - uso do Design System Admin v1;
   - operação do Console de Fontes v2 (runbook de fontes).
3. O bundle de evidências da S26 foi gerado e registrado (incluindo scorecards, logs principais e hash do arquivo).
4. Débitos que não cabem em W3 estão **explicitamente registrados** em Cap.6 como tech_debt/gaps com sugestão de encaixe em sprints futuras.

### W3.4 Gates relacionados

- **Diretos:**
  - G3 — Front-End Quality & Regression;
  - G5 — Documentação & Runbooks S26;
  - G6 — Evidence & ORR Bundle S26.

- **Indiretos:**
  - G1, G2, G4 — devem permanecer verdes após ajustes de UX/hardening.

---

## 6. Relação do Bloco 4.1 com os Blocos 4.2, 4.3 e 4.4

- O **Bloco 4.2 — Execution Matrix** vai pegar W0–W3 e transformá-las em uma matriz de execução: para cada wave, quais categorias de trabalho (frontend, backend, tests, docs, gates), quais comandos/scripts são permitidos e quais paths são tocados.
- O **Bloco 4.3 — Protocolo Codex** vai traduzir estas waves em **prompts e guardrails** para o agente Codex executar tasks sem sair do trilho (ordem de waves, limites de edição, quando rodar quais gates, como registrar evidências).
- O **Bloco 4.4 — Plano Operacional & Tasks** vai quebrar W0–W3 em tasks `S26-T-XXX` com:
  - wave associada;
  - categoria;
  - descrição com verbo no início;
  - artefatos esperados (paths do Cap.3);
  - gates e states-of-truth associados;
  - condição de done e evidências.

Este Bloco 4.1 é, portanto, o **mapa de cadência oficial** da S26. Se na execução real o time precisar desviar (por exemplo, misturar tarefas de W1 e W2), essa decisão deve ser registrada em Cap.6 como exceção consciente, nunca como improviso silencioso.