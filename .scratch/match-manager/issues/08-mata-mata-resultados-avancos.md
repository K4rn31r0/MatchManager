# 08: Mata-mata: resultados e avanços

**What to build:** Um usuário consegue registrar um vencedor com placar opcional, fazer a equipe avançar imediatamente e visualizar o progresso até a final.

**Blocked by:** 07 Mata-mata: chaveamento

**Status:** done

- [x] Toda partida exige um vencedor antes de ser concluída.
- [x] O vencedor pode ser informado diretamente sem placar.
- [x] O placar é opcional e não pode representar empate.
- [x] Placar parcial ou vencedor ausente impede a finalização.
- [x] O vencedor avança automaticamente para a próxima partida.
- [x] Uma partida subsequente mostra as equipes determinadas pelos resultados anteriores.
- [x] O vencedor da partida final é identificado como campeão ao encerrar o torneio.
- [x] Correções e avanços são testados independentemente de Flask e HTTP.

## Comments

O caso de uso registra e corrige resultados do mata-mata sem Flask, valida vencedor e placar e propaga o vencedor à posição correspondente na fase seguinte. Correções são bloqueadas quando uma partida posterior já foi concluída. A interface permite registrar vencedores e placares, acompanhar o chaveamento até a final, encerrar o torneio após concluir as partidas e consultar o campeão. Os testes focados e regressões relacionadas passaram (42 testes); a suíte completa foi deixada para a coordenação.

