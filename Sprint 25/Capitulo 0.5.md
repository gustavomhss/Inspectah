# Sprint 25 — Capítulo 0.5 (v3)
## Console Operacional do Sistema de Camadas & Agent Studio

Versão: v3 — State of the art, alinhado ao Capítulo 0 v3 (anatomia das camadas) e às exigências de Verdade & Governança da Sprint 25.

Este capítulo responde a uma pergunta simples e brutal: **como operar, ajustar e evoluir o Sistema de Camadas sem quebrar o Inspectah e sem transformar o time em refém de script secreto?**

Ele amarra três coisas:

1. A visão de produto do **Console Operacional** (UX, telas, botões, fluxos).  
2. A arquitetura de **APIs e segurança** que sustentam essas telas.  
3. O **Agent Studio**, que é o console do “cérebro” dos agentes (diretrizes, KB, anexos, ferramentas, versões), no mesmo espírito do console de GPT Agents que você já usa, mas com governança séria.

Tudo que está descrito aqui é contrato: Capítulos 1–6 só podem especializar e operacionalizar, não contradizer.

---

### 0.5.1. Personas, papéis e fronteiras

O console não é para “todo mundo”. Ele é para quem pilota a usina de verdade.

Principais personas:

- **Operador de Plantão**: acompanha dashboards, responde a alarmes, dispara reprocessamentos simples e controlados.  
- **Engenheiro de Pipeline**: desenha e ajusta fluxos de camadas, versões de pipeline, shadow mode, A/B.  
- **Curador de Agentes**: cuida do cérebro dos agentes (prompts, KB, anexos, ferramentas, testes, versões).  
- **Curador de Políticas**: define e ajusta políticas de TruthScore, thresholds e regras por tipo de claim.  
- **Revisor Humano**: atua na fila humano‑no‑loop, decide sobre claims críticas.  
- **Auditor / Compliance**: lê tudo, não altera nada.  
- **Admin de Segurança**: gerencia RBAC, permissões, segredos, janelas de mudança.

Essas personas são mapeadas em papéis RBAC, com fronteiras claras:

- `VIEWER`: leitura de quase tudo, zero escrita.  
- `OPERATOR`: executa ações operacionais (reprocessar, responder alertas), mas não toca em agentes, políticas ou pipelines.  
- `PIPELINE_ADMIN`: cria/edita pipelines e versões; não edita prompts nem TruthScore.  
- `AGENT_ADMIN`: edita agentes e KB; não mexe em políticas globais.  
- `POLICY_ADMIN`: edita políticas de Verdade/TruthScore; não edita agentes.  
- `SRE_ADMIN`: foco em observabilidade e incidentes; pode acionar modos de segurança.  
- `SECURITY_ADMIN`: configura RBAC, two‑man rule, janelas de mudança.  
- `SUPERADMIN`: pode tudo, mas todas as ações são extremamente auditadas.

Cada ação crítica (trocar pipeline ativo, alterar política global, publicar nova versão de agente que afeta camadas centrais) exige:

- permissão apropriada,  
- confirmação explícita na UI,  
- e, em muitos casos, **two‑man rule**: aprovação de outro humano com papel compatível.

---

### 0.5.2. Mapa macro do console

O console de admin do Sistema de Camadas é organizado em um menu fixo (lateral ou top‑nav), com módulos:

1. **Dashboard 24/7** — saúde geral do pipeline.  
2. **Dossiês & Claims** — explorer e drill‑down.  
3. **Pipelines & Camadas (Flow Designer)** — desenho e gestão de fluxos.  
4. **Agent Studio** — cérebro dos agentes + KB + ferramentas.  
5. **Debunker Console** — foco na Camada 8.  
6. **Fila Humano‑no‑loop** — operação da Camada 9.  
7. **Políticas & TruthScore** — regras de decisão.  
8. **Observabilidade & Logs** — métricas, logs, alarmes.  
9. **Versões & Experimentos** — shadow mode, A/B, rollback.  
10. **Segurança, RBAC & Auditoria** — quem pode o quê e rastreio de tudo.

Cada módulo tem:

- contrato de API próprio (`/api/admin/v1/...`),  
- modelos de dados coerentes com o Cap.0 v3 (Dossier, Claim, EvidenceBundle, etc.),  
- e comportamento padrão: ações destrutivas exigem confirmação dupla e geram registro de auditoria.

---

### 0.5.3. Dashboard 24/7 — Pulso do Sistema de Camadas

Função: responder em segundos “como o sistema está agora?”

Elementos principais:

- **KPIs globais (últimas 24h, com janela configurável)**:  
  - dossiês processados;  
  - claims criadas;  
  - claims promovidas (C_PROMOTED);  
  - claims marcadas como contestáveis (C_CONTESTABLE);  
  - claims rejeitadas (C_REJECTED);  
  - claims deferidas (C_DEFERRED);  
  - latência mediana e p95 da pipeline ingestão→decisão.

- **Mapa de calor de estados**: distribuição de claims por estado micro (C_NEW, C_PENDING_VALIDATION, C_UNDER_REVIEW, etc.). Clique abre o Explorer filtrado.

- **Throughput por camada**: gráfico em linhas mostrando quantos dossiês/claims passaram por cada camada nas últimas horas/dias. Ajuda a ver gargalos.

- **Alertas ativos**:  
  - aumento de `INTERPRETED_CONFLICT`;  
  - surto de `EVIDENCE_INSUFFICIENT`;  
  - fila humano‑no‑loop acima de limite;  
  - divergência anormal entre pipeline ativo e pipeline em shadow mode;  
  - taxa de erro elevada em um agente ou comitê específico.

Ações na UI:

- clicar em qualquer KPI leva para o Explorer com filtro aplicado;  
- clicar em um alerta abre painel de detalhe (o que, onde, desde quando, impacto esperado) com botão “ver claims/dossiês afetados”;  
- `OPERATOR+` pode marcar alerta como “em investigação” e adicionar nota;
- `SRE_ADMIN` pode criar ou editar regras de alerta a partir desta tela (mas grava no módulo Observabilidade).

Back‑end:

- métricas vêm de Prometheus/Grafana/Loki (ou equivalente), agregadas via API dedicada (`/api/admin/v1/metrics/dashboard`).

---

### 0.5.4. Explorer de Dossiês & Claims — Cirurgia de Precisão

Função: investigar e agir em nível de Dossiê ou Claim.

Componentes:

- **Barra de filtros avançados**:  
  - por `id_dossier`, `id_claim`, `id_fonte`;  
  - por estado macro do Dossiê, estado micro da Claim;  
  - por `tipo_claim`, domínio, sensibilidade, polarização;  
  - por decisão final (PROMOTED, CONTESTABLE, REJECTED, DEFERRED);  
  - por janela temporal (ingestão, decisão).

- **Lista paginada** (modo Dossiê e modo Claim):  
  - colunas configuráveis;  
  - ações de linha: abrir, reprocessar, comparar (legado vs novo), enviar para humano‑no‑loop.

- **Tela de detalhe de Dossiê**:  
  - metadados;  
  - link para raw content (via Evidence Vault);  
  - lista de claims derivadas com estado, tipo e TruthScore resumido.

- **Tela de detalhe de Claim (peça chave)**:  
  - cabeçalho com a claim “em linguagem humana”: sujeito, predicado, objeto, tempo, local, tipo, escopo, decisão;  
  - **timeline de processamento** com as 10 camadas (e transversais), cada uma expansível:  
    - entrada da camada,  
    - saída,  
    - scores gerados,  
    - logs resumidos,  
    - links para outputs completos, prompts/respostas (quando papel permite);  
  - acessos rápidos: abrir no Sistema de Blocos (Truth‑DB), ver bloco/sub‑bloco correspondente.

Ações importantes:

- reprocessar claim:  
  - escolher a partir de qual camada (ex.: reprocessar desde Camada 6, mantendo interpretação e claims);  
  - escolher pipeline alvo (prod, pipeline alternativo, pipeline em teste);
- marcar para revisão humana manual (injeta na fila com motivo estruturado);
- comparar com versões anteriores (ver histórico de `ClaimStateTransition` e `TruthDecisionRecord`).

Back‑end:

- `/api/admin/v1/dossiers`, `/api/admin/v1/claims`, `/api/admin/v1/claims/{id}/timeline`, `/api/admin/v1/claims/{id}/reprocess`.

---

### 0.5.5. Pipelines & Camadas (Flow Designer) — Mapa do Fluxo

Função: desenhar, versionar e operar pipelines de camadas, sem editar código na unha.

UI baseia‑se em grafo visual:

- nós são camadas ou sub‑pipelines;  
- arestas são transições condicionais (ex.: “se sensitivity = CRITICA, envia para Comitê extra + debunker reforçado”).

Elementos da tela:

- **Lista de pipelines**:  
  - por domínio (política, saúde, economia, etc.);  
  - por tipo de entrada (notícia, estatística, declaração, previsão);  
  - status: ACTIVE, SHADOW, EXPERIMENTAL, LEGACY.

- **Editor de pipeline**:  
  - painel esquerdo: grafo com camadas;  
  - painel direito: configurações do pipeline e da camada selecionada.

Configurações por pipeline:

- nome, descrição, domínio;  
- condições de entrada (quais claims/dossiês caem aqui: filtro por `tipo_claim`, `domain`, `sensitivity`…);  
- versão (v1, v2, v3…);  
- política de default: o que acontece se claim não casar com nenhum pipeline específico.

Configurações por camada dentro de um pipeline:

- parâmetros da camada (número de membros de comitê, intensidade do debunker, critérios para chamar humano‑no‑loop);
- flags de logging (quanto do raciocínio guardar);  
- tempo máximo e política de timeout/retry.

Ações principais:

- adicionar/remover camada (somente `PIPELINE_ADMIN+`);  
- criar condição de roteamento;  
- salvar como nova versão (vX+1, sem ativar ainda);  
- simular pipeline com Dossiê/Claim de teste;  
- ativar versão (com two‑man rule e log);
- arquivar versão legacy (sem apagar histórico).

Back‑end:

- `/api/admin/v1/pipelines` (CRUD), `/api/admin/v1/pipelines/{id}/versions`, `/api/admin/v1/pipelines/{id}/simulate`.

---

### 0.5.6. Agent Studio — Console do Cérebro dos Agentes

O Agent Studio é o lugar onde o "cérebro" dos agentes vive: instruções, KB, anexos, ferramentas, testes, versões. A UX deve lembrar um console de GPT Agent, mas com muito mais disciplina.

#### 0.5.6.1. Lista de agentes

Tabela filtrável por:

- tipo (Intérprete, Builder, Comitê‑Member, Debunker, Auxiliar…);  
- camada principal em que atua (2, 3, 4, 7, 8…);  
- status (ATIVO, TESTE, DESABILITADO);  
- versão ativa;  
- domínio (genérico, política, saúde, etc.).

Cada linha mostra:

- nome lógico (ex.: `Interpreter_A_politica_BR`);  
- papel/camada;  
- versão de cérebro (vN);  
- métricas agregadas: latência, taxa de erro, divergência vs pares, número de decisões que influenciou.

Ações rápidas:

- abrir editor;  
- clonar agente (nova variante);  
- desabilitar/habilitar;  
- rodar teste rápido (casos de benchmark predefinidos).

#### 0.5.6.2. Editor de agente (instruções e comportamento)

Quando um agente é aberto, a tela se organiza em abas:

1. **Perfil**: nome, descrição, camada, domínios, tags.  
2. **Instruções (System Prompt)**: área de texto rica, com seções explicitas:
   - Objetivo do agente.  
   - O que ele pode e não pode fazer.  
   - Estilo de resposta e formato de output (contrato de saída, ex.: JSON com campos X/Y/Z).  
   - Tratamento de incerteza (como dizer "não sei" ou "não há evidência").
3. **Limites & Guardrails**:  
   - máximo de tokens;  
   - comportamento em erro (tentar novamente? sinalizar falta de evidência?);  
   - restrições de uso (não inferir intenção, não inventar fonte oficial, etc.).

Ações:

- salvar rascunho;  
- rodar “lint de prompt” (checagem estrutural: exige campos, formatos, disclaimers);  
- comparar com versão anterior (diff visual);  
- enviar para sandbox de teste.

#### 0.5.6.3. KB & anexos por agente (igual GPT Agent, mas versionado)

A aba de KB do agente permite:

- anexar arquivos (PDF, MD, TXT, CSV resumido) por drag‑and‑drop ou file picker;  
- organizar arquivos em pastas/coleções lógicas (ex.: `legislacao_BR`, `guias_IBGE`, `manual_truth_db`);  
- marcar arquivos como sensíveis (acesso restrito, ex.: dados pessoais pseudo‑anônimos);  
- ver status de indexação (indexado, em fila, falhou) e logs.

O Agent Studio precisa suportar **dois níveis** de KB:

- KB específica do agente (coisas só dele);  
- KB compartilhada (coleções globais que podem ser plugadas em múltiplos agentes).

UI típica:

- painel esquerdo: árvore de coleções;  
- painel principal: lista de arquivos com ícone de tipo, tamanho, data, tags;  
- ações: anexar, remover, mover para coleção, marcar sensível.

Restrição importante:

- remover arquivo de KB ativa cujo conteúdo foi usado em decisões recentes deve acionar alerta e exigir justificativa; pode disparar tarefa de revalidação futura.

#### 0.5.6.4. Ferramentas & integrações por agente

A aba de ferramentas define o que o agente pode chamar:

- leitura da Truth‑DB (busca por claims relacionadas, blocos, histórico);  
- acesso a bases oficiais via adaptadores (IBGE, TSE, etc., só leitura);  
- utilitários internos (normalizar datas, unificar moedas, verificar consistência básica);  
- acesso a logs de pipeline (para agentes de inspeção/meta‑análise).

Para cada ferramenta:

- toggle ON/OFF por agente;  
- limites de uso (quantidade de chamadas por job, por minuto);  
- comportamento de erro (falha hard vs fallback com mensagem estruturada).

#### 0.5.6.5. Testes, benchmarks e cenários

Cada agente deve ter um painel de testes:

- casos de benchmark curados (entrada fixa, saída esperada aproximada ou contrato de validação);  
- casos “hardcore” para cada domínio (notícias confusas, dados incompletos, conflito de fontes).

No Agent Studio, o curador pode:

- rodar todos os testes para uma versão de agente;  
- ver pass/fail por caso e métricas agregadas;  
- comparar outputs da versão atual com versões anteriores;  
- gerar relatório para aprovação (por exemplo, para o squad ou conselho).

#### 0.5.6.6. Versionamento, sandbox, promoção e rollback

Fluxo de vida de uma versão de agente:

- edição cria `vN-draft`;  
- ao passar nos testes mínimos, vira `vN-candidate`;  
- após aprovação (talvez multi‑par), vira `vN-prod` (ativa);  
- versões antigas ficam disponíveis para rollback.

Regras:

- promoção de agente que atua em camadas críticas (4, 7, 8, 10) exige ao menos:  
  - testes automáticos OK;  
  - aprovação de Curador de Agentes;  
  - aprovação de pelo menos um PolicyAdmin ou PipelineAdmin, dependendo do impacto.

Cada mudança gera registro em audit trail: quem, quando, de qual versão para qual, com qual justificativa.

#### 0.5.6.7. Guardrails globais de agentes

Há ainda políticas globais no Agent Studio:

- nenhum agente decide sozinho promoção a Fato/Verdade;  
- agentes não podem alterar dados da Truth‑DB diretamente (só sugerir ou classificar);  
- agentes não podem “silenciar” evidência contrária: sempre devem sinalizar conflitos;  
- agentes têm limites globais de recursos para evitar abusos.

Esses guardrails são configurados por `SECURITY_ADMIN` e aplicados transparentemente a todos os agentes.

---

### 0.5.7. KB Global — Biblioteca do Inspectah

Além da KB por agente, o sistema precisa de um **Catálogo Global de Conhecimento**:

- coleções globais: `dados_oficiais_BR`, `ontologia_politica`, `ontologia_saude`, `manual_truth_db`, etc.;  
- metadados: versão, fonte, período de validade, escopo (ex.: legislação eleitoral 2024);  
- política de retenção e expurgo.

O console de KB global deve permitir:

- criar coleções;  
- anexar/remover arquivos;  
- ver quais agentes usam cada coleção;  
- fazer rollout de nova versão de coleção (ex.: `ontologia_politica v4`).

Sempre que uma coleção global usada em produção for alterada, o sistema deve:

- registrar evento de mudança;  
- opcionalmente agendar reprocessamento de claims impactadas (ou pelo menos marcar para inspeção);  
- atualizar testes/benchmarks que dependem daquela KB.

---

### 0.5.8. Debunker Console e Fila Humano‑no‑loop

Esses módulos foram descritos no v2; aqui só amarramos com o Agent Studio e com as políticas.

**Debunker Console**:

- lista claims atualmente sob debunking e claims recentes processadas;  
- para cada claim, mostra:  
  - `DebunkerReport` (pontos fracos, evidências contrárias, hipóteses alternativas);  
  - qual agente de debunking e qual versão geraram o relatório;  
  - link direto para o editor desse agente no Agent Studio.

Ações:

- reprocessar debunking com versão alternativa de agente;  
- marcar claim como "precisa intervenção humana" (vai para Fila Humano‑no‑loop);  
- abrir painel para ajustar somente parâmetros do Debunker para determinado pipeline (sem mexer no agente global).

**Fila Humano‑no‑loop**:

- lista de trabalho priorizada por sensibilidade, impacto, SLA;  
- cada item mostra motivo pelo qual chegou na fila (divergência de comitês, debunker flag alto, política exige humano, envio manual);  
- revisão humana tem acesso a timeline completa, EvidenceBundle, CommitteeReviewBundle, DebunkerReport, e pode escrever `HumanReviewRecord`.

Tudo que um humano decide também alimenta o Agent Studio e as políticas como dado de treinamento/meta‑análise.

---

### 0.5.9. Políticas & TruthScore — Painel de Verdade

O painel de políticas permite configurar:

- pesos e thresholds da função `TruthScore` por `tipo_claim` e domínio;  
- políticas da matriz 5D (Tempo, Fonte, Impacto, Reversibilidade, Conflito) integradas no score;  
- regras de roteamento obrigatório para humano/debunker em cenários de alto risco.

A UI precisa ter:

- tabela de políticas por tipo de claim;  
- sliders ou campos numéricos para pesos;  
- thresholds de promoção/contestável/rejeição/deferimento;
- botão “simular política” em conjunto de claims históricas (sem gravar nada);
- histórico de versões de política e diff entre versões.

Somente `POLICY_ADMIN+` mexe aqui, com two‑man rule para mudanças em domínios sensíveis (ex.: política, saúde pública).

---

### 0.5.10. Observabilidade, Logs e Incidentes

A aba de Observabilidade é onde SRE e produto entendem o comportamento real do Sistema de Camadas:

- métricas por camada: throughput, latência, erro, distribuição de estados;  
- métricas por pipeline: quantas claims processadas, quantas promovidas/contestáveis/rejeitadas, tempo médio de decisão;  
- métricas por agente: taxa de erro, divergência vs pares, quantidade de decisões influenciadas.

A UI permite:

- filtrar por intervalo de tempo, pipeline, camada, agente;  
- marcar eventos (deploys, mudança de política, promoção de agente) e vê‑los “anotados” nos gráficos;  
- abrir logs relacionados a um período de anomalia com um clique.

Incidentes:

- qualquer anomalia relevante pode ser marcada como incidente;  
- incidente tem timeline, owner, notas, ações tomadas;  
- incidente sempre referencia claims, pipelines, agentes e mudanças correlatas.

---

### 0.5.11. Versões, Experimentos & Shadow Mode

Este módulo gerencia convivência entre legado e novo, e entre versões de pipeline.

Recursos:

- lista de pipelines com suas versões, status (ACTIVE, SHADOW, LEGACY, EXPERIMENTAL);  
- criação de experimentos (A/B) definindo fatias de tráfego (ex.: 90% v2, 10% v3 em shadow);  
- comparação de resultados (qualidade de decisão, latência, contestáveis, incidentes).

Regras de segurança:

- promoção de uma versão para ACTIVE exige:  
  - scorecards de experimento satisfatórios (gates da S25);  
  - aprovação dupla (PipelineAdmin + PolicyAdmin ou equivalente);  
  - registro de mudança com justificativa.

Rollback:

- deve ser um botão claro: “Reverter pipeline X para versão Y”, com confirmação dupla;  
- ao reverter, sistema marca claims recentes processadas pela versão problemática para possível revalidação.

---

### 0.5.12. Segurança, RBAC e Auditoria — Parede de Proteção

Toda ação no console passa por:

- autenticação forte (idealmente SSO corporativo + MFA);  
- autorização via RBAC;  
- logging de auditoria.

Audit trail registra:

- quem fez;  
- o que mudou (antes/depois);  
- quando;  
- onde (módulo/tela);  
- por quê (justificativa quando exigida).

Consultas de auditoria:

- por usuário;  
- por recurso (agente, pipeline, política, claim);  
- por período;  
- por tipo de ação (deploy, rollback, alteração de política, reprocessamento em massa).

---

### 0.5.13. Amarração final com o Capítulo 0 v3

O Capítulo 0 diz **o que** o Sistema de Camadas é: Dossiê, Claim, estados, camadas, comitês, Debunker, humano‑no‑loop, TruthScore.

O Capítulo 0.5 v3 diz **como** humanos e times de engenharia interagem com esse sistema:

- como enxergam o que está acontecendo;  
- como investigam decisões;  
- como mexem no cérebro dos agentes (prompts, KB, anexos) de forma intuitiva, attachando arquivos como em um GPT Agent, porém com versionamento, RBAC e rollback;  
- como mudam fluxos e políticas sem derrubar tudo;  
- como experimentam com versões novas sem sacrificar segurança;  
- como corrigem erros, aprendem com eles e melhoram.

Este capítulo está completo quando qualquer pessoa do time, ao ser perguntada “como eu faria X no Sistema de Camadas?”, consegue responder apontando para uma tela, um botão e um fluxo descritos aqui — sem precisar inventar nada fora do console oficial.

