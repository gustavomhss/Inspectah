# Sprint 17 — Capítulo 1 (Refatorado)
## Visão, contexto e missão da UI de Consulta do Inspectah

### 1. Onde estamos no projeto Inspectah

O backend do Inspectah já saiu da fase de experimento e está em modo **motor de verdade v1**:

- Truth-DB e Sistema de Blocos consolidados (blocos, sub‑blocos, componentes, versões, claims, disputas).  
- Debunker v1 conseguindo ler múltiplas fontes, aplicar regras de sanidade e produzir relatórios de risco com `risk_flags` claros.  
- Comitês V1/V2/V3 funcionando como camadas independentes de avaliação (validação mecânica, multi‑cérebro, coerência).  
- Âncoras e cadeia de confiança com cliente de chain, batcher e registro de falhas/sucessos (inclusive sob cenários de Threat Model mapeados na S16).  
- Gates de backend (S13–S16) rodando com scorecards e evidências, levando o sistema a um patamar de **produção v1 com GO/GO_WITH_RESTRICTIONS**.

Ou seja: o Inspectah já sabe **pensar, duvidar e registrar** o que considera verdade ou risco — mas continua preso em APIs, scripts e scorecards. Falta o que qualquer humano comum precisa: uma **interface de consulta** que não exija conhecer DNA, scripts `bin/*` ou JSON.

A Sprint 17 é o primeiro passo de frontend e responde exatamente a isso: transformar esse motor em algo que qualquer pessoa consiga **perguntar** e **entender**.

### 2. Posição da Sprint 17 no roadmap de frontend

O roadmap de frontend foi dividido em quatro sprints principais:

- **S17 — UI de Consulta**: tela principal onde o usuário faz perguntas em linguagem natural, vê respostas consolidadas, nível de risco e um recorte de evidências. Nada de admin, nada de timeline. É a porta de entrada.  
- **S18 — Console de Admin**: visão de fontes, casos/temas e saúde geral do sistema, orientada ao operador/admin.  
- **S19 — Timeline e Raio‑X**: diagnóstico profundo, mostrando como o motor chegou ao veredito (blocos, Debunker, Comitês, Âncoras, histórico).  
- **S20 — Acabamento e Hardening de Front**: UX polida, design system mínimo, responsividade decente, auth básica, observabilidade de UI.

Dentro desse plano, a S17 tem um foco deliberadamente estreito:

> Fazer com que uma pessoa que nunca viu o Inspectah consiga **perguntar algo, ver uma resposta, entender o risco e ter um vislumbre das evidências**, sem precisar abrir terminal ou documentação.

S18–S20 só existem se S17 conseguir cumprir bem esse papel. Se a experiência de consulta for ruim ou confusa, todo o resto vira painel de controle sem carro.

### 3. Missão da Sprint 17

A missão da S17, vista em uma frase, é:

> "Entregar a primeira UI de consulta do Inspectah, onde qualquer pessoa consiga perguntar algo, ver a resposta consolidada, entender o risco e enxergar as principais evidências — com feedback honesto quando o sistema não sabe ou não consegue responder."

Essa missão implica alguns compromissos concretos:

1. **Consulta em linguagem natural, sem fricção de formato**  
   O usuário não precisa aprender sintaxe de query nem navegar em menus complexos. Ele vê uma caixa de pergunta, um botão de enviar e instruções curtas do tipo "Pergunte sobre um fato, evento ou caso".

2. **Resposta explicada, não apenas exibida**  
   A UI não é um chat genérico. A tela precisa explicitar:
   - resposta consolidada;  
   - nível de risco (baixo, médio, alto, incerto);  
   - principais evidências usadas pelo motor.  

   Visualmente, isso significa organizar a resposta em blocos lógicos, e não despejar texto corrido ou JSON.

3. **Risco em destaque e sempre honesto**  
   O Inspectah não existe só para dizer "sim" ou "não" — ele existe para dizer "quão seguro estou em dizer isso?". A UI deve:
   - destacar risco com cor, texto e ícone;  
   - não disfarçar risco alto ou incerteza;  
   - não inventar confiança quando o backend devolve "não sei" ou "informação insuficiente".

4. **Evidência como cidadão de primeira classe**  
   Mesmo no modo "v1 de front", a S17 precisa mostrar evidências:
   - fontes principais;  
   - tipo de evidência (ex.: notícia, banco de dados, documento oficial);  
   - sinal de credibilidade;  
   - como essa evidência se conecta com a resposta.  

   Não é necessário expor o Sistema de Blocos inteiro; basta um recorte coerente que prove que a resposta não saiu do nada.

5. **Erros e incerteza tratados com respeito ao usuário**  
   Quando o backend falha, está fora do ar ou não tem dado suficiente, a UI precisa responder com clareza:
   - mensagem em português direto;  
   - orientação de próxima ação (tentar de novo, reformular, tentar mais tarde);  
   - nunca expor stacktrace ou detalhes internos.

6. **Nada de poderes administrativos ou mutações perigosas**  
   Na S17, o usuário final só **consulta**. Ele não cadastra fonte, não edita bloco, não resolve disputa. Qualquer ação que altere o estado do Truth‑DB ou do Sistema de Blocos pertence a sprints futuras (e, em grande parte, ao backend/admin).

### 4. Bret Victor + Kent C. Dodds: dois guardiões da experiência

A Sprint 17 passa a ter co‑liderança explícita em frontend:

- **Bret Victor** — guardião da **experiência visual e interativa**, voltado a tornar o estado do sistema visível, manipulável e compreensível.  
- **Kent C. Dodds** — guardião da **arquitetura de UI, acessibilidade, testes e DX em React**, garantindo que o que o usuário vê seja sustentado por um código saudável, testável e simples.

Essa dupla define uma combinação de princípios que o Capítulo 1 fixa como norte.

#### 4.1 Princípios de Bret Victor aplicados à S17

1. **Estado visível**  
   Em cada momento, a UI deixa claro em que estágio o fluxo está:
   - pronto para perguntar;  
   - processando a consulta;  
   - resposta entregue;  
   - falha, com mensagem clara.  

   Nada fica implícito "só no backend". O usuário sempre tem uma pista visual do que está acontecendo.

2. **Feedback imediato**  
   Ao enviar a consulta:
   - o botão muda para estado de loading;  
   - surge um indicador que o Inspectah está trabalhando;  
   - se a resposta demora, a tela continua viva (skeletons, placeholder de resposta), nunca congelada.

3. **Estrutura visual alinhada ao modelo mental do usuário**  
   A forma da tela reflete a forma do problema:
   - pergunta no topo;  
   - resposta como bloco central;  
   - risco em destaque;  
   - evidências dispostas como prova de apoio.  

   O usuário não precisa conhecer "Debunker" ou "Comitê" — mas sente que existe um processo por trás porque a UI organiza o conteúdo de maneira consistente.

4. **Espaço para evolução interativa**  
   A S17 entrega o fluxo mínimo, mas o layout já reserva espaço e estrutura para, no futuro, permitir coisas como:
   - ver mais evidências;  
   - abrir detalhes por fonte;  
   - linkar para timeline/raio‑X (S19).  

   Ou seja, o design da S17 já é desenhado para crescer, sem exigir reescrita completa.

#### 4.2 Princípios de Kent C. Dodds aplicados à S17

1. **UI como função pura de estado**  
   A tela principal é pensada como "estado → UI":
   - estado `idle` (sem consulta ainda);  
   - estado `submitting` (consulta em andamento);  
   - estado `success` (resposta com risco/evidências);  
   - estado `error` (algo deu errado).  

   Isso força o time a explicitar estados e torna a UI mais previsível e mais fácil de testar.

2. **Acessibilidade desde o início**  
   Mesmo sendo v1, a S17 incorpora:
   - HTML semântico (formulário real, headings, landmarks);  
   - foco de teclado claro (input, botão de enviar, navegação básica);  
   - labels e `aria-*` quando necessário;  
   - contraste adequado para componentes críticos (especialmente risco/alertas).  

   A ideia não é passar em todos os checklists possíveis, mas evitar criar dívidas óbvias.

3. **Testes guiando confiança**  
   A Sprint 17 precisa sair com uma base mínima de testes:
   - testes de componentes e fluxo principal (React Testing Library), cobrindo pelo menos o envio de uma consulta, renderização de resposta, exibição de risco e manuseio de erro;  
   - espaço para, em sprints seguintes, adicionar testes E2E (por exemplo, com Playwright ou ferramenta similar).

   Kent puxa o time para pensar: "como saberemos que não quebramos o fluxo de consulta daqui a duas sprints?".

4. **DX simples, mas sólida**  
   O projeto de front precisa ser fácil de rodar e entender:
   - scripts claros (`npm run dev`, `npm run test`, `npm run build`);  
   - estrutura de pastas previsível (`components/`, `pages/`, `hooks/`);  
   - nenhum acoplamento desnecessário com detalhes do backend (o contrato fica em módulo dedicado).  

   A Sprint 17 não cria complexidade à toa; ela prepara terreno para S18–S20 sem virar um labirinto.

### 5. Personas e jornadas cobertas pela Sprint 17

A S17 mira um conjunto mínimo de personas, mas com jornadas bem claras.

#### 5.1 Usuário final (consulta)

É a pessoa que mais importa aqui. Pode ser um analista, jornalista, PM, investidor ou cidadão curioso, mas a UI assume que ele **não** quer aprender detalhes técnicos — só quer uma resposta confiável e honesta.

Jornada alvo:

1. Abre a página principal do Inspectah.  
2. Em uma ou duas frases, entende o que o sistema faz (ex.: "O Inspectah cruza fontes para verificar informações e te mostra risco e evidências").  
3. Digita uma pergunta em linguagem natural sobre um fato, evento, caso ou tema.  
4. Clica em enviar e vê que o sistema está processando.  
5. Recebe uma resposta com:  
   - um texto consolidado;  
   - um indicador de risco com texto claro;  
   - algumas evidências (fonte, tipo, resumo).  
6. Se algo der errado, vê uma mensagem compreensível e sabe que pode tentar de novo.

Se essa jornada não for fluida, a Sprint 17 falhou, independentemente de quantos detalhes técnicos estejam corretos por trás.

#### 5.2 PO / Equipe interna (produto/engenharia)

Esse grupo usa a UI da S17 como **vitrine do motor**:

- demonstrar o Inspectah para stakeholders internos/externos;  
- testar hipóteses de UX (como os usuários reagirão à exibição de risco/evidências);  
- identificar se a estrutura de resposta do backend está adequada para consumo por humanos.

Jornada alvo:

1. Levanta o backend e o front com poucos comandos.  
2. Usa a mesma UI de consulta do usuário final para testar casos reais ou cenários de demo.  
3. Não precisa abrir terminal ou scorecards para explicar o que o Inspectah faz em alto nível.  
4. Consegue anotar rapidamente pontos a melhorar para S18–S20.

#### 5.3 Operador/admin (em modo "observador")

Embora a S18 seja a sprint dedicada a admin, na prática alguns operadores vão usar a UI de S17 para sentir se as respostas estão "boas" ou "estranhas". A Sprint 17, portanto, precisa ser **legível também para quem está de olho na qualidade**, mesmo sem features de admin.

### 6. Escopo de produto da S17 (vista macro)

Capítulos seguintes vão detalhar, mas o Capítulo 1 fixa o escopo em alto nível.

#### 6.1 O que entra

- Tela principal de consulta com:
  - campo de pergunta;  
  - botão de enviar;  
  - mensagens de orientação;  
  - estado de loading.

- Área de resultado com:
  - resposta consolidada;  
  - indicador de risco;  
  - lista curta de evidências, com resumo e origem;  
  - mensagem sobre limites da resposta (quando aplicável).

- Tratamento básico de erros e estados vazios:
  - falha de backend/rede;  
  - consulta vazia ou inválida;  
  - ausência de dados suficientes para resposta confiável.

- Arquitetura de front mínima, mas correta, usando a stack definida (React + Vite, Tailwind) e integrada a um endpoint de consulta do backend.

#### 6.2 O que fica explicitamente fora

- Qualquer tela de admin (fontes, casos, saúde) — tudo isso é assunto da S18.  
- Timeline, histórico detalhado, raio‑X de blocos — S19.  
- Auth avançada, responsividade refinada, observabilidade de front e design system completo — S20 (com influência retroativa na S17, mas fora do escopo de implementação aqui).  
- Qualquer ação que altere o estado do Truth‑DB (resolução de disputas, edição de blocos, etc.).

### 7. Perguntas que a Sprint 17 precisa conseguir responder "sim"

Ao final da sprint, o time deve olhar para a UI de consulta e conseguir, honestamente, dizer "sim" para pelo menos estas perguntas:

1. **Uma pessoa não técnica entende, em menos de um minuto, o que pode fazer nessa tela?**  
2. **Ela consegue formular uma pergunta, enviar, perceber que o sistema está trabalhando e interpretar o resultado sem ajuda?**  
3. **O nível de risco associado à resposta está claro, sem truques visuais que minimizem perigo ou incerteza?**  
4. **Há evidências visíveis e compreensíveis o suficiente para dar confiança de que a resposta não é um chute?**  
5. **Quando algo dá errado (backend, rede, dados insuficientes), a interface se comporta de maneira digna, com mensagens claras e sem colapsar?**  
6. **O código de frontend está organizado de forma que possamos, em S18–S20, estender as telas para admin, timeline e acabamento sem jogar tudo fora?**  
7. **Existe cobertura mínima de testes de UI para nos proteger de regressões no fluxo de consulta?**

Se alguma dessas respostas for "não", a Sprint 17 não está pronta, mesmo que "tecnicamente funcione".

### 8. Ligações com os próximos capítulos da Sprint 17

Este Capítulo 1 define visão, contexto, missão, escopo macro e princípios de design. Ele se conecta diretamente com os capítulos seguintes:

- **Capítulo 2 — Gates e validação**  
  Vai traduzir esta visão em uma matriz de T0–T8 para a S17, definindo como testar a UI de consulta (manual, automático, experiência), quais scorecards serão gerados e quais critérios de GO/NO_GO se aplicam.

- **Capítulo 3 — Filemap e arquitetura de frontend**  
  Vai descer para o nível de pastas, componentes, rotas e contratos UI↔API, garantindo que a implementação siga os princípios Bret + Kent e fique alinhada ao DNA do projeto.

- **Capítulo 4 — Plano de execução (Codex + equipe)**  
  Vai transformar tudo isso em um plano concreto: comandos, tarefas, sequência de implementação, testes e evidências.

O objetivo deste Capítulo 1 é garantir que, antes de escrever uma linha de código de frontend, todo mundo (backend, produto, front, Debunker, Comitês, Bret, Kent) esteja olhando para a mesma imagem mental: 

> “Uma pessoa abre a UI, faz uma pergunta, vê uma resposta, entende o risco e enxerga evidências — e nós temos confiança técnica de que isso está sendo entregue de forma saudável e extensível.”
