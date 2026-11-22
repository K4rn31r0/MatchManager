# 09: Ciclo, correções e encerramento

**What to build:** Um usuário consegue iniciar, acompanhar e encerrar um torneio, corrigindo resultados permitidos sem alterar configurações estruturais depois do início.

**Blocked by:** 05 Pontos corridos: configuração e calendário; 06 Pontos corridos: resultados e classificação; 07 Mata-mata: chaveamento; 08 Mata-mata: resultados e avanços

**Status:** ready-for-agent

- [ ] O início exige pelo menos duas equipes e uma configuração válida.
- [ ] Ao iniciar, o torneio fecha novas inscrições e gera todas as partidas aplicáveis.
- [ ] A configuração de pontuação, critérios, estatísticas e estrutura fica bloqueada após o início.
- [ ] Partidas de pontos corridos podem ser corrigidas em andamento e no torneio encerrado.
- [ ] Correções em pontos corridos recalculam a classificação.
- [ ] Correções no mata-mata são bloqueadas após o início ou ocorrência de uma partida subsequente.
- [ ] Correções permitidas em torneio encerrado não mudam seu status.
- [ ] O encerramento é bloqueado enquanto existir partida aplicável pendente.
- [ ] O encerramento mantém o status fechado para nova estrutura ou configuração.
- [ ] Todos os estados e bloqueios são testados independentemente de Flask e HTTP.

