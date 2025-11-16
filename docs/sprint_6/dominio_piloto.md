# Domínio Piloto — Observatório Municipal da Cesta Básica

## 1. Contexto

O piloto da Sprint 6 acompanha semanalmente o comportamento de preços da **cesta básica municipal** de São Paulo. O objetivo é consolidar, em um único hub auditável, os sinais emitidos por três fontes públicas: boletins RSS de sindicatos de mercados, uma API JSON aberta do programa Feira Segura e um painel HTML publicado pelo Mercado Municipal. Cada registro consolidado representa um item essencial (arroz, feijão, proteínas, higiene) com preço, unidade e região onde o valor foi observado.

O domínio foi escolhido por atender aos critérios do Capítulo 1:

- fontes reais com URLs estáveis e formatos complementares (RSS, JSON e HTML);
- dados economicamente relevantes e sem restrições severas de LGPD (itens agregados, sem PII);
- volume moderado, permitindo validar o Evidence Vault e o bundle sem depender de internet.

Os snapshots utilizados pela sprint foram baixados em 2024‑10 e foram “congelados” em `fixtures/sprint_6/` para garantir reprodutibilidade offline.

## 2. Objetivo operacional

- Permitir que um operador cadastre as três fontes declarativamente (`config/sources/fonte_*.yaml`).
- Gerar registros canônicos com campos estáveis descritos em `config/fields/dominio_piloto.yaml`.
- Manter evidência completa em `out/evidence/dominio_piloto/...`, com manifest e hash.
- Disponibilizar consultas filtráveis/paginadas via `bin/inspectah_query.sh` e inspeção via `bin/inspectah_show_evidence.sh`.

## 3. Fontes do domínio piloto

| ID (`config/sources/`) | Nome curto | Formato | Snapshot | Frequência | Particularidades |
|-----------------------|------------|---------|----------|------------|------------------|
| `fonte_a` | Boletim RSS Sindicato SP | RSS 2.0 | `fixtures/sprint_6/fonte_a_rss.xml` | 1x hora | títulos trazem categoria; descrição resume contexto e faixa de preço. |
| `fonte_b` | API Feira Segura | JSON (lista em `items`) | `fixtures/sprint_6/fonte_b_api.json` | 1x hora | payload já inclui `price_brl`, `unit`, `region`, `notes`. |
| `fonte_c` | Painel HTML Mercado Municipal | HTML semântico (`div.product`) | `fixtures/sprint_6/fonte_c_html.html` | 1x dia | bloco HTML contém SKU (`data-item-id`), categoria e `time` ISO8601. |

Regras gerais:

- todas as fontes usam timezone `America/Sao_Paulo`;
- deduplicação baseia-se em `item_id + region + unit`;
- valores em BRL, com duas casas decimais;
- conteúdo textual normalizado para UTF‑8 e espaços simples.

## 4. Campos canônicos (`config/fields/dominio_piloto.yaml`)

| Campo | Tipo | Obrigatório | Descrição | Fontes que alimentam |
|-------|------|-------------|-----------|----------------------|
| `item_id` | string | Sim | Identificador único publicado pelo parceiro (GUID, SKU ou código interno). | `fonte_a` (`item.guid`), `fonte_b` (`payload.item_id`), `fonte_c` (`@data-item-id`). |
| `product_name` | string | Sim | Nome comercial do item. | `fonte_a` (título), `fonte_b` (`payload.product_name`), `fonte_c` (`span.name`). |
| `category` | string | Sim | Categoria da cesta básica (grãos, proteínas, higiene, laticínios…). | Todos. |
| `unit` | string | Sim | Unidade ou volume informado (ex.: `5kg`, `1L`). | Todos. |
| `price_brl` | number | Sim | Preço anunciado em reais. | Todos. |
| `region` | string | Sim | Região administrativa de coleta ou feira. | Todos. |
| `reported_at` | datetime | Sim | Momento informado pelo parceiro (UTC ISO8601). | Todos. |
| `source_url` | string | Sim | Link público para o item/boletim. | Todos. |
| `notes` | string | Não | Observações adicionais (variação, estoque, campanha). | `fonte_a` (descrição), `fonte_b` (`payload.notes`), `fonte_c` (`span.notes`). |

Campos auxiliares usados em consultas:

- `supporting_sources` — lista com IDs das fontes que sustentam cada registro consolidado.
- `hash_sha256` — calculado a partir do `raw` para garantir integridade dentro do manifest.

## 5. Restrições e ToS

- Dados são públicos e citam explicitamente “uso livre com atribuição”.
- Não existe limitação de volume para o piloto; ainda assim seguimos janelas de polling conservadoras para simular operação produtiva.
- Nenhum item contém dados pessoais; ainda assim o manifest armazena somente hashes e metadados necessários.

## 6. Operação prevista

1. Validar fontes com `bin/inspectah_sources_validate.sh`, garantindo que sample files existem e dedupe está configurado.
2. Rodar `bin/inspectah_fields_preview.sh dominio_piloto` para confirmar que os campos canônicos estão coerentes e com cobertura >95%.
3. Executar `bin/inspectah_collect_once.sh dominio_piloto` para gerar evidências individuais em `out/evidence/dominio_piloto/{fonte}/{YYYY}/{MM}/{DD}/{item_id}/`.
4. Consultar dados consolidados com `bin/inspectah_query.sh dominio_piloto --from ... --to ... --categoria ... --search ...`, exportando JSON/CSV conforme necessário.
5. Navegar até o pacote de evidência de um item usando `bin/inspectah_show_evidence.sh dominio_piloto <item_id>`.

## 7. Próximos passos e evolução

- Expandir para outras capitais após consolidar confiabilidade do bundle S6.
- Incluir fontes com dados históricos (CSV) para validar repetição diária.
- Integrar automaticamente com o Evidence Vault backend (`inspectah.evidence_vault`) em sprints futuras; na S6 o armazenamento é em disco, mas com manifest compatível.

Com este documento o domínio piloto fica “trancado” para a Sprint 6, permitindo que scripts, scorecards e bundles façam referência única ao mesmo contrato.
