Inspectah — Sprint 20
Capítulo 2 — Gates de Validação, Métricas e Evidências (Frontend — UX, Auth básica e Observabilidade) — Versão 3

0. One-liner de validação da Sprint 20
A Sprint 20 só é considerada “GO” quando: (a) as UIs de consulta, admin e diagnóstico se comportam como um único produto coerente, (b) nenhuma rota sensível fica exposta sem autenticação básica, (c) fluxos críticos de frontend são observáveis de forma minimamente estruturada, (d) a UI expõe corretamente incerteza/estado de verdade e (e) existe um fluxo de demo e uso interno que o squad e o Conselho assinariam de olhos abertos.

1. Princípios de validação da S20
A validação da Sprint 20 segue alguns princípios explícitos que alinham UX/Auth/observabilidade com o DNA do Inspectah:

1.1 Foco em acabamento, não em escopo novo
A S20 não cria funcionalidades gigantes novas: seus gates miram acabamento, consistência e endurecimento em cima do que foi construído nas S17–S19. Qualquer item que pareça “novo módulo” deve ser empurrado para backlog/Fase 2.

1.2 Nenhuma rota sensível sem auth
Depois da S20, `/admin` e rotas de timeline/raio-X passam a ser tratadas como áreas privadas. “URL secreta” deixa de ser modelo aceitável. Se um gate encontrar acesso direto a rota sensível sem auth, ele falha.

1.3 Incerteza é de primeira classe
A UI não pode vender certezas que o motor não tem. Estados como “em disputa”, “em análise”, “incerto” e “sem evidência suficiente” devem aparecer de forma clara quando o backend assim indicar. Gate que esconder incerteza ou rebatizar incerteza como fato falha.

1.4 Observabilidade mínima, mas real
Fluxos-chave (consulta, navegação admin, abertura de timeline/raio-X) precisam deixar trilha útil para troubleshooting, tanto em ambiente de dev quanto em uso interno/pilotos. Log não precisa ser perfeito, mas tem que existir, ser estruturado e correlacionável com o backend.

1.5 Demo e uso diário contam como teste
Não basta “build passar”. A S20 precisa ser confortável de usar em demos, pilotos internos e trabalho diário do squad. A régua é: o próprio squad confiaria em usar o front numa reunião com o Conselho ou com alguém importante.

1.6 Alinhamento com o pipeline global
Os gates da S20 respeitam a filosofia de ORR/gates do projeto: scorecards estruturados, evidências em diretórios padronizados e decisão GO/NO_GO centralizada no G7. Não há atalho manual para “dar GO na moralzinha”.

2. Métricas de referência da Sprint 20
As métricas abaixo não substituem os gates, mas os alimentam. São medidas observáveis que aparecem em scorecards e ajudam o Conselho a ler rapidamente o estado da S20.

M1 — Build & Teste de Frontend
Descrição: indicador binário se o frontend (S17–S19+S20) compila e passa seus testes/lints no pipeline padrão.
Meta: M1 = 1 (build e testes passam sem erros na branch da S20).

M2 — Coerência de Navegação
Descrição: proporção de cenários de navegação (consulta → evidências → admin → timeline/raio-X → volta) executados com sucesso, sem o usuário “se perder” nem cair em becos sem saída.
Medida: número de cenários bem-sucedidos / total de cenários testados.
Meta: M2 ≥ 0,9.

M3 — Responsividade Básica
Descrição: proporção de telas-chave (consulta, admin dashboard, lista de casos, timeline, raio-X) que se comportam de forma aceitável em resoluções de referência (desktop médio, tablet, mobile).
Medida: score médio tela×viewport normalizado para [0,1].
Meta: M3 ≥ 0,85, com zero “quebra crítica” (layout inutilizável) nas telas-chave.

M4 — Proteção de Rotas Sensíveis
Descrição: proporção de tentativas de acesso a rotas sensíveis sem autenticação que foram corretamente bloqueadas/redirecionadas.
Medida: tentativas_bloqueadas / tentativas_totais em cenários de teste definidos.
Meta: M4 = 1,0.

M5 — Cobertura de Observabilidade de UI
Descrição: porcentagem de eventos/erros definidos como críticos que estão instrumentados e geram logs/minimétricas de frontend com correlação com o backend.
Medida: eventos_instrumentados / eventos_planejados.
Meta: M5 ≥ 0,8.

M6 — Fluidez de Demo/Uso Interno
Descrição: avaliação qualitativa (convertida em score) da experiência de demo ponta a ponta feita pelo squad responsável + PO, em script definido.
Medida: score subjetivo médio em escala 0–1 (0,5 = aceitável, 0,8+ = bom, 0,95+ = excelente).
Meta: M6 ≥ 0,8, com o squad disposto a assinar embaixo publicamente.

M7 — Exposição Correta de Estados de Verdade/Incerteza
Descrição: proporção de cenários em que a UI exibe corretamente estados de verdade/incerteza vindos do backend (aceito, em disputa, em análise, sem evidência suficiente, etc.) sem promover incerteza a fato.
Medida: cenarios_ok / cenarios_totais em bateria específica de testes.
Meta: M7 ≥ 0,9.

3. Tabela-resumo dos Gates da Sprint 20

S20-G0 — Escopo & baseline congelados
S20-G1 — Build & Sanidade de Frontend
S20-G2 — UX & Navegação Coerente
S20-G3 — Responsividade & Acessibilidade Básica
S20-G4 — Auth & Rotas Protegidas
S20-G5 — Observabilidade de UI
S20-G6 — Demo, Uso Interno & Estados de Verdade
S20-G7 — GO/NO_GO da Sprint 20

Os tópicos a seguir detalham cada gate: objetivo, critérios de entrada, critérios de sucesso, métricas usadas e evidências esperadas.

4. Gate S20-G0 — Escopo & baseline congelados
Intenção
Garantir que a Sprint 20 começa de um ponto claro e estável, evitando validar “areia movediça”.

Critérios de entrada
– Capítulo 1 da S20 aprovado pelo squad e pelo PO.
– Branch da S20 criado ou apontado (ex.: `s20_frontend_ux_auth_obs`).
– Commit base (SHA) registrado.

Critérios de sucesso (PASS)
– M1 = 1 (build do frontend a partir do commit base passa em CI local ou remoto).
– Não há issues bloqueadoras herdadas que impeçam os fluxos principais.
– Escopo da S20 congelado em documento (Capítulo 1) com itens fora de escopo claramente marcados.

Evidências esperadas
– `out/scorecards/S20_G0_scope_and_baseline.json` contendo commit base, status de build/teste, lista de pendências conhecidas não-bloqueadoras e decisão PASS/FAIL.
– `out/evidence/S20_G0_scope_and_baseline/` com captura de `git rev-parse`, logs de build/teste e, se necessário, notas de revisão.

Tipo
Manual + script simples.

5. Gate S20-G1 — Build & Sanidade de Frontend
Intenção
Assegurar que o frontend unificado (com as alterações da S20) continua buildando, testando e integrando corretamente com o backend e o ambiente-alvo.

Critérios de entrada
– S20-G0 = PASS.

Critérios de sucesso (PASS)
– M1 = 1 na branch da S20.
– Pipeline de frontend (build + testes + lints básicos) executa com exit 0.
– Nenhuma dependência crítica quebrada (ex.: mudança de API do backend sem adaptação no front).

Evidências esperadas
– `out/scorecards/S20_G1_frontend_build_and_sanity.json` com status de build/teste, resumos de warnings, M1 e decisão PASS/FAIL.
– `out/evidence/S20_G1_frontend_build_and_sanity/` com logs relevantes.

Tipo
Predominantemente automatizado.

6. Gate S20-G2 — UX & Navegação Coerente
Intenção
Verificar se os fluxos principais de navegação se tornaram coerentes, previsíveis e utilizáveis, em especial:
– consulta → visualização de resposta/evidências;
– admin dashboard → fontes → casos;
– admin → caso → timeline → raio-X → volta.

Critérios de entrada
– S20-G1 = PASS.

Critérios de sucesso (PASS)
– M2 ≥ 0,9 em conjunto de cenários de navegação definidos.
– Nenhum fluxo principal termina em becos sem saída óbvios (sem volta possível, sem breadcrumb, sem ação clara).
– Labels, títulos e mensagens alinhados com o vocabulário do Inspectah.
– Diferença visual clara entre área de consulta pública e área de operação/admin.

Medição de M2 (exemplo)
– Definir lista de cenários de navegação (ex.: `s20_nav_1` a `s20_nav_N`).
– Para cada cenário, registrar sucesso (1) ou falha (0).
– M2 = soma(sucessos) / N.

Evidências esperadas
– `out/scorecards/S20_G2_ux_and_navigation.json` com lista de cenários, resultados, M2 e decisão PASS/FAIL.
– `out/evidence/S20_G2_ux_and_navigation/` com capturas de tela e/ou gravações curtas.

Tipo
Misto (execução manual guiada + consolidação automatizada).

7. Gate S20-G3 — Responsividade & Acessibilidade Básica
Intenção
Certificar que as telas-chave se comportam de forma aceitável em resoluções realistas (desktop, tablet, mobile), sem quebras graves de layout e com um mínimo de acessibilidade.

Critérios de entrada
– S20-G2 = PASS.

Critérios de sucesso (PASS)
– M3 ≥ 0,85 em conjunto de telas e viewports de referência.
– Zero “quebra crítica” nas telas de consulta, admin dashboard, lista de casos, timeline e raio-X.
– Existência de pelo menos:
  – foco visível em ações-chave;
  – `aria-label` em botões icônicos importantes;
  – contraste minimamente aceitável em textos principais.

Medição de M3 (exemplo)
– Para cada combinação tela×viewport, registrar um score discreto: 1 = ok; 0,5 = aceitável; 0 = ruim.
– M3 = média dos scores normalizada.

Evidências esperadas
– `out/scorecards/S20_G3_responsiveness_and_basic_accessibility.json` com matriz tela×viewport×score, M3, lista de problemas e decisão PASS/FAIL.
– `out/evidence/S20_G3_responsiveness_and_basic_accessibility/` com capturas em diferentes resoluções.

Tipo
Misto (testes manuais + apoio de ferramentas de dev).

8. Gate S20-G4 — Auth & Rotas Protegidas
Intenção
Garantir que `/admin` e rotas de timeline/raio-X exigem autenticação mínima, com comportamento previsível de sessão e erros.

Critérios de entrada
– S20-G1 = PASS.
– Mecanismo de auth definido e implementado conforme Capítulo 1.

Critérios de sucesso (PASS)
– M4 = 1,0 em conjunto de cenários de acesso indevido planejados.
– Fluxo de login/logout funcional e previsível.
– Comportamento elegante em token inválido/expirado (sessão limpa, redirecionamento para login, mensagem clara).
– Nenhuma mensagem de erro vazando detalhes sensíveis de backend ou infraestrutura.

Medição de M4 (exemplo)
– Definir cenários (acessar `/admin` sem login, timeline sem login, sessão expirada etc.).
– Para cada cenário, registrar 1 (comportamento correto) ou 0 (incorreto).
– M4 = soma(sucessos) / N (meta = 1,0).

Evidências esperadas
– `out/scorecards/S20_G4_auth_and_protected_routes.json` com cenários, M4 e decisão PASS/FAIL.
– `out/evidence/S20_G4_auth_and_protected_routes/` com capturas ou gravações dos fluxos de login/logout e acesso bloqueado.

Tipo
Misto (testes automatizáveis + verificação manual de UX/mensagens).

9. Gate S20-G5 — Observabilidade de UI
Intenção
Verificar se eventos e erros críticos de frontend estão instrumentados de forma útil, permitindo correlação com backend e facilitando debugging em produção interna/pilotos.

Critérios de entrada
– S20-G1 = PASS.

Critérios de sucesso (PASS)
– M5 ≥ 0,8 para o conjunto de eventos/erros marcados como críticos.
– Existência de wrapper/padrão único para logging de eventos/erros no frontend.
– Logs incluem, quando disponível, identificador de correlação com backend.
– Erros de UI renderizados de forma amigável, sem expor stacktrace bruto ao usuário final.

Medição de M5 (exemplo)
– Lista de eventos/erros críticos planejados (consulta ok/falha, admin page open, erro de carregamento de timeline, etc.).
– Para cada item, verificar se está instrumentado, loga de forma estruturada e permite correlação.
– M5 = itens_ok / itens_totais.

Evidências esperadas
– `out/scorecards/S20_G5_frontend_observability.json` com lista de eventos/erros, itens_ok, M5 e decisão PASS/FAIL.
– `out/evidence/S20_G5_frontend_observability/` com trechos de logs de frontend e exemplo de correlação com backend.

Tipo
Misto (inspeção de código + execução de cenários).

10. Gate S20-G6 — Demo, Uso Interno & Estados de Verdade
Intenção
Assegurar que a Sprint 20 resultou em um produto que o squad consegue demonstrar e usar no dia a dia, e que a UI respeita os estados de verdade/incerteza definidos pelo motor.

Critérios de entrada
– S20-G2, S20-G3, S20-G4 e S20-G5 = PASS.

Critérios de sucesso (PASS)
– Execução bem-sucedida de roteiro de demo/documentado cobrindo:
  – consulta pública (pergunta → resposta → evidências);
  – login em admin → visão de fontes/casos;
  – abertura de caso → timeline → raio-X → volta segura.
– M6 ≥ 0,8 no score subjetivo médio atribuído por pelo menos 1 pessoa do squad, PO e, se possível, 1 pessoa convidada interna.
– M7 ≥ 0,9 em bateria de cenários onde o backend retorna estados variados (aceito, em disputa, em análise, sem evidência suficiente) e a UI os exibe corretamente.
– Zero bugs bloqueadores identificados durante a demo (se aparecerem, precisam ser corrigidos e a demo repetida para o gate passar).

Evidências esperadas
– `out/scorecards/S20_G6_demo_internal_use_and_truth_states.json` com roteiro de demo, scores individuais, M6, M7, problemas encontrados/corrigidos e decisão PASS/FAIL.
– `out/evidence/S20_G6_demo_internal_use_and_truth_states/` com gravação da demo ou screenshots narrados, além de exemplos de respostas com estados diferentes de verdade/incerteza.

Tipo
Manual guiado (execução humana com registro estruturado).

11. Gate S20-G7 — GO/NO_GO da Sprint 20
Intenção
Consolidar o estado da Sprint 20 a partir dos gates anteriores e produzir uma decisão única de GO/NO_GO, acompanhada de resumo humano legível.

Critérios de entrada
– S20-G0 a S20-G6 executados (com PASS ou FAIL explícitos).

Critérios de sucesso (PASS = GO)
– Todos os gates S20-G0…S20-G6 com decisão PASS.
– Scorecards e evidências de cada gate presentes nos diretórios esperados.
– Wrap humano (resumo) revisado pelo squad responsável e aprovado pelo PO.

Comportamento em caso de FAIL
– Se qualquer gate tiver FAIL, S20-G7 marca a sprint como NO_GO.
– O resumo humano indica quais gates falharam, motivos principais e próximos passos sugeridos (hotfix, nova sprint, etc.).

Evidências esperadas
– `out/scorecards/S20_G7_go_no_go.json` com estado de cada gate (G0…G6), decisão final GO/NO_GO, carimbo de data/hora e identificação textual de quem rodou o gate.
– `out/evidence/S20_G7_go_no_go/summary.json` + `MANIFEST.json` listando scorecards e evidências usadas na decisão.
– Seção em `docs/sprint_20_orr_summary.md` (ou equivalente) com wrap da sprint sob a ótica dos gates.

Tipo
Automatizado + wrap humano.

12. Relação dos Gates da S20 com o restante do Inspectah
– Os gates da S20 são um recorte específico para validar o frontend nesta sprint, compatível com o pipeline global de ORR/observabilidade.
– A decisão S20-G7 alimenta o histórico de sprints e orienta se o front está realmente pronto para sustentar Fase 2 (Sistema de Blocos completo, Debunker forte, governança e comunidade) sem reescrita estrutural.
– Scorecards e evidências seguem convenções das sprints anteriores (S7, S10, etc.), permitindo auditoria futura e automação.
– Em caso de NO_GO, não há atalhos: a sprint continua em estado pendente até que os gates em FAIL sejam tratados e reexecutados com PASS.

Com este Capítulo 2, a Sprint 20 passa a ter uma régua objetiva de qualidade, ancorada nos princípios do Inspectah (verdade, incerteza explícita, auditabilidade), e um conjunto claro de gates, métricas e evidências necessários para declarar o frontend realmente “GO” em UX, Auth e Observabilidade.

