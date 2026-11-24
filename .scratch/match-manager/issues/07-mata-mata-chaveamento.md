# 07: Mata-mata: chaveamento

**What to build:** Um usuário consegue escolher a ordem das equipes, sortear opcionalmente, configurar estratégias de bye e visualizar as fases geradas automaticamente.

**Blocked by:** 03 Administração de torneios; 04 Inscrição de equipes em torneios

**Status:** done

- [x] O usuário pode ordenar as equipes manualmente ou sortear a ordem inicial.
- [x] Byes são permitidos para completar chaveamentos que não tenham potência de dois equipes.
- [x] O usuário pode usar ordem manual, sorteio ou prioridade por desempenho para distribuir byes.
- [x] Uma equipe com bye avança automaticamente sem gerar partida fictícia.
- [x] A chave gera fases e partidas válidas até a partida final.
- [x] O torneio não inicia quando o chaveamento não estiver válido.
- [x] A visão do chaveamento mostra fases, equipes, partidas e vencedores avançados.
- [x] Geração manual, sorteio e byes são testados independentemente de Flask e HTTP.


## Comments

A ordem inicial funciona como ranking de desempenho: as equipes melhor posicionadas recebem os byes primeiro, preservando a ordem inicial em caso de empate. Byes não criam partidas; a equipe é posicionada automaticamente na fase seguinte. A tela permite reordenar equipes, sortear a ordem e escolher byes manualmente, por sorteio ou pelo ranking. O torneio só inicia após validação do chaveamento persistido. Os testes focados das duas seams confirmadas e regressões relacionadas passaram (49 testes).

