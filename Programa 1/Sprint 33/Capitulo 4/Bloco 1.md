# Sprint 33 — Capítulo 4

## Bloco 1 — Estratégia de execução e filosofia operacional da S33

Este bloco abre o Capítulo 4 explicando **como** a Sprint 33 deve ser executada no mundo real: em que ordem, com qual mentalidade, como os gates guiam o trabalho e como evitamos cair em armadilhas clássicas (cockpit de mentirinha, SLO de papel, runbook que ninguém usa).

A S33 é uma sprint que constrói **camada de operação**. O objetivo não é apenas adicionar código, mas mudar a forma como o Inspectah é observado e operado no dia a dia. Por isso, a estratégia de execução é desenhada para ser:

- **orientada a gates** (G0–G5 como trilhos, não como burocracia);
- **orientada a operador** (cada entrega precisa fazer sentido para alguém que está operando o sistema);
- **orientada a evidência** (sem evidência, não há DONE, só opinião).

---

### 4.1.1 Linha mestra: executar na ordem dos gates (G0 → G5)

Os gates definidos no Capítulo 2 não são decoração, são a **espinha dorsal** da execução:

1. **G0 — Escopo e baseline de operação definidos**  
   Antes de qualquer linha de código, o time precisa saber **o que** a S33 está comprometida a operar: quais fontes, quais pipelines, quais APIs, quais SLOs. G0 é o gate que protege o time de sair codando cockpit genérico sem saber o recorte.

2. **G1 — Domínio de Incident e operação coerente**  
   Com o recorte definido, o próximo passo é dar linguagem à operação: como o sistema nomeia incidentes, estados, severidades, relações com componentes e SLOs. Sem G1 sólido, qualquer incidente vira ticket amorfo.

3. **G2 — Cockpit v1 navegável e conectado**  
   Só depois de G0 e G1 faz sentido investir em UI. G2 exige um cockpit que se conecta de verdade ao domínio e às métricas, mesmo que com recorte pequeno.

4. **G3 — SLOs e observabilidade aplicada**  
   Em seguida, a sprint amarra SLOs a métricas, consultas e alertas reais. SLO sem query é poesia, não é operação.

5. **G4 — Runbooks, bundles e aprendizado**  
   Com cockpit e SLOs de pé, o time garante que exista um caminho padrão para reagir a problemas e registrar aprendizados.

6. **G5 — ORR operacional**  
   Por fim, a sprint prova, em sessão guiada, que tudo isso funciona para alguém que não é autor do código.

A execução não precisa ser totalmente sequencial (é possível trabalhar em G2 e G3 em paralelo enquanto G1 amadurece), mas **nenhum gate pode ser declarado PASS sem as condições do Capítulo 2 + Capítulo 4 estarem cumpridas**.

---

### 4.1.2 Três eixos em paralelo: backend, frontend, operação

A S33 se move em três eixos que se alimentam mutuamente:

1. **Eixo backend (domínio + serviços + API)**  
   - Consolidar domínio de Incident, componentes e SLOs.
   - Implementar serviços de `health_summary` e `slo_evaluator`.
   - Expor API `ops_cockpit` estável para o frontend.
   
   Sem esse eixo, qualquer cockpit é casca vazia.

2. **Eixo frontend (cockpit v1 e UX operacional)**  
   - Construir páginas `Overview`, `ComponentDetails`, `IncidentsList`, `IncidentDetails`.
   - Plugá‑las na API de OracleOps via `opsCockpitClient`.
   - Validar a navegação com pessoas no papel de operador.

3. **Eixo operação (runbooks, evidência, ORR)**  
   - Escrever runbooks alinhados com o recorte de G0.
   - Simular incidentes e registrar bundles em `out/evidence/S33_G4_incidents/`.
   - Preparar e executar a ORR operacional (G5).

A estratégia é evitar que qualquer um desses eixos fique "morto" durante a sprint. Em vez de esperar o backend ficar perfeito para só então chamar alguém de Ops, o time faz **ciclos curtos**: pequenas fatias de backend + UI + operação, desde cedo.

---

### 4.1.3 Uso disciplinado de scripts de gate (bin/s33_g*_*.sh)

Uma marca registrada da S33 é o uso disciplinado de scripts para representar gates:

- Cada gate G0–G4 possui um script em `bin/` que encapsula suas verificações mínimas.
- Esses scripts são executáveis tanto localmente quanto no CI, garantindo que "rodar a sprint" não dependa de memória ou boa vontade.
- Os scripts são responsáveis por gerar scorecards em `out/scorecards/` e evidências em `out/evidence/`.

Exemplo de filosofia:

- Para G0, o script **não** só "dá um echo"; ele realmente valida o `components_map` e o `scope_ops`.
- Para G3, o script **não** só marca PASS; ele executa queries de SLO e registra o resultado.

**Regra prática:**  
> Se algo é importante o suficiente para fazer parte de um gate, é importante o suficiente para ter um script que o verifique.

---

### 4.1.4 Evidência não é pós‑produção: é parte da execução

Na S33, evidência não é tarefa de "último dia". A estratégia é:

- Toda vez que um gate é rodado, um subdiretório em `out/evidence/S33_G*/` é alimentado com logs, relatórios, prints ou artefatos relevantes.
- Quando um incidente é simulado ou tratado como estudo de caso, o bundle correspondente é montado **na hora**, não semanas depois.
- A ORR operacional (G5) produz evidências estruturadas (roteiro, tempos, feedbacks), não apenas memórias soltas dos participantes.

Isso garante que, ao final da sprint, o time não precise "reencenar" a S33 para produzir evidência — a trilha já estará lá.

---

### 4.1.5 Operador no centro: por que o roteiro importa

Uma sprint de operação pode falhar de dois jeitos clássicos:

1. **ser tecnicamente elegante, mas inutilizável para quem opera**;
2. **ser visualmente bonita, mas desconectada de dados e processos reais**.

A estratégia da S33 é evitar ambos mantendo o **operador no centro**:

- Testes de navegação do cockpit, desde G2, devem envolver alguém no papel de operador;
- Runbooks são escritos para humanos, não para agradar linter; precisam funcionar quando alguém está sob pressão;
- A ORR é desenhada como história guiada do operador com o sistema, não como apresentação de slides da equipe de desenvolvimento.

A pergunta‑guia em qualquer decisão de execução é:

> "Isso ajuda ou atrapalha a vida de quem estiver operando o Inspectah às 3h da manhã quando algo quebrar?"

Se a resposta for "atrapalha", o caminho está errado — mesmo que o código pareça bonito.

---

### 4.1.6 Critério filosófico de DONE na S33

Mais do que checklists, a S33 adota um critério filosófico de DONE:

> A sprint só está terminada quando **alguém que não escreveu o código** consegue operar o recorte da S33 usando o cockpit, os SLOs, os incidentes, os runbooks e os bundles de evidência — e isso foi comprovado em ORR com trilha de evidência.

Esse critério é o fio condutor de toda a execução. Os próximos blocos do Capítulo 4 descem essa filosofia para:

- plano tático por gate (Bloco 2);
- fluxo Git/PR/CI e rotina diária (Bloco 3);
- evidência, riscos e checklist de encerramento (Bloco 4).

Este Bloco 1 é a bússola: se em algum momento execução, código ou UI começarem a se afastar desses princípios, a sprint precisa ser recentrada antes de seguir adiante.

