# 06: Pontos corridos: resultados e classificação

**What to build:** Um usuário consegue registrar vitória, empate ou derrota com placar opcional e estatísticas, recalcular a tabela e ver o campeão após o encerramento.

**Blocked by:** 05 Pontos corridos: configuração e calendário

**Status:** ready-for-agent

- [ ] Uma partida aceita resultado direto ou placar completo.
- [ ] Placares parcialmente preenchidos são recusados.
- [ ] Empates são permitidos e alimentam a pontuação configurada.
- [ ] Estatísticas ausentes não são convertidas automaticamente em zero.
- [ ] Cada resultado recalcula jogos, vitórias, empates, derrotas, pontos e estatísticas agregadas.
- [ ] A classificação aplica os critérios configurados na ordem definida.
- [ ] Critérios positivos favorecem valores maiores e negativos favorecem valores menores.
- [ ] Empates totais são resolvidos pela ordem alfabética do nome da equipe.
- [ ] A tabela mostra posição, equipe, jogos, vitórias, empates, derrotas e pontos em destaque.
- [ ] O líder é destacado como campeão somente após o torneio ser encerrado.
- [ ] Os cálculos são testados independentemente de Flask e HTTP.

