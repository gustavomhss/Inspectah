# Sprint 29 — Capítulo 5
## Bloco 2 — Estrutura detalhada do documento de ORR da S29 (`docs/sprint_29_orr_summary.md`)

Este Bloco 2 especifica, em nível de contrato, como deve ser o documento de ORR da Sprint 29:

- localização canônica: `docs/sprint_29_orr_summary.md`;
- estrutura de seções e subseções;
- tipo de conteúdo esperado em cada parte (técnico e de produto);
- forma de referenciar gates, scorecards e evidências;
- padrão de escrita para facilitar leitura futura e comparação com ORRs de outras sprints.

A ideia é que qualquer pessoa consiga abrir `sprint_29_orr_summary.md` e, sem ler mais nada, entenda o que a S29 fez com o Inspectah e em que estado ela deixou o sistema.

---

### 1. Localização, formato e tom do ORR

**Arquivo:**

- `docs/sprint_29_orr_summary.md`

**Formato:**

- Markdown simples, compatível com renderização em qualquer viewer (GitHub, VS Code, etc.);
- sem dependência de imagens externas para compreensão (prints podem ser citados, mas não são obrigatórios);
- tabelas em Markdown para listas comparativas (gates, escopo planejado vs entregue, etc.).

**Tom:**

- objetivo, conciso e livre de jargão desnecessário;
- texto voltado tanto para engenharia quanto para produto (PM, stakeholders);
- evitar linguagem de commit ("ajustado X", "refatorado Y"), preferindo linguagem de efeito ("agora é possível", "passa a existir").

---

### 2. Seção 1 — Resumo executivo

Título sugerido:

- `## 1. Resumo executivo`

Conteúdo esperado:

- 3–6 parágrafos curtos respondendo:
  - o que a S29 colocou em pé em uma frase simples;  
  - quem se beneficia diretamente (operadores admin, pipeline de ingestão, camada de verdade, etc.);  
  - qual o escopo de uso recomendado (domínios piloto, ambiente de teste/staging/produção controlada);  
  - quais são as principais limitações ainda presentes.

Exemplo de perguntas que o texto deve responder explicitamente:

- "Qual é a novidade principal da S29 para o Inspectah?"  
- "Onde essa novidade já está sendo usada ou pode ser usada imediatamente?"  
- "Existe alguma recomendação de uso cauteloso ou gradual?"  

Formato sugerido:

- parágrafos corridos, sem listas, para leitura fluida;
- menção a termos chave como "fluxo de agentes configurável", "domínio piloto", "UI de admin".

---

### 3. Seção 2 — Escopo planejado vs escopo entregue

Título sugerido:

- `## 2. Escopo planejado vs escopo entregue`

Objetivo:

- tornar explícita a diferença entre o que foi planejado no Capítulo 1 e o que foi efetivamente entregue ao final da sprint;
- registrar cortes de escopo, adiamentos e ajustes, com justificativas sucintas.

Formato sugerido:

- tabela em Markdown com colunas, por exemplo:

  - `Item de escopo` — descrição concisa do item planejado (copiado/derivado do Cap. 1);
  - `Planejado` — status/descrição do que se queria alcançar;
  - `Entregue na S29` — o que realmente foi feito, em termos concretos;
  - `Status` — `COMPLETO`, `PARCIAL`, `NÃO ENTREGUE`;
  - `Observações` — justificativas, dependências, empurrão para E28.2/E28.3.

Critérios de preenchimento:

- todos os itens de escopo relevantes do Cap. 1 devem aparecer na tabela;  
- "PARCIAL" só deve ser usado quando há algo concreto entregue, mas insuficiente para chamar de completo;  
- itens "NÃO ENTREGUE" devem indicar, idealmente, para qual sprint futura são recomendados (ex.: "candidato forte para E28.2").

---

### 4. Seção 3 — Estado dos gates S29_G0–S29_G5

Título sugerido:

- `## 3. Estado dos gates e scorecards`

Objetivo:

- dar uma visão compacta do estado de todos os gates da S29, com referência clara aos scorecards e qualquer exceção.

Formato sugerido:

- tabela em Markdown com colunas:

  - `Gate` — ex.: `S29_G0_scope_and_baseline`;  
  - `Descrição` — uma frase sobre o propósito do gate;  
  - `Status` — `PASS` ou `FAIL` (ou `N/A` se algum gate foi conscientemente desativado, o que deve ser raro e justificado);  
  - `Scorecard` — caminho local para o JSON, ex.: `out/scorecards/S29_G0_scope_and_baseline.json`;  
  - `Observações` — qualquer nota relevante (re‑execução, flutuações, ajustes de script).

Regras:

- todos os gates definidos no Cap. 2 (G0–G5) devem aparecer;
- se algum gate estiver em `FAIL`, o ORR não deve recomendar GO pleno sem uma explicação muito explícita;
- se houver reexecuções, não é necessário detalhar logs aqui, apenas mencionar que a versão final está em PASS.

---

### 5. Seção 4 — Evidências principais e bundle

Título sugerido:

- `## 4. Evidências e bundle da Sprint 29`

Objetivo:

- registrar de forma centralizada onde estão as evidências principais da sprint e como chegar ao bundle consolidado.

Conteúdo esperado:

1. Lista dos diretórios de evidência:  
   - `out/evidence/S29_G0_scope_and_baseline/`;  
   - `out/evidence/S29_G1_model_and_migrations/`;  
   - `out/evidence/S29_G2_api_and_validator/`;  
   - `out/evidence/S29_G3_ui_and_frontend_quality/`;  
   - `out/evidence/S29_G4_runtime_and_observability/`;  
   - `out/evidence/S29_G5_orr_and_bundle/`.

2. Referência ao bundle consolidado:  
   - caminho exato: `out/bundles/inspectah_s29_evidence_bundle.zip`;
   - opcional: hash (SHA256) do arquivo, para verificação de integridade.

3. Descrição textual do que o bundle contém:  
   - logs de testes de backend/frontend;  
   - logs de execução de gates;  
   - snapshots/SUMMARYs de runtime (se houver);  
   - scorecards consolidados.

A ideia é que um auditor consiga, a partir desta seção, reconstruir rapidamente o conjunto de evidências da S29.

---

### 6. Seção 5 — Impacto no produto e no Programa 1

Título sugerido:

- `## 5. Impacto no produto e no Programa 1`

Objetivo:

- explicar em termos de produto o que mudou no Inspectah após a S29;
- situar a sprint dentro do Programa 1 (por exemplo, "Programa 1 — Eixo de Fluxos de Agentes & Interpretação").

Conteúdo esperado:

- parágrafos descrevendo:
  - o que o operador admin ganha (UI de fluxo, controle por domínio, justificativa de mudança, etc.);  
  - o que o pipeline ganha (fluxos configuráveis, menos hard‑code, logs de runtime de fluxos);  
  - quais domínios estão habilitados ou recomendados como piloto após a S29;  
  - como isso se conecta com iniciativas paralelas (ingestão, debunker, Truth‑DB, etc.).

Não é necessário repetir detalhes de implementação (isso já está nos capítulos anteriores); o foco é **efeito**.

---

### 7. Seção 6 — Riscos, limitações e recomendações

Título sugerido:

- `## 6. Riscos, limitações e recomendações`

Objetivo:

- registrar o que **não** está resolvido pela S29 e o que precisa ser considerado nas próximas sprints.

Formato sugerido:

- subseções ou tabela separando:
  - `Riscos técnicos` (ex.: complexidade futura de branching, acoplamento a catálogo de papéis, etc.);  
  - `Riscos de produto/governança` (ex.: quem pode alterar fluxo, necessidade de approvals, impacto de erro humano);  
  - `Limitações atuais da v1` (ex.: sem versionamento formal, sem simulador de fluxo, domínios limitados);
  - `Recomendações` (itens candidatos a E28.2/E28.3, condições para expandir escopo além de domínios piloto).

Cada risco deve ter, idealmente:

- descrição;  
- severidade (baixa/média/alta);  
- recomendação ou próxima ação sugerida.

---

### 8. Seção 7 — Conclusão e decisão de GO/NO-GO

Título sugerido:

- `## 7. Conclusão e decisão de GO/NO-GO`

Objetivo:

- registrar a decisão formal da Sprint 29 em relação ao uso do que foi entregue.

Conteúdo esperado:

- declaração explícita de GO/NO-GO, por exemplo:
  - `Recomendação: GO para uso da configuração de fluxo v1 em domínios piloto X, Y, Z.`  
  - `Recomendação: NO-GO para uso amplo em todos os domínios até que condições A, B, C sejam atendidas.`

- breve justificativa baseada:
  - no estado dos gates e scorecards;  
  - na robustez percebida da solução;  
  - nos riscos e limitações mapeados.

- se aplicável, lista de "pré-condições" para considerar GO ampliado em sprints futuras.

---

### 9. Amarração do Bloco 2

Este Bloco 2 define o contrato de estrutura e conteúdo do documento de ORR da Sprint 29. Em resumo:

- `docs/sprint_29_orr_summary.md` passa a ter uma anatomia clara, com seções fixas de Resumo, Escopo, Gates, Evidências, Impacto, Riscos e Conclusão;  
- cada seção tem um propósito específico e conteúdo mínimo esperado;  
- o ORR deixa de ser um texto ad hoc e passa a ser uma peça padronizada dentro do Programa 1.

Nos blocos seguintes do Capítulo 5, essa estrutura é alimentada com o conteúdo de produto (estado pós-S29), a integração com o Épico E28 e as recomendações formais que amarram S29 às próximas sprints.

