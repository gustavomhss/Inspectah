# Sprint 21 — Capítulo 2 (v2)
## Gates, Validação e Evidências do Console de Fontes

### 1. Papel deste capítulo na Sprint 21

O Capítulo 1 da Sprint 21 define o “porquê” da sprint: o Console de Fontes como fundação da onda 21–25. Este Capítulo 2 define o “como sabemos que chegamos lá”. Ele transforma objetivos em gates verificáveis, com critérios objetivos de entrada e saída, artefatos obrigatórios e pontos claros de automação e revisão humana.

A filosofia aqui é simples e rígida:

- Nada de “parece pronto”: cada gate precisa ser comprovado por evidências em arquivos reais do repositório.
- Nada de “depende de quem lê”: critérios de PASS/FAIL devem ser tão objetivos quanto possível.
- Nada de “uma única checada”: adotamos redundância tripla também na validação da sprint (automação + revisão interna + revisão externa).

Este capítulo é o contrato de validação do Squad 1 com o restante do projeto. Se este documento estiver bem desenhado e implementado, qualquer pessoa poderá abrir o repositório, rodar os scripts da sprint e chegar à mesma conclusão sobre o status da Sprint 21.

### 2. Arquitetura dos gates S21_G0…S21_G8

A Sprint 21 será validada por uma família de gates S21_G0 a S21_G8, executados em ordem lógica. Cada gate cobre um aspecto específico do Console de Fontes, mas todos juntos formam uma definição de pronto única para a sprint.

Ordem conceitual dos gates e suas responsabilidades:

- S21_G0 — Contexto e escopo consolidados.
- S21_G1 — Ontologia de fontes definida.
- S21_G2 — Modelo de dados e ciclo de vida especificados.
- S21_G3 — Fluxos administrativos (CRUD de fontes) definidos.
- S21_G4 — Ganchos para Debunker, contestação e redundância incorporados.
- S21_G5 — Contratos formais com as S22–S25.
- S21_G6 — Cenários de uso e casos de teste conceituais.
- S21_G7 — Scorecard de qualidade e risco do Console de Fontes.
- S21_G8 — Wrap final da Sprint 21 e decisão GO/NO-GO.

Dependências mínimas entre gates:

- S21_G0 é pré-requisito para todos os outros.
- S21_G1 deve estar em PASS antes de S21_G2, S21_G3, S21_G4 e S21_G6.
- S21_G2 é pré-requisito para S21_G3 e S21_G4.
- S21_G3 e S21_G4 alimentam S21_G6 e S21_G5.
- S21_G5 e S21_G6 alimentam S21_G7.
- S21_G7 alimenta S21_G8.

Na implementação, scripts específicos (bin/s21_gX_*.sh) devem respeitar essa ordem lógica, e um wrapper de sprint (por exemplo, bin/s21_all_gates.sh) pode orquestrar a execução sequencial.

### 3. Camadas de validação (redundância tripla)

Cada gate da Sprint 21 deve, idealmente, passar por três camadas de validação complementares:

1. Validação automatizada
   - Script dedicado em bin/s21_gX_nome_do_gate.sh.
   - Checagens mínimas: existência de arquivos obrigatórios, ausência de TODOs conhecidos, formato básico de JSONs e consistência estrutural simples (por exemplo, campos obrigatórios presentes, estados esperados declarados).
   - Resultado consolidado em um scorecard JSON sob out/scorecards/.

2. Revisão cruzada dentro do Squad 1
   - Pelo menos duas pessoas do Squad 1 revisam os artefatos principais do gate.
   - Foco: clareza de definição, ausência de contradições com o Capítulo 1, coerência entre documentos da sprint, aderência ao DNA do Inspectah e às decisões de Fase 1 versus Fase 2.
   - Resultado: comentários registrados em arquivos de evidência em out/evidence/S21_GX_*/ e campos reviewers_internal no scorecard.

3. Revisão externa (squads impactados e/ou conselho)
   - Pelo menos um revisor externo diretamente impactado pelo gate (por exemplo, alguém do Squad 2 para contratos de ingestão, do Squad 3 para ontologia, do Squad 4 para ganchos de Debunker ou do Squad 5 para governança).
   - Em gates críticos (S21_G1, S21_G2, S21_G4, S21_G5, S21_G8), pelo menos um membro do conselho pode ser envolvido.
   - Resultado: campos reviewers_external e external_notes no scorecard.

Formato mínimo padrão dos scorecards JSON:

- gate_id (string)
- status ("PASS" | "FAIL" | "PARTIAL")
- automated_checks: { status, details }
- reviewers_internal: [ { name, role, verdict } ]
- reviewers_external: [ { name, squad_or_board, verdict } ]
- risk_level ("low" | "medium" | "high")
- notes (string livre)
- ts_last_update (timestamp)

### 4. Definição detalhada dos gates

#### S21_G0 — Contexto e escopo consolidados

Objetivo
Garantir que o contexto, os objetivos e o escopo da Sprint 21 estão cristalinos, alinhados com o DNA do Inspectah e com a decisão de separar Fase 1 de Fase 2.

Escopo
Cobre o Capítulo 1 da Sprint 21 e qualquer anexo que defina o que entra e o que fica fora da sprint em relação a reputação avançada, blockchain automático, Sistema de Blocos completo e cadastros públicos.

Critérios de entrada
- Visão macro da sequência 21–25 definida.
- Fase 2 já descrita como blueprint separado em documentos de Sistema de Blocos.

Critérios de saída (DoD do gate)
- Arquivo docs/sprint_21_capitulo_1.md existe, sem seções vazias, sem TODOs e sem inconsistências com documentos mestres de produto.
- Escopo e fora de escopo estão explícitos, com exemplos concretos.
- Papel do Squad 1 está bem definido.
- Pelo menos um revisor do conselho registra PASS para clareza e alinhamento.

Artefatos obrigatórios
- docs/sprint_21_capitulo_1.md.
- docs/sprint_21_capitulo_2_gates.md (este capítulo), referenciando o Capítulo 1.
- out/scorecards/S21_G0_contexto.json.
- out/evidence/S21_G0_contexto/summary.json e MANIFEST.json.

Automação esperada
- Script: bin/s21_g0_contexto.sh.
- Comportamento: verificar existência de docs/sprint_21_capitulo_1.md, ausência de palavras-chave de TODO, existência de scorecard JSON com status preenchido. Em caso de PASS, exit 0.

Riscos
- Ambiguidade de escopo pode vazar para gates posteriores, gerando retrabalho em S21_G5 (contratos) e S21_G8 (wrap).

#### S21_G1 — Ontologia de fontes definida

Objetivo
Estabelecer uma ontologia canônica de fontes no Inspectah: tipos, atributos mínimos e relação com temas, casos e timelines.

Escopo
Cobre a definição textual de fonte, a taxonomia de tipos e os atributos mínimos/variáveis por tipo. Deve incluir exemplos mapeando domínios distintos, como:
- Notícias políticas e fatos políticos.
- Fofocas e notícias de celebridades.
- Resultados esportivos (jogos, campeonatos, rankings).
- Eventos climáticos (tempestades, furacões, ondas de calor).
- Mandatos políticos, projetos de lei e obras públicas.
- Fatos científicos (papers, resultados de estudos, consensos oficiais).

Critérios de entrada
- S21_G0 em PASS.

Critérios de saída
- Arquivo docs/sprint_21_ontologia_fontes.md descrevendo:
  - Definição genérica de fonte.
  - Lista de tipos de fonte suportados na Fase 1.
  - Campos obrigatórios e opcionais por tipo (nome, descrição, domínio temático, formato, protocolo, confiabilidade declarada, etc.).
  - Relação entre tipos de fonte e temas/casos/timelines do Inspectah.
- Exemplos concretos cobrindo todos os domínios listados no escopo.
- Revisão interna do Squad 1 e revisão externa de, pelo menos, alguém do Squad 3 (Interpretação e Classificação).

Artefatos obrigatórios
- docs/sprint_21_ontologia_fontes.md.
- out/scorecards/S21_G1_ontologia.json.
- out/evidence/S21_G1_ontologia/ contendo snapshot da versão do documento e, opcionalmente, uma versão JSON estruturada da ontologia (por exemplo docs/sprint_21_ontologia_fontes.json).

Automação esperada
- Script: bin/s21_g1_ontologia_fontes.sh.
- Comportamento: verificar presença do documento principal, checar que todos os domínios obrigatórios aparecem e que existe um JSON auxiliar (se adotado). Gerar scorecard em PASS apenas se a ontologia cobrir todos os domínios mínimos.

Riscos
- Ontologia fraca ou incompleta compromete diretamente a especificação da Sprint 23 e a clareza de evidências em Sprint 25.

#### S21_G2 — Modelo de dados e ciclo de vida das fontes

Objetivo
Especificar, de forma implementável, o modelo de dados e o ciclo de vida das fontes no Console de Fontes.

Escopo
Inclui:
- Entidades centrais (por exemplo, Fonte, FonteConfig, FonteStateHistory, FonteTag, etc.).
- Campos obrigatórios (identidade, tipo, domínios, endpoints, credenciais, flags de auditoria, timestamps, etc.).
- Relacionamentos entre entidades.
- Máquina de estados conceitual da fonte (proposta, em teste, ativa, sob revisão, suspeita, desativada, etc.).
- Ganchos mínimos para auditoria (created_by, updated_by, created_at, updated_at, fonte_origem_definicao, etc.).

Critérios de entrada
- S21_G0 e S21_G1 em PASS.

Critérios de saída
- docs/sprint_21_modelo_dados_fontes.md descrevendo todas as entidades e relacionamentos.
- docs/sprint_21_ciclo_vida_fontes.md com a máquina de estados, transições permitidas e eventos relevantes.
- Diagrama (mesmo que simples) ou representação textual que permita visualizar o modelo sem ambiguidade.
- Revisão externa de alguém com foco em dados/modelagem (por exemplo, representante indicado pelo conselho ou pelo Squad 5).

Artefatos obrigatórios
- docs/sprint_21_modelo_dados_fontes.md.
- docs/sprint_21_ciclo_vida_fontes.md.
- Opcional: imagem/diagrama em docs/img/sprint_21_modelo_dados_fontes.png.
- out/scorecards/S21_G2_modelo_dados.json.
- out/evidence/S21_G2_modelo_dados/ com MANIFEST.json e, se aplicável, o diagrama.

Automação esperada
- Script: bin/s21_g2_modelo_dados.sh.
- Comportamento: checar existência dos documentos e, no mínimo, confirmar que:
  - Todos os estados esperados aparecem no ciclo de vida.
  - Campos de auditoria básicos existem em todas as entidades centrais.

Riscos
- Modelagem mal feita aqui gera migrações caras e retrabalho nas S22–S25.

#### S21_G3 — Fluxos administrativos de cadastro, edição e desativação

Objetivo
Descrever como admins operam o Console de Fontes: criar, editar, revisar, marcar como suspeita, desativar e reativar fontes.

Escopo
Fluxos principais:
- Cadastro inicial de fonte.
- Clonagem de fonte como template.
- Edição de parâmetros (endpoints, credenciais, frequência de coleta, domínios, tags).
- Abertura de revisão (por exemplo, quando a fonte é questionada por Debunker ou por evidência externa).
- Marcação de fonte como suspeita ou comprometida.
- Desativação temporária ou permanente.
- Reativação após revisão bem-sucedida.

Critérios de entrada
- S21_G0, S21_G1 e S21_G2 em PASS.

Critérios de saída
- docs/sprint_21_fluxos_admin_fontes.md descrevendo cada fluxo com:
  - Nome do fluxo.
  - Objetivo.
  - Pré-condições.
  - Passos principais.
  - Pós-condições.
  - Relação com a máquina de estados.
- Pelo menos um cenário exemplo para cada fluxo, referenciando tipos de fonte distintos.
- Revisão externa mínima: alguém do Squad 2 (que vai consumir essas configurações) e alguém com foco em UX/admin (podendo ser um representante indicado por Bret Victor).

Artefatos obrigatórios
- docs/sprint_21_fluxos_admin_fontes.md.
- out/scorecards/S21_G3_fluxos_admin.json.
- out/evidence/S21_G3_fluxos_admin/ com comentários de revisão.

Automação esperada
- Script: bin/s21_g3_fluxos_admin.sh.
- Comportamento: checar presença do documento e verificar que todos os fluxos obrigatórios aparecem (por nome ou ID), falhando se algum estiver ausente.

Riscos
- Fluxos mal definidos dificultam qualquer implementação mínima de UI ou de CLI e geram uso inconsistente do Console de Fontes.

#### S21_G4 — Ganchos para Debunker, contestação e redundância

Objetivo
Garantir que o modelo de dados e o ciclo de vida da fonte incluem, desde a origem, ganchos para conflitos, contestação, revisão e redundância.

Escopo
Inclui:
- Campos e estruturas para registrar conflitos detectados pelo Debunker (por exemplo, fonte_em_conflito_com, tipo_de_conflito, severidade).
- Registro de contestação (tickets, estado da contestação, quem abriu, quem revisou).
- Flags de estado específicas para fontes sob investigação ou com histórico de problemas.
- Ligações para evidências (ids de evidência, links para blocos de verdade/fato futuros, etc.).

Critérios de entrada
- S21_G1, S21_G2 e S21_G3 em PASS.

Critérios de saída
- docs/sprint_21_ganchos_debunker_fontes.md descrevendo claramente:
  - Quais campos foram adicionados ao modelo de dados.
  - Quais estados e transições lidam com conflito e contestação.
  - Como o Debunker v0 (Sprint 24) deverá interagir com esses campos.
- Modelo de dados atualizado para refletir esses campos.
- Revisão externa de alguém do Squad 4 (Debunker v0 + Humano-no-loop).

Artefatos obrigatórios
- docs/sprint_21_ganchos_debunker_fontes.md.
- Atualização visível em docs/sprint_21_modelo_dados_fontes.md e docs/sprint_21_ciclo_vida_fontes.md.
- out/scorecards/S21_G4_ganchos_debunker.json.
- out/evidence/S21_G4_ganchos_debunker/ com diffs e comentários.

Automação esperada
- Script: bin/s21_g4_ganchos_debunker.sh.
- Comportamento: checar que os campos esperados foram adicionados, que aparecem no ciclo de vida e que há referência explícita à Sprint 24.

Riscos
- Sem ganchos claros, o Debunker será obrigado a trabalhar “por fora” do Console de Fontes, perdendo rastreabilidade.

#### S21_G5 — Contratos com S22–S25 definidos

Objetivo
Fixar contratos claros entre o Console de Fontes e as próximas sprints (S22, S23, S24, S25).

Escopo
Para cada sprint e squad impactado, descrever:
- O que o Console de Fontes garante entregar (campos, estados, semântica).
- O que espera de volta (feedback, campos adicionais, erros).
- Limitações conhecidas.

Critérios de entrada
- S21_G1 até S21_G4 em PASS.

Critérios de saída
- docs/sprint_21_contratos_s22_s25.md, organizado em seções:
  - Com Squad 2 / Sprint 22 (Ingestão 2.0).
  - Com Squad 3 / Sprint 23 (Interpretação e Classificação).
  - Com Squad 4 / Sprint 24 (Debunker v0 + Humano-no-loop).
  - Com Squad 5 / Sprint 25 (Governança, Verdade/Fato e promoção).
- Cada seção explicita campos e estados que a outra sprint pode assumir como garantidos.
- Cada squad impactado registra um veredito de revisão.

Artefatos obrigatórios
- docs/sprint_21_contratos_s22_s25.md.
- out/scorecards/S21_G5_contratos.json.
- out/evidence/S21_G5_contratos/ com comentários dos squads.

Automação esperada
- Script: bin/s21_g5_contratos_s22_s25.sh.
- Comportamento: checar existência de seções para S22, S23, S24 e S25 e presença de listas de “garantias” e “limitações” em cada uma.

Riscos
- Contratos frouxos geram divergências entre squads e retrabalho em código e dados.

#### S21_G6 — Cenários de uso e casos de teste conceituais

Objetivo
Testar a ontologia, o modelo de dados e os fluxos administrativos em cenários de mundo real, antes de qualquer linha de código de ingestão.

Escopo
Conjunto de cenários canônicos, por exemplo:
- Cadastrar uma agência de notícias políticas.
- Cadastrar um portal de fofocas de celebridades.
- Cadastrar um feed oficial de resultados esportivos.
- Cadastrar uma fonte de dados climáticos (por exemplo, serviço meteorológico oficial).
- Cadastrar uma base oficial de atos de governo.
- Cadastrar um projeto de lei relevante.
- Cadastrar um dataset científico (por exemplo, um repositório de papers ou banco de dados de estudos).

Critérios de entrada
- S21_G1, S21_G2 e S21_G3 em PASS.

Critérios de saída
- docs/sprint_21_cenarios_uso_fontes.md listando cenários com:
  - Nome, tipo de fonte, domínio.
  - Campos preenchidos segundo a ontologia.
  - Estados do ciclo de vida percorridos.
  - Fluxos administrativos acionados.
- Cenários suficientes para serem reutilizados como base de testes em Sprint 22 e Sprint 23.

Artefatos obrigatórios
- docs/sprint_21_cenarios_uso_fontes.md.
- out/scorecards/S21_G6_cenarios_uso.json.
- out/evidence/S21_G6_cenarios_uso/ contendo, se aplicável, versões em JSON ou YAML dos cenários para uso futuro.

Automação esperada
- Script: bin/s21_g6_cenarios_uso.sh.
- Comportamento: verificar número mínimo de cenários e cobertura dos domínios obrigatórios, falhando se faltar algum.

Riscos
- Sem cenários concretos, o modelo corre o risco de ser excessivamente teórico e quebrar na prática.

#### S21_G7 — Scorecard de qualidade e risco do Console de Fontes

Objetivo
Consolidar uma visão quantitativa/qualitativa da qualidade do Console de Fontes antes da decisão final.

Escopo
Definir e calcular indicadores como:
- Cobertura da ontologia (quantos domínios e tipos de fonte).
- Campos de auditoria presentes x esperados.
- Robustez da máquina de estados (número de estados, clareza de transições, ausência de loops não desejados).
- Clareza dos fluxos administrativos (número de fluxos, documentação por fluxo, presença de exemplos).
- Alinhamento com contratos S22–S25.
- Riscos residuais identificados (por exemplo, áreas ainda frágeis ou dependentes de decisões futuras).

Critérios de entrada
- S21_G1 até S21_G6 em PASS.

Critérios de saída
- docs/sprint_21_scorecard_console_fontes.md explicando os indicadores.
- out/scorecards/S21_G7_scorecard.json com valores dos indicadores e um campo status_geral ("PASS" | "FAIL" | "PASS_WITH_RISKS").

Artefatos obrigatórios
- docs/sprint_21_scorecard_console_fontes.md.
- out/scorecards/S21_G7_scorecard.json.
- out/evidence/S21_G7_scorecard/ com anotações de risco.

Automação esperada
- Script: bin/s21_g7_scorecard.sh.
- Comportamento: validar formato do JSON, checar presença de indicadores obrigatórios e consistência entre status_geral e os valores numéricos.

Riscos
- Sem scorecard, a decisão GO/NO-GO fica baseada em percepção difusa, abrindo espaço para viés ou otimismo exagerado.

#### S21_G8 — Wrap final e decisão GO/NO-GO da Sprint 21

Objetivo
Produzir o wrap final da Sprint 21 e registrar uma decisão formal de GO/NO-GO para o Console de Fontes.

Escopo
Inclui:
- Resumo dos objetivos da sprint.
- Tabela Gate × Status.
- Lista de principais entregas.
- Lista de riscos remanescentes.
- Recomendações para as S22–S25.
- Decisão GO/NO-GO ancorada nos scorecards dos gates anteriores.

Critérios de entrada
- S21_G0 até S21_G7 em PASS ou, se algum gate estiver em PARTIAL, com justificativa clara.

Critérios de saída
- docs/sprint_21_wrap_execucao.md contendo wrap humano completo.
- out/scorecards/S21_G8_go_no_go.json com:
  - decisão ("GO" | "NO_GO").
  - resumo de motivos.
  - referência aos scorecards dos gates anteriores.
- out/evidence/S21_G8_go_no_go/MANIFEST.json listando todos os arquivos-chave de evidência.

Artefatos obrigatórios
- docs/sprint_21_wrap_execucao.md.
- out/scorecards/S21_G8_go_no_go.json.
- out/evidence/S21_G8_go_no_go/MANIFEST.json.

Automação esperada
- Script: bin/s21_g8_go_no_go.sh.
- Comportamento: ler scorecards S21_G0…S21_G7, sintetizar decisão em S21_G8, gerar manifest de evidências e devolver exit 0 apenas se a decisão for GO.

Riscos
- Um GO sem wrap sólido e manifest de evidências enfraquece a governança do projeto; um NO_GO mal explicado paralisa as sprints seguintes.

### 5. Integração com CI/ORR e disciplina de repositório

Para manter consistência com sprints anteriores, a Sprint 21 deve seguir convenções de repositório e CI já adotadas:

- Scripts de gate em bin/s21_gX_*.sh, idempotentes e sem dependências externas não documentadas.
- Scorecards JSON em out/scorecards/ com nomes padronizados.
- Evidências em out/evidence/S21_GX_nome_gate/ com MANIFEST.json.
- Possível wrapper bin/s21_all_gates.sh para rodar toda a família de gates da sprint em sequência.
- Integração futura com pipelines de ORR (por exemplo, um job _s21-orr.yml no CI) que chama os scripts de gates e armazena artefatos.

O Capítulo 3 (filemap/arquitetura) deve refletir esses caminhos; o Capítulo 4 (plano de execução) deve instruir o Codex sobre como implementar scripts, scorecards e pastas.

### 6. Definição de pronto da Sprint 21

A Sprint 21 é considerada concluída com sucesso quando todas as condições abaixo forem verdadeiras:

- Todos os gates S21_G0…S21_G8 estão em status PASS (ou, em casos excepcionais, PASS_WITH_RISKS justificado em S21_G7 e explicitado em S21_G8).
- Todos os scorecards JSON esperados existem em out/scorecards/ e estão formatados corretamente.
- Todas as pastas de evidência existem em out/evidence/, com MANIFEST.json apontando para arquivos relevantes.
- Scripts bin/s21_gX_*.sh executam com exit 0 em ambiente limpo, respeitando as dependências declaradas.
- O wrap final docs/sprint_21_wrap_execucao.md conta a mesma história que os scorecards: não há contradições entre narrativa e números.

Quando essas condições forem atendidas, o Console de Fontes estará especificado em um nível de maturidade adequado para que:

- O Squad 2 implemente ingestão contínua na Sprint 22 com base sólida.
- O Squad 3 use a ontologia e os cenários de uso na Sprint 23.
- O Squad 4 conecte o Debunker aos ganchos definidos em S21.
- O Squad 5 use estados e metadados de fonte como base para decisões de verdade/fato na Sprint 25.

A partir daqui, a Sprint 21 deixa de ser apenas uma etapa de documentação e passa a funcionar como o “contrato de base” de tudo o que o Inspectah aceita como fonte de informação na Fase 1.

