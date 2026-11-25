# 09: Ciclo, correções e encerramento

**What to build:** Um usuário consegue iniciar, acompanhar e encerrar um torneio, corrigindo resultados permitidos sem alterar configurações estruturais depois do início.

**Blocked by:** 05 Pontos corridos: configuração e calendário; 06 Pontos corridos: resultados e classificação; 07 Mata-mata: chaveamento; 08 Mata-mata: resultados e avanços

**Status:** done

- [x] O início exige pelo menos duas equipes e uma configuração válida.
- [x] Ao iniciar, o torneio fecha novas inscrições e gera todas as partidas aplicáveis.
- [x] A configuração de pontuação, critérios, estatísticas e estrutura fica bloqueada após o início.
- [x] Partidas de pontos corridos podem ser corrigidas em andamento e no torneio encerrado.
- [x] Correções em pontos corridos recalculam a classificação.
- [x] Correções no mata-mata são bloqueadas após o início ou ocorrência de uma partida subsequente.
- [x] Correções permitidas em torneio encerrado não mudam seu status.
- [x] O encerramento é bloqueado enquanto existir partida aplicável pendente.
- [x] O encerramento mantém o status fechado para nova estrutura ou configuração.
- [x] Todos os estados e bloqueios são testados independentemente de Flask e HTTP.

## Comments

O início passou a ser um caso de uso único, `StartTournament`, que delega a uma estratégia por formato (`StartRoundRobinTournament` e `StartKnockoutTournament`). Pontos corridos ainda não tinham início: agora o início valida rascunho, configuração e pelo menos duas equipes, regenera o calendário completo e muda o status para em andamento. O calendário gerado no rascunho passa a ser apenas uma pré-visualização. A entidade `Tournament` ganhou `start()` e `ensure_accepts_results()`; resultados e correções são aceitos em torneios em andamento ou encerrados, sem alterar o status. No mata-mata, a correção é bloqueada somente quando a partida subsequente que depende daquele resultado já foi concluída (antes, qualquer partida concluída numa fase posterior bloqueava); por isso a final de um mata-mata encerrado pode ser corrigida e o campeão é recalculado. A interface ganhou a página de confirmação `/tournaments/<id>/start` com formato, regras e participantes. Os testes em `tests/use_cases/test_tournament_lifecycle.py` cobrem início, bloqueios em andamento e encerrado, correções e encerramento apenas com fakes; `tests/api/test_tournament_lifecycle.py` cobre o fluxo web. Suíte completa: 196 testes passando.

