# Sprint 25 — Checklist de Código Humano

Critérios objetivos de legibilidade e manutenção para avaliar mudanças da S25:

- **Nomenclatura clara**: funções, variáveis e módulos descrevem intenção; evitar siglas obscuras.
- **Funções pequenas**: foco em uma responsabilidade; blocos grandes devem ser quebrados ou comentados com intenção.
- **Contratos explícitos**: type hints presentes em serviços; docstrings curtas explicando o porquê de decisões não óbvias.
- **Invariantes visíveis**: regras de transição de estado e thresholds documentados próximo ao código que os aplica.
- **Testes cobrindo pontos críticos**: para estados de verdade, policies, pipelines, threatmodel; testes devem ser determinísticos.
- **Configuração declarativa**: políticas, thresholds e golden sets em YAML/JSON legíveis por humanos.
- **Ausência de TODO/FIXME**: débitos explícitos devem ser convertidos em tickets, não deixados no código.
- **Logs/Evidências**: scripts de gate devem produzir evidências em `out/evidence/` para auditoria rápida.
