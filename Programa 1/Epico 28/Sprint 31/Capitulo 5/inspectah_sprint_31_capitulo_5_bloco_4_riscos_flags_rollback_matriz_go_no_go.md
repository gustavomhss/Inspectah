# Inspectah — Sprint 31 (E28-S3)
## Capítulo 5 — Bloco 4: Riscos, Feature Flags, Rollback & Matriz GO/NO-GO

### 5.21 Por que explicitar riscos e mecanismos de controle

Provider-first + Console de Fontes v2 não é só mais um módulo: ele encosta em **custo recorrente**, **cobertura de informação** e na **camada de verdade** do Inspectah.

Isso traz uma consequência óbvia:

> Não existe Sprint 31 “segura” sem mecanismos claros de **controle de risco**.

Este bloco faz quatro coisas:

1. Nomeia os **riscos remanescentes** pós-S31 (mesmo com todos os gates verdes).
2. Define **feature flags** que permitem ligar/desligar partes da S31 sem cirurgia aberta no código.
3. Desenha um **plano de rollback** simples, executável em minutos, não em dias.
4. Amarra tudo isso em uma **matriz GO / GO_WITH_WARNINGS / NO_GO**, usada no ORR para tomar decisão honesta.

---

### 5.22 Riscos principais pós-S31

Mesmo com G0..G5 em PASS, a S31 deixa alguns riscos objetivos. Eles não invalidam a sprint, mas precisam ser **explícitos**.

#### Risco R1 — Dependência de provider externo (contrato, TOS, estabilidade)

- **Descrição**: Providers de news/social podem mudar TOS, limites de uso, formato de payload ou estabilidade sem aviso amigável.
- **Impacto**:
  - interrupção de ingestão para o domínio piloto;  
  - lacunas em cobertura de notícias;  
  - necessidade de ajustes rápidos em clients/normalizer.
- **Mitigação na S31**:
  - abstração via `base_client` + `Raw*` + `normalizer`;  
  - runbook `rb_incidente_provider_api.md` com steps claros de diagnóstico/ação;  
  - uso inicial apenas em perfis-piloto (flag `s31_provider_pilot_profiles_only`).

#### Risco R2 — Custo maior que o previsto (explosão de calls/volume)

- **Descrição**: Configuração agressiva de perfis, crescimento de volume ou bugs de scheduler podem causar uso de API muito acima do planejado.
- **Impacto**:
  - aumento abrupto de custo operacional;  
  - necessidade de apagar incêndio de budget em vez de focar em valor de produto.
- **Mitigação na S31**:
  - campos explícitos de `budget_limit_calls` e afins em `IngestionProfile`;  
  - métricas por perfil (`budget_usage_ratio`, calls, itens);  
  - runbook `rb_custo_explodindo_ingestao.md`;  
  - piloto limitado a poucos perfis relevantes (não ligar “mundo inteiro” de primeira).

#### Risco R3 — Cobertura enviesada ou incompleta

- **Descrição**: Provider pode cobrir melhor alguns países/temas do que outros, levando a um recorte de mundo enviesado se usado sozinho.
- **Impacto**:
  - viés na visão de mundo do Inspectah para o domínio piloto;  
  - dificuldade em avaliar verdades/fatos quando fontes relevantes não estão representadas.
- **Mitigação na S31**:
  - uso de provider-first **como complemento**, não substituto imediato de fontes legadas;  
  - Cenário E2E 4 (legado vs provider) explícito;  
  - plano de migração incremental em `S31_G4_legacy/migration_plan.md`.

#### Risco R4 — Bugs de dedupe/normalização

- **Descrição**: Erros na heurística de dedupe ou na normalização podem:
  - gerar duplicatas em massa;  
  - ou, pior, colapsar conteúdos distintos num único `ContentItem`.
- **Impacto**:
  - distorção de métricas de volume;  
  - perda de granularidade de informação;  
  - dificuldade de auditoria em Programas 2–3.
- **Mitigação na S31**:
  - `dedupe_service` explícito, com testes unitários e amostras em `dedupe_sample.json`;  
  - cenários de ingestão piloto com inspeção manual;  
  - registro de chaves usadas para dedupe (provider_id, external_id, hashes, etc.).

#### Risco R5 — Divergência UI ↔ realidade (Console mostra outra coisa)

- **Descrição**: Bugs na UI ou atraso nas métricas podem fazer o Console de Fontes mostrar estado “saudável” quando o backend está com problemas (ou vice-versa).
- **Impacto**:
  - operadores tomam decisões erradas;  
  - incidentes passam despercebidos ou são exagerados.
- **Mitigação na S31**:
  - definição clara de quais métricas a UI consome;  
  - uso dos mesmos contadores de G2/G3 nas telas de perfil;  
  - runbook de operação do Console descrevendo limitações e sinais de defasagem.

#### Risco R6 — Pressão para escalar antes da hora

- **Descrição**: Depois que piloto funciona, é tentador ligar provider-first em mais perfis/países/temas sem reforçar infraestrutura, monitoria e custos.
- **Impacto**:
  - perda de controle sobre custo e qualidade de ingestão;  
  - backlog de dívidas técnicas se acumulando.
- **Mitigação na S31**:
  - flag `s31_provider_pilot_profiles_only` explicitamente documentada;  
  - treinamento em runbooks reforçando que escala adicional exige decisão de produto/arquitetura;  
  - recomendação no ORR para expansão gradual.

Esses riscos devem aparecer resumidos em `sprint_31_orr_summary.md`, Seção “Riscos remanescentes & mitigação”.

---

### 5.23 Feature flags da Sprint 31

Em vez de depender de toggles improvisados no código, a S31 define um conjunto explícito de **feature flags** para controlar o rollout.

#### Flag F1 — `s31_provider_ingestion_enabled`

- **Escopo**: ambiente (dev / staging / prod).
- **Efeito**:
  - quando OFF: scheduler de provider-first não cria jobs; apenas runs manuais muito específicos podem ser permitidos (configurável);  
  - quando ON: scheduler considera perfis `ACTIVE` e enfileira jobs conforme cronograma.
- **Uso típico**:
  - ON em dev;  
  - ON em staging para perfis-piloto;  
  - em prod, inicialmente ON só se `s31_provider_pilot_profiles_only` também estiver ativa.

#### Flag F2 — `s31_console_v2_enabled`

- **Escopo**: ambiente e/ou papel de usuário.
- **Efeito**:
  - quando OFF: páginas do Console v2 são ocultadas ou mostram aviso de “em construção”;  
  - quando ON: Console v2 é acessível para os papéis autorizados.
- **Uso típico**:
  - ON em dev;  
  - ON em staging para operadores selecionados;  
  - em prod, ON inicialmente apenas para time interno / Truth Ops.

#### Flag F3 — `s31_provider_pilot_profiles_only`

- **Escopo**: ambiente.
- **Efeito**:
  - quando ON: apenas um conjunto whitelisted de perfis (pilotos BR news + 1 social) pode ser executado;  
  - quando OFF: qualquer perfil `ACTIVE` pode ser rodado, sujeito a outras regras.
- **Uso típico**:
  - ON por padrão em staging e prod durante o piloto;  
  - avaliação de desligar gradualmente à medida que sprints futuras consolidarem provider-first.

#### Flag F4 — `s31_p2_p3_provider_sources_allowed`

- **Escopo**: ambiente.
- **Efeito**:
  - quando OFF: Programas 2–3 ignoram ContentItems com `provider_id` em ambientes sensíveis;  
  - quando ON: P2–P3 consomem providers normalmente.
- **Uso típico**:
  - ON em dev;  
  - ON em staging para casos piloto;  
  - em prod, ON apenas quando o Conselho estiver confortável com impacto na camada de verdade.

Essas flags devem ser descritas em:

- Cap.3 (filemap/config);  
- Cap.5 (este bloco);  
- runbooks relevantes (como ligar/desligar);  
- se existir, em um arquivo central de flags (ex.: `config/feature_flags.yml`).

---

### 5.24 Plano de rollback da Sprint 31

Rollback aqui significa: **voltar a um estado conhecido e seguro**, sem remover o código da S31, mas reduzindo seu impacto.

#### Rollback Nível 1 — Frear ingestão provider-first

Objetivo: parar ingestão provider-first, mantendo o resto do Inspectah estável.

Passos típicos:

1. Ligar `s31_provider_ingestion_enabled = OFF` no ambiente afetado.  
2. Opcionalmente, marcar perfis provider-first críticos como `PAUSED`.  
3. Verificar que o scheduler não está mais enfileirando jobs de provider-first.  
4. Validar que ingestão legada continua rodando (usar scripts/gates derivados de G4).

#### Rollback Nível 2 — Congelar Console v2 em modo read-only

Objetivo: evitar ações arriscadas pelo Console enquanto o backend é estabilizado.

Passos típicos:

1. Manter `s31_console_v2_enabled = ON`, mas aplicar config de **read-only** para operadores (ou subset de rotas).
2. Esconder ou desabilitar botões de `Rodar agora`, criação/edição de perfil para usuários comuns.
3. Garantir que operações críticas ainda podem ser feitas via scripts por time técnico, se necessário.

#### Rollback Nível 3 — Isolar providers da cadeia de verdade (P2–P3)

Objetivo: garantir que problemas de ingestão provider-first não contaminem Programas 2–3.

Passos típicos:

1. Definir `s31_p2_p3_provider_sources_allowed = OFF` em ambientes sensíveis.
2. Confirmar que pipelines de P2–P3 estão ignorando ContentItems com `provider_id` (logs, métricas).  
3. Manter ingestão provider-first em dev/staging para debugging, se desejado.

#### Rollback Nível 4 — Recuo emergencial (não recomendado como rotina)

Objetivo: em caso de bug crítico de migrations ou modelo, voltar ao estado pré-S31.

Passos de alto nível:

1. Restaurar backup de banco pré-S31 (ou snapshot).  
2. Garantir que migrations S31 não são reaplicadas automaticamente em prod sem revisão.  
3. Tratar esse caminho como **último recurso**, associado a incidente grave.

Importante: o plano oficial da S31 privilegia **correções forward** sempre que possível. Rollback de migrations só entra em jogo em incidentes de alta gravidade.

---

### 5.25 Matriz GO / GO_WITH_WARNINGS / NO_GO

A decisão final do ORR usa uma matriz simples, baseada em três eixos:

1. Estado dos **gates G0..G5**.
2. Resultado dos **cenários E2E** (5.3–5.6). 
3. Situação dos **riscos R1..R6** e das flags F1..F4.

#### 5.25.1 Critérios para GO

A S31 recebe **GO** se, e somente se:

1. Todos os gates S31-G0..G5 estão em `PASS`, ou em `WARN` com justificativas muito claras e impacto limitado.
2. Os cenários E2E:
   - C1 (ingestão piloto) e C2 (Rodar agora) funcionam sem falhas graves;  
   - C3 (caso piloto P2–P3) funciona ao menos para um caso real;  
   - C4 (legado vs provider) não mostrou regressões graves.
3. Riscos R1..R6:
   - estão documentados;  
   - têm mitigação ativa;  
   - não há risco crítico ignorado.
4. Feature flags configuradas para rollout controlado, por exemplo:
   - em staging: `s31_provider_ingestion_enabled = ON`, `s31_provider_pilot_profiles_only = ON`, `s31_console_v2_enabled = ON`, `s31_p2_p3_provider_sources_allowed = ON`;  
   - em prod: provider-first ligado apenas para pilotos BR, Console v2 visível para operadores internos, P2–P3 consumindo providers sob escopo restrito.

O resumo de ORR deve então registrar um GO condicionado ao **escopo exato de rollout**.

#### 5.25.2 Critérios para GO_WITH_WARNINGS

A S31 recebe **GO_WITH_WARNINGS** quando:

1. Todos os gates rodaram, mas algum gate não-crítico está em `WARN` com impacto moderado (ex.: UX limitada na UI, métricas ainda rústicas).
2. Algum cenário E2E apresentou limitações, mas o caminho dourado do domínio piloto funciona (ex.: C3 funciona apenas para certos tipos de caso; C4 mostra divergências aceitáveis entre legado e provider).
3. Há riscos relevantes (ex.: custo mais volátil que o ideal), mas com mitigação clara via flags e runbooks.

Nesse caso, o rollout é mais conservador:

- provider-first ligado apenas em dev/staging;  
- ou ligado em prod **só** para perfis-piloto, com flags F1–F4 configuradas de forma protetiva;  
- uma sprint futura deve carregar explicitamente as melhorias necessárias para sair de GO_WITH_WARNINGS para GO pleno.

#### 5.25.3 Critérios para NO_GO

A S31 recebe **NO_GO** quando qualquer uma das condições abaixo é verdadeira:

1. Gate crítico (G2, G3 ou G5) está em `FAIL` sem correção pronta e testada.
2. Um ou mais cenários E2E falham de forma grave, por exemplo:
   - C1: ingestão piloto não gera ContentItems corretos;  
   - C2: fluxo “Rodar agora” é inconsistente ou perigoso;  
   - C3: Programas 2–3 não conseguem consumir providers de maneira estável;  
   - C4: regressão explícita em ingestão legada.
3. Riscos críticos identificados (ex.: custo fora de controle, dependência de provider sem mitigação) sem plano plausível de mitigação nas próximas semanas.

Nesse cenário:

- provider-first permanece restrito a dev (e, no máximo, staging sob forte limitação de escopo);  
- flags F1–F4 devem ser configuradas para isolar a S31 de ambientes sensíveis;  
- um mini-épico ou sprint subsequente precisa ser aberto especificamente para atacar os problemas bloqueadores.

---

### 5.26 Resultado esperado deste bloco

Com o Bloco 4, o Capítulo 5 fecha o ciclo da Sprint 31:

- os **riscos** de provider-first + Console v2 estão nomeados e com mitigação pensada;
- há um conjunto explícito de **feature flags** para ligar/desligar capacidades sem drama;
- existe um **plano de rollback em níveis**, documentado e acionável em minutos;
- o ORR ganha uma **matriz clara** de GO / GO_WITH_WARNINGS / NO_GO, baseada em fatos (gates, cenários, riscos) e não em intuição.

Isso garante que a S31 não é apenas um salto técnico, mas um avanço controlado na operação real do Inspectah para o domínio piloto de notícias BR, pronto para ser expandido em sprints futuras do Épico E28.