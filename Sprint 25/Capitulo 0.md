# Sprint 25 — Capítulo 0 (v3)
## Sistema de Camadas de Validação, Interpretação, Classificação e Decisão

> Versão: v3 — revisão pelo Squad Verdade & Interpretação + Conselho (Pearl, Stonebraker, Norvig, Percy, Knuth, Kleppmann, etc.).
> Meta: especificação state of the art, sem lacunas, pronta para implementação direta pelo Codex, substituindo o sistema atual de camadas sem colaterais.

---

### 0.1. Missão deste capítulo

Este capítulo define, em nível cirúrgico, o sistema de camadas que transforma entradas brutas em decisões de Verdade/Fato no Inspectah. Ele precisa cumprir simultaneamente três papéis:

1. **Blueprint conceitual completo** do pipeline de interpretação, validação, debunking e decisão — sem buracos, sem “caixas pretas mágicas”.
2. **Contrato de funcionamento** entre camadas, agentes, Truth-DB, Debunker (S24), Sistema de Blocos e as políticas de Verdade/Governança da S25.
3. **Guia de refatoração segura** para o Codex: como apagar o sistema atual de camadas por substituição, mantendo o Inspectah íntegro em produção.

Este capítulo responde, explicitamente:

- O que é processado a cada etapa, por qual algoritmo (ou tipo de algoritmo), com quais invariantes.
- Como os erros são tratados (falhas de modelo, dados faltantes, conflitos, violações de invariante).
- Como a redundância é construída (vários intérpretes, vários builders, vários comitês, debunker, humano-no-loop).
- Como tudo se ancora em estados formais (máquinas de estados) e em estruturas persistentes (Truth-DB, Evidence Vault, logs).

Tudo que vier nos Capítulos 1–6 da S25 deve ser um refinamento operacional deste capítulo, nunca uma correção estrutural.

---

### 0.2. Modelo mental global

O mundo externo produz artefatos: notícias, relatórios, bancadas de dados, discursos, tweets, atas, votos em plenário, resultados de jogos, séries temporais de indicadores, etc. O Inspectah não “acredita” nem “desacredita” em nada disso de cara. Em vez disso, ele:

1. Recebe o artefato e o encapsula em um **Dossiê de Ingestão** (Dossier).
2. Decompõe o conteúdo em **Claims** — enunciados atômicos, rastreáveis.
3. Submete cada claim a uma sequência de camadas: interpretação, classificação, corroboração, comitês, debunker, humano-no-loop.
4. Calcula um **TruthScore** e aplica políticas para decidir se a claim vira bloco/sub-bloco na Truth-DB, se fica como contestável ou se é rejeitada.

O sistema de camadas é, portanto, o **motor lógico** entre “coisas que o mundo diz/mostra” e “fatos que o Inspectah aceita como Verdade operacional”.

---

### 0.3. Entidades centrais e contratos formais

#### 0.3.1. Dossiê de Ingestão (IngestionDossier)

Modelo lógico mínimo (campos podem ser refinados no Cap.3):

- `id_dossier`: identificador global único.
- `id_fonte`: referência à fonte cadastrada (S21/S22).
- `tipo_fonte`: RSS, API, upload, arquivo, streaming, etc.
- `raw_ref`: ponte para o conteúdo bruto (texto, HTML, binário) no Evidence Vault.
- `raw_hash`: hash (ou Merkle root) do conteúdo bruto.
- `metadata_normalizada`: idioma, timezone, datas relevantes, autor(es) declarados, seção/editoria, sinalização de paywall, etc.
- `pipeline_version`: versão da pipeline de camadas usada.
- `states`: histórico de estados macro do Dossiê (ver 0.4).
- `claims_ids`: lista de IDs de claims derivadas.

Invariantes:

- O conteúdo bruto nunca é alterado; qualquer correção é metadado adicional.
- `raw_hash` é imutável e usado como base para deduplicação e integridade.

#### 0.3.2. Claim

Modelo lógico detalhado:

- `id_claim`
- `id_dossier`
- `sujeito`: referência a entidade ou conceito em ontologia interna.
- `predicado`: tipo de relação (eleito, aprovou, anunciou, divulgou, mediu, venceu, etc.).
- `objeto`: alvo da relação (lei, projeto, valor numérico, entidade, evento, índice, decisão judicial, etc.).
- `tempo`: instante ou intervalo (com timezone resolvido).
- `local`: referência geográfica ou administrativa (país, estado, município, órgão, arena, etc.).
- `tipo_claim`: enum (fato observável, estatística oficial, declaração, previsão, opinião, meta-claim, etc.).
- `escopo`: eixos como local/nacional/global, tema (economia, saúde, política, clima, esporte, ciência, etc.).
- `fonte_primaria_ref`: ponte precisa para trecho(s) do conteúdo ou célula(s)/linha(s) de um dataset.
- `estado_claim`: máquina de estados micro (ver 0.4.2).
- `routing_profile`: resultado da camada de roteamento (ver 0.10).
- `evidence_bundle_ref`: referência a evidências automáticas.
- `committee_bundle_ref`: referência aos pareceres de comitês.
- `debunker_report_ref`: referência ao relatório do debunker.
- `human_review_ref`: referência à revisão humana (se houver).
- `truth_decision_ref`: referência ao registro final de decisão.

Invariantes:

- As referências (`*_ref`) nunca são reusadas entre claims diferentes; cada claim tem sua própria trilha, mesmo que compartilhe dados.
- `tipo_claim` nunca muda após a fase de classificação; se precisar mudar, cria-se claim nova com rastro de superação.

---

### 0.4. Máquinas de estados (macro e micro)

#### 0.4.1. Estados do Dossiê (macro)

Estados principais (com subestados implícitos):

- `RAW_INGESTED`: dossiê criado, conteúdo bruto referenciado.
- `NORMALIZED`: metadados saneados, texto extraído, timezone resolvido.
- `INTERPRETED`: há `InterpretationSnapshot` estável (ou `INTERPRETED_CONFLICT` se a divergência entre intérpretes for alta).
- `ENTITIES_EVENTS_EXTRACTED`: entidades e eventos resolvidos ao máximo possível.
- `CLAIMS_BUILT`: claims atômicas construídas.
- `CLAIMS_ROUTED`: claims classificadas e roteadas.
- `AUTO_CORROBORATED`: evidências automáticas coletadas.
- `COMMITTEE_REVIEWED`: comitês multi-agente emitiram pareceres.
- `DEBUNKED_OR_ESCALATED`: debunker rodou e, se necessário, houve escalonamento para humano.
- `DECIDED`: todas as claims relevantes chegaram a uma decisão formal.

Cada mudança gera um `DossierStateTransition` com:

- de→para, timestamp, origem (camada/serviço), erro (se houve), snapshot de métricas relevantes.

#### 0.4.2. Estados da Claim (micro)

Estados e regras:

- `C_NEW`: claim recém-criada, ainda sem evidências.
- `C_PENDING_VALIDATION`: claim encaminhada para corroboração automática e comitês.
- `C_UNDER_REVIEW`: claim em processo ativo de análise (comitês, debunker, humano-no-loop).
- `C_PROMOTED`: claim promovida a Fato/Verdade; existe bloco/sub-bloco correspondente na Truth-DB.
- `C_CONTESTABLE`: claim marcada como contestável (e.g., evidência mista, alta polarização, fragilidade identificada).
- `C_REJECTED`: claim rejeitada (erro factual, manipulação, inconsistência forte).
- `C_DEFERRED`: claim estacionada aguardando eventos futuros (previsões, promessas, metas com prazo futuro).
- `C_SUPERSEDED`: claim superada por claim mais recente/precisa sobre o mesmo fato/intervalo.

Cada transição produz um `ClaimStateTransition` com:

- `from_state`, `to_state`, timestamp,
- componente responsável (corroborador, comitê X, debunker, humano),
- resumo estruturado da razão (motivos, scores, flags).

---

### 0.5. Camadas principais – visão geral

As camadas são tratadas como módulos independentes, conectados via contratos de dados. Cada camada consome um conjunto de artefatos (Dossiê, claims, evidências) e produz outro, sem invadir a responsabilidade da próxima.

1. Camada 1 – Ingestão & Normalização Bruta.
2. Camada 2 – Interpretação Semântica Inicial.
3. Camada 3 – Extração e Consolidação de Entidades/Eventos.
4. Camada 4 – Construção de Claims Atômicas.
5. Camada 5 – Classificação, Tipagem e Roteamento.
6. Camada 6 – Corroboração Automática.
7. Camada 7 – Comitês Multi-Agente.
8. Camada 8 – Debunker Automatizado.
9. Camada 9 – Humano-no-loop.
10. Camada 10 – Decisão Formal & Truth-DB.

Camadas transversais obrigatórias:

- T1 – Observabilidade & Telemetria.
- T2 – Segurança, Privacidade & LGPD.
- T3 – Aprendizado de Políticas & Feedback Loop.

O restante do capítulo aprofunda a anatomia de cada camada e sua interação com as demais.

---

### 0.6. Camada 1 – Ingestão & Normalização Bruta (detalhado)

Responsabilidade exclusiva: pegar o mundo sujo e transformá-lo em Dossiê limpo o suficiente para o resto do pipeline.

Entrada:

- Eventos de ingestão (cron, webhooks, polling, uploads),
- Conteúdo bruto (HTML, JSON, XML, CSV, PDF, texto, etc.).

Processos principais:

1. **Detecção de tipo e parsing:**
   - Identificar o tipo de artefato (página HTML, feed RSS, API JSON, tabela CSV, arquivo PDF).
   - Usar parsers fechados e testados (sem “gambiarras” dentro do pipeline de camadas).

2. **Extração de texto/estrutura base:**
   - Para HTML/PDF: extrair título, corpo, byline, data de publicação, seções.
   - Para CSV/JSON: detectar colunas-chave, tipos de dados numéricos, data/hora, categorias.

3. **Normalização:**
   - Idioma (lang + confidence),
   - Timezone e datas (resolver para UTC + fuso original),
   - Números (separador decimal, milhares, unidades),
   - Codificação de caracteres.

4. **Deduplicação e integridade:**
   - Calcular `raw_hash` a partir de representação canônica.
   - Verificar se já existe Dossiê com mesmo `raw_hash`.
   - Se sim, criar referência cruzada ou tratar como “espelho” (mesmo conteúdo vindo de múltiplas fontes).

Saída:

- Dossiê em `NORMALIZED`, pronto para a camada 2.

Falhas esperadas:

- Parser falhou, conteúdo ilegível: Dossiê marcado como `NORMALIZATION_FAILED` com detalhes, não entra em camadas seguintes (mas fica registrado como tentativa).

---

### 0.7. Camada 2 – Interpretação Semântica Inicial (detalhado)

Responsabilidade: responder “do que se trata isso?” sem ainda decidir se é verdade.

Arquitetura de intérpretes:

- Intérprete A — foco em estrutura jornalística (quem, o que, onde, quando, por quê).
- Intérprete B — foco em contexto histórico/político/econômico (situa a peça em narrativas maiores).
- Intérprete C — foco em atores (quem são os agentes, seus papéis, seus vínculos institucionalizados).
- Intérprete D — foco em sinalização de opinião vs. fato (identifica trechos opinativos, especulativos, valorativos).

Cada intérprete produz um `InterpretationDraft` com campos padronizados:

- `tipo_de_peca`,
- `resumo_1_frase`,
- `resumo_curto`,
- `resumo_estruturado`,
- `topicos`, `subtopicos`,
- `indicadores_de_tom`,
- `lacunas_percebidas` (ex.: falta fonte para números, não explica metodologia, etc.).

Um **Consolidation Engine**:

- compara os drafts,
- mede divergência (linguística e estrutural),
- resolve “maioria” e registra divergências relevantes em `InterpretationSnapshot`.

Se `conflict_score` > threshold:

- Dossiê recebe flag `INTERPRETED_CONFLICT`;
- `routing_profile` inicial sobe a prioridade e fortalece exigência de revisão humana posterior.

Saída:

- Dossiê em `INTERPRETED`, com snapshot versionado e assinaturas dos intérpretes (para rastrear variações futuras).

---

### 0.8. Camada 3 – Entidades & Eventos (detalhado)

Responsabilidade: mapear quem fez o quê, onde, quando.

Componentes:

- `EntityExtractor` com múltiplos backends (modelo A, modelo B, heurísticas C).
- `EventDetector` para identificar eventos discretos (aprovou, sancionou, votou, publicou, mediu, venceu, etc.).
- `OntologyLinker` para alinhar entidades/eventos à ontologia interna e a identificadores externos (quando possível).

Processo:

1. Rodar extratores em paralelo, registrar sugestões.
2. Unificar entidades:
   - mesclar aliases ("Lula" vs. "Luiz Inácio Lula da Silva"),
   - resolver ambiguidade com base em contexto (país, cargo, histórico).
3. Unificar eventos:
   - ligar atores, ação, contexto temporal e local.
   - identificar eventos compostos (ex.: "projeto foi aprovado na Câmara e no Senado" → dois eventos ligados).

Saída:

- `EntitySet` e `EventSet` ligados ao Dossiê.
- Dossiê em `ENTITIES_EVENTS_EXTRACTED`.

Erros e ambiguidades:

- Entidade com múltiplos candidatos plausíveis → flag de ambiguidade; aumenta prioridade de comitês e, possivelmente, de revisão humana.

---

### 0.9. Camada 4 – Construção de Claims Atômicas (detalhado)

Responsabilidade: transformar interpretação + entidades + eventos em “pixels lógicos” manipuláveis.

Princípios:

- Uma claim descreve **um** enunciado específico que pode ser verificado, contestado ou rastreado.
- Claims compostas são proibidas; preferir explodir em várias claims simples.

Builders:

- `FactBuilder`: extrai fatos objetivos (ex.: resultado de eleição, dado numérico, ocorrência de evento).
- `SpeechBuilder`: extrai declarações de agentes (quem disse o quê, quando e em que contexto).
- `ForecastBuilder`: extrai previsões, metas, promessas.
- `MetaBuilder`: extrai meta-claims (e.g., "pesquisa foi feita com margem de erro X").

Pipeline:

1. Cada Builder gera uma lista de pre-claims.
2. Um `ClaimNormalizer`:
   - garante forma (sujeito, predicado, objeto, tempo, local),
   - valida que há ponte clara para o conteúdo original,
   - remove duplicatas e mergeia claims equivalentes.

Saída:

- Claims em `C_NEW` e Dossiê em `CLAIMS_BUILT`.

---

### 0.10. Camada 5 – Classificação, Tipagem e Roteamento (detalhado)

Responsabilidade: decidir o quão duro e por qual caminho cada claim será processada.

Dimensões de classificação (formalizadas):

- `epistemic_type`: FATO_OBSERVAVEL, ESTATISTICA_OFICIAL, DECLARACAO, PREVISAO, OPINIAO, META_CLAIM.
- `domain`: SAUDE, ECONOMIA, POLITICA, CLIMA, ESPORTE, CIENCIA, TECNOLOGIA, etc.
- `sensitivity`: BAIXA, MEDIA, ALTA, CRITICA.
- `time_sensitivity`: QUENTE (horas/dias), NORMAL, HISTORICO.
- `polarization`: BAIXA, MEDIA, ALTA (calculado via heurísticas + histórico da ontologia).

O `ClaimRoutingProfile` inclui:

- filas alvo (normal, reforçada, crítica),
- necessidade de revisão humana obrigatória ou opcional,
- número mínimo de comitês e membros por comitê,
- exigência de debunker reforçado ou básico.

Saída:

- Claims marcadas com `routing_profile` e Dossiê em `CLAIMS_ROUTED`.

---

### 0.11. Camada 6 – Corroboração Automática (detalhado)

Responsabilidade: o algoritmo “advogado da realidade”: cruzar claims com dados estruturados.

Arquitetura:

- `SourceRegistry` (S21/S22/S10) sabe quais fontes oficiais existem por país/tema.
- `QueryPlanner` sabe como consultar cada fonte (API, SQL, CSV versionado, etc.).
- `EvidenceCollector` executa queries, consolida resultados, calcula alinhamento.

Para cada claim:

1. `SourceSelector` decide que fontes são relevantes.
2. `QueryPlanner` gera consultas específicas (evitando string-building frágil).
3. `EvidenceCollector` executa, normaliza e calcula `alignment_score` (0–1).
4. Cada resultado gera um `EvidenceRecord` com:
   - fonte, dataset, timestamp de coleta,
   - relação: SUPPORTS, CONTRADICTS, NO_EVIDENCE, PARTIAL,
   - força relativa.

Um `EvidenceAggregator` produz um `ClaimEvidenceBundle` por claim com:

- `AutoEvidenceScore`,
- lista de evidências,
- flags de conflito.

Saída:

- Dossiê em `AUTO_CORROBORATED`.

---

### 0.12. Camada 7 – Comitês Multi-Agente (detalhado)

Responsabilidade: “pensar” sobre a claim com múltiplas lentes.

Comitês típicos:

- Coerência Lógica,
- Contexto & Recorte,
- Epistemologia,
- Risco & Impacto.

Cada comitê tem pelo menos 3 membros (LLMs configurados de forma ligeiramente diferente). Cada membro recebe:

- claim,
- EvidenceBundle,
- contexto da Truth-DB (claims relacionadas, blocos relevantes),
- matriz 5D da claim (T/F/I/R/C pré-calculada).

Cada membro produz `CommitteeOpinion` com:

- recomendação, justificativa, notas numéricas.

O `Consensus Engine` calcula:

- `CommitteeConfidence`,
- divergência interna (baixa/média/alta),
- resumo textual para log e UI.

Saída:

- `CommitteeReviewBundle` anexado; Dossiê em `COMMITTEE_REVIEWED`.

---

### 0.13. Camada 8 – Debunker Automatizado (detalhado)

Responsabilidade: atacar a claim.

Contrato com S24:

- Entrada: claim + EvidenceBundle + CommitteeReviewBundle.
- Saída: `DebunkerReport` com:
  - hipóteses alternativas,
  - evidências contrárias,
  - possíveis manipulações narrativas,
  - classificação de fragilidade (0–1).

O Debunker tem acesso a:

- fontes alternativas às usadas na corroboração,
- histórico de casos parecidos (para detectar duplo padrão),
- sinais de manipulação (trechos cherry-picked, descontextualização).

Saída:

- Claims podem ganhar flag de alto risco; Dossiê em `DEBUNKED_OR_ESCALATED`.

---

### 0.14. Camada 9 – Humano-no-loop (detalhado)

Responsabilidade: aplicar julgamento humano explícito, com rastreio.

Critérios de roteamento para humano:

- `sensitivity` alta ou crítica,
- `polarization` alta,
- divergência forte entre comitês,
- `DebunkerFragility` alta,
- indicação manual.

A interface expõe:

- texto original,
- claims,
- evidências,
- pareceres de comitês,
- relatório do debunker,
- histórico de decisões correlatas.

O humano produz `HumanReviewRecord` com recomendação, justificativa estruturada, grau de confiança.

Saída:

- claims atualizadas; insumo direto para a Camada 10.

---

### 0.15. Camada 10 – Decisão Formal & Truth-DB (detalhado)

Responsabilidade: sintetizar tudo num ato formal de decisão.

Inputs:

- claim completa (com roteamento, evidências, comitês, debunker, humano),
- políticas de Verdade & Governança vigentes.

O `TruthScorer` calcula um vetor:

- `AutoEvidenceScore`,
- `CommitteeConfidence`,
- `DebunkerFragility` (invertida para “robustez”),
- `HumanConfidence`,
- dimensões da matriz 5D (Tempo, Fonte, Impacto, Reversibilidade, Conflito).

As políticas definem uma função `TruthScore` por tipo de claim.

Decisão:

- Se `TruthScore` >= threshold_promocao e sem bloqueios duros → `PROMOTE_TO_TRUTH`.
- Se entre limites ou com bloqueios suaves → `MARK_CONTESTABLE`.
- Se evidência forte contra + debunker confirmando fragilidade → `REJECT`.
- Se depender de evento futuro → `DEFER`.

Cada decisão gera `TruthDecisionRecord` com rastreio completo.

Integração com o Sistema de Blocos:

- Claims promovidas são mapeadas para blocos/sub-blocos/ componentes conforme as regras da Truth-DB (S10+),
- Atualizações de blocos podem superar claims antigas (C_SUPERSEDED) mantendo trilha histórica.

---

### 0.16. Camadas transversais (T1, T2, T3)

T1 – Observabilidade:

- Métricas por camada (volume, latência, erro, distribuição de estados),
- Logs estruturados com correlação por `id_dossier` e `id_claim`,
- Painéis para detectar gargalos, surtos de conflitos, padrões de fragilidade.

T2 – Segurança, Privacidade & LGPD:

- Minimização de dados pessoais nas camadas (expor só o necessário),
- Controles de acesso fortes para dados sensíveis,
- Anonimização/pseudonimização quando possível,
- Retenção controlada e registros de acesso.

T3 – Aprendizado de Políticas & Feedback:

- Reprocessar claims com novo contexto (ex.: novas evidências surgem),
- Ajustar pesos e thresholds quando pós-mortems mostrarem erros sistemáticos,
- Registrar "story" de evolução de políticas.

---

### 0.17. Matriz 5D de reflexão (operacional)

Para cada claim, calculamos explicitamente:

- Tempo (T): quão rapidamente o valor da claim se degrada (notícia quente vs. dado histórico consolidado).
- Fonte (F): reputação, transparência, independência, histórico de correções.
- Impacto (I): potencial de dano se a claim for errada ou ignorada.
- Reversibilidade (R): quão fácil é corrigir um erro (técnica e socialmente).
- Conflito (C): grau de conflito com a Truth-DB e claims vizinhas.

Esse vetor 5D alimenta o `routing_profile`, os comitês, o debunker e a função de decisão final.

---

### 0.18. Estratégia de substituição do sistema atual (refinada)

Regras obrigatórias para o Codex:

1. Isolar tudo que é "camada" atual em módulos marcados como legado.
2. Criar novos módulos e estruturas de dados conforme este capítulo, sem reutilizar nomes confusos.
3. Implementar pipeline nova em paralelo e habilitar shadow mode por um período mínimo definido nos gates da S25.
4. Construir ferramentas de comparação (decisões legado vs. novo, métricas de divergência, ganhos de robustez).
5. Só desligar o legado quando os scorecards da S25 mostrarem superioridade estável do novo sistema.

---

### 0.19. Critério de completude deste capítulo

Este capítulo é considerado completo quando:

- Não há mais decisões implícitas ou "mágicas"; tudo que é crítico está descrito em termos de estados, camadas, artefatos e políticas.
- Qualquer engenheiro lendo este capítulo consegue descrever, em detalhes, o caminho de uma claim da ingestão até a Truth-DB e todos os pontos de auditoria.
- O Conselho (Pearl, Stonebraker, Norvig, Percy, Knuth, Kleppmann, etc.) consegue apontar onde cada uma das suas preocupações (causalidade, dados, conhecimento, agentes, rigor formal) está refletida na arquitetura.

Os próximos capítulos apenas operacionalizam o que está aqui; a verdade sobre "como o Inspectah decide o que é verdade" está, por definição, contida neste Capítulo 0 v3.

