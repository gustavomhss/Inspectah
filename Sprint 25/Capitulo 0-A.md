# Sprint 25 — Capítulo 0 — Adendo v2
## Entidades, Casos, Context Service e Código Humano

> Versão v2 — Revisado pelo Squad Verdade & Interpretação + Conselho. Este adendo faz parte do Capítulo 0, não é opcional. Ele define a memória de longo prazo do Inspectah (por entidade e por caso) **e** como isso deve ser implementado em código legível, auditável e sustentável por humanos.

---

### 0.A.1. Missão deste adendo

O Capítulo 0 define o Sistema de Camadas: Dossiê → Claims → Interpretação → Comitês → Debunker → Humano → Decisão → Truth‑DB.

Este adendo v2 adiciona dois pilares que estavam implícitos, agora escritos em pedra:

1. **Memória Estruturada por Entidade e por Caso**  
   O Inspectah não é um papagaio de manchete. Sempre que chega algo novo sobre alguém ou sobre um caso, o sistema deve levar em conta **tudo que já sabe** sobre aquele ator e aquela história.

2. **Código Humano, Auditável e Evolutivo**  
   Todo esse mecanismo tem que ser implementado em código simples, legível, modular, testável e refatorável por humanos. Nada de monstros opacos que só uma IA entende. Codex é implementador, não feiticeiro.

Tudo que vier nos Capítulos 1–6 da S25 deve tratar este adendo como constituição para:

- modelagem de dados (Truth‑DB, banco operacional, System of Blocks),
- design da API de contexto (Context Service),
- e estilo de implementação (claridade > esperteza; simplicidade > truque obscuro).

---

### 0.A.2. Princípios de desenho (o que nunca pode ser violado)

1. **Entity‑centric & Case‑centric**  
   Toda claim relevante está ancorada em pelo menos uma Entidade. Claims que fazem parte de uma narrativa contínua pertencem a um ou mais Casos.

2. **Memória é parte da Verdade, não acessório**  
   Decisão sem contexto histórico em domínios sensíveis (política, justiça, obras públicas, saúde, etc.) é proibida. O pipeline deve consultar o histórico adequado antes de decidir.

3. **Contexto é resumido e parcimonioso**  
   O sistema não despeja o passado inteiro no LLM. Ele constrói dossiês resumidos (Entidade e Caso), com pointers claros para detalhes quando necessário.

4. **Código para humanos, com IA como assistente**  
   O Codex deve gerar código:
   - modular (módulos pequenos, bem nomeados),
   - com funções curtas e coesas,
   - com tipos/contratos explícitos,
   - com comentários cirúrgicos onde a intenção não for óbvia,
   - com testes cobrindo casos típicos e de borda.

   Qualquer engenheiro competente deve conseguir entender e manter o código sem “ler a mente” da IA.

5. **Nenhuma magia silenciosa**  
   - Algoritmos de agrupamento (Entidade, Caso),
   - heurísticas de relevância,
   - regras de priorização de contexto,

   devem estar descritos em termos claros de dados e invariantes, nunca escondidos em prompts opacos.

6. **Auditoria completa**  
   Toda decisão importante (mapeamento de entidade/caso, construção de dossiê, escolha de contexto, TruthScore) deve ter trilha de dados e logs que possam ser inspecionados meses depois.

---

### 0.A.3. Entidades — os “protagonistas” do Inspectah

Entidades são os nós centrais do grafo de verdade do Inspectah. Não são só pessoas, mas tudo que funciona como ator ou referência estável:

- Pessoas (políticos, autoridades, executivos, atletas, cientistas),
- Organizações (ministérios, prefeituras, empresas, ONGs, clubes, partidos),
- Instrumentos formais (leis, projetos de lei, obras, contratos, programas públicos),
- Eventos referenciais (eleições, campeonatos, operações, grandes conferências),
- Lugares institucionais relevantes (hospitais, tribunais, escolas, estádios).

Modelo lógico mínimo de Entidade:

- `entity_id`: identificador interno estável (chave primária).
- `entity_type`: enum (PESSOA, ORGAO_PUBLICO, EMPRESA, LEI, OBRA, MANDATO, EVENTO, etc.).
- `labels`: nomes canônicos.
- `aliases`: apelidos, siglas, grafias alternativas.
- `canonical_identifier`: quando existir (CNPJ, ID oficial, código de lei, etc.).
- `attributes`: mapa de atributos relevantes (país, cargo atual, esfera de atuação, período de mandato, etc.) com validade temporal.
- `references`: links para fontes oficiais (Wikidata, cadastros públicos, bases governamentais).

Invariantes de Entidade:

- `entity_id` nunca muda; merges geram histórico de fusão (quem foi mesclado em quem, quando, por qual critério).
- Alterações de atributos são versionadas (mudança de cargo, mudança de nome, etc.), não sobrescrevem o passado.
- Claims promovidas em domínios sensíveis não podem ficar penduradas em “texto solto”; precisam ser resolvidas para uma (`entity_id`) clara ou marcadas como ambíguas com flags específicas.

**Orientação ao Codex (implementação):**

- Criar uma tabela clara `entities` com colunas explícitas (sem JSON embolado para tudo).
- Criar tabelas auxiliares (`entity_aliases`, `entity_attributes`, `entity_references`) com FKs explícitas.
- Implementar camadas de aplicação para resolver entidades como funções pequenas, com código legível, em vez de enterrar heurísticas dentro de prompts.

---

### 0.A.4. Casos — onde as histórias moram

Casos são contêineres narrativos de médio/longo prazo. São a forma como o Inspectah diz: “isso aqui é tudo parte da mesma história”.

Exemplos de Casos:

- Escândalo de desvio de verbas X.
- Obra do metrô linha Y (licitação → execução → aditivos → atrasos → investigação).
- Operação policial Z (investigação, prisões, denúncias de abuso, julgamentos).
- Mandato do Governante W (promessas de campanha → ações → indicadores de resultado).
- Campeonato N (rodadas, decisões polêmicas, suspeitas de manipulação).
- Evento climático extremo (enchentes de 20XX, estiagem recorde de ano Y, etc.).

Modelo lógico mínimo de Caso:

- `case_id`.
- `case_type` (ESCANDALO, OBRA, MANDATO, OPERACAO, CAMPEONATO, EVENTO_CLIMATICO, etc.).
- `title`, `description`.
- `entities_involved`: relação N:N com Entidades, com campo `role` (acusado, órgão controlador, fiscalizador, beneficiário, etc.).
- `time_span`: `start_at`, `end_at` (ou null se aberto).
- `status`: EM_INVESTIGACAO, EM_JULGAMENTO, ENCERRADO, ARQUIVADO, EM_MONITORAMENTO.
- `tags`: temas principais (corrupção, saúde, educação, infraestrutura, esporte, clima…).

Invariantes de Caso:

- Casos não nascem por hype; seguem critérios mínimos (número de claims relacionadas, tipo, impacto potencial). Esses critérios devem ser codificados em funções explícitas.
- Casos podem ser divididos em fases (por exemplo, fase de investigação, fase judicial, fase de execução). Isso deve estar na estrutura de dados.

**Orientação ao Codex:**

- Implementar tabelas `cases`, `case_entities`, `case_tags` com chaves estrangeiras simples e claras.
- Encapsular lógica de criação/merge de casos em serviços pequenos e bem testados, não em scripts gigantes.

---

### 0.A.5. Claims, Entidades e Casos — relação formal

Cada Claim carrega consigo a ligação com o mundo real via Entidades e, quando fizer sentido, via Casos.

Extensões do modelo de Claim (Cap. 0):

- `entity_ids`: lista de entidades envolvidas, com um principal (sujeito) e, opcionalmente, secundários.
- `case_ids`: lista de casos aos quais a claim pertence.
- `entity_link_confidence`: indicador de quão segura está a ligação com cada entidade.
- `case_link_confidence`: idem para casos.

Regra de ouro:

- Claim importante sem entidade resolvida é dívida técnica explícita a ser tratada (com flags, fila de resolução e, se necessário, humano‑no‑loop).

**Orientação ao Codex:**

- Usar tabelas de junção (`claim_entities`, `claim_cases`) com colunas claras (`claim_id`, `entity_id`, `role`, `confidence`).
- Evitar campos “blob” JSON genéricos para relações que são estruturais.
- Fornecer funções de alto nível do tipo `link_claim_to_entity` / `link_claim_to_case` que encapsulam as regras de negócio, em vez de deixar a camada superior montando SQL manual.

---

### 0.A.6. Dossiês de Entidade e Dossiês de Caso — memória condensada

Além dos Dossiês de Ingestão, o Inspectah mantém dois tipos de dossiês agregados:

1. **Dossiê de Entidade**  
   Visão consolidada da entidade ao longo do tempo:
   - cronologias por tema (eleitoral, judicial, orçamentário, etc.);
   - conjunto de claims chave promovidas/contestáveis;
   - indicadores agregados (número de denúncias, taxa de claims rejeitadas, padrões temporais);
   - mudanças de cargo, papel institucional, contexto.

2. **Dossiê de Caso**  
   Visão consolidada de todo o Caso:
   - linha do tempo de eventos (notícias, relatórios, decisões, indicadores);
   - mapa de entidades envolvidas e suas relações;
   - claims backbone (aquelas que sustentam a narrativa principal) vs claims periféricas;
   - pontos de conflito explícitos (claims incompatíveis sobre o mesmo fato);
   - status atual no Inspectah (em análise pesada, consolidado, encerrado etc.).

Esses dossiês são estruturas persistidas, não PDFs soltos. Devem ter:

- snapshots versionados (v1, v2, v3…),
- campos estruturados (listas de claims, gráficos agregados, status),
- e possibilidade de re-geração incremental (por jobs assíncronos) quando fatos novos chegam.

**Orientação ao Codex:**

- Implementar tabelas ou estruturas dedicadas para snapshots de dossiês (`entity_dossiers`, `case_dossiers`) com metadados claros: versão, data de geração, escopo.
- Job de geração/atualização desses dossiês deve ser código simples de batch, com logs e métricas, não um “prompt mágico” escondido.

---

### 0.A.7. Context Service — cérebro de memória para agentes

O Context Service é o pedaço que tira o passado do banco e entrega algo útil ao agente.

Responsabilidades principais:

- Encontrar o histórico relevante para uma entidade e/ou caso, dado:  
  - tipo da claim,  
  - domínio (política, saúde, etc.),  
  - janela temporal,  
  - sensibilidade/impacto.
- Condensar esse histórico em um contexto enxuto:  
  - resumo estruturado (eventos chave, indicadores agregados),  
  - subconjunto de claims e decisões mais importantes,
  - pointers para detalhes se o agente quiser aprofundar.

API conceitual mínima:

- `get_entity_context(entity_id, options)`  
  - `options`: janela de tempo, domínios, limite de itens, nível de detalhe.

- `get_case_context(case_id, options)`

- `get_entity_case_context(entity_id, case_id, options)`

Formato de resposta (alto nível):

- `entity_summary` ou `case_summary`: estrutura pequena, previsível (não texto solto sem forma).
- `key_claims`: lista de claims chave com campos compactos (id, resumo, decisão, tempo).
- `timelines`: eventos cronológicos simplificados.
- `links`: IDs de claims, dossiês e blocos Truth‑DB para drill‑down.

Políticas de custo e limite:

- tamanho máximo de contexto por chamada (por ex.: N tokens estimados).
- estratégias de corte (priorizar claims recentes ou backbone do caso, dependendo da tarefa).
- caching de contextos para entidades/casos muito acessados.

**Orientação ao Codex (muito importante):**

- Implementar o Context Service como módulo de aplicação legível, com funções bem nomeadas (`build_entity_summary`, `select_key_claims_for_entity`, etc.).
- Evitar “metralhar” dados pro LLM: sempre montar estruturas compactas primeiro.
- Codificar regras de seleção/priorização em código “clássico” (Python/SQL/...): ordenações, filtros, thresholds; usar LLM só para síntese textual final quando necessário.

---

### 0.A.8. Integração com o Sistema de Camadas

O Context Service não é um bônus; ele é parte da pipeline descrita no Capítulo 0.

Pontos obrigatórios de uso:

- **Camadas 2/3 (Interpretação & Entidades/Eventos)**  
  Ao reconhecer uma entidade conhecida (ou candidato forte), o pipeline já registra essa ligação, para que dossiês de entidade/caso possam ser atualizados depois.

- **Camada 4/5 (Claims & Classificação/Roteamento)**  
  O routing_profile deve incorporar:
  - presença de entidade/caso sensível,  
  - status do caso (quente, histórico, encerrado),  
  - histórico de conflito sobre aquela entidade/caso.

- **Camada 7 (Comitês)**  
  Antes de deliberar, comitês devem receber:
  - o texto/dados atuais,  
  - + contexto de entidade/caso via Context Service (resumos & key_claims).

- **Camada 8 (Debunker)**  
  Debunker precisa ver não só evidências externas, mas também padrões históricos daquela entidade/caso (recorrência de denúncias infundadas, ou o contrário, etc.).

- **Camada 10 (Decisão & Truth‑DB)**  
  O TruthScorer pode incorporar sinais do contexto:  
  - grau de conflito acumulado,  
  - histórico de correções/erros sobre o mesmo tema,
  - distribuição prévia de decisões sobre o caso.

**Orientação ao Codex:**

- Na implementação da pipeline, chamar o Context Service via funções utilitárias dedicadas, não espalhar chamadas diretas ao banco por todo lado.
- Isolar bem a fronteira: camadas “pedem contexto” para o Context Service, que fala com o banco.

---

### 0.A.9. Falhas, cenários tortos e autodefesa do sistema

Precisamos assumir o caos:

1. **Entidade ambígua (vários "José Silva" possíveis)**  
   - Registrar `entity_candidates` com scores,  
   - evitar tomar decisão forte de verdade até desambiguar,  
   - opcionalmente mandar para humano‑no‑loop.

2. **Caso embrionário (parece caso, ainda não é)**  
   - Manter clusters internos de claims sem ainda promover a Caso oficial,  
   - codificar limiares claros para promoção a `case_id` (quantidade, impacto, fontes).

3. **Casos longos e cheios de ruído**  
   - Dossiês de caso devem suportar segmentação por fases,  
   - Context Service pode oferecer modos: “fase atual + resumo histórico”.

4. **Correções e retratações**  
   - Claims rejeitadas, retratadas ou superadas permanecem no histórico,  
   - Dossiês de entidade/caso mostram não só “verdades aceitas”, mas também tentativas de manipulação e erros passados.

**Orientação ao Codex:**

- Implementar mecanismos de flag/estado explícitos (ambíguo, proto‑caso, em revisão, etc.), não inferências mágicas.
- Manter lógica de limiares e decisões em funções que possam ser revisadas, testadas e ajustadas, não enterradas em prompts.

---

### 0.A.10. Código legível, auditável e amigável para humanos

Este trecho é o recado direto ao Codex e a qualquer pessoa que vá implementar ou refatorar essa parte da S25.

Requisitos explícitos de estilo e arquitetura:

1. **Modularidade explícita**  
   - Separar claramente: modelos de dados, serviços de domínio (entidade, caso, contexto), camada de API, scripts auxiliares.
   - Nada de arquivos monstros de mil linhas com tudo misturado.

2. **Nomenclatura clara**  
   - nomes de funções, métodos e variáveis devem dizer o que fazem (`build_case_timeline`, `select_key_claims`, etc.),
   - evitar siglas obscuras e “variável lixo” (`x1`, `tmp`, `foo`).

3. **Contratos de função & tipos**  
   - usar type hints sempre que a linguagem permitir,
   - documentar inputs/outputs em docstrings curtas, focadas em intenção, não em novela.

4. **Comentários cirúrgicos, não enxurrada**  
   - comentar **por quê** algo é feito de determinada forma, não repetir óbvio;
   - sempre comentar heurísticas e limites (ex.: “limite de 50 claims por contexto por causa de custo/token”).

5. **Testes em volta dos pontos críticos**  
   - testes para: resolução de entidade, criação/merge de caso, geração de dossiês, seleção de contexto;
   - cenários felizes e cenários quebrados (input incompleto, entidades ambíguas, caso muito grande).

6. **Nenhuma lógica crítica escondida só em prompt**  
   - regras de negócio (limiares, estados, tipagem) devem existir em código;
   - o prompt pode descrever a mesma regra pro LLM, mas o “ground truth” está no código e nos dados.

7. **Documentação mínima, porém viva**  
   - manter um README/overview técnico da parte de Entidades/Casos/Context Service,
   - o Cap.3 (filemap) deve apontar para os principais módulos gerados.

Em resumo: o Codex deve agir como um dev sênior escrevendo algo que outra equipe vai manter, não como um gerador de scripts descartáveis.

---

### 0.A.11. Custo, performance e viabilidade

A boa notícia: nada aqui exige magia cara se for feito direito.

- Banco relacional/colunar/grafo com bons índices em `entity_id`, `case_id`, `time` é tecnologia padrão.
- Jobs de geração de dossiês podem rodar em background, em lotes, com monitoramento.
- O Context Service só conversa com LLMs depois de fazer o trabalho pesado de filtrar e condensar.

A parte cara — chamadas de LLM — é controlada ao:

- trabalhar com resumos enxutos,
- usar thresholds para quando profundidade extra é necessária,
- e evitar redundância de chamadas em pipelines repetitivos.

---

### 0.A.12. Critério de completude do adendo v2

Este adendo cumpre sua função quando:

- ninguém no projeto consegue falar seriamente sobre “como o Inspectah decide verdade sobre alguém ou sobre um caso” sem mencionar Entidades, Casos, Dossiês e Context Service;
- qualquer engenheiro consegue, a partir deste texto, desenhar um esquema de banco e um módulo de serviço legível para Entidades/Casos/Contexto;
- qualquer pessoa técnica lendo Cap.0 + este adendo entende a frase:  
  
  > “Saiu nova reportagem sobre o político XYZ, no Caso ABC. O Inspectah vai buscar o dossiê histórico dessa entidade e desse caso, condensar em contexto, alimentar as camadas (comitês, debunker, decisão) e só então escolher o que vira Fato/Verdade.”

- e, principalmente, quando o código que nasce disso é algo que você olha daqui a um ano e pensa:  
  “Isso foi feito por gente séria, não por um robô apressado.”

Este adendo faz parte do Capítulo 0. Capítulos 1–6 da S25 apenas concretizam, refinam e operacionalizam o que está escrito aqui.

