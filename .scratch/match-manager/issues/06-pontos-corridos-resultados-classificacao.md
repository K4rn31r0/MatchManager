# 06: Pontos corridos: resultados e classificação

**What to build:** Um usuário consegue registrar vitória, empate ou derrota com placar opcional e estatísticas, recalcular a tabela e ver o campeão após o encerramento.

**Blocked by:** 05 Pontos corridos: configuração e calendário

**Status:** done

- [x] Uma partida aceita resultado direto ou placar completo.
- [x] Placares parcialmente preenchidos são recusados.
- [x] Empates são permitidos e alimentam a pontuação configurada.
- [x] Estatísticas ausentes não são convertidas automaticamente em zero.
- [x] Cada resultado recalcula jogos, vitórias, empates, derrotas, pontos e estatísticas agregadas.
- [x] A classificação aplica os critérios configurados na ordem definida.
- [x] Critérios positivos favorecem valores maiores e negativos favorecem valores menores.
- [x] Empates totais são resolvidos pela ordem alfabética do nome da equipe.
- [x] A tabela mostra posição, equipe, jogos, vitórias, empates, derrotas e pontos em destaque.
- [x] O líder é destacado como campeão somente após o torneio ser encerrado.
- [x] Os cálculos são testados independentemente de Flask e HTTP.

