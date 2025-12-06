# Guia de arquitetura de uso de LLM no Inspectah

## 0. Contexto e relação com o roadmap

Este guia é parte da espinha dorsal de arquitetura do Inspectah. Ele se aplica diretamente às sprints e programas que tratam de ingestão, interpretação, debunking, verdade/fato e features avançadas baseadas em LLM:

- S22: Ingestão 2.0 por fonte
- S23: Agentes de interpretação e classificação
- S24: Debunker v0 e humano‑no‑loop
- S25: Governança, verdade/fato e política de promoção
- Programa 1 (E26+): Cockpit de casos, monitores avançados, painéis de narrativas, mentiras em circulação, radar de manipulação etc.

Sempre que qualquer squad desenhar ou alterar fluxos que envolvam LLM, comitês de agentes, Debunker, Truth‑DB ou features de análise, este guia é a referência principal. Ele existe para impedir três falhas clássicas:

1. Arquitetura inchada de LLM que explode custo de token sem aumentar qualidade.
2. Uso ingênuo de modelos (efeito “oráculo”), degradando rigor de verdade/fato.
3. Divergência entre squads, criando pipelines incoerentes e difíceis de auditar.

## 1. Propósito e escopo

Propósito: definir **como** o Inspectah deve usar LLM em toda a cadeia ingestão → interpretação → debunking → verdade/fato, de forma que o sistema seja:

- Epistemicamente robusto (focado em verdade, coerência, auditabilidade).
- Economicamente sustentável (tokens tratados como orçamento de produto).
- Operacionalmente previsível (latência e carga controladas, com métricas).

Escopo:

- Abrange o desenho de agentes, comitês, tiers de modelo, critérios de chamada, formato de entrada/saída, budget de tokens, segurança e observabilidade.
- Não define prompts concretos nem código, mas define restrições que qualquer prompt/código deve respeitar.
- É obrigatório para decisões de arquitetura de S22–S25 e de qualquer épico que consuma LLM em produção.

## 2. Princípios de design (não negociáveis)

2.1 Verdade/fato como produto principal

O objetivo do Inspectah não é produzir “respostas bonitas”, e sim manter um **estado de verdade/fato** por claim e por caso. Qualquer uso de LLM é aceitável apenas se reforça esse estado: mais claro, mais confiável, mais auditável.

2.2 Arquitetura acima de modelo

Modelos são commodities; arquitetura é o ativo. O sistema não deve depender de um modelo específico. Trocar de modelo (ou provedor) deve ser principalmente questão de configuração, não de reescrever o produto.

2.3 Funil progressivo de custo

Quanto mais cedo no pipeline, mais barato e mais simples o uso de LLM (idealmente zero). Quanto mais próximo da decisão de verdade/fato, maior a profundidade de raciocínio, porém em **volume muito menor** de chamadas.

2.4 Unidade de verdade = claim

A unidade que o Inspectah julga não é “documento”, é **alegação estruturada (claim)**. Documentos são evidências que suportam ou contestam claims. Toda arquitetura de LLM deve refletir isso.

2.5 Raciocínio incremental

O sistema nunca reanalisa o universo inteiro a cada novo documento. Sempre trabalha com a pergunta: “Dado o estado atual deste caso/claim, o que este novo insumo muda?”. Isso vale para prompts, fluxos e design de dados.

2.6 Tokens como orçamento de produto

Tokens são um recurso escasso, como tempo de time ou dinheiro em caixa. O sistema deve ter:

- Limites explícitos de consumo por dia, por caso, por tema.
- Modo de degradação controlada quando orçamento se aproxima do limite.

2.7 Múltiplas perspectivas e Debunker como cidadãos de primeira classe

Nenhum agente único decide “a verdade”. O núcleo de verdade se baseia em comitês com papéis complementares e um Debunker com mandato explícito para atacar conclusões, não apenas explicar.

2.8 Auditabilidade e reprodutibilidade

Para qualquer decisão de verdade/fato, deve ser possível responder:

- Quais claims estavam em jogo?
- Quais evidências foram consideradas?
- Quais agentes participaram e o que concluíram?
- Qual era o estado anterior e por que mudou?

LLM nunca deve gerar saídas “mágicas” não reconectadas às evidências.

## 3. Taxonomia de componentes LLM no Inspectah

Para evitar ambiguidade, este guia trata os seguintes componentes:

- **Modelos base (LLM)**: GPT‑x, modelos open‑source, etc.
- **Tiers de modelo**:
  - Tier 3: open‑source/local, tarefas simples e baratas.
  - Tier 2: modelo comercial “mini” / custo médio, backbone principal.
  - Tier 1: modelo premium, usado apenas em casos críticos.
- **Agentes**: instâncias de LLM com instruções específicas (intérprete, classificador, analista, debunker, decision maker, etc.).
- **Comitês**: grupos coordenados de agentes que atuam sobre uma claim/caso com regras de agregação.
- **Truth‑DB**: camada que guarda claims, estados de verdade/fato, evidências e histórico de decisões.

## 4. Arquitetura macro de uso de LLM

Visão em camadas, do Firehose de dados ao estado de verdade:

1. Ingestão bruta (Data Firehose)
2. Triagem e pré‑classificação barata
3. Extração de claims
4. Gestão de claims e casos (Truth‑DB)
5. Comitês de verdade/fato e Debunker
6. Decisão, explicabilidade e exposição

LLM aparece de forma crescente de 1 → 6. As seções seguintes detalham regras de uso em cada camada.

## 5. Regras por camada

### 5.1 Ingestão bruta

Responsabilidades:

- Coletar documentos de 5.000+ fontes com cadências heterogêneas.
- Normalizar formatos (HTML, JSON, CSV, PDF) em representações de texto/estrutura estáveis.
- Deduplicar conteúdos óbvios (mesma URL, mesmo hash, espelhos).

Regras de LLM:

- Não usar LLM de alta potência nesta camada.
- Preferir pipelines determinísticos (libs, regex, parsers) para limpeza e extração de texto.
- LLM Tier 3 só em casos extremos (conteúdo muito sujo ou idiossincrático) e sempre com orçamento estrito.

Pontos de atenção:

- Esta camada deve aguentar aumentos de ordem de grandeza no volume sem afetar o custo de LLM.

### 5.2 Triagem e pré‑classificação

Responsabilidades:

- Identificar idioma, tipo (notícia, coluna, tweet, decisão judicial, relatório), canal e tema macro.
- Atribuir prioridade inicial (baixa/média/alta) com base em regras + heurísticas.
- Decidir destino: descartar, armazenar como evidência fria, enviar para extração de claims ou escalar para triagem humana.

Regras de LLM:

- Usar Tier 3 (open‑source/local) ou Tier 2 com prompts minimalistas.
- Saídas sempre estruturadas (JSON com campos: idioma, tipo, tema, prioridade, flags de risco).
- Não invocar comitê nem Debunker aqui.

Critérios de sucesso:

- Alta cobertura (recall) de itens potencialmente relevantes.
- Baixo consumo de tokens por documento.

### 5.3 Extração de claims

Responsabilidades:

- Converter documentos priorizados em uma lista de claims estruturadas.
- Capturar: sujeito, predicado, objeto, tempo, lugar, fonte, contexto mínimo, tipo de claim (fato verificável, opinião, previsão etc.).

Regras de LLM:

- Usar Tier 2 como padrão; Tier 1 é proibido aqui.
- Prompt focado em extração, não em julgamento.
- Entrada: texto (ou trecho relevante) + metadados.
- Saída: lista de claims em JSON.

Decisões críticas:

- Uma claim bem extraída é muito mais importante que um resumo “legal” do documento.
- Claims devem ter uma chave de identidade estável (hash semântico + normalização) para permitir deduplicação ao nível de alegação.

### 5.4 Gestão de claims e Truth‑DB

Responsabilidades:

- Manter catálogo de claims com estados de verdade/fato.
- Associar claims a casos, temas, entidades, pessoas.
- Vincular evidências (documentos, datasets, citações) a cada claim.

Regras de LLM:

- Uso mínimo de LLM; preferir lógica determinística para linking (chaves, similaridade, regras).
- LLM Tier 2 ou 3 apenas para matching semântico complexo, sempre com fallback determinístico.

Decisões críticas:

- A decisão de enviar uma claim a um comitê de verdade é tomada aqui, com base em critérios formais (ver seção 6.3).

### 5.5 Comitês de verdade/fato e Debunker

Responsabilidades:

- Analisar claims selecionadas à luz de todas as evidências disponíveis.
- Produzir propostas de estado de verdade/fato com níveis de confiança e justificativas.
- Detectar contradições, lacunas, narrativas alternativas e possíveis manipulações.

Composição típica de comitê para uma claim relevante:

- Intérprete: garante leitura correta do texto e das evidências.
- Classificador especializado: identifica tipo de claim e requisitos de prova.
- Analistas múltiplos: olham o mesmo conjunto de evidências por ângulos diferentes (institucional, estatístico, jurídico etc.).
- Debunker: procura falhas, cherry‑picking, vieses, contradições internas.
- Decision maker: sintetiza o conjunto e propõe estado de verdade/fato.

Regras de LLM:

- Backbone em Tier 2.
- Tier 1 só permitido em:
  - claims de alto impacto (vida, dinheiro público, eleições),
  - conflitos fortes entre agentes,
  - pedidos explícitos de “revisão de alto rigor” configurados em política.

Entrada dos comitês:

- Snapshot estrutural do caso/claim (estado atual no Truth‑DB).
- Conjunto de evidências resumidas (resumos factuais, não textos integrais).
- Metadados de contexto (origem, priorização, histórico de controvérsias).

Saída dos comitês:

- Proposta de estado: desconhecido, em análise, suportado, verdadeiro, falso, contestado, revisado etc.
- Nível de confiança numérico e qualitativo.
- Lista de evidências chave usadas na decisão.
- Sinalizações do Debunker (riscos, gaps, pontos frágeis).

### 5.6 Decisão final, explicabilidade e exposição

Responsabilidades:

- Persistir o estado de verdade/fato no Truth‑DB.
- Registrar trilha completa de como se chegou à decisão.
- Gerar explicações em linguagem natural sob demanda.
- Alimentar painéis (mentiras em circulação, radar de manipulação, campo de batalha de narrativas, etc.).

Regras de LLM:

- LLM pode ser usado para:
  - traduzir decisões estruturadas em explicações para humanos,
  - adaptar explicações ao contexto (leigo, especialista, “como se eu tivesse 12 anos”).
- É proibido que a camada de explicação mude o estado de verdade/fato.

## 6. Política de custo e tiers de modelo

### 6.1 Tiers de modelo (liga de acesso)

- Tier 3: modelos open‑source / locais
  - Tarefas: limpeza, idioma, classificação macro, matching simples.
  - Meta: custo quase zero; latência baixa.

- Tier 2: modelo comercial otimizado (ex.: GPT “mini”)
  - Tarefas: extração de claims, resumos factuais, primeiras leituras de evidência, comitês padrão.
  - Meta: backbone, bom compromisso custo/qualidade.

- Tier 1: modelo premium
  - Tarefas: arbitragem em casos críticos, síntese de decisões complexas, análise em cenários ambíguos.
  - Meta: uso raro, monitorado, sempre justificado.

### 6.2 Orçamentos e limites

Para cada ambiente (dev, staging, produção) e para cada programa/sprint relevante, devem existir:

- Limites diários de tokens por tier.
- Limites de tokens por claim/caso.
- Alertas quando consumo ultrapassa thresholds.

Quando qualquer limite se aproxima do teto, o sistema entra em modo degradado:

- Prioriza temas/casos críticos.
- Reduz uso de Tier 1.
- Adia análises de baixa prioridade.

### 6.3 Critérios para enviar uma claim ao comitê

Uma claim pode ser elegível para comitê se satisfazer ao menos um dos critérios:

- Alta novidade: informação ainda não coberta por claims existentes.
- Conflito: contradiz estado de verdade/fato já estabelecido.
- Alta sensibilidade: eleições, saúde pública, grandes valores financeiros, segurança.
- Alta autoridade: vinda de órgãos oficiais, tribunais, reguladores, grandes veículos.
- Configuração de usuário/produto: temas marcados como “sempre tratar com rigor máximo”.

Decisões sobre thresholds (ex.: “quão conflitante”, “quão sensível”) são de produto/governança, não de engenharia.

## 7. Segurança, riscos e mitigação

### 7.1 Prompt injection e conteúdo malicioso

Riscos:

- Conteúdo tentando instruir o modelo a ignorar políticas do Inspectah.
- Inserção de comandos no texto para manipular respostas.

Mitigação:

- Instruções de sistema imutáveis e nunca sobrescritas por conteúdo.
- Agentes Debunker com instrução explícita para detectar tentativas de manipulação.
- Sanitização de entrada (remoção de segmentos suspeitos, delimitação de citações).

### 7.2 Viés e narrativas hegemônicas

Riscos:

- Modelos replicando vieses culturais/políticos.
- Sub‑representação de narrativas minoritárias.

Mitigação:

- Múltiplos analistas com “personalidades” epistêmicas diferentes.
- Debunker especializado em detectar enquadramentos e cherry‑picking.
- Painéis de “campo de batalha de narrativas” e “radar de manipulação” alimentados pelas próprias saídas dos comitês.

### 7.3 Erros sistemáticos de modelo

Riscos:

- Erros recorrentes em domínios específicos (jurídico, estatístico, técnico).

Mitigação:

- Testes de regressão com conjuntos de casos canônicos.
- Linhas de base determinísticas (regras, cálculos) para cruzar com LLM.
- Possibilidade de rotular e reprocessar claims com resultados ruins.

## 8. Observabilidade, métricas e SLOs de LLM

Para que este guia seja operável, alguns indicadores são obrigatórios:

- Tokens por claim
- Tokens por caso
- Tokens por tema/topologia (política, saúde, economia etc.)
- Percentual de claims que avançam para comitê
- Percentual de casos que usam Tier 1
- Latência média e p95 de:
  - triagem,
  - extração de claims,
  - comitês.
- Taxa de reversão de decisões de verdade/fato
- Número de incidentes (ex.: decisões graves revertidas por auditoria humana)

SLOs mínimos recomendados (podem ser refinados por sprint):

- X% das decisões em casos críticos revisadas por humano em até Y horas.
- Latência p95 de comitê abaixo de Z segundos para fila estável.
- Uso de Tier 1 abaixo de N% das chamadas de comitê.

## 9. Evolução, experimentação e versões do guia

Este guia não é estático. Qualquer mudança de grande porte em:

- modelo principal,
- política de comitê,
- limiares de budget,
- estrutura de Truth‑DB,

exige uma revisão deste documento.

Experimentos com novos modelos, prompt‑engineering ou stratégy de comitês devem ser feitos sempre em trilhos controlados, com:

- comparação A/B contra baseline,
- métricas de custo e qualidade,
- rollback simples.

## 10. Checklists de aplicação por sprint

S22 (Ingestão 2.0):

- Ingestão bruta sem LLM caro.
- Triagem com Tier 3/Tier 2, saídas estruturadas.
- Deduplicação no nível de documento.

S23 (Agentes de interpretação/classificação):

- Extração de claims com Tier 2 e JSON bem definido.
- Nenhum julgamento de verdade na extração.

S24 (Debunker v0, humano‑no‑loop):

- Composição de comitês seguindo este guia.
- Debunker configurado como papel obrigatório.
- Critérios de escalonamento para humano definidos.

S25 (Governança de verdade/fato):

- Políticas de promoção (desconhecido → em análise → suportado → verdadeiro/falso) alinhadas com fluxo de comitês.
- Budget de tokens por caso/tema implementado.

Programa 1 e além:

- Qualquer feature baseada em LLM (mentiras em circulação, radar de manipulação, campo de batalha de narrativas, etc.) deve:
  - declarar em qual camada deste guia opera,
  - justificar uso de Tier 1 (se houver),
  - definir limites de tokens.

---

Este “Guia de arquitetura de uso de LLM no Inspectah” é a referência definitiva para qualquer decisão de design envolvendo modelos de linguagem no produto. Squads que o seguirem devem conseguir escalar para milhares de fontes, dezenas de milhares de claims e casos complexos mantendo três coisas simultaneamente: contas pagas, latência sob controle e um compromisso rígido com verdade e auditabilidade.

