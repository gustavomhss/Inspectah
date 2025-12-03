# Sprint 29 — Capítulo 2
## Bloco 2 — Gate S29_G0 (Scope & Baseline) em detalhe

O primeiro gate da Sprint 29, **S29_G0 — Scope & Baseline**, existe para impedir que a sprint seja construída em cima de areia fofa. Antes de falar em modelo, API, UI ou runtime, ele responde a uma pergunta básica:

> "A S29 realmente existe como sprint estruturada dentro do repositório e da documentação, ou estamos improvisando em cima de pedaços soltos?"

Este bloco detalha o objetivo, os checks, as métricas, o scorecard e o critério de aprovação do S29_G0.

---

### 1. Objetivo do gate S29_G0

O objetivo do S29_G0 é **validar a fundação da sprint**, garantindo que:

1. A S29 está **documentada** em nível mínimo aceitável (macro + início dos capítulos).  
2. O **filemap base** da sprint para fluxo de agentes existe (pastas e arquivos-chave criados).  
3. Os **caminhos de evidência** da sprint estão prontos para receber artefatos (pastas de evidence e scorecards).

S29_G0 não testa lógica de negócio, não roda migrations e não chama APIs. Ele responde "sim / não" para uma questão mais simples: "A casa está minimamente montada para começar a construção?".

---

### 2. Script e comportamento esperado

**Script sugerido:**  
`bin/s29_g0_scope_and_baseline.sh`

**Responsabilidades do script:**

1. Verificar a presença dos documentos centrais da S29.  
2. Verificar a existência dos diretórios e arquivos base de código para fluxo de agentes.  
3. Garantir que os diretórios `out/evidence/` e `out/scorecards/` estão preparados.  
4. Produzir um **relatório simples** (texto/JSON) com o que foi encontrado e o que está faltando.  
5. Gerar o **scorecard JSON** do gate em `out/scorecards/S29_G0_scope_and_baseline.json`.

O script deve falhar (non‑zero exit code) se qualquer exigência obrigatória não for atendida.

---

### 3. Checks detalhados do S29_G0

#### 3.1. Documentos obrigatórios da S29

O gate verifica a presença, pelo menos, dos seguintes arquivos:

- `docs/sprint_29_macro.md`  
  Visão geral da sprint, objetivos macro, escopo e vínculo com o Épico E28.

- `docs/sprint_29_capitulo_1.md` (ou equivalente consolidando os blocos 1–4)  
  Capítulo 1 completo: contexto, problema, linguagem, riscos, narrativa de sucesso.

- `docs/sprint_29_capitulo_2.md`  
  Capítulo 2 consolidando gates, métricas e GO/NO-GO (do qual este bloco faz parte).

- Estrutura inicial para Capítulos 3 e 4:
  - `docs/sprint_29_capitulo_3*.md` (arquitetura & filemap);
  - `docs/sprint_29_capitulo_4*.md` (execução & evidências).

A verificação não exige que Cap. 3 e 4 estejam completos, mas exige que:

- os arquivos existam;
- tenham pelo menos uma estrutura básica (título, seções iniciais), indicando que a sprint foi planejada e não improvisada.

Se algum desses documentos estiver ausente, o script registra em uma lista `missing_docs` e marca o gate como `FAIL`.

#### 3.2. Filemap mínimo de backend para fluxo de agentes

O gate também garante que o repositório já tenha os caminhos base onde o trabalho de S29 vai acontecer, por exemplo:

- Diretório de lógica de fluxo:
  - `app/agents/flows/`
    - `__init__.py`
    - `models.py`
    - `schemas.py`
    - `validator.py`
    - `runtime_adapter.py`

- Rotas de admin para fluxos:
  - `app/api/admin_agent_flows_routes.py` (nome exato pode variar, mas precisa existir um módulo claro e único para essas rotas).

Alguns arquivos (como `validator.py` e `runtime_adapter.py`) podem estar inicialmente vazios ou com esqueleto mínimo (funções stub/documentação). O que importa para o G0 é que:

- o **espaço de nomes** do fluxo de agentes já está reservado;
- o time não vai "espalhar" a implementação ao longo da sprint.

#### 3.3. Filemap mínimo de frontend para UI de fluxo

Analogamente, o gate verifica se a estrutura de frontend já reconhece a feature de fluxo de agentes, com algo como:

- `frontend/inspectah-ui/src/features/agent-flows/`
  - `AgentFlowsPage.tsx`
  - `AgentFlowEditor.tsx`
  - `agentFlowsApi.ts`
  - `agentFlowsTypes.ts`

Aqui, novamente, o conteúdo ainda pode ser básico. O ponto é garantir que:

- a feature tenha um lugar dedicado no frontend;
- não nasça como um emaranhado de componentes soltos espalhados em outras pastas.

#### 3.4. Estrutura de evidências e scorecards

Por fim, o gate checa se:

- o diretório `out/evidence/` existe;  
- o diretório `out/evidence/S29_G0_scope_and_baseline` é criado (o próprio script pode criá‑lo se não existir);
- o diretório `out/scorecards/` existe (pode ser compartilhado com outras sprints e gates).

Isso prepara o terreno para que todos os outros gates possam salvar logs, outputs de testes e scorecards sem reinventar a roda a cada script.

---

### 4. Métricas e evidências do S29_G0

O S29_G0 produz elementos simples, mas importantes, como:

- uma listagem dos **documentos encontrados** e dos **ausentes**;
- uma listagem dos **caminhos de código** esperados (e se foram encontrados);
- um log de criação/verificação de diretórios de evidência.

Essas informações podem ser salvas em arquivos como:

- `out/evidence/S29_G0_scope_and_baseline/docs_check.txt`;
- `out/evidence/S29_G0_scope_and_baseline/filemap_check.txt`.

Eles servem como rastro mínimo para, no futuro, entender se a sprint foi de fato estruturada desde o início.

---

### 5. Scorecard do S29_G0

O scorecard do gate S29_G0 fica em:

- `out/scorecards/S29_G0_scope_and_baseline.json`

Campos mínimos sugeridos:

```json
{
  "gate_id": "S29_G0",
  "status": "PASS" | "FAIL",
  "missing_docs": ["…"],
  "missing_paths": ["…"],
  "evidence_paths": {
    "docs_check": "out/evidence/S29_G0_scope_and_baseline/docs_check.txt",
    "filemap_check": "out/evidence/S29_G0_scope_and_baseline/filemap_check.txt"
  },
  "timestamp": "2025-..-..T..:..:..Z",
  "notes": "…"
}
```

O campo `missing_docs` e `missing_paths` deve ser uma lista vazia em caso de `PASS`. Em caso de `FAIL`, o conselho pode olhar diretamente ali para entender qual foi a lacuna básica de preparação da sprint.

---

### 6. Critério de aprovação do S29_G0

O gate S29_G0 só é considerado **aprovado (PASS)** se:

1. Todos os documentos obrigatórios listados na seção 3.1 existem.  
2. O filemap base de backend e frontend para fluxo de agentes existe (seções 3.2 e 3.3).  
3. Os diretórios de evidência e scorecards existem e estão acessíveis.  
4. O script `bin/s29_g0_scope_and_baseline.sh` termina com exit code 0 **e** o scorecard registra `status == "PASS"`.

Se qualquer uma dessas condições falhar, o gate é **FAIL** e a sprint não deveria avançar para integração séria de código sem antes corrigir a base.

---

### 7. Por que o S29_G0 não é opcional

Em sprints com escopos menos delicados, seria tentador “pular” um gate de baseline ou tratá‑lo como formalidade vazia. Na S29, isso seria um erro.

Mexer no fluxo de agentes é mexer na forma como o Inspectah pensa. Fazer isso sem garantir, logo de saída, que:

- a sprint está minimamente documentada;
- os arquivos estão no lugar certo;
- a estrutura de evidência está pronta;

é um convite ao caos, à dívida técnica e à repetição de erros que o projeto já jurou abandonar.

O S29_G0 é, portanto, o gate que garante que a Sprint 29 não será uma gambiarra: ele obriga a equipe a **montar a mesa antes de começar a operar o paciente**. A partir dele, os próximos gates (G1–G4) podem trabalhar em cima de uma fundação clara e rastreável.

