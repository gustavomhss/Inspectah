# Inspectah — Sprint 31 (E28-S3)
## Capítulo 1 — Bloco 1: Contexto & Tese da Sprint

### 1.1. Onde a Sprint 31 entra na história

A Sprint 31 é a sprint em que o Inspectah **assume de vez** o modelo de ingestão provider-first para notícias e social, sem mais viver em modo híbrido confuso entre scrapers, APIs ad hoc e o roadmap novo.

Até aqui, o filme está assim:

- O **Roadmap Macro v3** e os **Programas 1–4** já dizem com todas as letras que a ingestão de conteúdo dinâmico deve ser feita via **omni-providers** (news_provider e social_provider), com perfis de ingestão configuráveis, budgets e observabilidade.
- As sprints anteriores (S21–S30) montaram a base: Console de Fontes, Data Hub v1, ingestão 2.0, observabilidade, Truth-DB e ClaimGraph em design avançado.
- Mas o código e a operação ainda carregam muita herança de “fonte = site”, com scrapers e APIs específicas tratados como caminho principal, e providers aparecendo mais no discurso do que na prática.

A S31 é justamente a sprint que fecha essa lacuna entre **visão** e **realidade operacional**.

### 1.2. Tese central da Sprint 31

A tese da Sprint 31 pode ser resumida em uma frase:

> "A partir do final da S31, notícias e social entram no Inspectah principalmente via **perfis de ingestão de providers**, e não mais fonte a fonte."

Isso significa, na prática:

- Providers passam a ser **entidades de primeira classe** no modelo de dados e no Console de Fontes.
- Perfis de ingestão (por país, idioma, tema, recorte de interesse) se tornam a unidade operacional: o operador pensa em ligar/desligar perfis, não scripts individuais.
- Scrapers e integrações diretas deixam de ser o caminho natural e passam a ser **exceções controladas**, com justificativa clara para existir.
- Todo ContentItem gerado por esses perfis vem com **proveniência rastreável** (provider + perfil + source), pronto para alimentar ClaimGraph, Truth-DB e Cockpits sem ambiguidades.

A Sprint 31 não precisa resolver todo o mundo de uma vez. Mas precisa deixar o sistema preparado para crescer, com uma arquitetura de ingestão coerente que seja:

- **escalável**: acrescentar novas regiões/temas é questão de criar novos perfis, não novos conectores do zero;
- **controlável em custo**: budgets, limites e métricas por perfil evitam que a fatura de providers exploda;
- **observável**: é possível ver o que cada perfil está trazendo, quanto está custando e como está se comportando.

### 1.3. O recorte de ambição da S31

Para manter foco e disciplina, a Sprint 31 se compromete com um recorte de ambição bem definido:

1. **Cobrir muito bem um conjunto pequeno de perfis críticos**, em vez de cobrir o planeta de forma rasa. Tipicamente:
   - Brasil / PT / política + economia (hard news);
   - um recorte internacional piloto (Latam ES ou EUA/UE EN) para validar multi-região;
   - um perfil social relevante para narrativas políticas/financeiras.
2. **Encaixar providers no ecossistema que já existe**, sem reinventar a roda:
   - respeitar o Data Hub, Console de Fontes, fila/worker, observabilidade e gates que já foram construídos nas sprints anteriores;
   - fazer o retrofit de modelos e fluxos para que providers convivam com fontes diretas, com um plano de aposentadoria gradual do legado.
3. **Preparar a pista para Programas 2–4**, garantindo que:
   - Programas 2 (Claims & Sinais) possam confiar que certos perfis de ingestão são estáveis e bem definidos;
   - Programas 3–4 encontrem ContentItems com proveniência limpa ao construir FactBlocks, EvidenceBlocks, Cockpits e Fact Cards.

A S31, portanto, é menos sobre “fazer coisas novas” e mais sobre **enquadrar o que já temos no modelo certo**, para que as sprints seguintes possam acelerar sem refazer a fundação da ingestão a cada épico novo.

