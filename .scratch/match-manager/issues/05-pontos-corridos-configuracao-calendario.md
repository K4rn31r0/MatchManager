# 05: Pontos corridos: configuração e calendário

**What to build:** Um usuário consegue configurar pontos corridos, informar pontuação e desempates e gerar partidas válidas para turno único ou ida e volta.

**Blocked by:** 03 Administração de torneios; 04 Inscrição de equipes em torneios

**Status:** done

- [x] O usuário pode escolher turno único ou ida e volta.
- [x] Vitória, empate e derrota têm valores configuráveis, com vitória igual a três, empate igual a um e derrota igual a zero como sugestão inicial.
- [x] A configuração rejeita pontuação em que vitória não seja maior que empate ou empate não seja maior que derrota.
- [x] Existe pelo menos um critério de desempate positivo ou negativo.
- [x] Cada critério possui nome e direção positiva ou negativa; os valores agregados são alimentados por partidas futuras.
- [x] Campos estatísticos podem ser definidos para alimentação posterior pelas partidas.
- [x] O calendário gera um confronto por par no turno único e confrontos em ambos os sentidos na ida e volta.
- [x] Número ímpar de equipes gera rodadas de descanso válidas.
- [x] As configurações e o calendário são testados independentemente de Flask e HTTP.

