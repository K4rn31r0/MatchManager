# 05: Pontos corridos: configuração e calendário

**What to build:** Um usuário consegue configurar pontos corridos, informar pontuação e desempates e gerar partidas válidas para turno único ou ida e volta.

**Blocked by:** 03 Administração de torneios; 04 Inscrição de equipes em torneios

**Status:** ready-for-agent

- [ ] O usuário pode escolher turno único ou ida e volta.
- [ ] Vitória, empate e derrota têm valores configuráveis, com vitória igual a três, empate igual a um e derrota igual a zero como sugestão inicial.
- [ ] A configuração rejeita pontuação em que vitória não seja maior que empate ou empate não seja maior que derrota.
- [ ] Existe pelo menos um critério de desempate positivo ou negativo.
- [ ] Cada critério possui nome, valor agregado e direção positiva ou negativa.
- [ ] Campos estatísticos podem ser definidos para alimentação posterior pelas partidas.
- [ ] O calendário gera um confronto por par no turno único e confrontos em ambos os sentidos na ida e volta.
- [ ] Número ímpar de equipes gera rodadas de descanso válidas.
- [ ] As configurações e o calendário são testados independentemente de Flask e HTTP.

