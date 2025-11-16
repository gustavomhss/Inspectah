# Inspectah — Sprint 4 — Capítulo 4  
**Guia Supremo v2 — Padrões, Anti‑padrões, Heurísticas e Cheatsheets (200%+)**

> Cap 1 = **Visão**. Cap 2 = **Validação (gates)**. Cap 3 = **Execução (trilhas/PRs)**.  
> Cap 4 = **Mentalidade & Disciplina**: como o Codex pensa, decide e age para manter a Sprint 4 em nível 200%+.

Este capítulo deve estar literalmente colado na parede da war room e aberto na tela do Codex enquanto ele trabalha.

---

## 0. Como ler e aplicar este capítulo

- **PO:** usa como régua de qualidade de PR. Se um PR contraria este capítulo, ele está errado, mesmo que o teste passe.  
- **Codex / Engenheiros:** usam como manual de combate diário:  
  - Seção 1 = **Cheat sheet A4** (antes de qualquer PR).  
  - Seção 2 = **DO / DON’T** (paredão de regras).  
  - Seção 3 = **Mapa Heurística → Gate → Invariante → SLO** (cola com Caps 1–3).  
  - Seção 4 = **Micro‑exemplos práticos** (como pensar em cenários típicos).  
  - Seções 5–7 = fluxo de trabalho, debug e evolução segura.

Nada neste capítulo é opcional.

---

## 1. Cheat sheet A4 — “Antes de abrir QUALQUER PR na S4”

O Codex deve conseguir responder **SIM** a tudo abaixo **antes** de criar um PR:

1. **Identidade do trabalho**  
   - Sei qual **ID do quadro mestre** (Cap 3, seção 3) estou atacando (ex.: `A2`, `B1`, `D2`).  
   - Sei qual **gate principal** esse trabalho mira (ex.: T3, T6, T7...).

2. **Ligação com invariantes e SLOs**  
   - Consigo dizer qual **invariante** do Cap 1 estou protegendo (ex.: “Nenhum Item P0 sem Evidência completa”).  
   - Sei qual **SLO**, se houver, pode ser impactado (ex.: `evidence_completeness_rate`, `explore_query_p95_ms`).

3. **Artefatos em jogo**  
   - Já listei, em rascunho, quais arquivos/pastas de:  
     - `docs/`  
     - `config/`  
     - `fixtures/`  
     - `goldens/`  
     - `out/evidence/`  
     - `out/scorecards/`  
     vão nascer ou ser alterados por este PR.

4. **Impacto nos gates**  
   - Sei exatamente **que saída de scorecard** quero ver mudando (ex.: campo novo em `S4_T3_fixtures.json`).  
   - Sei quais gates não devo quebrar (ex.: T2/T4/T5 quando mexo na ingestão).

5. **Plano de verificação**  
   - Sei qual pedaço da **ORR S4** vou rodar localmente (Cap 3, trilha/gate correspondente).  
   - Sei quais arquivos de evidência vou olhar manualmente (ex.: `report.txt`, `metrics_snapshot.json`).

6. **Anti‑gambiarra checado**  
   - Não vou “despromover” fonte P0 para fugir de gate.  
   - Não vou mexer em fixtures/goldens só para verde aparecer.  
   - Não vou brinca com thresholds de SLO sem alinhar com PO (Cap 2 e 3).

Se uma dessas respostas é “não sei ainda”, **o PR não está pronto nem para nascer**.

---

## 2. DO / DON’T — Parede de regras da Sprint 4

### 2.1 DO — Sempre faça

1. **DO ligar cada mudança a um gate**  
   - Ex.: “Este PR fortalece T3/T4 para Fonte P0 X”.

2. **DO pensar primeiro em fixtures/goldens, depois no parser**  
   - Começar de um exemplo real, não de dados inventados.

3. **DO tornar toda decisão auditável em artefatos**  
   - Se algo é importante (mudança de regra, exceção, novo caso de uso), deve aparecer em `docs/`, `fixtures/`, `goldens/` ou `out/evidence/`.

4. **DO proteger a rastreabilidade (Fonte → Run → Item → Evidência)**  
   - Toda Evidência precisa “contar a história” inteira.

5. **DO tratar métricas/logs como produto**  
   - Perguntar: “este log/métrica ajuda alguém a entender a saúde da fonte sem me ligar no Slack?”

### 2.2 DON’T — Nunca faça

1. **DON’T alterar fixture/golden sem justificativa e contexto**  
   - Isso viola a “constituição” do comportamento esperado. Se precisar, atualize relato de T4 e docs.

2. **DON’T esconder falhas com try/ignore, redirects silenciosos ou flags mágicas**  
   - Gate vermelho é sinal, não incômodo. O incômodo é o bug, não o gate.

3. **DON’T codificar configuração de fonte em código**  
   - URLs, seletores, campos de interesse: tudo no registry + Field Designer, nunca espalhado pela lógica.

4. **DON’T inventar métricas confusas ou sem contexto**  
   - Nome de métrica deve ser óbvio. Se um humano não entende em 5s, está ruim.

5. **DON’T mexer em SLO ou thresholds na surdina**  
   - Todo SLO é compromisso de produto, não ajuste oportunista.

6. **DON’T criar caminhos paralelos de validação**  
   - Se algo é importante, tem que virar parte de T0–T7 e aparecer nos scorecards.

---

## 3. Mapa Heurística → Gate → Invariante → SLO

> Esta seção “amarra” as ideias deste capítulo com os capítulos 1–3.

### 3.1 Tabela de correspondência

| Heurística-chave | Gate(s) principal(is) | Invariante afetado | SLO mais sensível |
|------------------|-----------------------|--------------------|-------------------|
| “Gates primeiro, código depois” | Todos, especialmente T3–T7 | Todos, pois evita funcionalidades sem validação | Todos (depende do gate) |
| “Config acima de código” | T2, T3, T4 | Nenhum ajuste estrutural apenas em código | onboarding_p50_min |
| “Fixtures reais como constituição” | T3, T4, T7 | Fixtures do ORR vêm de dados reais e são versionadas | evidence_completeness_rate |
| “Parsers pequenos e explícitos” | T3, T4 | Nenhum Item P0 sem Evidência completa | evidence_completeness_rate |
| “Vault idempotente” | T5 | Nenhum Item P0 sem Evidência; ausência de duplicações | evidence_completeness_rate |
| “Observabilidade como produto” | T6, T7, T8 | Nenhuma Fonte P0 ativa invisível; quebras detectadas em tempo finito | detection_latency_p95_min, run_success_rate |
| “Explore nunca mostra Item sem Evidência” | T3, T4, T6, T7 | Explore M0 nunca mostra Item sem Evidência | explore_query_p95_ms |
| “ORR como contrato social” | T7, T8 | Todos, via malha T0–T7 | Todos |

Sempre que o Codex estiver em dúvida sobre uma decisão, deve localizar sua heurística nesta tabela e olhar **que gate, invariante e SLO** estão em risco.

---

## 4. Erro típico → Gate onde estoura → SLO/Invariante → Reação recomendada

| Erro típico | Gate onde tende a explodir | Invariante/SLO ameaçado | Reação recomendada |
|------------|----------------------------|-------------------------|---------------------|
| Parser “faz tudo”, difícil de testar | T3/T4 | Nenhum Item P0 sem Evidência completa | Fatiar parser, extrair responsabilidades, reforçar fixtures/goldens |
| Fonte P0 ajustada em código, não no registry | T2/T3/T6 | Nenhum ajuste estrutural em Fonte P0 apenas em código | Migrar parâmetros para YAML, atualizar T2, revisar T3/T6 |
| Mudança de comportamento que “obriga” trocar golden | T4/T7 | Fixtures do ORR vêm de dados reais e são versionadas | Discutir com PO: é mudança de produto ou bugfix? Atualizar docs e relatórios T4 |
| Vault crescendo de forma explosiva sem motivo claro | T5 | Integridade de evidência, completude | Revisar chaves lógicas, idempotência, ajustar pipeline antes de rodar T5 novamente |
| health_matrix mostra fonte “ok” enquanto claramente está quebrada | T6/T8 | Nenhuma Fonte P0 ativa invisível em métricas/logs | Revisar geração de métricas/logs, saneamento de status, reexecutar T6 |
| explore_query_p95_ms estourando o alvo | T6/T8 | Explore M0 nunca mostra Item sem Evidência; UX de consulta | Revisar consultas típicas, índices/estratégias de acesso, ajustar cenário de teste em `explore_queries_bench` |
| ORR passa local, mas quebra em CI | T7 | Reprodutibilidade e integração | Revisar dependências de ambiente, caminhos de arquivo, suposições locais; alinhar ORR local com pipeline de CI |

O Codex deve usar esta tabela como **roteiro de investigação** sempre que aparecer um sintoma parecido.

---

## 5. Micro‑exemplos práticos (sem código, só raciocínio)

### 5.1 Exemplo 1 — Parser “ruim” vs parser “bom” na prática

- **Cenário:** Fonte P0 `noticias_html` com página de notícias em HTML.

**Abordagem ruim (mentalidade):**

- Um único fluxo que: faz request HTTP, parseia HTML inteiro, extrai todos os campos, grava direto no Vault, escreve logs e atualiza métricas.  
- Não há fixtures específicas; o dev testa na própria máquina com a página ao vivo.  
- T3/T4 dependem de “replay” complexo do fluxo inteiro.

**Abordagem boa (mentalidade):**

- O Codex primeiro captura 3–5 HTMLs reais e salva em `fixtures/sprint_4/fontes_p0/noticias_html/`.  
- Define, com o PO, quais campos são críticos (título, data, link canônico) e descreve isso no Field Designer da fonte.  
- Implementa parsing como transformação **HTML → Item normalizado**, separada de HTTP, persistência e métricas.  
- Cria goldens com a saída esperada para cada fixture.  
- T3/T4 operam diretamente nessas transformações, sem depender de rede nem do Vault real.

**Resultado:**

- Quando algo quebrar (mudança na estrutura da página), T3/T4 acusam de forma clara.  
- Ajustar o parser é questão de alinhar fixture + golden + transformações, sem mexer no resto do sistema.

---

### 5.2 Exemplo 2 — Bug de duplicação no Vault (T5)

- **Sintoma:** T5 mostra no `vault_diff.txt` centenas de novos Itens e Evidências após reprocessar as mesmas fixtures, sem justificativa.

**Raciocínio esperado do Codex:**

1. Confirmar que as fixtures usadas em T3/T4 são as mesmas usadas em T5.  
2. Verificar como o Vault identifica “unicidade”: quais campos definem que um Item/Evidência já existe.  
3. Revisar se a pipeline de ingestão está reutilizando essas chaves ou gerando IDs sempre novos.  
4. Ajustar a lógica de idempotência (por exemplo, respeitando identificadores externos + Fonte + timestamp) e reexecutar T5.  
5. Só considerar o problema resolvido quando o diff mostrar crescimento compatível com o esperado (ou zero).

**Ligação com Cap 1–3:**

- Cap 1: integridade do Vault é parte da visão de confiabilidade.  
- Cap 2: T5 protege explicitamente esse aspecto.  
- Cap 3: Trilha C (C1) descreve artefatos e critérios de aceite.

---

### 5.3 Exemplo 3 — Observabilidade enganosa (T6)

- **Sintoma:** uma Fonte P0 `precos_api` está com falhas constantes em produção interna, mas `health_matrix.json` mostra status `"ok"`.

**Raciocínio esperado do Codex:**

1. Abrir `metrics_snapshot.json` e verificar se a fonte `precos_api` aparece com contadores de falha.  
2. Conferir se a lógica que traduz métricas → status (ok/degradada/quebrada) está considerando os sinais relevantes (ex.: taxa de falha nos últimos N runs).  
3. Garantir que logs dessa fonte incluam o identificador da fonte e que erros sejam registrados de forma estruturada.  
4. Ajustar a função que monta `health_matrix.json` para refletir corretamente a situação.  
5. Reexecutar T6 e validar que agora a fonte aparece como degradada/quebrada.

**Impacto:**

- Invariante “Nenhuma Fonte P0 ativa invisível em métricas/logs” volta a ser respeitada.  
- SLOs `detection_latency_p95_min` e `run_success_rate` recuperam sua credibilidade.

---

### 5.4 Exemplo 4 — Latência de Explore alta (T6/T8)

- **Sintoma:** `explore_query_p95_ms` está acima do alvo nos resultados de `explore_queries_bench.json`.

**Raciocínio esperado do Codex:**

1. Identificar quais consultas estão sendo usadas no benchmark (típicas ou artificiais?).  
2. Validar se essas consultas correspondem a casos de uso reais (pode revisar Cap 1 e 3).  
3. Ver se há oportunidades simples: filtros redundantes, ordenações caras, falta de índices lógicos.  
4. Se mexer em estrutura de dados, atualizar modelo e docs (Cap 1/3) para refletir a mudança.  
5. Reexecutar o benchmark, atualizar `explore_queries_bench.json` e T6/T8.

**Ponto central:**

- Nunca “apertar o threshold” de SLO para mascarar lentidão. A solução é **melhorar a consulta e o armazenamento**, não afrouxar alvo.

---

## 6. Fluxo recomendado de trabalho (refinado)

1. **Escolher o bloco de trabalho (ID A1…F1)** no quadro mestre do Cap 3.  
2. **Passar pelo Cheat Sheet A4** (seção 1) e garantir que todas as respostas são SIM.  
3. **Reler as seções relevantes de Cap 1–3** (visão, gate, trilha).  
4. **Planejar artefatos** que serão tocados antes de mexer em qualquer implementação.  
5. **Aplicar os DO/DON’T** da seção 2 conscientemente (pode literalmente marcar checkboxes no PR).  
6. **Rodar o pedaço adequado da ORR** (por gate) e inspecionar evidências.  
7. **Documentar no PR**: gate, invariante, SLO, artefatos, comandos rodados, resultados.  
8. **Responder feedback com evidência**, não opinião.

---

## 7. Debug de gates vermelhos (versão 2.0)

Quando um gate falhar, o Codex deve:

1. **Localizar o gate** (T3, T4, T5, T6, T7, T8) e abrir o scorecard correspondente em `out/scorecards/`.  
2. **Ir ao diretório de evidências** (`out/evidence/S4_Tx_*`) e ler relatórios/snapshots.  
3. **Mapear o erro para a tabela da seção 4** (erro típico → gate → SLO/invariante).  
4. **Checar se o comportamento esperado não mudou** (consultar Cap 1/2). Se mudou, talvez o problema esteja no spec, não na implementação.  
5. **Atacar causa raiz** na camada certa (ingestão, Vault, observabilidade, Explore, ORR).  
6. **Atualizar docs se necessário** (modelo de dados, invariantes, SLOs, Cap 3).  
7. **Reexecutar o gate e registrar resultado** (incluindo trechos relevantes dos relatórios no PR).

---

## 8. Evolução segura da S4 (recap)

Sempre que for necessário mudar algo importante durante ou após a Sprint 4:

1. Atualizar primeiro a **visão/contrato** (Cap 1 e 2).  
2. Refletir a mudança no **plano de execução** (Cap 3).  
3. Ajustar este **Guia Supremo** se a mudança impactar padrões, heurísticas ou anti‑padrões.  
4. Só então mexer em implementação.

---

## 9. Fechamento — Padrão 200%+

Com esta versão, o Capítulo 4 deixa de ser apenas um texto inspirador e se torna:

- Um **cheat sheet operacional** (seção 1).  
- Um **painel DO/DON’T** que trava más decisões (seção 2).  
- Um **mapa formal** de heurísticas → gates → invariantes → SLOs (seções 3 e 4).  
- Um conjunto de **exemplos práticos** que mostram como pensar como “engenheiro de evidência” na S4 (seção 5).  
- Um **roteiro disciplinado** para trabalhar, debugar e evoluir sem quebrar a confiança (seções 6–8).

Cap 1, 2 e 3 definem **o que**, **como provar** e **como executar**.  
Cap 4 v2 garante que o Codex e o time **pensem certo** o tempo todo, no nível de excelência que o Inspectah exige.

