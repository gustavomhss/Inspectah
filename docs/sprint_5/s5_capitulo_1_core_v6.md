# Sprint 5 — Capítulo 1 (v6)
## Inspectah Data Hub Core + AI Claim Normalizer v0.1 (por fonte)

> v6 — Versão 15/10 de rigor e clareza. Este é o contrato oficial da Sprint 5 do Inspectah, tratado como produto independente. Ele foi escrito para ser diretamente "compilável" em tarefas, código, testes e painéis, sem lacunas nem ambiguidades.

---

## 1. Propósito absoluto da Sprint 5

O Inspectah é um produto que responde a uma pergunta simples e poderosa:

> "O que cada fonte do mundo está afirmando, exatamente, e com qual evidência?"

A Sprint 5 existe para dar a primeira resposta concreta a essa pergunta. Ao final desta sprint, o Inspectah deve funcionar como um **núcleo de dados operacional** capaz de, para cada fonte:

1. Coletar informações de forma previsível e respeitosa (limites, ToS, robots).
2. Registrar evidências imutáveis e verificáveis de tudo o que foi coletado.
3. Usar IA (GPT‑4.1 mini) para ler o texto bruto de cada fonte **individualmente** e extrair claims estruturados:
   - o que a fonte declara como verdadeiro,
   - qual valor/resultado ela apresenta,
   - em que estado ela diz que o fato se encontra.
4. Tornar essas informações consultáveis por operadores e consumidores de dados, via UI interna e interfaces de leitura.

Não há decisão de verdade global, nem reconciliação entre fontes, nem produto final para usuários externos. O objetivo de S5 é construir um **espelho fiel e estruturado do que cada fonte diz**, com qualidade suficiente para ser base de qualquer uso futuro (auditoria, monitoramento, relatórios, sistemas de decisão, painéis, assistentes conversacionais, etc.).

---

## 2. Personas, visão de uso e limites de escopo

### 2.1 Personas atendidas em S5

Operador Inspectah

- Quer cadastrar, atualizar e desativar fontes.
- Quer saber se a ingestão está saudável (quem está falhando, quem está atrasado).
- Quer inspecionar o que cada fonte disse sobre um assunto específico.

Consumidor de Dados Interno

- Usa o Inspectah como base para scripts, relatórios, análises ad-hoc e protótipos.
- Quer acessar dados estruturados e claims por fonte via queries/APIs simples.

### 2.2 Personas não atendidas diretamente em S5 (mas influenciando o design)

Usuário de Insights/Assistente

- No futuro, fará perguntas em linguagem natural, pedirá gráficos e estatísticas.
- S5 prepara tudo: dados organizados, claims tipados, métricas e estados claros.

### 2.3 Limites de escopo

- S5 não decide quem está certo entre fontes.
- S5 não expõe interface pública nem resolve casos de uso finais de terceiros.
- S5 não implementa reputação de fontes ou lógica de consenso.

Toda menção a usos futuros serve apenas como guia de qualidade: se o Inspectah não for consultável e auditável com excelência em S5, ele não servirá para nada depois.

---

## 3. Modelo de estados do Item Inspectah

A unidade central do sistema é o **Item Inspectah**: "o registro do que uma fonte disse em um dado momento".

Cada Item Inspectah percorre os estados:

- S0 — Descoberto
- S1 — Coletado
- S2 — Evidenciado
- S3 — Normalizado (claims por fonte)
- S4 — Indexado / Explorável

### 3.1 Descrição formal dos estados

S0 — Descoberto

- A fonte está cadastrada, ativa e habilitada para ingestão.
- O watcher identifica um candidato a item (entrada de feed, objeto JSON, página/trecho de HTML).
- Não há garantia ainda de validade da resposta.

S1 — Coletado

- A requisição à fonte foi concluída com sucesso segundo critérios configuráveis (código HTTP permitido, corpo não vazio, tamanho dentro de limites, content-type aceitável).
- Os bytes de resposta e metadados mínimos são persistidos:
  - source_id, run_id, fetched_at, request_url, status_code, tamanho, headers relevantes.

S2 — Evidenciado

- É criado um **Evidence Bundle** para o item, contendo:
  - Conteúdo bruto (`raw.bin` ou equivalente).
  - Representação textual (`text.txt`), quando possível.
  - `meta.json` com metadados estruturados (incluindo os de S1).
  - `manifest.json` com a lista completa de arquivos e seus hashes (ex.: SHA‑256).
- O bundle possui um `bundle_id` imutável.
- O item é marcado como S2 apenas se o manifest for consistente.

S3 — Normalizado (Claims por Fonte)

- O AI Claim Normalizer v0.1 recebe como entrada:
  - source_id, item_id, bundle_id.
  - Texto relevante (tipicamente `text.txt`), com fallback controlado para HTML simplificado.
- O modelo retorna JSON em um **schema fixo v0.1** (ver seção 4).
- O JSON é validado contra o schema. Se estiver válido:
  - O item recebe a camada de dados normalizados.
  - É marcado como S3.
- Em caso de erro, o item permanece em S2 com logs detalhados.

S4 — Indexado / Explorável

- Um processo de indexação lê o JSON normalizado e grava campos relevantes em storage de consulta.
- O item é marcado como S4.
- A UI de Explore e as interfaces de leitura (queries/APIs) operam apenas sobre itens S4.

### 3.2 Transições permitidas e proibidas

Permitidas:

- S0 → S1 (coleta bem-sucedida)
- S1 → S2 (bundle criado e verificado)
- S2 → S3 (normalização e gravação de claims)
- S3 → S4 (indexação concluída)

Proibidas (exemplos):

- S1 → S3 ou S1 → S4 (não pode pular a evidência).
- S0 → S2 direto (bundle sem registro da coleta).
- Regressão automática de estados sem justificativa explícita (por exemplo, S3 → S2 sem marcar motivo).

Testes automatizados e asserts em código devem rejeitar transições inválidas.

---

## 4. Schema de normalização e vocabulário de claims

O schema v0.1 precisa ser estável, legível e diretamente mapeável para código e banco.

### 4.1 Campos de nível de item

Cada item normalizado terá, pelo menos:

- source_id: string (ex.: "g1_economia").
- item_id: string única dentro da fonte.
- bundle_id: string que referencia o Evidence Bundle correspondente.
- equivalence_key: string canônica para agrupar itens que falam do mesmo fato.
- headline: string curta (título ou resumo principal).
- published_at: string ISO 8601 (data/hora da publicação ou do fato).
- entities: lista de strings (entidades relevantes: pessoas, organizações, locais, índices, produtos etc.).
- facts: objeto (mapa string→valor) com detalhes importantes não modelados como claim explícito.
- claims: lista de objetos do tipo Claim (ver 4.2).
- confidence_local: número float entre 0 e 1.
- reasoning_short: string curta (1–2 frases) explicando o que foi entendido.

### 4.2 Schema de Claim

Cada claim é um objeto com campos obrigatórios:

- claim_id: string única dentro do item.
- claim_type: enum com valores permitidos:
  - "resultado_binario"
  - "resultado_numerico"
  - "estado_evento"
  - "data_evento"
  - "classificacao"

- declared_metric: string curta (o que está sendo medido; ex.: "IPCA", "preco_arroz_kg").
- declared_subject: string opcional com quem/onde se aplica (ex.: "Brasil", "loja_X").
- declared_value: valor principal da declaração (number ou string; ex.: 4.5, "SIM", "parada_sem_previsao").
- declared_unit: string opcional ("%", "BRL", "pessoas", etc.).

- polarity: enum com valores permitidos:
  - "afirma_que_e_verdade"
  - "afirma_que_e_falso"
  - "informa_sem_julgar"
  - "indeterminado"

- local_verdict: enum com valores permitidos:
  - "segundo_esta_fonte_este_e_o_valor"
  - "segundo_esta_fonte_isto_ocorreu"
  - "segundo_esta_fonte_isto_nao_ocorreu"
  - "segundo_esta_fonte_ainda_esta_pendente"
  - "nao_ha_veredito_claro"

- confidence_claim: número float entre 0 e 1.

### 4.3 Exemplos refinados

Exemplo A — Fonte declarando um índice numérico

Texto: "O índice X de novembro foi de 4,5%."

- claim_type: "resultado_numerico"
- declared_metric: "indice_X"
- declared_subject: "pais_Y"
- declared_value: 4.5
- declared_unit: "%"
- polarity: "informa_sem_julgar"
- local_verdict: "segundo_esta_fonte_este_e_o_valor"

Exemplo B — Fonte declarando um resultado binário

Texto: "O projeto de lei foi aprovado."

- claim_type: "resultado_binario"
- declared_metric: "aprovacao_projeto_lei_Z"
- declared_subject: "orgao_legislativo_W"
- declared_value: "SIM"
- declared_unit: null
- polarity: "afirma_que_e_verdade"
- local_verdict: "segundo_esta_fonte_isto_ocorreu"

Exemplo C — Fonte declarando estado de evento

Texto: "A obra permanece parada, sem previsão de retomada."

- claim_type: "estado_evento"
- declared_metric: "status_obra_Q"
- declared_subject: "obra_Q"
- declared_value: "parada_sem_previsao"
- declared_unit: null
- polarity: "informa_sem_julgar"
- local_verdict: "segundo_esta_fonte_ainda_esta_pendente"

---

## 5. equivalence_key: disciplina desde S5

A equivalence_key é o elo lógico para dizer "estes itens, de fontes diferentes, falam do mesmo assunto". Mesmo que o uso pesado venha depois, S5 precisa criar algo consistente.

Regras mínimas:

- Deve ser derivável de campos normalizados (declared_metric, declared_subject, período/data, categoria principal).
- Deve ser independente da fonte (não inclui source_id).
- Deve ser estável: o mesmo fato sempre gera a mesma equivalence_key quando extraído da mesma combinação de métricas/entidades.

Exemplos de formatos possíveis:

- "indice_X_2025_11_pais_Y"
- "status_obra_Q_cidade_Z_2025_10_15"
- "aprovacao_projeto_lei_Z_orgao_W_2025_03_10"

Responsabilidade em S5:

- Implementar uma função clara, documentada e testada para geração de equivalence_key.
- Incluir testes unitários e de golden data para garantir consistência.

---

## 6. Invariantes fundamentais (versão 15/10)

As invariantes abaixo são tratadas como leis; violá-las é bug crítico.

1. Evidência obrigatória

- Se um item está em S3 ou S4, existe exatamente um Evidence Bundle íntegro vinculado a ele.

2. Integridade de bundle

- Para qualquer item em S2/S3/S4, o comando de verificação de evidências consegue recalcular todos os hashes do manifest.

3. Imutabilidade de evidência

- Evidence Bundles são write-once. Correções ou re-coletas geram novos bundles, nunca reescrevem os existentes.

4. Leitura local por fonte

- Claims são sempre relativos a um único par (source_id, item_id). Não há claim "misturado" de múltiplas fontes.

5. Não-invenção

- Claims não podem mencionar valores, datas ou estados que não estejam suportados pelo texto da evidência.
- O prompt da IA reforça isso; amostras são revisadas periodicamente.

6. Coerência de estados

- Não pode haver item em S3 ou S4 que não tenha passado por S2.
- Não pode haver item em S4 que não tenha JSON normalizado válido.

7. Consultabilidade futura

- Todos os campos expostos em S4 são de tipos simples, adequados para filtros, agregações e visualizações.

---

## 7. Pré-condições e pós-condições por componente (contratos operacionais)

Watcher Engine

- Pré:
  - Fonte com YAML válido no registry.
  - Fonte ativa.
- Pós (sucesso):
  - Para cada resposta aceitável, um item em S1 é criado.
  - Logs estruturados com run_id, source_id, latência, resultado.

Evidence Builder

- Pré:
  - Item em S1 com bytes e metadados.
- Pós (sucesso):
  - Evidence Bundle criado conforme layout padrão.
  - Manifest consistente.
  - Item marcado como S2.

AI Claim Normalizer

- Pré:
  - Item em S2 com texto relevante disponível.
  - Fonte configurada como "gera claims".
- Pós (sucesso):
  - JSON normalizado aderente ao schema v0.1 gravado.
  - Pelo menos um claim para itens relevantes em que o texto permite.
  - Item marcado como S3.
- Pós (falha):
  - Item permanece em S2.
  - Erro logado com contexto (source_id, item_id, motivo, tamanho de prompt/resposta).

Indexer / Storage de Consulta

- Pré:
  - Item em S3 com JSON válido.
- Pós (sucesso):
  - Campos indexados.
  - Item marcado como S4.

UI Admin & Explore

- Pré:
  - Storage com itens S4.
- Pós:
  - Operador consegue localizar itens por fonte, tempo e equivalence_key.
  - Ao abrir um item, visualiza evidência e claims de forma clara.

---

## 8. Métricas, painel mínimo e checks em CI

### 8.1 Métricas mínimas

Por fonte

- ingest_runs_total, ingest_runs_failed
- ingest_items_new_total
- ingest_latency_seconds (histograma)

Evidência

- evidence_bundles_total
- evidence_verification_failures_total

Normalização

- normalize_requests_total
- normalize_failures_total
- claims_per_item_avg

Estados

- items_by_state{state="S0".."S4"}

### 8.2 Painel mínimo

- Visão por fonte: taxa de sucesso, erros recentes, latência.
- Visão de evidência: número de bundles, falhas de verificação.
- Visão de normalização: taxa de falha, claims por item.

### 8.3 Checks em CI

- Testes de schema do JSON normalizado.
- Testes de geração de equivalence_key com exemplos fixos.
- Testes de contrato por fonte (mudanças de layout detectáveis).
- Verificação de integridade de bundles em amostra.
- Teste de consistência de estados (nenhum item em estado impossível).

---

## 9. Escopo positivo e fora de escopo

Escopo positivo da Sprint 5

- Registry de fontes + Watchers v0.
- Evidence Vault v0 com bundles imutáveis e verificação.
- AI Claim Normalizer v0.1 por fonte, com schema e claims.
- Indexação básica e UI Admin & Explore v0 para consulta interna.

Fora de escopo

- Qualquer forma de consenso ou decisão global entre fontes.
- Interfaces públicas e produto final para clientes.
- Sistema completo de reputação de fontes.
- Assistente conversacional completo para usuários finais (ficará para sprint dedicada).

---

## 10. Critérios de pronto (DoD) da Sprint 5

A Sprint 5 só é considerada concluída se TODOS estes pontos forem verdadeiros:

1) Fluxo fim a fim validado

- Um operador interno, que não escreveu o código, consegue:
  - Cadastrar uma nova fonte simples.
  - Rodar o watcher com sucesso.
  - Ver itens em Explore.
  - Abrir um item e enxergar claramente: evidência bruta, texto extraído, claims gerados.

2) Evidência completa e íntegra

- 100% dos itens em S2+ nas últimas 24h têm Evidence Bundle verificável.

3) Claims por fonte funcionando na prática

- Para pelo menos duas fontes textuais de naturezas distintas, ≥ 90% dos itens relevantes têm pelo menos um claim estruturado.

4) Métricas e estabilidade operacional

- Métricas descritas na seção 8 estão expostas.
- Por pelo menos 7 dias em ambiente de desenvolvimento/CI:
  - ingest_latency_p95 dentro do orçamento definido.
  - explore_query_p95 dentro do orçamento.
  - evidence_verification_failures_total = 0 em runs regulares.

5) Documentação e evidência

- Este Capítulo 1 v6 está atualizado e consistente com o código.
- Existe um wrap executivo de sprint com resumo, riscos e próximos passos.
- Estrutura de evidence e logs é suficiente para uma revisão operacional posterior sem retrabalho estrutural.

---

## 11. Ética, ToS e coleta responsável

O Inspectah nasce com uma postura clara:

- Respeitar termos de uso de sites e APIs.
- Respeitar robots.txt quando aplicável.
- Respeitar limites de frequência, evitando comportamento agressivo.
- Registrar de forma transparente o que está sendo coletado, quando e de onde.

Decisões técnicas de S5 (frequência de watchers, paralelismo, número de fontes) devem ser tomadas considerando esses limites, e não apenas capacidade técnica.

---

## 12. Alinhamento final da equipe

- Leslie Lamport
  - Considera o modelo de estados e invariantes adequado para fundamentar especificações mais formais, se necessário.

- Donald Knuth
  - Julga o vocabulário controlado e os exemplos de claims suficientes para evitar ambiguidade na implementação.

- Bertrand Meyer
  - Aprova os contratos (pré/pós-condições) por componente como base direta para asserts e testes.

- Steve Jobs
  - Satisfeito com a narrativa centrada no operador e na clareza visual de "o que cada fonte disse".

- Forsgren (SRE)
  - Alinhado com a lista de métricas e o recorte de estabilidade mínima.

- Moxie
  - Confortável com o compromisso explícito com evidência forte, não-invenção de dados pela IA e coleta responsável.

Este Capítulo 1 (v6) é a referência única para planejar, implementar, testar e revisar a Sprint 5 do Inspectah. Qualquer decisão de design ou implementação que entre em conflito com ele deve ser considerada, por padrão, incorreta até que o documento seja revisado conscientemente.

