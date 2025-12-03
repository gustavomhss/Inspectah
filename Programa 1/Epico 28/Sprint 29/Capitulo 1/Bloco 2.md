# Sprint 29 — Capítulo 1
## Bloco 2 — Problema central que a S29 precisa resolver (autópsia completa)

Se o Bloco 1 explica "onde" a Sprint 29 se encaixa no filme do Inspectah, este bloco explica o **"por que isso é inegociável"**. O problema que a S29 ataca não é cosmético, é estrutural: hoje, o cérebro de agentes do Inspectah vive em uma mistura perigosa de código, convenções implícitas e memória tribal.

Na prática, o fluxo de agentes por domínio — a sequência de quem interpreta, quem classifica, quem checa, quem decide — está espalhado em:

- dicionários e enums em módulos internos;
- condições específicas dentro de pipelines ("se domínio X, então roda esse conjunto de agentes");
- decisões históricas que foram tomadas em uma sprint e nunca mais explicitadas em lugar nenhum.

Isso gera um conjunto de efeitos colaterais que, combinados, são incompatíveis com a ambição do Inspectah.

### 1. Acoplamento rígido ao código e deploy

Hoje, responder à pergunta "como esse domínio é tratado?" normalmente exige abrir arquivos de código, navegar por módulos e entender lógica condicional. Ajustar algo simples, como inserir um segundo `DEBUNKER` entre dois `ANALYSTS` em um domínio sensível, implica:

1. Alterar código (em pontos que nem sempre são óbvios).
2. Abrir PR, esperar revisão, rodar CI.
3. Realizar deploy, monitorar, torcer.

Isso até pode ser aceitável em contexto de laboratório, mas é incompatível com o cenário de produto em que:

- crises acontecem em janelas de horas, não em ciclos de sprint;
- ondas de desinformação surgem e mudam de forma rápida;
- domínios novos precisam ser tratados com mais rigor em períodos sensíveis (eleições, pandemias, crises econômicas).

Sem uma camada de configuração, o Inspectah fica **lento para reagir** — e, em um sistema que se propõe a ser guardião de verdade, lentidão operacional vira vulnerabilidade.

### 2. Invisibilidade estrutural do fluxo de agentes

Não existe hoje um único lugar dentro da plataforma que responda, de forma direta, a perguntas como:

- "Qual é o fluxo de agentes para ‘Notícia — Política BR’?";
- "Quais papéis atuam antes do `DECISION_MAKER` em dados econômicos federais?";
- "Em quais domínios um `DEBUNKER` duplo está ativo?".

Essas respostas estão espalhadas em:

- código de ingestão;
- código de orquestração de agentes;
- eventualmente, anotações soltas em documentos antigos.

Sem uma **visão consolidada de fluxo por domínio**, o comportamento do sistema é opaco até para quem desenvolve, e quase indecifrável para quem opera ou audita. Isso mina:

- a capacidade de explicar decisões para stakeholders externos;
- a confiança interna de que todos entendem como o sistema está raciocinando;
- qualquer tentativa séria de governança sobre o "como" a verdade é produzida.

### 3. Ausência de versionamento e rastro de decisões do cérebro

Hoje, se alguém pergunta "quando endurecemos o fluxo de agentes para o domínio X e por quê?", a resposta típica envolve vasculhar:

- histórico de commits;
- comentários de PR;
- lembranças de quem participou da sprint.

Esse tipo de arqueologia é frágil e insustentável. Para um sistema que pretende ser referência em verdade, é crucial ter:

- registro claro de **quem** alterou o fluxo de um domínio;
- **quando** a alteração foi feita;
- **qual** foi a mudança (antes x depois, mesmo que em formato simplificado);
- **por que** essa mudança foi feita (por exemplo, "endurecer checagens durante o período eleitoral").

Sem isso, qualquer discussão sobre governança, auditoria ou conformidade regulatória fica no campo da boa vontade, não de evidência.

### 4. Risco real de fluxos incoerentes e violações de invariantes

Quando o fluxo de agentes está espalhado em lógica de código, invariantes importantes não são explicitadas — são apenas "esperadas". Exemplos de problemas que se tornam possíveis:

- um domínio novo é adicionado com um fluxo "mínimo demais" (por exemplo, `INTERPRETER` seguido direto de `DECISION_MAKER`, sem `CLASSIFIER` ou `DEBUNKER` intermediários);
- alguém altera o código para simplificar um pipeline e, sem querer, remove um passo crítico de validação para um domínio sensível;
- um `DECISION_MAKER` passa a atuar antes de todas as análises anteriores que deveriam alimentá‑lo.

Esses erros não são trivialmente detectáveis por testes unitários dispersos. Eles são, na essência, **erros de modelagem de fluxo**, que deveriam ser bloqueados por invariantes bem definidas em um lugar central. Enquanto isso não existe, o sistema vive sob o risco permanente de:

- tomar decisões com base em análise insuficiente;
- classificar como "fato" algo que não passou por debunking apropriado;
- criar experiências inconsistentes entre domínios similares.

### 5. Operação sem alavancas táticas

Um ponto crítico: hoje, mesmo que o time de produto/ops perceba um problema na forma como um domínio está sendo tratado, as ferramentas disponíveis são essencialmente:

- abrir ticket para time de desenvolvimento;
- pedir mudança de código;
- aguardar.

Isso significa que a operação não tem **alavancas diretas** para agir sobre o fluxo de agentes, como:

- inserir um passo adicional de análise em domínios recém‑abertos;
- reforçar debunking em um recorte geopolítico sensível;
- testar um fluxo alternativo de agentes em um ambiente controlado.

Sem essas alavancas, o modelo mental do produto continua sendo "código manda, operação observa". A Sprint 29 existe para inverter parte dessa lógica: fluxos de agentes passam a ser **ativos de configuração**, não detalhes internos da implementação.

### 6. Incompatibilidade com a visão de verdade governável

O Inspectah tem, como princípio central, a ideia de que "nada vira verdade sem trilha de evidência, sem auditoria possível e sem governança sobre o processo". Essa visão vale tanto para os **dados** quanto para o **processo** que gera interpretações e decisões.

Se o fluxo de agentes — que é exatamente o processo que transforma dados em estados de verdade — não é visível, configurável e auditável, há um desalinhamento grave entre:

- o discurso de verdade e transparência;
- e a infraestrutura real que decide essa verdade.

Em outras palavras: não basta ter evidências bem guardadas se ninguém consegue inspecionar **como** a decisão foi produzida. Sem fluxo explicitado, toda a camada de agentes permanece como uma "caixa preta", o que contradiz diretamente os objetivos do projeto.

### 7. A formulação do problema da S29

A Sprint 29, portanto, é convocada para resolver um problema que pode ser resumido em uma frase:

> "Hoje, o fluxo de agentes por domínio é um detalhe escondido no código; precisamos torná‑lo um objeto de domínio configurável, visível, validado por invariantes fortes e integrado ao runtime, de forma que produto/ops possam governá‑lo sem quebrar o sistema."

Esse enunciado se desdobra em uma série de exigências concretas que serão tratadas nos próximos blocos e capítulos:

- criar um modelo explícito para fluxos de agentes por domínio;
- expor APIs seguras para leitura e escrita dessa configuração;
- oferecer uma UI mínima, porém clara, para visualização e edição do fluxo;
- integrar a resolução de fluxo com o runtime, sem reescrever o mundo em uma sprint;
- impor invariantes que impeçam fluxos perigosos ou incoerentes;
- começar a registrar, de forma estruturada, quem mexe no cérebro do sistema.

Esse é o problema central da S29 em sua forma completa. Os capítulos seguintes vão transformar essa autópsia em **gates, métricas, arquitetura e plano de execução**, até que "fluxo de agentes configurável por domínio" deixe de ser apenas uma intenção e passe a ser uma realidade operável dentro do Inspectah.

