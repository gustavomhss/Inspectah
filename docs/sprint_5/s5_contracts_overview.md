# Inspectah S5 — Contracts Overview

## Watcher Engine
- **Pré-condições:** fonte cadastrada em `sources_registry.yaml`, habilitada e com frequência configurada; limites de tempo definidos.
- **Pós-condições:** itens novos recebem `state=S1`, metadados completos (run_id, fetched_at, status_code, response_size_bytes, content_type) e logs estruturados por fonte; falhas são isoladas e não derrubam outras fontes.

## Evidence Builder
- **Pré-condições:** item em S1 com bytes e metadados persistidos e diretório de destino disponível.
- **Pós-condições:** bundle criado em `data/evidence/{source_id}/{date}/{item_id}` contendo `raw.bin`, `text.txt`, `meta.json`, `manifest.json` com hashes SHA-256; item sobe para `state=S2` somente se o manifest for consistente.

## Normalizer (AI Claim Normalizer v0.1)
- **Pré-condições:** item em S2, texto extraído disponível e fonte configurada para geração de claims; equivalence_key calculável.
- **Pós-condições:** JSON aderente aos schemas v0.1 gravado, claims validados, campo `state` avança para S3 apenas após validação; falhas mantêm item em S2 com erro rastreável.

## Indexer / Query API
- **Pré-condições:** item em S3 com JSON válido e equivalence_key definido.
- **Pós-condições:** documento indexado para consulta (S4), queries permitem filtro por fonte, período e equivalence_key, e retornam evidência + claims suficientes para a UI.

## UI Admin & Explore
- **Pré-condições:** fontes configuráveis via API/serviço e itens S4 disponíveis.
- **Pós-condições:** operador consegue cadastrar/editar fontes, acompanhar status de ingestão e explorar itens (lista + detalhe com evidência, texto e claims) sem navegar em múltiplas telas obscuras.
