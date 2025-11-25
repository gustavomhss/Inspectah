# Sprint 21.2 — Ontologia de Fontes v2 (extensão da S21)

A ontologia de fontes da S21 permanece a base. A v2 adiciona **refresh_interval**, um tipo formal de **fonte oficial aberta** e endurece a leitura da **máquina de status** para ciclos de aprovação/suspensão/desativação. Nada aqui substitui a S21 ou a S21.1; apenas refina e torna explícito o que o Console e o Copiloto passam a exigir.

## 1. Princípios

- Compatibilidade: nenhum campo ou estado da S21 é removido; os novos campos são opcionais apenas onde a S21 já permitia lacunas, mas são tratados como de primeira classe na UX e no Copiloto.
- Segurança: fluxos de status e oficiais abertas exigem confirmação humana e logs auditáveis.
- Simetria: tudo que o Copiloto sugere deve existir no domínio (schemas, validators, service) e vice-versa.

## 2. Campos adicionados/fortalecidos

### 2.1 refresh_interval
- Tipo: inteiro positivo (unidade operada em minutos/horas conforme validação do serviço).
- Papel: representa a cadência esperada de atualização/checagem da fonte.
- Relação com `frequency` da S21: complementa o enum, permitindo granularidade explícita sem quebrar contratos existentes.
- Defaults: definidos pelo serviço de domínio por tipo de fonte (conservador se o admin não informar).
- Validações: rejeitar valores nulos ou claramente abusivos; restringir combinações incoerentes com fontes manuais ou muito estáticas.

### 2.2 Tipo de fonte oficial aberta
- Enum previsto: `SourceType.OFFICIAL_OPEN` (nome técnico; label de UI “fonte oficial aberta”).
- Escopo: órgãos/portais oficiais sem API/RSS, mas com dados públicos em HTML/PDF/CSV/etc.
- Campos obrigatórios adicionais (além da S21):
  - `description` clara do que a fonte entrega.
  - `endpoint`/`url_base` pública legível.
  - `themes`/`info_types` coerentes com o órgão.
- Restrições: não prometer scraping/ingestão automática além do razoável; tratar como leitura manual/assistida até S22+.

### 2.3 Tipo de fonte “API de dados”
- Identificador: `data_api`.
- Escopo: APIs REST/JSON/GraphQL de indicadores/estatísticas/datasets.
- Campos: `endpoint`/`url_base` com rota de API (ex.: `/api/v1/...`), `themes` e `info_types` alinhados ao dado retornado.
- Refresh: sugerido conservador (ex.: 240 min) a depender da criticidade da API.
- Validação: endpoint deve aparentar rota de API; auth segue regras gerais (não travado nesta fase).

## 3. Status e ciclo de vida (enfoque v2)

A S21 define a máquina completa em `docs/sprint_21_ciclo_vida_fontes.md` (PROPOSED, TESTING, ACTIVE, UNDER_REVIEW, SUSPECT, DISABLED_TEMP, DISABLED_PERM). A S21.2 endurece o uso operacional, expondo um recorte admin-friendly:

- **PENDENTE/PROPOSED** → aprovação obrigatória antes de uso.
- **ATIVA/ACTIVE** → fluxo normal de coleta.
- **SUSPENSA/UNDER_REVIEW ou SUSPECT** → pausa controlada com plano de ação.
- **DESATIVADA/DISABLED_TEMP ou DISABLED_PERM** → bloqueio explícito; retorno apenas via transição válida e justificada.

Transições proibidas continuam vetadas conforme a tabela da S21; a v2 apenas documenta e valida as rotas aprovadas para o Console (aprovar, suspender, reativar, desativar) mantendo a coerência com o histórico e os estados terminais.

## 4. Ontologia por tipo

- **Notícias / Clima / Esportes / Fofoca**: mantêm campos da S21, agora com refresh_interval sugerido pelo Copiloto conforme tipo e canal (RSS/API/HTML).
- **Oficial aberta**: tipo dedicado, com perguntas adicionais no Copiloto (órgão emissor, página fonte, formato disponível) e defaults conservadores de refresh.

## 5. Regras de validação de alto nível

- Nenhuma criação/edição persiste sem checar se o tipo é reconhecido e se refresh_interval está dentro de limites definidos.
- Fontes oficiais abertas sempre exigem descrição e URL pública; requests de automação não são aceitos no escopo da S21.2.
- Mudanças de status seguem a máquina da S21; transições fora da tabela são bloqueadas e registradas.

## 6. Traço com demais docs

- Este texto se ancora em `docs/sprint_21_modelo_dados_fontes.md` e `docs/sprint_21_ciclo_vida_fontes.md`.
- Fluxos admin e FSM do Copiloto são descritos em `docs/sprint_21_2_fluxos_admin_fontes_v2.md` e `docs/sprint_21_2_maquina_estados_copiloto.md`.
- A política de segurança específica está em `docs/sprint_21_2_politica_seguranca_copiloto_v2.md`.
