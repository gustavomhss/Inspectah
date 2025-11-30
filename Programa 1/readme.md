# Inspectah — Programa 1

> Diretório absoluto no dev local:  
> `/Users/gustavoschneiter/Documents/Inspectah/Programa 1`
>
> Este README descreve **como está organizado o Programa 1** dentro do projeto Inspectah: o que ele é, onde vivem os épicos e sprints, como navegar pelos capítulos/blocos, e como esta pasta se relaciona com o resto do repositório.

---

## 1. O que é o Programa 1

O **Programa 1** é o primeiro programa operacional do Inspectah. Aqui é onde o Inspectah deixa de ser só um conjunto de serviços e passa a operar um fluxo real, envolvendo:

- **Fontes** — cadastro, saúde, governança e monitoramento das fontes de dados;  
- **Ingestão 2.0** — ingestão estruturada e rastreável dos dados vindos das fontes;  
- **Debunker** — camada de análise de casos, evidências e decisões sobre contestação/verdade.

O objetivo do Programa 1 é ser o **primeiro case completo** de:

- UI admin real (Admin v1) em produção,  
- fluxos E2E coerentes (Fontes → Ingestão → Debunker),  
- operação guiada por runbooks,  
- governança via gates, ORR e scorecards.

Toda a documentação de **produto, arquitetura, estratégia e execução** desse programa vive aqui.

---

## 2. Estrutura geral da pasta `Programa 1/`

Raiz do repo no dev local:

```text
/Users/gustavoschneiter/Documents/Inspectah
```

Dentro dela, o Programa 1 fica em:

```text
/Users/gustavoschneiter/Documents/Inspectah/Programa 1
```

Estrutura atual:

```text
Programa 1/
    Programa 1.md

    Epico 26/
        Epico 26.md

        Sprint 26/
            Capitulo 1/
                Capitulo 1.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 2/
                Capitulo 2.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 3/
                Capitulo 3.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 4/
                Capitulo 4.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 5/
                Capitulo 5.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 6/
                Capitulo 6.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md

        Sprint 27/
            Sprint 27.md
            Capitulo 1/
                Capitulo 1.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 2/
                Capitulo 2.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 3/
                Capitulo 3.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 4/
                Capitulo 4.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 5/
                Capitulo 5.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md
            Capitulo 6/
                Capitulo 6.md
                Bloco 1.md
                Bloco 2.md
                Bloco 3.md
                Bloco 4.md

    Epico 27/
        Epico 27.md

    Epico 28/
        Epico 28.md

    Epico 29/
        Epico 29.md

    Epico 30/
        Epico 30.md

    Epico 31/
        Epico 31.md

    Epico 32/
        Epico 32.md
```

Arquivos `.DS_Store` do macOS podem ser ignorados; o conteúdo relevante está todo nos `.md`.

---

## 3. Papéis dos arquivos de topo

### 3.1 `Programa 1.md`

Documento macro do programa. Deve responder, com clareza:

- qual é a missão do Programa 1 dentro do Inspectah;  
- quais domínios estão sob este programa (Fontes, Ingestão 2.0, Debunker, etc.);  
- como os épicos (E26–E32) se encadeiam ao longo do tempo;  
- quais estados-alvo de maturidade definem "Programa 1 pronto".

Esse arquivo é o **primeiro lugar** para alguém que acabou de chegar e quer entender o programa sem cair direto em detalhes de sprint.

### 3.2 `Epico 26/` — Admin v1 em Programa 1

- `Epico 26.md`: visão macro do Épico 26. Deve explicar:
  - objetivo do épico (consolidar Admin v1 em Programa 1);  
  - relação com Fontes, Ingestão e Debunker;  
  - quais sprints compõem o épico (S26 e S27);  
  - critérios de "E26 concluído".

- `Sprint 26/` e `Sprint 27/`: documentação completa das sprints que entregam o E26:
  - S26: funda a base de Admin v1 em Programa 1.  
  - S27: leva Admin v1 a padrão real, amarra fluxos E2E e ORR/Operação.

### 3.3 `Epico 27` a `Epico 32`

Cada pasta `Epico XX/` contém `Epico XX.md`, usado como:

- contêiner da visão macro de épicos futuros ligados ao Programa 1;  
- espaço para registrar objetivos, hipóteses, riscos e relação com E26;  
- ponto de ancoragem para quando esses épicos ganharem suas próprias sprints.

Eles ainda podem estar em estado de esboço, mas a convenção de nomenclatura e local já está fixada.

---

## 4. Sprint Playbook dentro de cada sprint

Cada sprint em `Epico 26` segue o **Sprint Playbook v2**, espelhado nesta estrutura fixa de capítulos e blocos:

- `Sprint 27.md` (ou `Sprint 26.md`):  
  - resumo executivo da sprint;  
  - objetivo, escopo, principais entregas;  
  - relação com o épico e com o Programa 1.

Em seguida, os capítulos:

### Capítulo 1 — Contexto & Problemas a Resolver

Diretório: `Capitulo 1/`

- `Capitulo 1.md` — visão macro do capítulo;  
- `Bloco 1.md`…`Bloco 4.md` — detalham, por exemplo:  
  - contexto, dores e hipóteses;  
  - estados-alvo da sprint;  
  - escopo in/out;  
  - riscos de alto nível.

### Capítulo 2 — Gates, Métricas & DoD

Diretório: `Capitulo 2/`

Define a malha de segurança da sprint:

- gates (G0–Gx) e o que cada um garante;  
- scorecards esperados (`SXX_GY_*.json`, do lado de `out/scorecards/`);  
- métricas, critérios de GO/NO_GO, DoD por frente.

### Capítulo 3 — Arquitetura & Filemap

Diretório: `Capitulo 3/`

Explica **como o trabalho da sprint entra no repo** em `/Users/gustavoschneiter/Documents/Inspectah`:

- mapeia features para módulos/pastas (backend, frontend, scripts, testes);  
- descreve contratos (APIs, modelos, eventos) relevantes;  
- estabelece o filemap esperado para que o Codex/CI saiba onde tocar.

### Capítulo 4 — Execução & Evidências

Diretório: `Capitulo 4/`

Conecta plano → execução → evidências:

- organização em waves (W0–W3);  
- tasks-chave e como elas acionam scripts (ex.: `bin/sXX_gY_*.sh`);  
- relação entre passos de execução local e o que aparecerá em `out/evidence/` e `out/scorecards/`.

### Capítulo 5 — ORR (Operational Readiness Review)

Diretório: `Capitulo 5/`

Define **como a sprint é julgada**:

- estados-alvo que o ORR precisa avaliar (ex.: Admin v1 padrão real em Programa 1);  
- entradas obrigatórias (scorecards G0–G6, evidências, bundle `.zip`);  
- formato do `SXX_G6_orr_summary.json`;  
- roteiro do ORR, tipos de veredito e regras de GO/NO_GO/GO_WITH_RISKS.

### Capítulo 6 — Learnings, Dívidas & Roadmap

Diretório: `Capitulo 6/`

Fecha o ciclo, transformando a sprint em memória útil:

- aprendizados por eixo (produto/UX, engenharia, operação, processo);  
- dívidas `DEBT-XXX` (técnicas, UX, operação, processo) e suas relações com `RISK-XXX`/`ACT-XXX`;  
- impacto no roadmap (curto, médio, longo prazo);  
- recomendações explícitas “se eu fosse a próxima sprint”.

Cada `Bloco N.md` dentro de `Capitulo X/` aprofunda um subtema com mais granularidade, mantendo o capítulo em si legível e o bloco com densidade máxima.

---

## 5. Convenções de nomenclatura (importante para automação)

Para manter a pasta automatizável e previsível:

- **Pastas de épico**:  
  - `Epico 26/`, `Epico 27/`, …, `Epico 32/`  
  - arquivo principal: `Epico 26.md`, `Epico 27.md`, etc.

- **Pastas de sprint** dentro do épico:  
  - `Sprint 26/`, `Sprint 27/`, etc.

- **Capítulos da sprint**:  
  - diretórios `Capitulo 1/` … `Capitulo 6/`;  
  - arquivo principal do capítulo: `Capitulo X.md` (padrão unificado, já corrigido no Capítulo 6 da S26).

- **Blocos**:  
  - `Bloco 1.md` até `Bloco 4.md` dentro de cada `Capitulo X/`.

Seguir essas convenções garante que futuros scripts (por exemplo, para montar bundles, gerar navegação ou sincronizar com `docs/`) consigam percorrer a árvore sem hacks.

---

## 6. Relação desta pasta com o resto do repositório

Repo raiz:

```text
/Users/gustavoschneiter/Documents/Inspectah
```

A pasta `Programa 1/` é, por desenho:

- o **espaço de produto/estratégia** do Programa 1;  
- a visão densa e humana de tudo que E26–E32 fazem nesse domínio.

Ela conversa com o resto do repo assim:

- código, APIs, frontend, scripts, testes → seguem nas pastas usuais (`app/`, `frontend/`, `bin/`, `tests/`, etc.);  
- esta pasta fornece o **mapa de sentido**: qual código atende qual programa, qual épico, qual sprint, qual fluxo.

Num passo seguinte (quando fizer sentido), partes desta árvore podem ser espelhadas em algo como:

```text
/Users/gustavoschneiter/Documents/Inspectah/docs/programa_1/
```

para consumo mais direto via GitHub (por exemplo, só os Capítulos 1, 2, 5 e 6 de sprints selecionadas, e os `Epico XX.md`).

---

## 7. Como criar novos épicos e sprints para o Programa 1

Quando um novo épico de Programa 1 for nascer (por exemplo, `Epico 33`):

1. Criar a pasta do épico na raiz de Programa 1:

   ```bash
   cd "/Users/gustavoschneiter/Documents/Inspectah/Programa 1"
   mkdir "Epico 33"
   ```

2. Criar o arquivo macro do épico:

   ```bash
   touch "Epico 33/Epico 33.md"
   ```

3. Ao abrir a primeira sprint deste épico (ex.: `Sprint 33`), usar a estrutura padrão:

   ```text
   Epico 33/
       Epico 33.md
       Sprint 33/
           Sprint 33.md
           Capitulo 1/
               Capitulo 1.md
               Bloco 1.md
               Bloco 2.md
               Bloco 3.md
               Bloco 4.md
           ...
           Capitulo 6/
               Capitulo 6.md
               Bloco 1.md
               Bloco 2.md
               Bloco 3.md
               Bloco 4.md
   ```

4. Preencher os capítulos e blocos conforme o Sprint Playbook v2, usando **S26 e S27 como referência de qualidade**.

---

## 8. Regras de ouro ao editar `Programa 1/`

- **Não renomear arquivos/pastas consolidados sem motivo forte**  
  Se precisar renomear, alinhar tudo junto (docs, scripts, referências em outros capítulos).

- **Manter `Programa 1.md` e `Epico 26.md` sempre coerentes**  
  Eles são o resumo oficial da história do Programa 1 e do Épico 26.

- **Tratar Capítulos 5 e 6 como histórico sério, não marketing**  
  ORR e Learnings/Dívidas/Roadmap são a memória crítica do programa.

- **Usar esta pasta como truth source de produto para Programa 1**  
  Quando houver dúvida sobre por que algo existe em Admin v1 ou nos consoles de Programa 1, a resposta deve estar aqui.

Assim, qualquer pessoa que abra `/Users/gustavoschneiter/Documents/Inspectah/Programa 1` com este README consegue, em poucos minutos, entender **o que é o Programa 1, o que o Épico 26 entregou (via S26/S27) e como os próximos épicos (27–32) vão estender essa história**.