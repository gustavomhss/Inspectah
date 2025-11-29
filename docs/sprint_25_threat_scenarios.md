# Sprint 25 — Cenários Adversariais (ThreatModel)

Lista de cenários cobertos:

- **Flood narrativo** (politics_case_01): múltiplas claims sobre o mesmo tema; espera-se sinal `flood` ou `single_source_dependency`.
- **Fonte única / círculo de citações** (gossip_case_01): várias claims apontando para a mesma origem; sinal `single_source_dependency`.
- **Reversões em massa** (cenário sintético ciência): eventos alternando estados em curto prazo; sinal de `reversal_rate` acima do threshold.
- **Casos corporativo/clima**: monitorar ausência de flood e diversidade mínima de fontes.

Como rodar:
1. `bin/s25_g5_threatmodel_signals_and_metrics.sh` para métricas básicas.
2. `bin/s25_g7_threat_model_coverage.sh` para cenários avançados usando golden sets.

Thresholds configurados em `configs/threatmodel/thresholds.yaml`. Ajustes futuros devem manter cenários verdes ou justificar mudanças.
