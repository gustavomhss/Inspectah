# Inspectah — Capítulo 1 vFinal
## Hub de Fontes, Log de Fatos, Consenso, Certeza (%) & Trilha de Decisão Explicável

---

### 0. Manifesto (por que o Inspectah existe)

Hoje, para checar um fato simples, você abre dez abas, cruza manchetes, compara prints, confia na memória e no “feeling”. Cada site tem um pedaço da verdade, ninguém te mostra a origem de forma clara e você não tem como auditar nada sem virar detetive full time. Muitas vezes, a decisão final é baseada em “qual fonte parece mais confiável”, sem nenhuma métrica objetiva por trás.

O Inspectah existe para matar esse padrão.

Ele é um **hub único de informações**, onde você consegue:

- Consultar dados vindos de **múltiplas fontes ao mesmo tempo**.
- Ver **de onde cada informação veio**, com evidência bruta guardada, versionada e rastreável.
- Entender **quando** um dado foi observado, como ele mudou ao longo do tempo e o quanto as fontes concordam ou divergem entre si.
- Ver **passo a passo como o sistema chegou a um valor ou conclusão**: quais fontes foram consideradas, quais foram descartadas, qual método de agregação foi usado.
- Saber **o grau de certeza do próprio Inspectah em relação àquela informação**, expresso em um percentual de 0% a 100%, com explicação dos fatores que contribuíram para esse número.

Exemplos de perguntas que o Inspectah quer tornar triviais:

- "Qual o preço médio do frango congelado nos principais apps de mercado em diferentes bairros de São Paulo, na última semana? Quais fontes estão destoando da maioria, quanto o Inspectah confia nesse número e por quê?"
- "Esse número que um político está citando apareceu no Diário Oficial, em relatórios oficiais ou só em matérias de jornal? Qual a trilha exata de documentos que sustenta esse número e qual o grau de certeza do Inspectah sobre ele?"
- "Quais foram as últimas alterações relevantes em uma tabela de referência (ex.: taxas, índices, parâmetros), quando ocorreram, quais fontes publicaram versões conflitantes e qual a confiança do Inspectah em relação ao valor que está me mostrando agora?"

No recorte atual, o Inspectah é **um hub de consulta + cadastro de fontes escalável, auditável, explicável e honesto sobre sua própria certeza**. Ele organiza tudo em torno de **log de fatos**, **versões de conteúdo**, **consenso prático entre fontes**, **grau de certeza (%) calculado de forma transparente** e **trilha de decisão consultável por usuários e admins**. BI avançado e integrações profundas com oráculos/mercados são camadas posteriores.

---

### 1. Visão Geral

O Inspectah é um **Hub de Fontes e Fatos com Certeza Explicável**: uma plataforma que varre múltiplas fontes, registra observações como fatos imutáveis em um log append-only, extrai dados estruturados, organiza tudo em categorias e oferece interfaces de consulta, comparação entre fontes, cálculo de grau de certeza (%) e explicação completa de como cada resposta foi construída.

Escopo atual:

1. Cadastrar e orquestrar fontes de dados de forma extremamente escalável e customizável.
2. Ler, interpretar e extrair informação de textos e estruturas diversas (HTML, APIs, RSS, JSON, tabelas simples etc.).
3. Registrar cada coleta como um **fato imutável**, preservando histórico.
4. Consolidar esses fatos em **visões consultáveis** (Itens e Campos) com trilha de evidências completa.
5. Organizar tudo por categorias, subcategorias e variantes.
6. Para determinados tipos de dado, **consultar múltiplas fontes simultaneamente e produzir uma visão de consenso prático** (mediana, maioria, intervalo simples), sem esconder divergências.
7. Para cada resposta relevante, atribuir um **grau de certeza (%) do Inspectah**, calculado a partir de múltiplos fatores (acordo entre fontes, reputação, frescor, qualidade dos dados) e apresentar esse número ao Usuário e ao Admin, junto com a trilha de decisão.

Este capítulo é conceitual por desenho: ele define objetos, princípios e contratos. Fórmulas detalhadas, SLOs, thresholds de uso e experimentos de calibração são especificados em capítulos técnicos posteriores.

---

### 2. Papéis, Workspaces e Limites Claros

Usuários finais só consultam. Cadastro, configuração e manutenção de fontes são feitos por perfis administrativos. O Inspectah opera em **Workspaces** (ou Projetos), que agrupam fontes, categorias, políticas de acesso e parâmetros de confiança.

#### 2.1. Workspace (Projeto)

Um Workspace é um contêiner lógico que reúne:

- Conjunto de Fontes cadastradas.
- Estrutura de categorias/subcategorias/variantes.
- Políticas de acesso e visibilidade.
- Regras específicas de reputação/consenso.
- Perfis de cálculo de certeza (parâmetros e pesos do algoritmo de confiança).

Workspaces permitem multi-tenant lógico: times diferentes podem operar conjuntos independentes de fontes, categorias e políticas de confiança.

#### 2.2. Admin de Fontes (Administrador)

Responsável por um ou mais Workspaces. Funções:

- Cadastrar Fontes.
- Definir categorias, subcategororias e variantes.
- Configurar Field Designer e mapear Campos para Sinais.
- Ajustar parâmetros de reputação e perfis de cálculo de certeza dentro do Workspace (quando expostos).
- Auditar trilhas de decisão e verificar se o grau de certeza calculado está condizente com o contexto.

#### 2.3. Usuário Consultor (Leitor)

Dentro de um Workspace, o Usuário Consultor:

- Consulta Itens, Campos, Sinais, visões de consenso e **grau de certeza (%)**.
- Usa filtros, busca, categorias e facetas.
- Visualiza evidências, origens de dados, trilha de decisão simplificada e o percentual de certeza do Inspectah.
- Não modifica Fontes, Campos, categorias, regras ou perfis de confiança.

#### 2.4. Operações/Owner de Dados

- Observa métricas de saúde das Fontes.
- Ajusta prioridades e SLAs de coleta.
- Monitora reputação de Fontes e comportamento do algoritmo de certeza.
- Usa trilhas de decisão como instrumento de auditoria e investigação.

---

### 3. Princípios de Produto

Princípios não negociáveis para o Inspectah:

1. **Escalabilidade** de Workspaces, Fontes, Campos e Sinais.
2. **Customização máxima por Fonte**, sem precisar de deploy de código.
3. **Log de fatos imutável**: Observações como eventos append-only.
4. **Auditabilidade total**: sempre responder “de onde veio?”, “quando foi visto?”, “o que mudou?”.
5. **Organização hierárquica flexível** por categorias.
6. **Multi-fonte como primeira classe**, com consenso prático que nunca esconde a composição.
7. **Evolução de schema compatível**, com versionamento de mapeamentos e backfill sobre fatos imutáveis.
8. **Componentização**: Collectors, Extractors, Field Designer, Projeções, Evidence Vault, Indexadores, API/UI, Confidence Engine, Camada de Explicação.
9. **Hub de consulta primeiro, BI depois**.
10. **Explicabilidade e trilha de decisão**: nenhuma resposta como caixa-preta.
11. **Certeza transparente**: o grau de certeza do Inspectah é sempre visível, explicável e nunca vendido como “verdade absoluta”.

---

### 4. Domínio de Informação (Definições formais)

#### 4.1. Fonte

Uma **Fonte** é uma origem de dados (site, API, feed, base, etc.) dentro de um Workspace.

Cada Fonte possui, no mínimo:

- `id_fonte` (identificador interno único no Workspace).
- `nome_fonte` (nome legível).
- `tipo_fonte` (API REST, RSS, HTML, CSV etc.).
- Configurações de acesso (URLs, headers, autenticação, limites).
- Configurações de coleta (frequência, timeout, limites de itens por ciclo).
- Associação a uma ou mais categorias/subcategorias/variantes.
- Estado operacional (Ativa, Pausada, Em erro, Arquivada).
- Metadados de reputação básica (ex.: oficial/primária, secundária, agregador).

#### 4.2. Observação (fato imutável)

Uma **Observação** é um evento que representa uma coleta bem-sucedida de conteúdo de uma Fonte para uma determinada `chave_canônica` em um momento específico.

Conceitualmente, uma Observação é:

- `(Workspace, Fonte, chave_canônica, ts_observacao, payload_bruto + metadados)`

Regras:

- Observações são armazenadas em log append-only por `(Workspace, Fonte, chave_canônica)`.
- A sequência temporal nunca é reordenada ou truncada.
- Nenhum reprocessamento modifica Observações existentes.

#### 4.3. Item (materialização de estado)

Um **Item** é uma visão materializada derivada de Observações de uma mesma `(Workspace, Fonte, chave_canônica)`.

- `Item_atual`: projeção das Observações mais recentes.
- `Itens_históricos`: projeções passadas.

Cada Item inclui:

- Referência à Fonte e ao Workspace.
- `chave_canônica`.
- `versao_item`.
- Conjunto de Observações consideradas.
- Timestamps de criação/atualização.
- Estado (Válido, Em quarentena, Obsoleto).

#### 4.4. Campo (dado estruturado)

Um **Campo** é uma unidade de dado estruturado extraída de um Item.

Conceitualmente:

- `(nome_lógico, tipo, valor, origem_no_documento)`

onde `origem_no_documento` descreve:

- qual Observação originou o valor;
- quais seletores/offsets foram usados (CSS/XPath/JSON/range de texto);
- qual `versao_mapeamento` estava ativa.

Nenhum Campo é considerado consistente sem origem registrada.

#### 4.5. Sinal (entidade lógica multi-fonte)

Um **Sinal** representa “o mesmo conceito” observado em múltiplas Fontes (por exemplo, `preco_produto_local`, `indice_numerico`, `contagem_evento`).

Campos de diferentes Fontes podem ser mapeados para um tipo de Sinal usando chaves de alinhamento (produto, local, unidade, moeda, janela de tempo etc.). Consultas multi-fonte operam principalmente sobre Sinais.

#### 4.6. Certeza (confidence_score) do Inspectah

Para cada resposta relevante (especialmente em nível de Sinal), o Inspectah associa um **`confidence_score`** entre 0 e 100 (%), que representa “quão forte é a evidência disponível agora para suportar esta resposta, dado o que o Inspectah enxerga das Fontes”.

Propriedades conceituais:

- Não é “verdade absoluta”; é o grau de certeza do sistema.
- Leva em conta, no mínimo:
  - número e diversidade de Fontes independentes contribuindo;
  - nível de concordância entre Fontes (dispersão, maioria, distribuição);
  - reputação e tipo das Fontes (oficiais, primárias, secundárias etc.);
  - frescor das Observações (staleness, janelas de tempo);
  - qualidade e completude dos dados (parse, validações, lacunas).
- É sempre acompanhado de uma **explicação estruturada**: por que esse número é, por exemplo, 92% e não 60%.
- Cada score é etiquetado com um **perfil de confiança** (ex.: `confidence_profile_id`), identificando a configuração do Confidence Engine usada para produzi-lo (importante para interpretação histórica).

Escala interpretável (sujeita a ajustes finos por Workspace):

- 0–30%: baixa confiança.
- 30–60%: confiança moderada.
- 60–85%: alta confiança.
- 85–100%: confiança muito alta.

O Capítulo 1 não fixa uma fórmula única; ele define dimensões, invariantes e a necessidade de perfis versionados. Fórmulas concretas e sua calibração aparecem em capítulos técnicos.

---

### 5. Cadastro de Fontes, Field Designer, Schema e Sinais

O fluxo é:

1. Criação da Fonte em um Workspace (nome, tipo, categorias iniciais).
2. Configuração de acesso (URLs, headers, autenticação, limites, frequência).
3. Definição de Campos no Field Designer:
   - nome lógico, tipo, origem (selectors/JSON/texto), transformações e validações;
   - mapeamento opcional para Sinais (com chaves de alinhamento);
   - metadados relevantes para confiança (tipo de Fonte, criticidade do dado etc.).
4. Dry-run com Observações de exemplo, exibindo “texto original → Campo extraído → Sinal (se houver)”.
5. Publicação do mapeamento (`versao_mapeamento` ativa).

Mapeamentos são versionados. Evolução de schema e backfill:

- Observações antigas podem ser reprocessadas com nova `versao_mapeamento`.
- Isso gera novos Itens/Campos com nova `versao_item`.
- Histórico antigo permanece preservado (pode ser marcado como obsoleto para visões “current”).

---

### 6. Categorias, Subcategorias e Variantes

Por Workspace, o Inspectah mantém uma hierarquia:

- Categoria (ex.: Mercados, Política, Saúde, Esportes).
- Subcategoria (ex.: Cripto, Eleições, Doenças crônicas, Futebol).
- Variante (ex.: BR, EUA, Municipal, Federal, Série A, Sub-20).

Categorias são pontos de entrada para consulta e ajudam a organizar filtros e facetas relevantes. O mesmo Sinal pode aparecer em múltiplas categorias, conforme o contexto.

---

### 7. Estados, falhas e invariantes

#### 7.1. Estados de Fonte

- Ativa: coletando normalmente.
- Pausada: sem novas coletas temporariamente.
- Em erro: falhas recorrentes de coleta/parse.
- Arquivada: descontinuada; histórico preservado, sem novas coletas.

#### 7.2. Estados de Item

- Válido: extração e validações bem-sucedidas.
- Em quarentena: falha crítica de validação; pode ser oculto ou sinalizado.
- Obsoleto: substituído por Item mais recente ou reprocessado para a mesma chave.

#### 7.3. Invariantes

- A sequência de Observações para uma chave nunca é reordenada ou truncada.
- Nenhum reprocessamento modifica Observações já registradas.
- Itens são sempre derivados de um subconjunto bem definido de Observações.
- Nenhum Campo é exibido sem evidência correspondente.
- Alterar mapeamento nunca apaga histórico; apenas gera novas visões.
- Consultas com `confidence_score` sempre podem ser explicadas via trilha de decisão.

---

### 8. Múltiplas Fontes, divergência, consenso prático & trilha de decisão

Consultas multi-fonte operam sobre Sinais. O Inspectah:

1. Identifica Sinais relevantes para a pergunta (tipo de Sinal + chaves de alinhamento).
2. Reúne contribuições de Campos de múltiplas Fontes para esses Sinais.
3. Exibe os valores por Fonte, com evidência.
4. Calcula uma visão de consenso (mediana, média, maioria, intervalo simples etc.), quando aplicável.
5. Gera uma **trilha de decisão** que explica:
   - quais Fontes e Observações foram consideradas;
   - quais foram excluídas (erros, staleness excessivo, outliers extremos);
   - qual método de agregação foi usado;
   - como esses fatores influenciaram o `confidence_score`.

Regras conceituais:

- Consenso nunca esconde as Fontes: a lista de contribuições está sempre acessível.
- Maioria não é verdade absoluta; é apenas um sinal sobre o que as Fontes indicam.
- Divergências fortes são explicitamente sinalizadas.
- Usuários veem uma trilha de decisão legível; Admins/Operações veem a versão completa, estruturada.

---

### 9. Confiança, reputação, cálculo de certeza (%) e calibração

O `confidence_score` é calculado por um **Confidence Engine**, componente lógico que atua principalmente em nível de Sinal (e, em alguns casos, de Item). Dimensões usadas:

- quantidade e diversidade de Fontes;
- grau de concordância (dispersão/maioria);
- reputação das Fontes (tipo, histórico de falhas/correções/divergência);
- frescor dos dados;
- qualidade e completude dos Campos.

O resultado é:

- um valor entre 0 e 100;
- um resumo legível para o Usuário (ex.: "5 fontes independentes, alta concordância, dados das últimas 24h");
- uma explicação detalhada para Admins/Operações (pesos, distribuição, flags de reputação, staleness, `confidence_profile_id`).

Cada Workspace pode definir um ou mais **perfis de confiança** (`confidence_profile_id`), que representam configurações diferentes do Confidence Engine (pesos, thresholds, heurísticas). Cada score é etiquetado com o perfil usado, preservando interpretabilidade histórica.

Calibração (tema para capítulos técnicos, mas exigência de produto):

- Ao longo do tempo, o Inspectah deve ser capaz de avaliar se, por exemplo, respostas marcadas com 80% de confiança realmente se mostram corretas em aproximadamente 8 de cada 10 casos auditados.
- Mudanças em perfis de confiança devem ser introduzidas de forma controlada, com testes A/B ou janelas de sombra, preservando a semântica básica do score para o Usuário.

---

### 10. Pipeline modular (eventos, projeções, consenso, explicação e certeza)

O pipeline conceitual do Inspectah é orientado a eventos e projeções:

1. Coleta (Collectors): lê Fontes conforme configuração e gera Observações.
2. Extração (Extractors): transforma `payload_bruto` em representações internas.
3. Field Designer Engine: aplica mapeamentos, gera Campos e, quando cabível, associa a Sinais.
4. Projeções: gera/atualiza Itens por Fonte e visões de Sinais (incluindo projeções multi-fonte).
5. Confidence Engine: calcula `confidence_score` para Sinais/Itens relevantes, usando dimenções definidas.
6. Evidence Vault: armazena Observações, Itens, Campos, Sinais, trilhas de decisão e metadados de confiança.
7. Indexadores: indexam Itens, Campos, Sinais, estados e scores para busca e filtros.
8. API de Consulta e UI/Explore: expõem consultas single-fonte e multi-fonte, resultados, consenso, `confidence_score` e acesso à trilha de decisão.
9. Camada de Explicação: consolida, para cada resposta, como o valor e o score foram obtidos.

---

### 11. Pré-condições e pós-condições (contratos de operações chave)

Em nível conceitual, Capítulo 1 fixa contratos para:

- Cadastrar nova Fonte.
- Publicar mapeamento de Fonte.
- Reprocessar (backfill) Observações.
- Consultar single-fonte.
- Consultar multi-fonte.
- Gerar resposta com `confidence_score`.

Exemplo resumido (gerar resposta com `confidence_score`):

Pré-condições:

- Consulta bem definida (sobre Itens ou Sinais).
- Dados mínimos disponíveis conforme política do Workspace (por exemplo, ao menos uma Fonte com reputação conhecida e dados recentes, ou fallback explícito para "evidência insuficiente").

Pós-condições:

- A resposta inclui:
  - valor(es) principal(is) (ex.: preço de consenso, valor de indicador);
  - `confidence_score` (0–100%) etiquetado com `confidence_profile_id`;
  - acesso à trilha de decisão (legível para Usuário, completa para Admin).

Outras operações seguem o mesmo padrão de pré/pós-condições já descrito nas versões anteriores, preservando o espírito de Design by Contract.

---

### 12. Critérios de sucesso (produto)

O Capítulo 1 considera sucesso quando:

- Admins conseguem cadastrar Fontes complexas em poucos minutos, incluindo Campos, Sinais e metadados relevantes para confiança, sem tocar em código.
- Usuários conseguem responder perguntas reais navegando por categorias/filtros e, quando fizer sentido, comparando múltiplas Fontes para o mesmo Sinal.
- Qualquer dado exibido pode ser rastreado até Observações específicas, com trilha de decisão clara.
- A plataforma suporta crescimento da matriz [Workspaces × Fontes × Campos × Sinais × Categorias] sem colapsar em confusão ou schemas rígidos.
- Fontes problemáticas (falhas, divergências, correções frequentes) não passam despercebidas; seu impacto é visível para Operações.
- Consultas multi-fonte apontam não só um valor de consenso, mas também o nível de concordância entre Fontes e a explicação de como se chegou ali.
- Usuários entendem, em linguagem simples, o que significa um `confidence_score` alto ou baixo, e Admins conseguem auditar por que o score é X% e não Y%.

---

### 13. Resumo para o Codex

Para o Codex (ou qualquer agente executor), este Capítulo 1 vFinal estabelece que:

- O Inspectah é um hub de fatos e fontes com Workspaces, Observações imutáveis, Itens materializados, Campos estruturados e Sinais multi-fonte.
- Multi-fonte é padrão, e o sistema precisa comparar valores entre Fontes para construir visões de consenso.
- Cada resposta relevante deve, quando fizer sentido, vir acompanhada de um `confidence_score` (0–100%) e de uma trilha de decisão acessível a Usuários e Admins.
- O Confidence Engine é um componente de primeira classe; scores são determinísticos para o mesmo conjunto de entradas e etiquetados com `confidence_profile_id`.
- Fórmulas específicas, SLOs, thresholds e experimentos de calibração do score são especificados em capítulos técnicos (por exemplo, Capítulo 2/3, anexos ou specs dedicadas), mas devem respeitar todas as definições e invariantes deste capítulo.

Este Capítulo 1 vFinal é a âncora conceitual do Inspectah enquanto **Hub de Fontes, Log de Fatos, Consenso entre Fontes, Certeza (%) Transparente e Trilha de Decisão Explicável**. Nenhum capítulo posterior deve contradizer estes princípios; apenas refiná-los e torná-los executáveis em código, pipelines e SLOs concretos.

