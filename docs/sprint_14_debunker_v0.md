# Inspectah — Sprint 14 Debunker v0

## Objetivo e posição no backbone
O Debunker v0 segue como guardião obrigatório da linha de verdade do Inspectah. A S14 o organiza como serviço lógico único, alinhado ao truth kernel v0 e aos Capítulos 1–3.

## Decisões e estados de saída
- Estados básicos esperados: `aceito`, `incerto`, `suspeito` (e `rejeitado` para cenários futuros, não usado nos heurísticos atuais).
- Toda decisão precisa de `rationale` legível (explicação mínima rastreável).
- Integração direta com contestação v0: decisões suspeitas/incipientes alimentam eventos de contestação.

## Heurísticas por domínio
- `obra_publica`: denúncias/paralisações → `suspeito`; eventos financeiros → `aceito`; relatórios → `incerto`; demais → `aceito`.
- `evento_climatico`: nível vermelho → `suspeito`; laranja → `incerto`; abaixo de laranja → `aceito`.
- `projeto_lei`, `carreira_politica`, `influencer`, `atleta`: mantidos como `incerto` por padrão com rationale explícito (“domínio não calibrado”), servindo de sinal para contestação e futura calibração.
- Sensibilidade e thresholds por domínio definidos em `config/s14_debunker_rules.yml`.

## Expectativa de explicabilidade
- `debunker_explanation_coverage` mede a fração de decisões com rationale não vazio (global e por domínio).
- SLO G2: coverage ≥ 0.95 → PASS; 0.90–0.95 → WARN; < 0.90 → FAIL.
- Eventos sintéticos fixos exercitam cada domínio para garantir estabilidade/consistência.

## Relação com truth kernel e contestação v0
- Reexecuções do Debunker alimentam correções do truth kernel quando contestação for procedente.
- Evidências do G2 ficam em `out/evidence/S14_G2/debunker_consistency_report.json` e guiam ajustes futuros ou abertura de contestações para domínios não calibrados.
