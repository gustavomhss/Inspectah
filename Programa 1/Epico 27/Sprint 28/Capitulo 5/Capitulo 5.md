# Inspectah — Sprint 28
## Capítulo 5 — Riscos, Dívida, Backlog e Próximos Passos
### E27.1 — CRUD & ON/OFF de Fonte

---

### 5.1 Objetivo deste capítulo

Este capítulo consolida a visão de **riscos**, **dívida técnica** e **backlog de continuidade** da Sprint 28, conectando o que foi feito aqui com o restante do Programa 1 e, em especial, com as próximas etapas do Épico **E27 — Fonte como Cidadã de Primeira Classe da Operação**.

Em termos práticos, Capítulo 5 responde:

- Quais riscos ainda existem mesmo após S28 estar em GO?  
- Que dívidas técnicas foram assumidas de forma consciente?  
- O que foi empurrado para **E27.2/E27.3** (Sprints 29/30) e além?  
- Como garantir que o que foi entregue em S28 continue saudável no tempo (watchers, sanity, monitoração)?

---

### 5.2 Riscos remanescentes após S28 (por categoria)

Mesmo com todos os gates G0–G7 em PASS, algumas frentes permanecem com risco residual. Esta seção os explicita, com foco em transparência e ação futura.

#### 5.2.1 Riscos de produto/experiência

Risco P1 — Console ainda não cobre todos os cenários reais de operação
- Sintoma: S28 focou nos fluxos A–D (criar, desativar, reativar, editar), mais estados extremos simples, mas ainda não cobre:
  - filtros avançados (por domínio + criticidade + modo + estado combinados),  
  - buscas por texto livre com relevância,  
  - visão por "grupos de fontes" (por exemplo, todas as fontes relacionadas a um mesmo tema ou cliente).
- Impacto: operador pode sentir falta de ferramentas mais ricas à medida que o volume de fontes cresce.  
- Mitigação: backlog em E27.2 para evoluir filtros, agrupamentos e UX de navegação.

Risco P2 — Sem trilha de auditoria completa de operações de fonte
- Sintoma: console permite ON/OFF, mas trilha de quem fez o quê, quando e por quê ainda é limitada (além de `state_changed_at` e `state_reason`).  
- Impacto: em incidentes de produção, pode ser difícil reconstruir a sequência exata de decisões humanas.  
- Mitigação: E27.2/E27.3 incluirão camada de auditoria explícita (logs estruturados de ações de operador + quem/onde), além de integração futura com o Truth-DB/Sistema de Blocos.

Risco P2 — UX de formulários ainda básica
- Sintoma: validações em frontend são principalmente de obrigatoriedade e formato simples.  
- Impacto: operadores podem cometer erros de configuração complexa (por exemplo, URLs com parâmetros incorretos) que só aparecem na hora da ingestão, em logs.  
- Mitigação: E27.2 introduzirá validações guiadas por tipo de fonte (wizards/presets) e integração com testes rápidos de conexão.

---

#### 5.2.2 Riscos técnicos — backend & domínio

Risco P1 — Evolução futura do modelo `Source` quebrar APIs existentes
- Sintoma: S28 consolida uma versão de `Source`, mas E27.2/E27.3 certamente vão expandir campos (score de saúde, rating de confiabilidade, vínculos com outros domínios).  
- Impacto: se expansão for feita sem cuidado, pode quebrar Admin API e ingestion scripts.  
- Mitigação:  
  - Adotar versionamento controlado dos schemas (DTOs) e migrações.  
  - Manter testes de contrato (API e domínio) como parte obrigatória de futuras sprints.

Risco P2 — Divergência entre invariantes de domínio e lógica da API
- Sintoma: invariantes vivem em `Source`/serviços, mas a API poderia (no futuro) implementar lógica paralela.  
- Impacto: divergências silenciosas entre operações feitas via scripts diretos e via API.  
- Mitigação:  
  - Continuar reforçando que a **única forma** de mudar `state` em produção é via Admin API.  
  - Manter testes que criam/mutam fontes exclusivamente por rotas públicas.

Risco P2 — Crescimento de volume de fontes e migrações futuras
- Sintoma: com o tempo, tabela de fontes pode crescer significativamente.  
- Impacto: migrações mal planejadas em sprints futuras podem se tornar caras.  
- Mitigação:  
  - Evitar migrações desnecessárias em campos volumosos (ex.: `config`).  
  - Planejar alterações de schema com janelas de migração progressiva onde necessário.

---

#### 5.2.3 Riscos técnicos — ingestão 2.0

Risco P1 — Lógica de elegibilidade duplicada fora do scheduler
- Sintoma: S28 define claramente `get_auto_eligible_sources`, mas nada impede que código futuro crie lógica paralela, por exemplo para "injeção manual" de runs.  
- Impacto: fontes `DISABLED` poderiam voltar a ser ingeridas se outro módulo ignorar `state` e `mode`.  
- Mitigação:  
  - Designar `get_auto_eligible_sources` (ou serviço equivalente) como **fonte única de verdade** para ingestão automática.  
  - Cobrir integrações futuras com testes semelhantes aos de G4.

Risco P2 — Falta de proteção contra corrida na troca rápida de estados
- Sintoma: operador pode alternar `ACTIVE` → `DISABLED` → `ACTIVE` muito rápido.  
- Impacto: dependendo da janela, scheduler pode criar runs que parecem contradizer o estado final esperado.  
- Mitigação:  
  - E27.2/E27.3 podem introduzir restrições mínimas de intervalo entre mudanças de estado, ou comportamento de "debounce".  
  - Monitorar, nas primeiras semanas, logs de ingestão versus mudanças de estado para calibrar.

Risco P3 — Observabilidade de ingestão ainda básica
- Sintoma: logs existem, mas painéis e métricas ainda não foram expandidos especificamente para fontes e estados.  
- Impacto: pode ser mais difícil identificar rapidamente uma fonte que voltou a falhar após reativação.  
- Mitigação:  
  - Usar S28 como base e, em E27.2, criar métricas de ingestão por fonte/estado/mode (Ingressões por fonte/dia, taxa de erro, etc.).

---

#### 5.2.4 Riscos operacionais

Risco P1 — Operadores usando caminhos alternativos para alterar fontes
- Sintoma: scripts manuais de banco, ferramentas de admin genéricas ou até fallback de CLI podem, na prática, editar diretamente `Source`.  
- Impacto: estados e campos fora de invariantes (ex.: `state` incoerente com `state_reason`).  
- Mitigação:  
  - Formalizar política de operação: só Admin API + console podem ser usados em produção.  
  - Logs de auditoria para acessos diretos ao banco, quando aplicável.

Risco P2 — Capacitação insuficiente dos operadores
- Sintoma: S28 introduz conceitos de `mode`, `state`, `criticality` e outras dimensões que precisam ser compreendidas.  
- Impacto: uso incorreto dos estados (ex.: desativar fonte crítica sem entender impacto).  
- Mitigação:  
  - Criar material de treinamento leve baseado nos cenários A–D.  
  - Realizar mais de uma demo/treinamento se o número de operadores crescer.

---

### 5.3 Dívida técnica assumida conscientemente

Nem tudo que é desejável coube em S28. Esta seção explicita dívidas técnicas **intencionais**, ou seja, escolhas conscientes de não fazer algo agora para não travar o épico.

#### 5.3.1 Auditoria avançada de operações em fonte

- Situação atual:  
  - `Source` registra `state`, `state_changed_at`, `state_reason`.  
  - Não há ainda uma entidade formal do tipo `SourceActionLog` com autor, origem, contexto, etc.

- Dívida:  
  - Sem esse log estruturado, a reconstrução de incidentes complexos fica mais manual (correlação de logs de API, etc.).

- Justificativa:  
  - Introduzir trilha de auditoria completa exige decisões de modelo, armazenamento, retenção e privacidade que merecem um capítulo próprio.  
  - Para S28, o foco foi consolidar o básico de CRUD & ON/OFF + ingestão obediente.

- Endereço futuro:  
  - **E27.2**: desenho do modelo de auditoria e endpoints básicos.  
  - **E27.3**: integração com UI (timeline por fonte) e eventual ancoragem em Truth-DB/Sistema de Blocos.

#### 5.3.2 Validações profundas por tipo de fonte

- Situação atual:  
  - Validações simples em API/front sobre obrigatoriedade e formato.  
  - Pouca lógica específica por tipo (ex.: `news_rss` vs. `api_json`).

- Dívida:  
  - Risco de permitir configurações tecnicamente inválidas que só explodem na ingestão.

- Justificativa:  
  - Evitar enfiar toda complexidade de parsing/validação de tipos no escopo da primeira sprint de E27.  
  - Melhor abordar por camadas: primeiro consolidar modelo/console/ingestão, depois afinar por tipo.

- Endereço futuro:  
  - **E27.2**: presets por tipo de fonte (templates de config) e validações mínimas testáveis.  
  - **E27.3**: wizards mais inteligentes e integração com testes de conexão.

#### 5.3.3 Observabilidade refinada de ingestão por fonte

- Situação atual:  
  - Logs e possivelmente algumas métricas herdadas de S22.  
  - Sem dashboards dedicados por fonte/estado/mode.

- Dívida:  
  - Equipe de operação ainda não tem visão "1 clique" de quais fontes falham mais, quais estão desativadas há muito tempo, etc.

- Justificativa:  
  - Evitar misturar novos requisitos de observabilidade com consolidação do fluxo ON/OFF.  
  - Melhor fazer uma rodada de ajustes depois de observar o uso real do console.

- Endereço futuro:  
  - **E27.2**: métricas e painéis iniciais por fonte/estado.  
  - **E27.3**: cruzamento com saúde de ingestão, alertas, integração com squads de Debunker/Truth-DB.

---

### 5.4 Backlog de continuidade (E27.2, E27.3 e além)

Esta seção lista itens que nascem diretamente da Sprint 28 e alimentam as próximas sprints do Épico E27.

#### 5.4.1 Itens candidatos para E27.2 (Sprint 29)

1. Auditoria básica de operações em fonte
- Criar entidade `SourceActionLog` com:  
  - `id`, `source_id`, `action_type` (CREATE/UPDATE/ACTIVATE/DISABLE/DEPRECATE),  
  - `performed_by`, `performed_at`,  
  - `metadata` (campo livre/JSON).  
- Expor rota de leitura (timeline de ações por fonte).  
- Ajustar Admin API para registrar ações no log.

2. Validações guiadas por tipo de fonte (nível 1)
- Para tipos principais (ex.: RSS de notícias, APIs REST), definir conjunto mínimo de campos obrigatórios e validações específicas.  
- Surfacear essas validações tanto na API quanto no front.

3. Métricas básicas por fonte
- Incluir contadores de ingestão por `source_id`, `status` e `state`.  
- Expor métricas em formato compatível com stack de observabilidade existente (ex.: Prometheus).

4. UX de filtros avançados no console
- Implementar filtros combinados (estado + modo + domínio + criticidade).  
- Permitir salvar "visões" de filtros frequentes (por exemplo, "Fontes críticas ativas").

#### 5.4.2 Itens candidatos para E27.3 (Sprint 30)

1. Auditoria avançada + integração com Truth-DB/Sistema de Blocos
- Expandir `SourceActionLog` com possibilidade de geração de eventos/anchors para o Sistema de Blocos.  
- Modelar vínculos entre ações em fonte e blocos de evidência em verdade/fato.

2. Wizards inteligentes de criação de fonte
- Formular flows específicos por tipo de fonte com passos guiados (ex.: testar URL RSS, validar headers de API, etc.).  
- Incluir testes rápidos de conectividade durante o cadastro.

3. Painéis de operação de fontes
- Criar página dedicada no cockpit/admin com visão agregada de fontes:  
  - número de fontes por estado/mode,  
  - taxa de erro de ingestão por fonte,  
  - fontes mais instáveis.  
- Integrar com alertas simples (ex.: fonte crítica falhando repetidamente).

#### 5.4.3 Itens de backlog de longo prazo

1. Políticas automáticas de ON/OFF
- Regras que desativem automaticamente fontes com comportamento crítico (ex.: sequência longa de falhas), com trilha de auditoria claramente registrada.

2. Integração com Debunker e Comitês de Verdade
- Em sprints futuras do Programa Verdade & Interpretação, conectar fontes com reputação, confiabilidade e impacto no Truth-DB.  
- Permitir que decisões de desativar fontes possam ser sugeridas automaticamente por agentes Debunker.

3. Mapeamento entre fontes e "temas"/"casos" do Inspectah
- Evoluir modelo de dados para relacionar fontes com os casos/temas que alimentam, facilitando operações por contexto (ex.: todas as fontes ligadas a um tema específico).

---

### 5.5 Medidas de monitoração e sanity pós-sprint

Para garantir que S28 continue saudável após o merge em `main`, algumas rotinas são recomendadas.

#### 5.5.1 Rotinas semanais

- Rodar (ou agendar) um job que execute scripts equivalentes aos de G5 em ambiente de staging/produção controlada, por exemplo:
  - verificação de fontes cadastradas vs. estados esperados,  
  - mini-bateria de ingestão de teste em fontes de sandbox.

- Verificar logs de ingestão à procura de:
  - fontes `DISABLED` com ingestões recentes (indicaria bug grave),  
  - padrões estranhos (ex.: fonte recém-criada já com falhas contínuas).

#### 5.5.2 Rotinas mensais

- Revisão das fontes `DISABLED` há muito tempo:  
  - decidir se devem ser definitivamente deprecadas ou reativadas.  
- Revisão das fontes `ACTIVE` com alto índice de erro:  
  - criar tickets para ajuste de config ou discussões com responsáveis por essas fontes.

#### 5.5.3 Watchers/alerts sugeridos

- Alertas de ingestão:
  - fonte crítica com N falhas consecutivas em ingestão.  
  - fonte crítica desativada sem justificativa clara em `state_reason`.

- Alertas de configuração:
  - fontes em `state = ACTIVE` mas sem ingestões há muito tempo (sugerindo problema oculto).  
  - fontes em `state = DISABLED` há meses, sem decisão de deprecar.

---

### 5.6 Sumário executivo para o Conselho / ORR

Para fins de revisão por Conselho (Jobs, Kleppmann, Stonebraker, Percy, etc.), a Sprint 28 pode ser resumida assim:

1. **O que S28 entregou de forma concreta**  
   - Modelo `Source` consolidado como entidade de primeira classe.  
   - Admin API `/admin/sources` com CRUD & ON/OFF completo e testado.  
   - Console de Fontes v2 permitindo operação de fontes com UX mínima estável.  
   - Ingestão 2.0 obedecendo `mode` + `state`, com testes de integração cobrindo cenários-chave.  
   - Gates G0–G7 em PASS, com evidências e scorecards sob `out/evidence/` e `out/scorecards/`.

2. **Por que isso é importante para o Programa 1 e E27**  
   - Sem fonte bem modelada e operacionalizada, o Inspectah permanece "cego" ou vulnerável a ingestão caótica.  
   - S28 marca o ponto em que ligar/desligar uma fonte se torna um ato de alto nível, consistente entre UI, API e ingestão.

3. **Onde ainda há trabalho a ser feito**  
   - Auditoria, validações especializadas por tipo de fonte, observabilidade refinada e automação de políticas são capítulos seguintes (E27.2/E27.3).  
   - S28 é deliberadamente "núcleo sólido" e não "solução final".

4. **Critério de sucesso pós-GO**  
   - Operadores usam o console para todas as operações de fonte.  
   - Nenhuma ingestão automática de fonte `DISABLED` é observada em produção.  
   - Feedback da operação é de que a ferramenta reduz fricção em vez de adicioná-la.

---

Com este Capítulo 5, a Sprint 28 fica contextualizada dentro de uma linha contínua de evolução: entrega forte e comprovada agora, riscos conhecidos, dívidas intencionais e um backlog claro que conecta S28 às próximas etapas do Épico E27 e do Programa 1 como um todo.

