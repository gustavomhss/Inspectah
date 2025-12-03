# Sprint 29 — Capítulo 3
## Bloco 1 — Papel da arquitetura da S29 e mapa mental geral

Os Capítulos 1 e 2 da Sprint 29 responderam a três perguntas fundamentais:

1. **Por que** precisamos tornar o fluxo de agentes configurável por domínio (problema e objetivos de produto).  
2. **Que resultado** consideramos aceitável (narrativa de sucesso, riscos e não‑metas).  
3. **Como vamos provar** que chegamos lá (gates, métricas, scorecards e GO/NO-GO).

O Capítulo 3 entra em cena para responder a uma quarta pergunta, tão crítica quanto as anteriores:

> "Onde, exatamente, cada parte da Sprint 29 mora na arquitetura do Inspectah e como essas partes se conectam?"

Este Bloco 1 define o papel da arquitetura da S29, o mapa mental geral e as fronteiras entre as camadas. Os blocos seguintes descem o zoom para o nível de módulos, arquivos e integrações específicas.

---

### 1. O que a arquitetura da S29 precisa garantir

A Sprint 29 não é sobre "criar uma tela" ou "fazer um endpoint novo". Ela mexe em algo bem mais sensível: **como o Inspectah decide, passo a passo, o que fazer com um item de informação dentro de um domínio**.

A arquitetura da S29 precisa garantir, ao mesmo tempo:

1. Que exista um **núcleo de domínio** para fluxos de agentes — com modelos, invariantes e serviços claros.  
2. Que esse núcleo seja exposto via uma **API de admin** estável e segura, sobre a qual o frontend possa se apoiar.  
3. Que haja uma **UI de fluxo** capaz de transformar intenção humana ("quero um fluxo mais rígido para este domínio") em configuração concreta.  
4. Que o **runtime do Inspectah** (pipelines de ingestão, agentes e comitês) passe a obedecer ao fluxo configurado por domínio, e não a tabelas soltas no código.  
5. Que exista **observabilidade mínima** para entender, na prática, como os fluxos estão sendo executados e quando o sistema recorre a fallbacks.

Em outras palavras: a arquitetura da S29 precisa criar um caminho contínuo que vai de **"decisão de produto" → "configuração" → "execução" → "evidência"**.

---

### 2. Quatro camadas centrais da S29

Para organizar esse caminho, a S29 se estrutura em quatro camadas arquiteturais, que se conversam de forma explícita:

1. **Camada de domínio de fluxo de agentes (backend)**  
   Aqui moram as ideias duras:
   - o que é um `AgentFlowConfig` e um `AgentFlowStep` na prática;
   - como representamos isso em banco e em objetos de domínio;
   - quais invariantes definem se um fluxo é aceitável ou não;
   - quais operações de alto nível existem (criar, atualizar, buscar por domínio).

2. **Camada de API de admin (backend)**  
   Essa é a borda HTTP do cérebro de fluxo:
   - expõe rotas para que a UI e automações possam criar/ler/atualizar fluxos;
   - converte exceções de domínio em respostas HTTP claras e tipadas;
   - aplica autenticação/autorização de admin.

3. **Camada de UI de fluxo de agentes (frontend)**  
   Essa é a face humana da S29:
   - oferece uma visualização linear do fluxo de um domínio;
   - permite operações básicas (adicionar/remover/reordenar passos);
   - traduz mensagens de erro de invariantes em feedback compreensível para o operador;
   - exige justificativa textual para mudanças relevantes, alimentando auditoria.

4. **Camada de runtime & observabilidade**  
   Essa é a parte que prova que não estamos só brincando de CRUD:
   - ajusta o pipeline de ingestão/agentes para buscar o fluxo configurado por domínio;
   - orquestra a execução dos papéis na ordem definida;
   - registra logs estruturados e métricas básicas sobre a execução de fluxos e uso de fallback.

Cada uma dessas camadas tem responsabilidades claras. A arquitetura da S29 é, essencialmente, o contrato que impede que essas responsabilidades se misturem de forma caótica.

---

### 3. Relação entre arquitetura e gates da S29

O desenho arquitetural da S29 não é abstrato: ele conversa diretamente com os gates definidos no Capítulo 2.

- **S29_G1 (Modelos, Schemas e Migrations)** exige que a camada de domínio esteja bem formada (`models.py`, `schemas.py`).
- **S29_G2 (API de Admin & Validador)** exige que a camada de domínio + validação esteja exposta corretamente via API.
- **S29_G3 (UI & Frontend Quality)** foca na camada de UI usando a API de forma coerente.
- **S29_G4 (Runtime & Observabilidade)** testa a camada de runtime consumindo o domínio de forma real.
- **S29_G5 (ORR & Bundle)** costura evidências geradas por todas as camadas.

Ou seja:

> Se a arquitetura estiver mal definida, os gates viram uma colcha de retalhos.  
> Se os gates estiverem bem definidos, mas a arquitetura não os refletir, viram teoria desconectada.

Este Bloco 1 fixa o princípio de que **cada gate tem uma âncora arquitetural clara**, e que o Capítulo 3 existe justamente para amarrar essas âncoras ao filemap e às integrações reais.

---

### 4. Resultado esperado deste capítulo

Ao final do Capítulo 3 como um todo, queremos que uma pessoa nova no projeto consiga:

- abrir o repositório;
- navegar para os diretórios certos em backend e frontend;
- entender, em minutos, onde o fluxo de agentes é definido, validado, exposto, editado e executado;
- cruzar essa visão com os gates (Capítulo 2) e com os objetivos de produto (Capítulo 1).

Os próximos blocos vão decompor essa visão em:

- desenho detalhado da camada de domínio de fluxo (modelos, schemas, validator, service, runtime_adapter);
- arquitetura da API de admin (rotas, tratamento de erros, integração com auth);
- arquitetura da UI (página, editor, cliente de API, hooks);
- integrações com o pipeline de ingestão e o plano de observabilidade;
- filemap completo da S29.

Este Bloco 1 é, portanto, o "mapa mental" da Sprint 29 do ponto de vista de arquitetura: um resumo de **quais peças existem**, **como se falam** e **por que foram organizadas desse jeito** para que a ideia de fluxo de agentes configurável por domínio vire realidade concreta no Inspectah.

