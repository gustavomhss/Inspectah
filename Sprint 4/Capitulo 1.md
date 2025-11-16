# Inspectah — Sprint 4 — Capítulo 1  
**North Star, Invariantes e Regra do Jogo (versão 10/10)**

> Depois desta sprint, o Inspectah deixa oficialmente de ser um experimento de laboratório e passa a ser uma ferramenta interna confiável para acompanhar **poucas fontes reais prioritárias**, com **evidência completa**, **visão operacional clara** e **consulta humana simples e segura**.

---

## 1. North Star da Sprint 4 (uma frase)

Colocar o Inspectah em operação interna com **3–5 fontes reais P0**, sob **SLOs explícitos**, com **Evidence Vault vivo e auditável** e **Explore mínimo para operadores**, tudo protegido por um **ORR T0–T8 ajustado para dados reais e reprodutível**.

Se qualquer pessoa do time não conseguir repetir essa frase de cabeça, a Sprint 4 não está bem alinhada.

---

## 2. Ponto de partida — estado após a Sprint 3

Ao final da Sprint 3, temos:

- Um **ORR completo T0–T8** operando com fixtures (dados de laboratório).  
- Scorecards e evidências versionadas, com decisão T8 GO/NO_GO automatizada.  
- Um wrap humano registrando objetivo, riscos e próximos passos.  
- Um Inspectah ainda **conectado apenas a dados simulados**.

A Sprint 4 existe para resolver um único gap: **conectar o Inspectah ao mundo real sem perder reprodutibilidade, auditoria e controle de qualidade**.

---

## 3. Modelo mental da Sprint 4

Para esta sprint, o Inspectah é visto como três camadas ligadas por cinco objetos centrais.

### 3.1 Três camadas

1. **Ingestão (Input)**  
   Puxa dados reais de cada Fonte P0 de forma previsível.

2. **Evidência (Truth)**  
   Guarda o que foi visto, de forma íntegra, versionada e auditável.

3. **Exploração (View)**  
   Permite que humanos encontrem e inspecionem evidências com segurança.

### 3.2 Cinco objetos centrais

- **Fonte (Source)** — definição estável da origem (id, tipo, URL, cadência, campos de interesse).  
- **Execução de Coleta (Run)** — tentativa concreta de buscar dados de uma Fonte em um instante.  
- **Item** — unidade de informação extraída de uma Execução (uma notícia, um registro, etc.).  
- **Evidência** — pacote que liga Item ao que foi observado (bruto, extraído, metadados, hash, manifesto).  
- **Consulta** — combinação de filtros + busca usada por humanos para localizar itens e suas evidências.

Se no fim da sprint o time não consegue desenhar esses cinco objetos e explicar como se relacionam, a Sprint 4 falhou.

---

## 4. Invariantes de produto da Sprint 4 (não negociáveis)

Se qualquer invariante abaixo for violado, o T8 desta sprint **não deveria** ser GO.

1. **Nenhum Item P0 sem Evidência completa**  
   Todo Item vindo de fonte P0 deve ter: bruto, extraído, metadados mínimos e hash de integridade.

2. **Toda Evidência P0 é rastreável à Fonte e ao Run**  
   Dado um Item/Evidência, é possível responder: “de qual fonte veio, em qual execução e quando foi coletado”.

3. **Nenhuma Fonte P0 ativa é invisível em métricas e logs**  
   Se a fonte está marcada como ativa, ela aparece claramente na observabilidade.

4. **Explore M0 nunca mostra Item sem caminho para a Evidência**  
   Ver um Item na interface sem conseguir abrir sua evidência é bug de produto.

5. **Fixtures do ORR S4 vêm de dados reais e são versionadas**  
   O ORR continua determinístico, mas alimentado por capturas do mundo real (não por dados inventados).

6. **Quebras relevantes em Fonte P0 são detectadas em tempo finito**  
   Mudanças que causem falhas de coleta ou staleness excessivo aparecem em métricas, logs e scorecards dentro da janela acordada.

7. **Nenhum ajuste estrutural em Fonte P0 é feito apenas em código**  
   A descrição oficial vive no registry; qualquer fonte “especial” fora dele está fora do padrão.

---

## 5. Escopo — o que a Sprint 4 promete (e o que explicitamente não promete)

### 5.1 Escopo IN (compromissos obrigatórios)

1. **Fontes reais P0 configuradas e ativas**  
   - 3–5 fontes reais de domínio público e risco jurídico baixo.  
   - Cada fonte descrita no registry com: id, nome, tipo, localização, cadência alvo, campos de interesse via Field Designer.

2. **Onboarding reproduzível por Operador (sem código)**  
   - Fluxo claro para cadastrar uma nova fonte similar às P0: preencher dados, definir campos, rodar coleta de teste, revisar, ativar.  
   - Tempo alvo de onboarding **p50 ≤ 15 minutos** em ambiente real.

3. **Evidence Vault vivo sob dados reais**  
   - Cada Execução gera Evidências para os Itens encontrados, respeitando os invariantes da seção 4.  
   - Procedimento simples (descrito no Capítulo 2) para listar e localizar evidências por Fonte e intervalo de tempo.

4. **Observabilidade externa mínima por Fonte**  
   - Métricas por Fonte P0: número de coletas, sucessos/falhas, latência, staleness.  
   - Logs explicando erros relevantes (quando começaram, qual erro, qual impacto).  
   - Regra objetiva para classificar Fonte em **ok / degradada / quebrada**.

5. **Explore M0 para operadores**  
   - Um único mecanismo (definido no Capítulo 2) para:  
     - filtrar por Fonte e intervalo de tempo;  
     - buscar por termos de texto;  
     - aplicar filtros simples por campos de interesse;  
     - abrir a Evidência completa de um Item.  
   - Comportamento previsível até um volume moderado (milhares de Itens).

6. **ORR S4 adaptado a dados reais**  
   - Gates T0–T8 atualizados para incorporar fontes reais, Evidence Vault vivo, métricas e Explore M0.  
   - T8 só deve marcar GO se SLOs e invariantes desta sprint estiverem verdes.

### 5.2 Escopo OUT (explicitamente fora)

1. Interface/API pública para usuários externos.  
2. Contas, billing, multi‑tenant ou gestão avançada de permissões.  
3. Integrações específicas com outros sistemas.  
4. Dashboards analíticos/BI avançados ou gráficos complexos.  
5. Escala para grandes quantidades de fontes; foco é em poucas P0 muito bem cuidadas.

---

## 6. Personas e cenários obrigatórios

### 6.1 Personas

1. **Operador Admin (Fonte Keeper)**  
   Cadastra, ajusta e desativa fontes; entende o domínio, não escreve código.

2. **Analista Verificador (Checker)**  
   Usa o Inspectah para confirmar informações específicas, com foco em rapidez e confiança.

3. **Engenheiro de Plataforma / Observabilidade**  
   Garante saúde do sistema conforme novas fontes entram; reage a quedas de qualidade.

### 6.2 Três cenários que precisam funcionar

1. **Onboarding de nova Fonte similar às P0**  
   - Operador segue o fluxo; faz coleta de teste; ajusta campos; ativa.  
   - Analista encontra Itens dessa Fonte no Explore M0 e abre Evidências completas.

2. **Investigação de Item pontual**  
   - Analista recebe um fato com fonte provável e janela de tempo.  
   - Usa filtros e busca; localiza o Item; inspeciona Evidência; decide se confia.

3. **Detecção de problema em Fonte P0**  
   - Fonte falha (timeouts, formato mudou, respostas vazias).  
   - Métricas e logs mostram a queda; ORR reflete o estado; time consegue apontar causa e impacto.

Se qualquer um desses cenários não estiver confiável ao final da sprint, T8 tende a NO_GO.

---

## 7. Métricas, SLOs e experimentos

### 7.1 Métricas principais

1. **onboarding_p50_min** — tempo mediano para cadastrar e ativar uma nova Fonte similar às P0 até surgirem primeiros Itens visíveis.  
2. **detection_latency_p95_min** — tempo entre o dado aparecer na Fonte e ser coletado pelo Inspectah.  
3. **run_success_rate** — % de Execuções de coleta bem‑sucedidas por Fonte em janela definida.  
4. **evidence_completeness_rate** — % de Itens P0 com pacote de Evidência completo (bruto+extraído+metadados+hash).  
5. **explore_query_p95_ms** — tempo p95 de resposta para consultas típicas do Explore M0.

### 7.2 SLOs mínimos para elegibilidade de GO

1. **onboarding_p50_min ≤ 15 min** para Fontes P0 da sprint.  
2. **detection_latency_p95_min ≤ 10 min** para Fontes P0 sob uso normal.  
3. **run_success_rate ≥ 97%** em 24h para Fontes P0 ativas.  
4. **evidence_completeness_rate = 100%** em amostra de N Itens recentes por Fonte P0 (N definido no Capítulo 2).  
5. **explore_query_p95_ms ≤ 800 ms** para consultas simples em volume moderado.

### 7.3 Experimentos canônicos da sprint

1. **Experimento de onboarding cronometrado**  
   Operador faz onboarding de uma nova Fonte similar às P0; o tempo é medido e os passos são avaliados.

2. **Experimento de falha controlada de Fonte**  
   Uma falha é simulada (ou observada) em ambiente controlado; time verifica como métricas, logs e ORR reagem.

3. **Experimento de consulta típica**  
   Analista executa 2–3 perguntas reais no Explore M0; mede latência e clareza da Evidência exibida.

Se esses experimentos não puderem ser executados, ou os resultados forem incompatíveis com SLOs e invariantes, a sprint não está pronta para GO.

---

## 8. Mapa de gates T0–T8 para a Sprint 4

Esta seção liga invariantes e SLOs aos gates do Sprint Playbook.

- **T0 — Descoberta e alinhamento**  
  - Fontes P0 definidas, com donos internos e riscos básicos.  
  - Personas e cenários da seção 6 revisados.

- **T1 — Especificação de dados e invariantes**  
  - Objetos centrais (Fonte, Run, Item, Evidência, Consulta) descritos.  
  - Invariantes da seção 4 formalizados em documentação/checklist.

- **T2 — Validação estática e de configuração**  
  - Registry de Fontes sem inconsistências óbvias e sem segredos em código.  
  - Field Designer cobre todos os campos relevantes das Fontes P0.

- **T3 — Testes com fixtures reais**  
  - Parsers/normalizadores validados contra fixtures derivadas de coletas reais.  
  - Garantia de que pequenas variações de dados não quebram o pipeline.

- **T4 — Goldens estáveis**  
  - Dado um conjunto de fixtures reais, o output normalizado e a Evidência gerada são determinísticos e idempotentes.

- **T5 — Comportamento sob repetição**  
  - Execuções repetidas (modo fixture) não corrompem o Vault nem explodem artefatos de forma silenciosa.

- **T6 — Observabilidade**  
  - Métricas e logs das seções 4 e 7 implementados e cobrindo todas as Fontes P0.  
  - Estados ok/degradada/quebrada inferíveis de forma objetiva.

- **T7 — Integração contínua**  
  - ORR completo roda com fixtures reais em ambiente controlado, sem flutuações arbitrárias.

- **T8 — GO/NO_GO**  
  - Scorecard inclui invariantes, SLOs, resultados de experimentos e DoD.  
  - GO só é aceitável se nada da seção 4 foi quebrado e SLOs da seção 7.2 foram atendidos.

---

## 9. Definition of Ready (DoR) e Definition of Done (DoD)

### 9.1 Definition of Ready

A Sprint 4 só começa de fato se:

1. Lista de Fontes P0 estiver fechada e aceita.  
2. Personas e cenários críticos estiverem compreendidos pelo time.  
3. ORR S3 estiver estável (T0–T8 verdes com fixtures).

### 9.2 Definition of Done

A Sprint 4 só termina com GO se **todas** as condições forem verdadeiras:

1. Entregas de escopo IN concretizadas para Fontes P0.  
2. SLOs mínimos da seção 7.2 atingidos.  
3. Nenhum invariante da seção 4 violado.  
4. ORR T0–T8 rodando limpo com fixtures derivadas de dados reais.  
5. Wrap humano da sprint produzido, registrando decisões, riscos, aprendizados e próximos passos.

---

## 10. Fronteira de confiança após a Sprint 4

Depois da Sprint 4, o Inspectah é confiável para:

- Acompanhar continuamente um pequeno conjunto de Fontes P0.  
- Dizer, com base em métricas e Evidências, se essas Fontes estão saudáveis, degradadas ou quebradas.  
- Permitir que Analistas encontrem e validem Itens específicos com Evidência completa.

Ele **ainda não** é:

- Um catálogo completo de todas as fontes imagináveis.  
- Uma plataforma de análise avançada/BI.  
- Um serviço público em larga escala.

Próximas sprints podem, conscientemente, expandir essa fronteira.

---

## 11. Juramento da Sprint 4 (mantra da equipe)

1. **“Nenhum Item sem Evidência.”**  
2. **“Nenhuma Fonte ativa invisível.”**  
3. **“Nenhuma decisão de GO se não estiver tudo mensurável e rastreável.”**

Se em algum momento do ciclo de desenvolvimento alguma decisão violar esse juramento, o time deve parar, corrigir e só então seguir.

