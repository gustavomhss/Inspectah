# D9 — Inspectah — Sprint 1 (Spec & Roadmap)
## Capítulo 2 — Gates de Validação, Evidências e DoD (v1.1)

> Leslie no comando: este capítulo é o "cinto de segurança" da sprint. Nada em D9 é considerado pronto só porque "parece bom" — cada entregável D9.x precisa passar por um gate explícito, com critérios objetivos, evidências guardadas e kill criteria claros.

---

## 0) Propósito do Capítulo 2

- Transformar o Capítulo 1 (contexto + objetivos + entregáveis D9.0–D9.8) em um **conjunto de gates concretos**.  
- Garantir que cada documento produzido em D9 **encaixa num gate**, com critérios de aprovação binários (aprovado/reprovado).  
- Definir para cada gate:  
  - qual entregável cobre,  
  - que perguntas ele precisa responder,  
  - quais checagens são obrigatórias,  
  - onde ficam as evidências de que o gate foi cumprido,  
  - quais são os motivos para "parar tudo" (kill criteria).  
- Criar uma estrutura que permita, no futuro, automatizar parte destes gates em scripts/ORR, mas que já funcione perfeitamente de forma manual.

### 0.1 Mapeamento mental para T0–T8

Para manter a continuidade com o restante do projeto (onde usamos T0–T8), os gates documentais da D9 se alinham mentalmente assim:

- **D9-G0** ≈ T0 documental — descoberta, leitura obrigatória, alinhamento de contexto.  
- **D9-G1** ≈ T1/T2 documental — especificação macro consistente (blueprint + overview).  
- **D9-G2–G4** ≈ T2/T3 documental — definição precisa de contratos (campos, APIs, dados, LGPD).  
- **D9-G5** ≈ T4/T5 documental — plano de execução e evolução (roadmap + playbook).  
- **D9-G6** ≈ T6/T7 documental — ponte para implementação (superprompt) preparada para ser exercitada por código.

Não vamos reaproveitar diretamente os nomes T0–T8 aqui para evitar confusão, mas a mentalidade de "gates de maturidade" é a mesma.

---

## 1) Filemap lógico da Sprint D9 (artefatos esperados)

A D9 produz um conjunto específico de documentos. Para o Capítulo 2, não importa o path exato no repositório, mas **todos os gates assumem que estes arquivos existem** com nomes estáveis (ou equivalentes claramente rastreáveis).

Sugestão de filemap lógico:

- **Capítulos da Sprint**  
  - `d9_capitulo_1_contexto_objetivos_v1_1.md`  
  - `d9_capitulo_2_gates_validacao_dod_v1_1.md`

- **Blueprint & Overview**  
  - `d9_0_inspectah_blueprint_consolidado_v1_2_x.md`  
  - `d9_1_inspectah_overview_human_friendly_v1_0.md`

- **Anexos Técnicos e Legais**  
  - `d9_2_anexo_a_field_designer_v1_0.md`  
  - `d9_3_anexo_b_explore_api_integracoes_v1_0.md`  
  - `d9_4_anexo_c_data_model_ddl_migracao_v1_0.md`  
  - `d9_5_anexo_d_lgpd_tos_envelope_risco_v1_0.md`

- **Roadmap, Superprompt e Playbook de Evolução**  
  - `d9_6_roadmap_inspectah_v0_v1_v1x_v1_0.md`  
  - `d9_7_superprompt_codex_v1_inspectah_v0_core_data_hub.md`  
  - `d9_8_miniplaybook_evolucao_inspectah_v1_0.md`

- **Evidências dos Gates**  
  - `evidence/d9_g1_blueprint_overview_checklist.md`  
  - `evidence/d9_g2_field_designer_checklist.md`  
  - `evidence/d9_g3_explore_api_integracoes_checklist.md`  
  - `evidence/d9_g4_data_model_lgpd_checklist.md`  
  - `evidence/d9_g5_roadmap_playbook_checklist.md`  
  - `evidence/d9_g6_superprompt_codex_checklist.md`  
  - `evidence/d9_g0_preflight_checklist.md`  
  - `evidence/d9_summary_gate_matrix.json`

Obs.: os caminhos acima são **referência** para o Capítulo 2. A sprint só é considerada coerente se existir um mapeamento 1:1 entre D9.x e arquivos reais, com evidências em `evidence/` ou equivalente. Esses nomes foram pensados para serem **estáveis e automação-friendly**: scripts futuros podem depender deles sem surpresas.

---

## 2) Modelo de Gates da D9

Em vez de reaproveitar diretamente T0–T8 (mais associados a código/ORR), a D9 usa uma sequência de **gates documentais**:

- **D9-G0** — Pré‑flight & alinhamento de contexto.  
- **D9-G1** — Blueprint Consolidado + Overview (D9.0–D9.1).  
- **D9-G2** — Field Designer (D9.2).  
- **D9-G3** — Explore API & Integrações (D9.3).  
- **D9-G4** — Data Model + LGPD/ToS (D9.4–D9.5).  
- **D9-G5** — Roadmap + Mini‑Playbook (D9.6–D9.8).  
- **D9-G6** — Superprompt Codex v1 (D9.7) pronto para uso.

Cada gate é independente, mas há uma **ordem natural**: G0 → G1 → G2 → G3 → G4 → G5 → G6.  
Os gates G1–G5 podem ser trabalhados em paralelo, mas só podem ser marcados como concluídos quando seus pré‑requisitos estiverem atendidos.

Esses gates são **componíveis**: qualquer sprint futura de implementação do Inspectah pode declarar, por contrato, que só começa se determinados gates D9-Gx estiverem em PASS (por exemplo, "nenhum código de Field Designer pode ser escrito sem D9-G2 em PASS").

Todos os gates seguem o mesmo formato:

- Objetivo do gate.  
- Escopo (quais entregáveis D9.x cobre).  
- Pré‑condições para abrir o gate.  
- Checagens obrigatórias.  
- Evidência mínima.  
- Critério de aprovação (PASS).  
- Kill criteria (FAIL).

### 2.1 Gate Cheat Sheet (visão de 1 página)

| Gate   | O que garante                                                    | Entregáveis principais |
|--------|-------------------------------------------------------------------|------------------------|
| D9-G0  | Todo mundo leu o DNA relevante; ninguém está "no escuro".       | Cap.1, Blocos 0–5, Lessons, blueprint bruto |
| D9-G1  | Visão macro do Inspectah é consistente e explicável para leigos. | D9.0, D9.1           |
| D9-G2  | Field Designer tem contrato claro e exemplos concretos.          | D9.2                |
| D9-G3  | APIs/exports/webhooks são bem definidos e integráveis.           | D9.3                |
| D9-G4  | Modelo de dados e limites legais são coerentes entre si.         | D9.4, D9.5          |
| D9-G5  | Existe caminho de evolução (v0, v1, v1.x) e playbook de mudança. | D9.6, D9.8          |
| D9-G6  | Ponte para código (superprompt Codex) está pronta e confiável.   | D9.7                |

---

## 3) D9-G0 — Pré‑flight & Alinhamento de Contexto

**Objetivo**  
Garantir que ninguém começa a escrever/avaliar entregáveis de D9 sem ter lido o que precisa ser lido: DNA do MBP/Oráculo, Lessons Learned, Capítulo 1 e blueprint bruto do Inspectah.

**Escopo**  
- Pré‑condição para todos os demais gates.

**Pré‑condições para abrir o gate**  
- Blocos 0–5 do MBP/Oráculo acessíveis.  
- `Leasson Learned so far v1.md` acessível.  
- Capítulo 1 v1.1 disponível (`d9_capitulo_1_contexto_objetivos_v1_1.md`).  
- Versão base do blueprint Inspectah (v1.2.1) acessível.

**Checagens obrigatórias**  
- Pelo menos uma pessoa com papel de **Leslie/Arquiteto** confirma, em checklist:  
  - [ ] Leu Blocos 0–5.  
  - [ ] Leu `Leasson Learned so far v1.md`.  
  - [ ] Leu Capítulo 1 v1.1.  
  - [ ] Leu o blueprint v1.2.1 original do Inspectah.  
- Gaps óbvios ou contradições flagrantes entre Capítulo 1 e o blueprint são anotados em uma pequena seção "To‑fix" do D9.0 (serão resolvidos em G1).

**Evidência mínima**  
- `evidence/d9_g0_preflight_checklist.md` com:  
  - nomes de quem leu;  
  - datas;  
  - confirmações (checkboxes) das leituras;  
  - lista de pontos de atenção detectados.

**Critério de aprovação (PASS)**  
- Checklist preenchido e salvo;  
- Não há bloqueios de entendimento (apenas ajustes finos a serem tratados em G1–G4);
- Todos os pontos de atenção relevantes estão anotados para endereçamento posterior.

**Kill criteria (FAIL)**  
- Alguém tenta abrir G1–G5 sem checklist de G0 preenchido.  
- Contradições graves entre DNA MBP e visão do Inspectah passam batido (ex.: Inspectah assumindo papel de oráculo principal, o que viola o escopo).  
- Presença de TBD/TODO em Capítulo 1 em pontos essenciais de definição.

---

## 4) D9-G1 — Blueprint Consolidado + Overview (D9.0–D9.1)

**Objetivo**  
Garantir que o blueprint consolidado e o overview human‑friendly descrevem o Inspectah de forma consistente, sem lacunas graves, e alinhados com o Capítulo 1 e com o DNA do MBP.

**Escopo**  
- D9.0 — Inspectah Blueprint Consolidado (v1.2.x).  
- D9.1 — Overview Human‑Friendly do Inspectah.

**Pré‑condições para abrir o gate**  
- G0 aprovado.  
- Rascunhos de D9.0 e D9.1 escritos (não precisam estar perfeitos, mas completos).

**Checagens obrigatórias**  
- Consistência entre D9.0 e Capítulo 1:  
  - [ ] Objetivos, escopo IN/OUT e personas batem.  
  - [ ] Métricas citadas em Cap.1 aparecem contextualizadas em D9.0 (nem que de forma resumida).  
- Qualidade do overview (D9.1):  
  - [ ] Pessoa que nunca viu o projeto lê D9.1 e consegue explicar, em 2–3 frases, o que é o Inspectah.  
  - [ ] Não há termos internos opacos sem pelo menos uma explicação leve.  
- Sanidade estrutural:  
  - [ ] D9.0 não contém "TBD/TODO" em seções centrais (objetivos, escopo, capacidades v0).  
  - [ ] Não há contradições explícitas entre diferentes seções do blueprint (ex.: uma seção dizendo que Inspectah fará scraping agressivo e outra dizendo o contrário).  
- Alinhamento com MBP:  
  - [ ] Fica explícito que o Inspectah **não contém lógica de payout/resolução** do MBP; é hub de dados/evidência.  
  - [ ] Ficou claro o papel do Inspectah como subsistema do ecossistema CE/MBP.

**Evidência mínima**  
- `evidence/d9_g1_blueprint_overview_checklist.md` com as checkboxes acima marcadas (PASS/FAIL) e comentários.  
- Versões de D9.0 e D9.1 salvas com sufixo de versão (ex.: `_v1_2_1`, `_v1_0`).

**Critério de aprovação (PASS)**  
- Todas as checkboxes marcadas como OK ou com justificativa clara para qualquer exceção.  
- Nenhuma contradição grave pendente; no máximo ajustes de redação.  
- Pelo menos uma pessoa "externa" ao núcleo (ou você lendo com mentalidade de terceira pessoa) consegue explicar o Inspectah a partir de D9.1.

**Kill criteria (FAIL)**  
- Ainda há TBD/TODO em seções centrais.  
- Existem contradições não resolvidas sobre o papel do Inspectah no ecossistema.  
- D9.1 é incompreensível para alguém que não viveu a conversa inteira.

---

## 5) D9-G2 — Field Designer (D9.2)

**Objetivo**  
Garantir que o Anexo A (Field Designer) especifica, com precisão suficiente, como dados brutos viram campos estruturados — tipos, transforms, computed fields e comportamento em caso de erro.

**Escopo**  
- D9.2 — Anexo A: Field Designer.

**Pré‑condições para abrir o gate**  
- G1 aprovado (visão macro estável).  
- Rascunho completo do Anexo A escrito.

**Checagens obrigatórias**  
- Tipos de campo:  
  - [ ] Lista finita de tipos suportados (ex.: text, number, bool, timestamp, enum) está definida.  
  - [ ] Cada tipo tem descrição clara, exemplos e limites conhecidos.  
- Transforms:  
  - [ ] Existe um catálogo explícito de transforms (parse_date, parse_number, regex_extract, map, etc.).  
  - [ ] Cada transform define entradas esperadas, saídas e o que acontece em caso de erro (null, default, drop, log?).  
- Computed fields:  
  - [ ] A linguagem de expressões é especificada (operadores, funções permitidas, ausência de side effects).  
  - [ ] São proibidos I/O, loops não controlados e qualquer coisa que torne avaliação não determinística.  
- Erros & validação:  
  - [ ] Comportamento padrão quando um campo obrigatório falha está definido.  
  - [ ] Há exemplos concretos de mapeamento real (pelo menos 2–3 fontes fictícias/reais) mostrando Field Designer em ação.  
- Segurança de schema:  
  - [ ] Fica claro como versões de schema são gerenciadas (ex.: versionamento de FieldDefinition).  
  - [ ] Há indicação de como futuras mudanças em campos não quebram dados antigos.

**Evidência mínima**  
- `evidence/d9_g2_field_designer_checklist.md` com as checagens acima.  
- Referência, na evidência, às seções específicas de D9.2 onde cada ponto é coberto.

**Critério de aprovação (PASS)**  
- Não há transforms "mágicos" ou implícitos; tudo que o Codex precisar implementar está descrito.  
- Os exemplos concretos são suficientes para orientar implementação e testes.  
- Fica claro como tratar erros sem quebrar o pipeline inteiro.

**Kill criteria (FAIL)**  
- Transformações importantes são descritas apenas em termos vagos ("dá um jeito de extrair isso").  
- Há ambiguidade sobre o que fazer em caso de erro (campos obrigatórios vs opcionais).  
- Computed fields permitem comportamentos perigosos (I/O, chamadas externas, recursão solta).

### 5.1 Exemplo concreto: como executar D9-G2 na prática

Passo-a-passo sugerido para revisar D9-G2:

1) Abrir `d9_2_anexo_a_field_designer_v1_0.md`.  
2) Ler a seção de tipos e marcar, no checklist, se todos os tipos esperados estão lá e bem definidos.  
3) Percorrer o catálogo de transforms, marcando para cada transform se:  
   - há descrição clara;  
   - há exemplo;  
   - comportamento de erro está especificado.  
4) Ler a seção de computed fields, checando se a linguagem é segura (sem I/O, sem loops abertos).  
5) Validar os exemplos concretos: tentar, mentalmente, aplicar o Field Designer a uma fonte real e ver se o doc é suficiente.  
6) Preencher `evidence/d9_g2_field_designer_checklist.md` marcando os itens e anotando qualquer pendência.  
7) Só marcar D9-G2 como PASS quando nenhuma pendência for estrutural (apenas ajustes de texto são aceitáveis).

---

## 6) D9-G3 — Explore API & Integrações (D9.3)

**Objetivo**  
Garantir que o Anexo B define contratos claros para consulta (Explore), export e integração do Inspectah com outros sistemas.

**Escopo**  
- D9.3 — Anexo B: Explore API & Superfícies de Integração.

**Pré‑condições para abrir o gate**  
- G1 aprovado.  
- Rascunho completo de D9.3 escrito.

**Checagens obrigatórias**  
- Endpoints de Explore:  
  - [ ] Lista de endpoints principais (GET /items, GET /items/{id}, GET /sources...) está definida.  
  - [ ] Filtros permitidos, paginação e ordenação estão especificados.  
- Formatos de resposta:  
  - [ ] Estrutura dos JSON de resposta está descrita (campos, tipos, significado).  
  - [ ] Erros (4xx/5xx) têm formato padrão.  
- Export:  
  - [ ] Formatos de export (CSV/JSON) estão definidos, com exemplo.  
  - [ ] Limites (tamanho máximo, paginação em export) estão claros.  
- Webhooks:  
  - [ ] Tipos de evento (item.created, item.updated, source.error, etc.) definidos.  
  - [ ] Payload completo de cada evento exemplificado.  
  - [ ] Modo de autenticação (token simples, HMAC) descrito.  
- Views / consumo por BI:  
  - [ ] Estratégia de views de leitura e/ou materializações explicada em alto nível.  
- Integração com MBP e outros sistemas:  
  - [ ] Há exemplos de como o MBP pode consumir dados do Inspectah (ex.: via webhook ou job batch).  
  - [ ] Fica claro que a responsabilidade de lógica de negócio permanece fora do Inspectah.

**Evidência mínima**  
- `evidence/d9_g3_explore_api_integracoes_checklist.md` com as checagens acima.  
- Referências a seções de D9.3 para cada item.

**Critério de aprovação (PASS)**  
- Um engenheiro consegue, lendo D9.3, implementar um backend de API e um consumidor simples sem precisar perguntar "como deve ser o payload" ou "como pagina isso".  
- As integrações com MBP e outros sistemas não exigem supor comportamentos não especificados.

**Kill criteria (FAIL)**  
- Falta definição de filtros/paginação;  
- Webhooks são mencionados mas não especificados;  
- Não há formato de erro padrão;  
- Há ambiguidade sobre quem faz o quê na integração (Inspectah vs consumidor).

---

## 7) D9-G4 — Data Model + LGPD/ToS (D9.4–D9.5)

**Objetivo**  
Garantir que o modelo de dados do Inspectah é suficiente e consistente com as restrições legais/éticas de uso de dados.

**Escopo**  
- D9.4 — Anexo C: Data Model, DDL & Migração.  
- D9.5 — Anexo D: LGPD, ToS & Envelope de Risco.

**Pré‑condições para abrir o gate**  
- G1 aprovado.  
- Rascunhos completos de D9.4 e D9.5 escritos.

**Checagens obrigatórias**  
- Data Model / DDL:  
  - [ ] Esquemas de Source, Item, ItemKV, FTS e Evidence Vault estão especificados.  
  - [ ] Chaves primárias, índices e principais FKs estão descritos.  
  - [ ] Estratégia de migração SQLite → Postgres desenhada (mesmo que em alto nível).  
- Retenção e volume:  
  - [ ] Prazos de retenção de dados raw vs manifests/índices estão definidos.  
  - [ ] Há noção de limites de volume (ex.: ordem de grandeza de itens/dia).  
- LGPD/ToS:  
  - [ ] O que é permitido/aceitável em termos de fontes (públicas, com acordo, proibidas) está claro.  
  - [ ] Tratamento de dados pessoais (quando inevitáveis) está descrito.  
  - [ ] Há orientação explícita sobre respeito a robots.txt e ToS de terceiros.  
- Envelope de risco:  
  - [ ] Existem exemplos de fontes borderline e como decidir se são aceitáveis.  
  - [ ] Fica claro que o Inspectah não deve depender de scraping agressivo para funcionar.

**Evidência mínima**  
- `evidence/d9_g4_data_model_lgpd_checklist.md` com checagens.  
- Trechos de D9.4 e D9.5 referenciados para cada ponto.

**Critério de aprovação (PASS)**  
- O modelo de dados cobre os casos de uso de v0 sem gambiarras óbvias.  
- Qualquer decisão de adicionar uma nova fonte pode ser checada contra D9.5.  
- Não há contradição entre o que o modelo suporta e o que é permitido legalmente.

**Kill criteria (FAIL)**  
- Campos essenciais não têm tipo definido.  
- Não há plano de retenção.  
- D9.5 é vago a ponto de não orientar decisões ("use bom senso" não é suficiente).  
- Há brechas claras para uso indevido de dados.

---

## 8) D9-G5 — Roadmap + Mini‑Playbook de Evolução (D9.6–D9.8)

**Objetivo**  
Garantir que o Inspectah tem um caminho claro de evolução (v0, v1, v1.x) e um mini‑playbook para mudanças futuras.

**Escopo**  
- D9.6 — Roadmap Inspectah v0 / v1 / v1.x.  
- D9.8 — Mini‑Playbook de Evolução do Inspectah.

**Pré‑condições para abrir o gate**  
- G1–G4 aprovados (visão, Field Designer, APIs, dados, LGPD certificados).  
- Rascunhos de D9.6 e D9.8 escritos.

**Checagens obrigatórias**  
- Roadmap:  
  - [ ] v0, v1, v1.x têm objetivos claros e não se sobrepõem.  
  - [ ] Cada versão descreve o que é "in" e "out" (escopo).  
  - [ ] Há noção de dependências entre versões e com outros módulos CE/MBP.  
- Mini‑Playbook:  
  - [ ] Explica como propor mudanças de schema sem quebrar dados antigos.  
  - [ ] Explica como versionar APIs e comunicar breaking changes.  
  - [ ] Dá exemplos de como introduzir novas fontes/tipos de campo de forma segura.  
- Coerência temporal:  
  - [ ] O roadmap não exige, em v0, coisas que só são especificadas para v1/v1.x.  
  - [ ] Não há dependência circular entre Inspectah e MBP.

**Evidência mínima**  
- `evidence/d9_g5_roadmap_playbook_checklist.md` com checagens.  
- Referências a seções específicas de D9.6 e D9.8.

**Critério de aprovação (PASS)**  
- É possível montar um plano de sprints para implementar o Inspectah sem inventar nada além do que está no pacote D9.  
- Qualquer proposta de mudança futura tem um caminho descrito em D9.8.

**Kill criteria (FAIL)**  
- Roadmap é só uma lista solta de desejos, sem recorte por versão.  
- Playbook não orienta decisões concretas ("evoluir com cuidado" não conta).  
- Dependências entre Inspectah e MBP ficam circulares ou opacas.

---

## 9) D9-G6 — Superprompt Codex v1 (D9.7)

**Objetivo**  
Garantir que o superprompt Codex v1 é uma ponte confiável entre especificação (D9.0–D9.6, D9.8) e implementação do Inspectah v0.

**Escopo**  
- D9.7 — Superprompt Codex v1 — Inspectah v0 (Core Data Hub).

**Pré‑condições para abrir o gate**  
- G1–G5 aprovados (pacote D9.x estabilizado).  
- Versão candidata do superprompt escrita.

**Checagens obrigatórias**  
- Contexto:  
  - [ ] O superprompt resume, em poucas linhas, o que é o Inspectah e o que é v0.  
  - [ ] Ele referencia explicitamente os documentos D9.0–D9.6 e D9.8 como fonte de verdade.  
- Escopo para Codex:  
  - [ ] Fica claro que o objetivo é implementar **apenas o v0** (Core Data Hub).  
  - [ ] Há lista explícita de componentes que o Codex deve criar (serviços, módulos, scripts, testes básicos).  
- Regras de implementação:  
  - [ ] Stack técnica desejada (quando aplicável) está descrita sem ambiguidade.  
  - [ ] Limites (ex.: nada de scraping agressivo, nada de bypass em LGPD) estão explícitos.  
- Critérios de aceite:  
  - [ ] O superprompt inclui critérios de "pronto" para o código gerado (testes mínimos, scripts de bootstrap, etc.).  
- Teste de mesa:  
  - [ ] Leitura crítica: alguém se pergunta "se eu fosse o Codex, eu saberia exatamente por onde começar?" — a resposta precisa ser "sim".

**Evidência mínima**  
- `evidence/d9_g6_superprompt_codex_checklist.md` com checagens.  
- Opcional, mas desejável: um rascunho de sessão de Codex (até mesmo hipotética) mostrando como o superprompt seria usado.

**Critério de aprovação (PASS)**  
- O superprompt é autocontido o suficiente para ser colado no Codex e gerar um primeiro esqueleto de implementação v0 sem dúvidas estruturais.  
- Não há contradições entre o que o superprompt pede e o que está nos docs de D9.

**Kill criteria (FAIL)**  
- Superprompt depende de informações que não estão nos docs (ex.: "considere a conversa com o ChatGPT").  
- Escopo mal recortado (pede para fazer v0, v1 e v1.x ao mesmo tempo).  
- Falta explicitar limites de uso de dados e respeito a LGPD/ToS.

---

## 10) Gate Final da Sprint D9 — Matriz de Gates e DoD da Sprint

A sprint D9 é considerada **concluída** quando:

- Todos os gates **D9-G0 → D9-G6** estão marcados como PASS.  
- Todos os entregáveis D9.0–D9.8 existem, estão versionados e apontam para os gates correspondentes.  
- Existe um artefato de resumo unificado dos gates e do estado final.

### 10.1 Matriz de gates (evidence summary)

Artefato recomendado:

- `evidence/d9_summary_gate_matrix.json` contendo, para cada gate G0–G6:  
  - `gate_id` ("D9-G0" ... "D9-G6");  
  - `status` ("PASS"/"FAIL");  
  - `checked_by`;  
  - `checked_at`;  
  - `evidence_path` (ex.: `evidence/d9_g3_explore_api_integracoes_checklist.md`);  
  - `notes` (campo livre opcional para comentários).

**Schema mínimo esperado do JSON:**

```json
{
  "gates": [
    {
      "gate_id": "D9-G2",
      "status": "PASS",
      "checked_by": "nome_sobrenome",
      "checked_at": "2025-10-31T23:59:59Z",
      "evidence_path": "evidence/d9_g2_field_designer_checklist.md",
      "notes": "opcional, comentários adicionais"
    }
  ]
}
```

- `gate_id`, `status`, `checked_by`, `checked_at` e `evidence_path` são obrigatórios.  
- `status` deve ser sempre `PASS` ou `FAIL` (sem meio-termo).  
- `notes` é opcional.  

Esse formato foi pensado para ser trivialmente consumido por scripts futuros (ex.: `bin/d9_check_gates.sh`).

### 10.2 DoD da Sprint D9 (vista de alto nível + invariantes)

DoD (Definition of Done) da sprint D9:

1) Capítulos 1 e 2 escritos, coerentes, sem TBD/TODO em partes críticas.  
2) D9.0–D9.8 existem como documentos, com versão clara.  
3) Todos os gates D9-G0–D9-G6 estão em PASS, com evidências registradas.  
4) Qualquer pessoa consegue:
   - entender o que é o Inspectah lendo D9.1;  
   - entender como ele funciona lendo D9.0 + D9.2–D9.4;  
   - entender limites legais lendo D9.5;  
   - entender como implementá‑lo e evoluí‑lo lendo D9.6–D9.8 + o superprompt D9.7.  
5) Existe um caminho claro e documentado para que a próxima sprint deixe de ser "sprint de especificação" e passe a ser a primeira sprint de **implementação do Inspectah v0**, usando D9 como fonte única de verdade.

**Invariantes que não podem ser quebradas:**

- Nenhum entregável D9.x existe "sem dono": cada D9.x precisa estar claramente associado a pelo menos um gate D9-Gx.  
- Não se declara D9 concluída se **qualquer** gate estiver em `FAIL` ou sem evidência associada na matriz JSON.  
- Nenhum documento D9.x pode contradizer o Capítulo 1 ou o DNA do MBP no que diz respeito ao papel do Inspectah (Data Hub + OracleOps interno, sem lógica de payout/resolução).  
- Nomes dos arquivos de evidência e o formato de `d9_summary_gate_matrix.json` só podem ser alterados se este capítulo for versionado (v1.2, v1.3, etc.) para manter automação e scripts alinhados.

Com isso, o Capítulo 2 cumpre seu papel: qualquer entregável de D9 que não passa claramente em um gate está **incompleto por definição**, e a sprint não fecha enquanto isso não for resolvido.

