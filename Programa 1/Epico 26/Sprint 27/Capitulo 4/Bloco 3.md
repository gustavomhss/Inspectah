# Inspectah — Sprint 27 (S27)
## Capítulo 4 — Bloco 3
### Estratégia de Gates & Execução Local/CI

> Arquivo-alvo no repo: `docs/s27_cap_4_3_estrategia_de_gates_execucao.md`
>
> Função: definir **como** G0–G6 serão executados ao longo da S27 (local e, quando aplicável, em CI), em que momentos, com que ordem e com que disciplina mínima. Este bloco é o manual de uso dos gates na prática.

---

## 1. Papel deste bloco na S27

Os gates G0–G6 só produzem o efeito desejado se forem usados com disciplina. Este bloco evita dois extremos ruins:

- rodar gates apenas no fim da sprint, descobrindo tarde problemas profundos;  
- rodar gates de forma caótica, sem relação com waves nem tasks.

Aqui definimos:

- qual é a **assinatura de execução** de cada gate (comandos e pré-requisitos);  
- como gates se encaixam no ritmo de waves W0–W3;  
- como integrar a execução em ambiente local e, depois, em CI;  
- como registrar resultados de forma útil para ORR e Cap.6.

---

## 2. Assinatura de execução de cada gate (G0–G6)

### 2.1 G0 — Escopo, Grounding & Sanidade de Ambiente

- Script principal:  
  - `bin/s27_g0_env_repo.sh`

- Execução típica (local):

```bash
cd /Users/<dev>/Documents/Inspectah
source .venv/bin/activate
bin/s27_g0_env_repo.sh
```

- Pré-requisitos:
  - venv criado e ativado;  
  - dependências mínimas instaladas;  
  - diretório do repo correto;  
  - docs Cap.1–Cap.3 presentes.

- Resultado esperado:
  - Atualização de `out/scorecards/S27_G0_scope_and_env.json`;  
  - logs em `out/evidence/S27_G0_env_repo/`.

### 2.2 G1 — Admin Design System (Tokens & Componentes)

- Script principal:  
  - `bin/s27_g1_admin_design_system.sh`

- Execução típica (local):

```bash
cd /Users/<dev>/Documents/Inspectah
source .venv/bin/activate
bin/s27_g1_admin_design_system.sh
```

- Tarefas internas esperadas do script:
  - validar build dos componentes de Admin v1;  
  - rodar testes específicos de `ui/admin` (se existirem);  
  - varrer `features/sources`, `features/ingestion`, `features/debunker` em busca de imports do Admin v1;  
  - consolidar resultado no scorecard G1.

### 2.3 G2 — Fluxos de Consoles Admin

- Script principal:  
  - `bin/s27_g2_admin_flows.sh`

- Execução típica (local):

```bash
cd /Users/<dev>/Documents/Inspectah
source .venv/bin/activate
bin/s27_g2_admin_flows.sh
```

- Responsabilidades:
  - subir ambiente necessário (backend + frontend, ou ambiente de testes E2E);  
  - rodar cenários E2E definidos em Cap.2;  
  - consolidar resultados em scorecard G2.

### 2.4 G3 — Qualidade de Frontend Admin

- Script principal:  
  - `bin/s27_g3_front_quality_admin.sh`

- Execução típica (local):

```bash
cd /Users/<dev>/Documents/Inspectah
source .venv/bin/activate
bin/s27_g3_front_quality_admin.sh
```

- Responsabilidades:
  - rodar `npm run lint`, `npm test` e `npm run build` (ou equivalentes);  
  - registrar saídas em `out/evidence/S27_G3_front_quality_admin/`;  
  - preencher `S27_G3_front_quality_admin.json` com flags de sucesso/falha.

### 2.5 G4 — Contratos & APIs

- Script principal:  
  - `bin/s27_g4_admin_contracts.sh`

- Execução típica (local):

```bash
cd /Users/<dev>/Documents/Inspectah
source .venv/bin/activate
bin/s27_g4_admin_contracts.sh
```

- Responsabilidades:
  - rodar testes de contrato de API (Fontes, Ingestão, Debunker);  
  - validar schemas (OpenAPI/JSON Schema), se existirem;  
  - gerar scorecard com `*_api_ok` e `schema_mismatches`.

### 2.6 G5 — Documentação & Runbooks

- Script principal:  
  - `bin/s27_g5_docs_runbooks.sh`

- Execução típica (local):

```bash
cd /Users/<dev>/Documents/Inspectah
source .venv/bin/activate
bin/s27_g5_docs_runbooks.sh
```

- Responsabilidades:
  - verificar presença de guia e runbooks;  
  - checar headings mínimos;  
  - opcionalmente validar referências cruzadas;  
  - preencher `S27_G5_docs_runbooks.json` e logs.

### 2.7 G6 — ORR & Bundle de Evidências

- Script principal:  
  - `bin/s27_g6_orr_bundle.sh`

- Execução típica (local ou CI):

```bash
cd /Users/<dev>/Documents/Inspectah
source .venv/bin/activate
bin/s27_g6_orr_bundle.sh
```

- Responsabilidades:
  - verificar presença dos scorecards G0–G5;  
  - checar existência de docs-chave e runbooks;  
  - montar `out/bundles/inspectah_s27_evidence_bundle.zip`;  
  - gerar/atualizar `S27_G6_orr_summary.json` com visão agregada.

---

## 3. Ritmo de execução de gates por wave

### 3.1 W0 — Groundwork

- G0:  
  - executar pelo menos 1x, idealmente logo no início;  
  - reexecutar se houver mudanças significativas de ambiente ou estrutura.

- G1–G6:  
  - execução opcional, apenas para medir estado atual (sem compromisso de GO).

### 3.2 W1 — Núcleo funcional Admin v1

- G1:  
  - deve ser rodado sempre que houver mudanças relevantes em `ui/admin` ou na adesão dos consoles;  
  - pelo menos 2 execuções completas em W1: uma no meio, uma no fim da wave.

- G2:  
  - após implementação dos primeiros cenários E2E por console;  
  - sempre que um fluxo principal for alterado.

- G3:  
  - pelo menos 1x por dia útil durante W1, ou a cada conjunto significativo de merges de front.

- G4–G6:  
  - podem ser rodados em modo exploratório, mas a expectativa de GO ainda é baixa.

### 3.3 W2 — Refinos, Contratos & Operação

- G2:  
  - rodado após cada conjunto de novos cenários E2E;  
  - rodadas completas ao final de W2.

- G3:  
  - rodado no mínimo 2x em W2 (meio e fim), ou sempre que surgirem regressões.

- G4:  
  - rodado após ajustes de contratos de API;  
  - necessário deixar `S27_G4_admin_contracts.json` em estado consistente antes de W3.

- G5:  
  - rodado após a primeira versão dos runbooks;  
  - reexecutado após ajustes significativos em docs.

- G0/G1:  
  - reexecutados conforme necessário se houver mudanças estruturais relevantes.

### 3.4 W3 — Hardening, ORR & Bundle

- Corrida final de G0–G5:  
  - uma rodada completa, em sequência, com registrado o commit/estado do repo;

- G6:  
  - rodado após G0–G5 estarem em estado aceitável;  
  - pode ser executado mais de uma vez se o ORR exigir ajustes.

O objetivo é chegar ao ORR com todos os gates rodados e scorecards refletindo o estado final da sprint.

---

## 4. Execução local vs Execução em CI

### 4.1 Execução local

Na S27, a execução local é a linha de frente:

- Desenvolvedores rodam G1, G2, G3 e G4 conforme mexem em front/back.  
- G5 é frequentemente rodado por quem está cuidando de docs/runbooks.  
- G0 e G6 são menos frequentes localmente, mas podem ser usados para checagens completas.

Boas práticas locais:

- manter scripts idempotentes;  
- limpar o mínimo de estado entre execuções (quando necessário, deixar explícito no script);  
- usar caminhos relativos e variáveis de ambiente, evitando hardcodes de máquina.

### 4.2 Execução em CI (quando integrada)

Quando a S27 for integrada ao pipeline de CI padrão do Inspectah, recomenda-se:

- workflow dedicado, por exemplo: `.github/workflows/s27_gates.yml`;  
- jobs separados por gate ou grupo de gates (G0–G3, G4–G5, G6);  
- uso dos mesmos scripts `bin/s27_g*_*.sh` para evitar duplicação de lógica.

Padrão recomendado:

- PRs que mexem em front: rodar G1 + G3 + subconjunto de G2.  
- PRs que mexem em back: rodar G2 (cenários afetados) + G4.  
- PR de fechamento da S27: rodar G0–G6.

Mesmo sem CI integrada no início, este bloco já define o padrão a ser seguido.

---

## 5. Registro dos resultados de gates

Para que o ORR e Cap.6 tenham material de qualidade, a S27 define algumas regras de registro:

1) Scorecards são sempre a fonte primária de verdade sobre gates.  
2) Logs em `out/evidence/` devem ser suficientes para reproduzir/entender falhas.  
3) O campo `notes` de cada scorecard deve ser usado de forma ativa (não decorativa) para explicar:
   - exceções;  
   - decisões de aceitar riscos;  
   - limitações temporárias.
4) Em caso de falhas intermitentes (flaky), registrar em `notes` e, se necessário, em Cap.6.

---

## 6. Checkpoints de gates ao longo da S27

Sugestão de checkpoints mínimos:

- Fim de W0:  
  - G0 rodado e verde.

- Meio de W1:  
  - primeira rodada útil de G1, G2 (mínimo) e G3.

- Fim de W1:  
  - segunda rodada de G1, G2 (mínimo) e G3;  
  - ausência de quebras flagrantes nas telas principais.

- Meio de W2:  
  - G2 com cenários ampliados;  
  - G3 e G4 já rodando com contrato estável em boa parte;  
  - G5 rodado ao menos uma vez.

- Fim de W2:  
  - G2/G3/G4/G5 em estado decente;  
  - doc/runbooks razoavelmente maduros.

- W3:  
  - corrida completa G0–G6;  
  - geração de bundle;  
  - ORR.

Esses checkpoints podem ser usados como pauta das dailies e das reuniões de fechamento de wave.

---

## 7. Como este bloco conversa com Blocos 4.1, 4.2 e 4.4

- Com **Bloco 4.1 (Plano de Waves)**:  
  - Este bloco diz como gates se distribuem no tempo; Bloco 4.1 define objetivos de cada wave.  

- Com **Bloco 4.2 (Plano de Evidências & Logs)**:  
  - Este bloco diz quando e como rodar scripts; Bloco 4.2 diz o que deve ser produzido e onde será armazenado.  

- Com **Bloco 4.4 (Tasks S27-T-XXX)**:  
  - Tasks que criam/ajustam scripts ou cenários de teste devem citar este bloco;  
  - Tasks que visam "melhorar a saúde de G2/G3/G4/G5" devem usar esta estratégia como referência.

Com esta estratégia de gates e de execução local/CI estabelecida, a S27 passa a ter não só **o que** verificar (Cap.2) e **onde** (Cap.3), mas também **quando e como** isso é feito, reduzindo surpresas no final da sprint e deixando o ORR muito mais objetivo.

