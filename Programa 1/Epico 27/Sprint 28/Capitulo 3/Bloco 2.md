# Inspectah — Sprint 28
## Capítulo 3 — Bloco 2
### Backend em detalhe — Domínio de Fontes, Persistência e Admin API

---

#### 3.2.1 Mapa detalhado do domínio de fontes

Neste bloco, o foco é o **backend** da Sprint 28: como o domínio de fontes é modelado, persistido e exposto via Admin API. A ideia é que alguém consiga implementar ou revisar o backend apenas com este bloco + Cap. 2.

A peça central é o **módulo de fontes**, que consolida:
- a entidade `Source` como unidade de operação,  
- o catálogo de tipos de fonte (`SourceType` ou enum equivalente),  
- os enums normativos de estado (`SourceState`), modo (`SourceMode`) e criticidade (`SourceCriticality`),  
- as invariantes que garantem que uma fonte nunca entra em estados ilegais.

**Localização principal**  
`app/sources/models.py`

A partir deste módulo, três responsabilidades ficam claras:
1. Definir **estrutura de dados** que o banco precisa refletir.  
2. Incorporar **regras de domínio** (métodos auxiliares, invariantes, conveniências).  
3. Ser a **fonte de verdade** consultada pela Admin API e pelo scheduler de Ingestão 2.0.

---

#### 3.2.2 Entidade `Source` — estrutura e responsabilidades

A entidade `Source` representa uma origem de dados que o Inspectah pode ingerir, monitorar e usar como base para narrativas, análises e verdades futuras.

Campos esperados (vista conceitual, independente de ORM exato):

- **Identidade & narrativa básica**  
  - `id`: identificador único.  
  - `name`: nome curto, claro e único no contexto operacional.  
  - `slug` (opcional): identificador estável e amigável para uso interno em URLs ou configs.  
  - `description`: texto explicando o que é a fonte e para que é usada.

- **Classificação & contexto funcional**  
  - `type`: tipo de fonte, ligado ao mecanismo de ingestão (ex.: `news_rss`, `http_json`, `price_feed`, `file_drop`, etc.).  
  - `category`: categoria de uso (ex.: `news`, `official_data`, `market`, `regulatory`, etc.).  
  - `domain`: domínio temático do Inspectah (ex.: `politica`, `economia`, `mercado_financeiro`, `saude_publica`).

- **Operação & configuração técnica**  
  - `config`: blob JSON (ou estrutura equivalente) com a configuração específica do tipo. Exemplos:  
    - para `news_rss`: `{ "url": "https://.../rss", "timeout_s": 10 }`  
    - para `http_json`: `{ "url": "https://api...", "method": "GET", "headers": {...} }`  
  - `credentials_ref`: ponteiro para segredo guardado em store seguro (quando necessário).  
  - `mode`: `AUTO` ou `MANUAL`.  
    - `AUTO`: a ingestão 2.0 agenda execuções automaticamente.  
    - `MANUAL`: execuções ocorrem apenas sob demanda (fora do escopo direto de S28, mas o campo precisa existir).  
  - `cadence`/`schedule`: representação da cadência de ingestão para fontes `AUTO` (pode ser string tipo cron, intervalo em minutos, etc., conforme padrão em S22).

- **Criticidade & risco operacional**  
  - `criticality`: enum indicando importância da fonte (`LOW`, `MEDIUM`, `HIGH`).  
    - `HIGH`: fontes cujos problemas podem comprometer análises centrais (ex.: dados oficiais de inflação).  
    - `LOW`: fontes auxiliares, menos críticas.

- **Ciclo de vida & estado operacional**  
  - `state`: enum `SourceState` com valores como `ACTIVE`, `DISABLED`, `DEPRECATED`.  
  - `state_changed_at`: timestamp da última mudança de estado.  
  - `state_reason`: texto curto explicando a razão da mudança (ex.: "spam", "maintenance", "deprecated: migrated to new API").

- **Metadados padrão**  
  - `created_at`, `updated_at`.

Responsabilidades de `Source` no código:
- Expor métodos auxiliares como `can_be_activated()`, `can_be_deprecated()`, `is_auto_active()`, etc.  
- Implementar (diretamente ou via services) helpers de transição de estado que a Admin API possa usar, evitando duplicar lógica de permissão de transições.

---

#### 3.2.3 Enums normativos e suas regras

Três enums são fundamentais na S28:

1. `SourceState`
   - Valores típicos: `ACTIVE`, `DISABLED`, `DEPRECATED`.  
   - Regras de transição (resumidas, detalhadas no Cap. 2):  
     - Permitidas:  
       - `ACTIVE → DISABLED`  
       - `DISABLED → ACTIVE`  
       - `ACTIVE → DEPRECATED`  
     - Proibidas:  
       - `DEPRECATED → ACTIVE`  
       - qualquer transição que volte de um estado final (`DEPRECATED`) para estado operacional.

2. `SourceMode`
   - Valores: `AUTO`, `MANUAL`.  
   - Regras:  
     - `AUTO`: elegível para ingestão automática se `state = ACTIVE`.  
     - `MANUAL`: só será ingerida por mecanismos manuais (fora da S28), mas precisa existir no modelo desde já.

3. `SourceCriticality`
   - Valores: ex.: `LOW`, `MEDIUM`, `HIGH`.  
   - Utilizado por:  
     - operadores para priorizar atenção,  
     - futuros módulos de health score e painel de riscos (E27.3, E29–E32),  
     - potenciais políticas diferenciadas de alerta.

Esses enums devem ser usados em toda a base de código (API, scheduler, UI) para evitar strings soltas e divergências.

---

#### 3.2.4 Migrations da Sprint 28

A Sprint 28 consolida o schema de fontes via uma migration específica:

Arquivo esperado:  
`migrations/versions/00xx_s28_sources_model_consolidation.py`

Objetivos da migration:
- Adicionar campos que faltavam para o modelo consolidado (`criticality`, `state_reason`, possivelmente `domain`, `category`, `mode`, `cadence`).  
- Ajustar tipos/constraints de campos existentes (ex.: tornar `state` obrigatório, normalizar `type`).  
- Garantir defaults sensatos para dados legados (ex.: fontes antigas ganhando `criticality = MEDIUM` se não houver melhor inferência; `state` padrão coerente com o estado anterior).

Cuidados importantes:
- **Não perder dados históricos**: migrations devem ser incrementais e reversíveis quando possível.  
- Registrar, em comentários ou em doc auxiliar, qualquer decisão de migração que não seja óbvia (ex.: mapeamento de campos antigos para novos enums).

---

#### 3.2.5 Admin API em detalhe — `/admin/sources`

A Admin API é a porta oficial para operar o domínio de fontes. Toda mudança relevante deve passar por aqui.

**Arquivo de rotas**  
`app/api/admin_sources_routes.py`

Rotas esperadas (contrato conceitual):

- `GET /admin/sources`
  - Lista paginada de fontes.  
  - Suporta filtros por: `type`, `state`, `category`, `domain`, `mode`, `criticality`.  
  - Retorna lista de `SourceListItem`.

- `GET /admin/sources/{source_id}`
  - Retorna um `SourceDetail` com todos os campos relevantes.

- `POST /admin/sources`
  - Cria uma nova fonte.  
  - Payload: `SourceCreate`.  
  - Valida existência de campos obrigatórios e consistência com o tipo.

- `PUT /admin/sources/{source_id}`
  - Atualiza uma fonte existente.  
  - Payload: `SourceUpdate`.  
  - Respeita restrições de edição (ex.: o que pode ou não mudar quando fonte está `DEPRECATED`).

- `POST /admin/sources/{source_id}/activate`
  - Muda state de fonte conforme regras (`DISABLED → ACTIVE`).

- `POST /admin/sources/{source_id}/disable`
  - Muda state (`ACTIVE → DISABLED`).  
  - Deve permitir registrar `state_reason`.

- `POST /admin/sources/{source_id}/deprecate`
  - Muda state (`ACTIVE → DEPRECATED`).  
  - Marca fonte como fora de circulação definitiva para operação normal.

**Schemas (DTOs)**  
Local: `app/sources/schemas.py`

Estruturas esperadas:
- `SourceCreate`  
  - Campos obrigatórios: `name`, `type`, `mode`, `category`, `domain`, `config`, possivelmente `criticality`.  
  - Campos opcionais com defaults razoáveis.

- `SourceUpdate`  
  - Campos editáveis (ex.: `description`, `config`, `cadence`, `criticality`, `domain`, `category`).  
  - Não deve permitir mudanças em campos que poderiam violar invariantes de forma sutil (por exemplo, trocar `type` arbitrariamente em instância antiga, se isso não fizer sentido).

- `SourceDetail`  
  - Representação completa, incluindo `state`, `state_changed_at`, `state_reason`, timestamps.

- `SourceListItem`  
  - Campos suficientes para tabelas de listagem (nome, tipo, domínio, modo, estado, criticidade, datas principais).

**Tratamento de erros**
- `400 Bad Request`: payload inválido, campos obrigatórios faltando, combinações impossíveis (ex.: tipo `news_rss` sem URL na `config`).  
- `404 Not Found`: `source_id` inexistente.  
- `409 Conflict`: transições proibidas de estado (ex.: tentar reativar fonte `DEPRECATED`).

OpenAPI deve refletir com precisão esse contrato — a S28 não precisa desenhar todos os detalhes do schema OpenAPI à mão, mas precisa garantir que a geração automática está correta.

---

#### 3.2.6 Acoplamento entre domínio, API e ingestão

O backend da S28 forma um triângulo bem definido:

1. **Domínio de fontes (`app/sources/models.py`)**  
   - Define o que uma fonte é, seus estados e invariantes.  
   - Não conhece detalhes de UI e conhece o mínimo de ingestão (apenas via referências e consultas).

2. **Admin API (`app/api/admin_sources_routes.py` + `app/sources/schemas.py`)**  
   - Orquestra mutações e leituras do domínio.  
   - É a fronteira externa para o console e automações internas.  
   - Não fala diretamente com o scheduler — atualiza o banco/modelo; quem observa mudanças é a ingestão.

3. **Ingestão 2.0 (`app/ingestion/scheduler.py` e adjacentes)**  
   - Lê o modelo `Source` e decide o que ingerir com base em `state` e `mode`.  
   - Nunca altera `Source` diretamente (não muda estado, não edita config).  
   - Depende apenas de projeções estáveis do domínio.

Essa separação garante que:
- mudanças na UI não quebrem o scheduler,  
- testes de integração possam simular cenários reais usando Admin API + scheduler,  
- futuras evoluções (E27.2/E27.3) possam enriquecer ingestão e logs sem precisar reescrever o domínio.

---

#### 3.2.7 Testes backend da Sprint 28 (visão agrupada)

Para tornar essa arquitetura verificável, alguns testes são obrigatórios:

- **Domínio**  
  - `tests/domain/test_sources_model_invariants.py`  
    - Criação de fontes válidas/ inválidas.  
    - Transições de estado permitidas e proibidas.  
    - Validações específicas por tipo.

- **API**  
  - `tests/api/test_admin_sources_crud_onoff.py`  
    - CRUD completo.  
    - Operações de ON/OFF/DEPRECATE.  
    - Erros 400, 404, 409.

- **Integração ON/OFF × Ingestão**  
  - `tests/integration/test_sources_ingestion_onoff.py`  
    - Cenários 1–3 (criar/ingerir, desativar/parar, reativar/retomar) e opcionalmente cenário 4 (modo MANUAL).

Esses testes, combinados com os scripts de gate, formam o cinturão de segurança da S28 para o backend.

---

Com isso, o Bloco 2 do Capítulo 3 destrincha o backend da Sprint 28: domínio de fontes, enums, schema, migrations e Admin API — incluindo como essas peças se conectam à ingestão 2.0 e como são validadas por testes. O Bloco 3 poderá agora descer o zoom em ingestão/scheduler em si; o Bloco 4, em frontend e filemap completo, amarrando com CI e evidências.

