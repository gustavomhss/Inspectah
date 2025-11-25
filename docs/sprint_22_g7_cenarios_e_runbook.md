# Sprint 22 — G7 Cenários E2E e Runbook

## 1. Objetivo
Comprovar ingestão 2.0 fim a fim em fontes representativas da Fase 1, com runbook reproduzível por operador não desenvolvedor.

## 2. Cenários definidos
1. **C1 — news_rss (Valor Econômico demo)**  
   - Fixture: `data/s22_scenarios/news_rss/fonte_valor_economico.yaml`  
   - Passos: cadastrar fonte via console S21 (ou seed), criar IngestionConfig `AUTOMATIC`, disparar run manual, validar itens no NDJSON e na UI.  
   - Critério: >=5 itens processados, status SUCCESS, métricas atualizadas.
2. **C2 — data_api (IBGE população demo)**  
   - Fixture: `data/s22_scenarios/data_api/fonte_ibge_populacao.yaml`  
   - Passos: modo MANUAL_ONLY, run manual, verificar payload_ref e itens processados.  
   - Critério: SUCCESS com `items_processed>=3`, dados acessíveis por run_id.
3. **C3 — prices_feed (preço BTC demo)**  
   - Fixture: `data/s22_scenarios/prices_feed/fonte_preco_btc_demo.yaml`  
   - Passos: modo AUTOMATIC com intervalo curto; simular falha de rede para gerar PARTIAL_SUCCESS/FAIL; observar métricas e logs.  
   - Critério: PARTIAL_SUCCESS ou FAIL registrado com error_code, alerta em métricas e ausência de runs recentes sinalizada.

## 3. Runbook resumido
1. Ativar ambiente: `source .venv/bin/activate`.
2. Aplicar migrations: `python -m scripts.db.migrate db/migrations/022_sprint22_ingestion.sql`.
3. Carregar fixtures: script dos testes E2E popula `ingestion_configs` e gera fontes se necessário.
4. Executar: `bash bin/s22_g7_e2e_scenarios.sh`.
5. Verificar UI de admin para C1–C3, conferir NDJSON em `data/ingestion_raw/...` e métricas em painel.

## 4. Métricas do gate G7
- `e2e_scenarios_defined`: 3
- `e2e_scenarios_passed`: 3 (meta)
- `e2e_non_dev_runner_present`: true (execução cruzada documentada na evidência)
- `e2e_demo_recorded`: true (gravação curta salva em evidence)

## 5. Evidências
- Logs e dumps em `out/evidence/S22_G7_e2e_scenarios/`.
- Capturas ou gravação curta de dois cenários completos.
