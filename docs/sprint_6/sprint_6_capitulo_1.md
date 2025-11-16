# Sprint 6 — Capítulo 1 (v3)

Inspectah Data Hub Alpha — back‑end utilizável, auditável e repetível para um caso de uso real

---

## 0) Papel deste capítulo

Este Capítulo 1 define o contrato da Sprint 6 do Inspectah: contexto, objetivo único, escopo positivo/negativo, modelo conceitual, artefatos obrigatórios, invariantes, critérios de pronto (DoR) e de pronto‑pronto (DoD), além de um "filme" concreto do operador usando o Inspectah Data Hub Alpha.

Ao final da leitura, qualquer pessoa deve conseguir responder, sem ambiguidade:

- O que o Inspectah passa a ser capaz de fazer depois da Sprint 6.
- O que está dentro e fora da Sprint 6.
- Quais arquivos, diretórios, comandos e evidências precisam existir para a sprint ser considerada concluída.
- Como validar, na prática, que o Inspectah Data Hub Alpha está vivo.

---

## 1) Contexto e ponto de partida

### 1.1. Projeto

O Inspectah é um Data Hub/OracleOps interno focado em três pilares fundamentais:

1. Cadastro declarativo de fontes de informação.
2. Coleta de dados com evidência completa (raw + manifesto + hash + metadados).
3. Exposição desses dados em um modelo canônico consultável e auditável.

Ele não é uma UI bonitinha, nem um produto externo nesta fase. É uma ferramenta interna que precisa ser sólida o bastante para servir de base para futuras interfaces e integrações.

### 1.2. Estado ao final da Sprint 5

No início da Sprint 6, o projeto está neste estado:

- Repositório local com **layout consolidado**: Sprint 5 encerrada localmente e estrutura de diretórios estável.
- **Disciplina de ORR e observabilidade** já exercitada nas Sprints 3–5: scripts, scorecards, bundles de evidência e rotinas de validação.
- **Documentação viva**, incluindo status das Sprints 1–5 e lições aprendidas consolidadas.

O que ainda não existe é um fluxo de uso concreto, ponta a ponta, em que alguém consiga, sem gambiarras:

> Escolher um tipo de informação real, cadastrar algumas fontes desse domínio, rodar watchers, ver evidência e depois consultar os dados consolidados de forma simples e repetível.

### 1.3. Problema que a Sprint 6 resolve

A Sprint 6 existe para fechar justamente esse buraco: transformar o Inspectah de um conjunto de peças bem projetadas em um **Data Hub Alpha utilizável** para um caso de uso real, ainda sem interface gráfica rica, mas com:

- Modelo de fontes claro.
- Modelo de dados canônico claro.
- Fluxo de coleta, evidência e consulta funcionando ponta a ponta.
- Operabilidade mínima: qualquer pessoa técnica consegue usar, desde que siga o manual da sprint.

---

## 2) Objetivo Único da Sprint 6

### 2.1. Declaração de objetivo

**Objetivo Único da Sprint 6 (OU‑S6):**

> Entregar o Inspectah Data Hub Alpha, em que um operador consegue, para um único domínio de informação real:
> 1. cadastrar fontes via arquivos declarativos versionados;
> 2. rodar watchers que coletam e armazenam evidência completa por item;
> 3. consultar e comparar os dados consolidados via CLI/HTTP local;
> 4. repetir todo esse fluxo apenas seguindo a documentação produzida na Sprint 6.

Se qualquer um desses quatro pontos não for verdadeiro de forma demonstrável ao final da sprint, a Sprint 6 **não** é considerada concluída, independentemente da quantidade de código entregue.

### 2.2. Critério de sucesso em uma frase

> Depois da Sprint 6, o Inspectah deixa de ser “um conjunto de pipelines” e passa a ser “um Data Hub Alpha utilizável”, capaz de resolver um caso real de consulta consolidada com evidência, ainda que operado só por CLI/HTTP.

---

## 3) Filme do operador: como o Inspectah Alpha é usado

Esta seção descreve, em forma de narrativa curta, a experiência concreta de um operador utilizando o Inspectah Data Hub Alpha ao final da Sprint 6.

1. O operador clona o repositório do Inspectah e segue um guia curto de preparação de ambiente.
2. Ele abre o diretório `config/sources/` e vê três arquivos YAML de fontes do **domínio piloto** (por exemplo, `fonte_a.yaml`, `fonte_b.yaml`, `fonte_c.yaml`), cada um descrevendo o tipo da fonte, URL, política de polling e como deduplicar itens.
3. No diretório `config/fields/`, o operador encontra um arquivo como `dominio_piloto.yaml`, definindo o **modelo canônico** do domínio (campos, tipos, origens e transformações) e como cada fonte preenche esses campos.
4. O operador roda um comando de validação, algo como:
   - `bin/inspectah_sources_validate.sh` — o comando lê todos os YAML de fontes e campos, faz dry‑run nas fontes, exibe um resumo do que foi encontrado e acusa qualquer erro de configuração.
5. Com tudo validado, ele roda um ciclo completo de coleta:
   - `bin/inspectah_collect_once.sh dominio_piloto` — o comando dispara os watchers das três fontes, coleta itens novos, aplica deduplicação e grava evidência em `out/evidence/dominio_piloto/...`.
6. Terminada a coleta, o operador executa um comando de consulta:
   - `bin/inspectah_query.sh dominio_piloto --from 2025-01-01 --to 2025-01-31 --categoria X` — e recebe uma listagem paginada de itens consolidados, com campos canônicos preenchidos e indicando de quais fontes cada item veio.
7. Se ele quiser, pode exportar o resultado da consulta:
   - `bin/inspectah_query.sh dominio_piloto --from ... --to ... --categoria ... --format csv > out/queries/dominio_piloto_2025-01_categoria_x.csv`
8. Ao se interessar por um item específico, o operador usa um identificador canônico (por exemplo, `item_id`) e roda:
   - `bin/inspectah_show_evidence.sh dominio_piloto item_id`
9. O comando imprime o manifesto do item (JSON) e mostra os caminhos para o conteúdo bruto (HTML/JSON/XML), além do hash que comprova integridade.
10. Durante todo o processo, métricas de latência, volume de itens e erros por fonte estão expostas em um endpoint local de métricas e podem ser inspecionadas via Prometheus/Grafana ou por um script de inspeção.

Se essa sequência não for executável por um operador que apenas leu o manual da Sprint 6, o objetivo da sprint não foi atingido.

---

## 4) Modelo conceitual da Sprint 6

A Sprint 6 fixa um modelo conceitual mínimo que passa a ser **invariante** a partir daqui (podendo ser estendido, mas não quebrado).

### 4.1. Entidades principais

- **Fonte**: definição declarativa de onde o Inspectah busca dados.
- **Item bruto**: unidade de informação exatamente como vem da fonte (HTML, JSON, XML, etc.).
- **Registro canônico**: representação normalizada de um item do domínio piloto, com campos estáveis definidos no Field Designer.
- **Pacote de evidência**: conjunto `{raw, texto extraído, manifesto, hash, metadados}` associado a um registro canônico.
- **Consulta consolidada**: visão agregada de registros canônicos que permite saber:
  - quais campos canônicos foram preenchidos;
  - quais fontes suportam cada item;
  - como chegar na evidência do item.

### 4.2. Invariantes conceituais

A partir da Sprint 6, valem as seguintes invariantes de alto nível:

1. Todo registro canônico do domínio piloto está associado a pelo menos um pacote de evidência completo.
2. Pacotes de evidência são **imutáveis**: uma vez criados, não são reescritos; no máximo, novos pacotes podem ser gerados.
3. A deduplicação é determinística: dois itens que representam a mesma informação geram o mesmo identificador canônico ou uma relação explícita no manifesto.
4. Consultas consolidadas nunca retornam um registro sem referência para evidência.
5. Campos canônicos do domínio piloto não são renomeados ou removidos sem um plano explícito de migração — esta restrição passa a ser um contrato entre S6 e sprints futuras.

---

## 5) Escopo positivo: o que a Sprint 6 entrega

A Sprint 6 se organiza em cinco pilares de entrega.

### 5.1. P1 — Registro declarativo de fontes (Source Registry v0)

Entregável: diretório dedicado, por exemplo `config/sources/`, contendo os arquivos declarativos das fontes do domínio piloto.

Cada arquivo de fonte deve conter, no mínimo:

- identificador interno da fonte;
- tipo de fonte (`rss`, `api_json`, `html_plain` v0, etc.);
- endpoints/URLs e parâmetros fixos;
- política de polling (frequência mínima, janela padrão);
- estratégia de deduplicação (por exemplo, chave composta + hash do conteúdo);
- apontamento para o domínio/Field Designer correspondente.

Artefatos mínimos:

- `config/sources/fonte_a.yaml`
- `config/sources/fonte_b.yaml`
- `config/sources/fonte_c.yaml`
- script/entrypoint de validação, por exemplo `bin/inspectah_sources_validate.sh`

### 5.2. P2 — Field Designer v0

Entregável: diretório `config/fields/` com a definição do modelo canônico do domínio piloto e o mapeamento de cada fonte para esse modelo.

Características:

- Arquivo principal do domínio (por exemplo `config/fields/dominio_piloto.yaml`) definindo:
  - campos canônicos (nome, tipo, descrição);
  - se o campo é obrigatório ou opcional;
  - origem em cada tipo de fonte (JSONPath, XPath, chave, seletor);
  - transformações mínimas (parse de data, normalização, truncamento, etc.).
- Comando de preview, por exemplo `bin/inspectah_fields_preview.sh dominio_piloto fonte_a`, que:
  - faz dry‑run na fonte;
  - aplica o Field Designer;
  - mostra registros canônicos resultantes, incluindo erros de mapeamento.

Artefatos mínimos:

- `config/fields/dominio_piloto.yaml`
- scripts de preview/validação de campos

### 5.3. P3 — Watchers + Evidence Vault v0

Entregável: pipeline de coleta para todas as fontes do domínio piloto, produzindo pacotes de evidência estáveis.

Características:

- Script principal de coleta, por exemplo `bin/inspectah_collect_once.sh dominio_piloto`, que:
  - lê os arquivos de fontes do domínio;
  - dispara watchers individuais (
    `fonte_a`, `fonte_b`, `fonte_c`);
  - aplica deduplicação;
  - grava pacotes de evidência em `out/evidence/dominio_piloto/...`.
- Estrutura padrão sugerida para evidências:
  - `out/evidence/dominio_piloto/{fonte}/{YYYY}/{MM}/{DD}/{item_id}/`
  - arquivos esperados por item:
    - `raw.*` (HTML, JSON, XML, etc.);
    - `text.txt` (quando aplicável);
    - `manifest.json` (metadados + hash + fonte(s));
    - `hash.txt` (hash forte do conteúdo bruto ou presente dentro do manifest).

Artefatos mínimos:

- scripts de coleta (por exemplo, `bin/inspectah_collect_once.sh` e helpers)
- diretório `out/evidence/dominio_piloto/` com pacotes reais de evidência

### 5.4. P4 — Explore & Verify v0 (CLI/HTTP)

Entregável: funcionalidades para explorar e verificar os registros canônicos do domínio piloto, sem UI gráfica.

Características:

- Comando principal de consulta, por exemplo `bin/inspectah_query.sh`, com opções como:
  - `dominio_piloto`
  - `--from` / `--to` (intervalo de datas);
  - um filtro por campo categórico (ex.: `--categoria`);
  - um filtro de texto simples (ex.: `--search` em um campo textual);
  - `--page` / `--page-size` para paginação;
  - `--format json|csv` para formato de saída.
- Para cada item retornado, a saída inclui:
  - identificador canônico (`item_id`);
  - campos canônicos principais do domínio;
  - lista de fontes que suportam o item;
  - referência direta ao manifesto/evidência.
- Comando para inspecionar evidência de um item específico, por exemplo `bin/inspectah_show_evidence.sh dominio_piloto item_id`.

Artefatos mínimos:

- scripts/entrypoints de consulta e inspeção
- diretório `out/queries/` contendo exemplos de export (CSV/JSON)

### 5.5. P5 — Observabilidade, ORR e bundle de evidência da Sprint 6

Entregável: conjunto mínimo de métricas e evidências para provar que o fluxo Alpha está saudável.

Características:

- Métricas expostas (via endpoint de métricas ou arquivo de saída) para:
  - latência de execução dos watchers;
  - quantidade de itens coletados por fonte em uma janela;
  - falhas por fonte (por tipo de erro);
  - frescor dos dados (tempo desde o último item por fonte).
- Script simples (ex.: `bin/inspectah_metrics_snapshot.sh dominio_piloto`) que gera um snapshot legível dos valores principais.
- Um bundle de evidência da Sprint 6, por exemplo em `out/s6_bundle/`, contendo:
  - cópia dos YAML de fontes e campos usados durante a sprint;
  - log completo de pelo menos uma corrida de coleta;
  - amostras de manifests e pacotes de evidência;
  - saídas de consultas típicas (JSON/CSV) com metadados.

Artefatos mínimos:

- docs descrevendo onde estão métricas e como inspecioná‑las
- diretório `out/s6_bundle/` com o conjunto de evidências da sprint

---

## 6) Escopo negativo: o que não entra na Sprint 6

Para manter o foco, **não fazem parte da Sprint 6**:

1. UI gráfica rica (telas de cadastro de fonte, Designers visuais, dashboards complexos).
2. Suporte a múltiplos domínios distintos em produção simultânea — S6 foca em **um domínio piloto bem resolvido**.
3. Algoritmos avançados de consenso, reputação de fonte, pesos e scoring sofisticado.
4. Multi‑tenant, autenticação avançada, autorização granular.
5. Integrações externas fortes com outros sistemas além de rodar localmente e expor dados via CLI/HTTP.

Qualquer trabalho nesses temas só é aceitável se não comprometer **nenhum** dos pilares P1–P5.

---

## 7) Contrato de artefatos da Sprint 6 (filemap mínimo)

Este capítulo se torna também um contrato de artefatos mínimos que devem existir ao final da Sprint 6:

- `config/sources/`
  - `fonte_a.yaml`
  - `fonte_b.yaml`
  - `fonte_c.yaml`
- `config/fields/`
  - `dominio_piloto.yaml`
- `bin/`
  - `inspectah_sources_validate.sh`
  - `inspectah_fields_preview.sh`
  - `inspectah_collect_once.sh`
  - `inspectah_query.sh`
  - `inspectah_show_evidence.sh`
  - `inspectah_metrics_snapshot.sh`
- `out/evidence/dominio_piloto/...`
  - diretórios por `{fonte}/{YYYY}/{MM}/{DD}/{item_id}/` com pacotes de evidência reais
- `out/queries/`
  - arquivos de export (CSV/JSON) de consultas reais do domínio piloto
- `out/s6_bundle/`
  - conjunto curado de evidências e artefatos da Sprint 6
- `docs/sprint_6/`
  - `sprint_6_capitulo_1.md` (versão deste capítulo)
  - `sprint_6_capitulo_2.md` (plano detalhado, fora do escopo deste texto)
  - `sprint_6_resultados.md` (wrap final da sprint, produzido ao final)

Este filemap pode ser refineado no Capítulo 2, mas alterações estruturais devem respeitar as invariantes conceituais da seção 4.

---

## 8) Definition of Ready (DoR) da Sprint 6

A Sprint 6 só pode ser considerada **iniciada** quando todas as condições abaixo forem verdadeiras:

1. Repositório local limpo, sem alterações não commitadas, com a Sprint 5 encerrada localmente.
2. Domínio piloto escolhido, descrito em um documento curto (1–2 páginas) armazenado em `docs/sprint_6/dominio_piloto.md`, contendo:
   - descrição do domínio;
   - lista das fontes candidatas;
   - formato de cada fonte (RSS, JSON, etc.);
   - URLs/endereços exemplares;
   - qualquer restrição relevante (ToS, limites de acesso, etc.).
3. Ambiente local validado com um conjunto mínimo de smokes:
   - scripts de testes básicos rodando sem erro;
   - ORR/observabilidade anterior não quebrada.
4. Este Capítulo 1 salvo em `docs/sprint_6/sprint_6_capitulo_1.md` e aceito pela equipe como verdade única para a Sprint 6.

Enquanto qualquer uma dessas condições não estiver satisfeita, o Capítulo 2 (planejamento detalhado) não deve ser "lockado".

---

## 9) Definition of Done (DoD) da Sprint 6

A Sprint 6 é considerada **concluída** apenas se todas as afirmações abaixo forem verdadeiras e demonstráveis com evidência:

1. Existem pelo menos três fontes do domínio piloto definidas em `config/sources/*.yaml`, e o comando de validação de fontes roda sem erros críticos.
2. O Field Designer v0 está implementado para o domínio piloto em `config/fields/dominio_piloto.yaml`, e o comando de preview produz registros canônicos válidos para uma amostra de itens de cada fonte.
3. O script de coleta (`inspectah_collect_once.sh` ou equivalente) consegue rodar um ciclo completo para todas as fontes, produzindo pacotes de evidência em `out/evidence/dominio_piloto/...` com estrutura esperada.
4. Deduplicação funciona de forma determinística: executar a coleta duas vezes em sequência não gera registros canônicos duplicados para o mesmo item, e esse comportamento é demonstrado em evidência.
5. O comando de consulta (`inspectah_query.sh`) permite:
   - listar itens com paginação;
   - aplicar pelo menos três filtros distintos (por exemplo, intervalo de datas, categoria, busca textual);
   - retornar campos canônicos e informações sobre as fontes que suportam cada item.
6. Export de consultas para CSV/JSON funciona e há arquivos reais em `out/queries/` que podem ser usados como exemplos.
7. O comando de inspeção de evidência (`inspectah_show_evidence.sh`) permite navegar da visão consolidada até o pacote de evidência de um item específico, incluindo manifesto e raw.
8. Métricas mínimas estão disponíveis e documentadas, e um snapshot produzido por `inspectah_metrics_snapshot.sh` (ou equivalente) está incluído no bundle da sprint.
9. O bundle `out/s6_bundle/` existe e contém:
   - versões dos YAML de fontes e campos usados na sprint;
   - log completo de uma corrida típica de coleta;
   - amostras de manifests e evidências;
   - saídas de consultas reais (JSON/CSV);
   - snapshot de métricas.
10. Uma pessoa técnica que não participou do desenvolvimento consegue, em uma sessão guiada apenas pelos docs em `docs/sprint_6/`, executar ponta a ponta o filme do operador descrito na seção 3.

Se qualquer um desses itens estiver ausente ou não puder ser demonstrado com evidência concreta, a Sprint 6 **não** está DONE.

---

## 10) Invariantes e contratos formais da Sprint 6

Além do DoD, a Sprint 6 instaura alguns contratos que passam a ser obrigatórios para as sprints seguintes:

1. **Contrato de evidência**: todo registro canônico do domínio piloto possui um manifesto acessível e um hash verificável do conteúdo bruto. É proibido introduzir caminhos em que dados consolidados não tenham uma trilha de evidência correspondente.
2. **Contrato de imutabilidade**: evidência escrita não é sobrescrita. Correções são feitas por acréscimo, nunca por mutação silenciosa de pacotes antigos.
3. **Contrato de campos canônicos**: nomes e semântica dos campos definidos em `config/fields/dominio_piloto.yaml` são tratados como estáveis. Alterações futuras exigem plano explícito de migração.
4. **Contrato de deduplicação**: a lógica de deduplicação é determinística e documentada. É proibido introduzir heurísticas que gerem decisões não reproduzíveis sem explicação.
5. **Contrato de operabilidade**: qualquer nova funcionalidade ligada ao domínio piloto deve respeitar e, de preferência, reforçar a jornada do operador descrita na seção 3, em vez de criar caminhos paralelos e secretos.

Esses contratos garantem que o que for construído na Sprint 6 não será descartado ou reescrito de forma caótica nas sprints seguintes.

---

## 11) Métricas e SLOs da Sprint 6

Para evitar que o Alpha seja apenas "funcional" no papel, a Sprint 6 define SLOs mínimos em ambiente local (valores podem ser calibrados, mas não ignorados):

1. **SLO de coleta**: um ciclo completo de coleta do domínio piloto (todas as fontes) deve terminar, em ambiente local saudável, dentro de uma janela razoável (por exemplo, até 5 minutos), salvo problemas externos nas fontes.
2. **SLO de consulta**: consultas típicas retornando até 50 itens paginados devem responder em até 1 segundo em ambiente local.
3. **SLO de estabilidade**: executar o ciclo "coleta + consulta" três vezes em sequência não deve gerar erros inesperados nem corromper evidência; divergências aceitáveis são apenas as de dados novos.

Os valores exatos usados na prática devem ser registrados em `docs/sprint_6/sprint_6_resultados.md` ao final da sprint, junto com os resultados medidos.

---

## 12) Riscos principais e anti‑padrões

### 12.1. Riscos

- **Risco 1 — Domínio mal escolhido**: fontes instáveis, inconsistentes ou com restrições severas de uso.
  - Mitigação: investir tempo explícito na seleção e teste manual das fontes antes de congelar o domínio.

- **Risco 2 — Escopo inflado**: tentar construir UI rica, múltiplos domínios e features avançadas antes de fechar o fluxo Alpha.
  - Mitigação: respeitar os cortes da seção 6; qualquer desvio precisa ser justificado e não pode comprometer P1–P5.

- **Risco 3 — Over‑engineering do Field Designer**: criar linguagem complexa demais para o estágio atual.
  - Mitigação: focar em cobrir bem os campos essenciais do domínio piloto com tipos simples e transformações mínimas.

- **Risco 4 — Observabilidade fraca**: depender apenas de logs soltos e prints de console.
  - Mitigação: exigir desde cedo métricas mínimas e o snapshot formal da seção 11.

### 12.2. Anti‑padrões a evitar

- "Funciona na minha máquina" sem bundle de evidência.
- Scripts ad‑hoc fora de `bin/` que não entram no filemap oficial.
- Configurações de fonte ou campo não versionadas (arquivos soltos fora de `config/`).
- Consultas manuais em banco/dados que não passem pelos comandos de Explore & Verify.

---

## 13) Como este capítulo guia os próximos

- O **Capítulo 2** da Sprint 6 (planejamento detalhado) deve decompor P1–P5 em tarefas concretas, amarradas ao filemap da seção 7 e às invariantes da seção 10.
- O **Capítulo 3** deve registrar a execução: o que foi implementado, ajustes de escopo, trade‑offs e desvios controlados.
- O **Capítulo 4** deve concentrar os resultados, evidências, métricas e lições aprendidas, sempre referenciando o DoD da seção 9.

A partir deste Capítulo 1, a Sprint 6 tem um norte único, concreto e verificável: entregar um Inspectah Data Hub Alpha que resolve um caso de uso real, com back‑end sólido, evidência robusta e jornada do operador clara — pronto para, na sprint seguinte, ganhar uma interface mais amigável sem precisar refazer o coração do sistema.

