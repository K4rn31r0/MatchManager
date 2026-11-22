# Especificacao do MatchManager

Status: ready-for-agent

## Problem Statement

Um grupo esportivo precisa organizar campeonatos sem depender de um tipo especifico de esporte, login ou infraestrutura externa. Atualmente nao existe uma forma simples de cadastrar torneios e equipes, configurar formatos diferentes, registrar partidas e calcular classificacoes com regras distintas em um mesmo produto.

O aplicativo precisa permitir essas tarefas em uma interface acessivel por celular e desktop, mantendo os dados localmente. As regras devem funcionar mesmo sem interface web ou Flask, pois o esporte nao define previamente resultados, placares, estatisticas ou desempates.

## Solution

O MatchManager sera um gerenciador de torneios esportivos generico. O usuario podera:

- criar, listar, abrir, editar e excluir torneios;
- criar, listar, abrir, editar e excluir equipes;
- inscrever equipes em torneios;
- configurar torneios em pontos corridos ou mata-mata;
- gerar partidas;
- registrar vencedores, placares e estatisticas opcionais;
- acompanhar classificacao, chaveamento e campeao;
- corrigir resultados dentro das regras permitidas.

O ciclo principal sera realizado no mesmo ambiente pelo proprio usuario:

1. criar torneio e equipes;
2. configurar o formato e as regras;
3. inscrever as equipes;
4. iniciar o torneio;
5. registrar os resultados das partidas;
6. encerrar o torneio;
7. consultar o resultado final.

Nao existira login, conta de usuario ou associacao de acoes a pessoas.

## User Stories

1. Como organizador, quero criar um torneio com nome unico, modalidade opcional, formato e datas opcionais, para iniciar o cadastro da competicao.
2. Como organizador, quero ver o status de cada torneio, para saber quais estao em rascunho, em andamento ou encerrados.
3. Como organizador, quero editar um torneio em rascunho, para ajustar dados antes de iniciar a competicao.
4. Como organizador, quero excluir um torneio com confirmacao, para remover competicoes criadas por engano.
5. Como organizador, quero remover todas as inscricoes e partidas ao excluir um torneio, para nao deixar dados orfaos.
6. Como organizador, quero impedir nomes de torneios repetidos sem diferenciar maiusculas e minusculas ou acentos, para evitar ambiguidade.
7. Como organizador, quero manter um nome de torneio preservado exatamente como foi digitado, para usa-lo como exibicao.
8. Como organizador, quero criar uma equipe com nome, sigla opcional, cor opcional e observacoes, para representa-la no sistema.
9. Como organizador, quero que o nome da equipe seja unico sem diferenciar maiusculas e minusculas, para evitar equipes duplicadas.
10. Como organizador, quero que uma sigla nao informada seja gerada automaticamente com ate tres letras significativas do nome, para nao depender de preenchimento manual.
11. Como organizador, quero que siglas duplicadas sejam permitidas, para evitar impedimentos em esportes com nomes semelhantes.
12. Como organizador, quero normalizar a sigla automatica removendo pontuacao e diacriticos e usando letras maiusculas, para obter uma representacao consistente.
13. Como organizador, quero editar uma sigla existente, para corrigir uma abreviacao gerada automaticamente.
14. Como organizador, quero buscar equipes pelo nome, para encontrar uma equipe rapidamente.
15. Como organizador, quero abrir os dados de uma equipe, para consultar seu cadastro e os torneios em que participa.
16. Como organizador, quero consultar em quais torneios uma equipe participa e o status de cada torneio, para entender seu historico.
17. Como organizador, quero consultar a fase ou classificacao alcancada pela equipe em torneios encerrados, para resumir sua participacao.
18. Como organizador, quero editar uma equipe, para manter nome, sigla, cor e observacoes atualizados.
19. Como organizador, quero excluir uma equipe, mas somente fora de torneios iniciados, para nao quebrar dados de competicoes em andamento.
20. Como organizador, quero criar uma equipe diretamente durante a inscricao em um torneio, para evitar voltar a varias telas.
21. Como organizador, quero adicionar equipes existentes a um torneio em rascunho, para montar a lista de participantes.
22. Como organizador, quero remover uma equipe inscrita antes do inicio do torneio, para corrigir a lista.
23. Como organizador, quero impedir a inscricao repetida da mesma equipe no mesmo torneio, para garantir uma entrada unica.
24. Como organizador, quero filtrar equipes disponiveis entre as ja inscritas, para nao escolher uma equipe duplicada.
25. Como organizador, quero configurar um torneio como pontos corridos, para calcular classificacao por uma tabela geral.
26. Como organizador, quero configurar um torneio como mata-mata, para eliminar equipes ao longo de fases.
27. Como organizador, quero escolher turno unico em pontos corridos, para gerar um confronto por par de equipes.
28. Como organizador, quero escolher ida e volta em pontos corridos, para gerar confrontos em dois sentidos.
29. Como organizador, quero que o sistema gere todas as partidas de pontos corridos automaticamente, para evitar montagem manual.
30. Como organizador, quero que equipes sem adversario em uma rodada de pontos corridos tenham descanso, para manter o calendario valido.
31. Como organizador, quero repetir os descansos em cada turno da configuracao ida e volta, para manter cada equipe em equivalencia.
32. Como organizador, quero definir vitoria, empate e derrota em pontos, para adaptar a pontuacao ao esporte ou jogo.
33. Como organizador, quero usar vitoria igual a tres pontos, empate igual a um ponto e derrota igual a zero como valores sugeridos, para comecar rapidamente.
34. Como organizador, quero que os pontos sigam a relacao vitoria maior que empate maior que derrota, para manter regras coerentes.
35. Como organizador, quero cadastrar pelo menos um criterio de desempate em pontos corridos, para a tabela possuir uma ordem deterministica.
36. Como organizador, quero nomear um criterio de desempate e informar um valor numerico por equipe, para representar a estatistica usada.
37. Como organizador, quero indicar que um criterio deve favorecer numeros maiores ou menores, para distinguir criterios positivos e negativos.
38. Como organizador, quero usar gols marcados como criterio positivo e faltas como criterio negativo, como exemplos de configuracao generica.
39. Como organizador, quero que estatisticas sejam registradas por equipe em uma partida, para alimentar a classificacao e os criterios definidos.
40. Como organizador, quero registrar uma partida de pontos corridos informando uma vitoria, empate ou derrota sem placar, para servir a esportes ou jogos que nao usam pontuacao numerica.
41. Como organizador, quero registrar placar em pontos corridos quando ele existir, para detalhar o resultado.
42. Como organizador, quero impedir placar parcialmente preenchido, para nao salvar resultados incompletos.
43. Como organizador, quero que placar obrigatoriamente tenha vitoria, empate ou derrota coerente com o resultado registrado, para evitar contradicoes.
44. Como organizador, quero permitir estatisticas de partida vazias, sem interpreta-las automaticamente como zero, para nao inventar dados inexistentes.
45. Como organizador, quero selecionar manualmente a ordem inicial das equipes em mata-mata, para definir o chaveamento.
46. Como organizador, quero sortear aleatoriamente a ordem inicial em mata-mata, como alternativa opcional ao chaveamento manual.
47. Como organizador, quero completar automaticamente o chaveamento com byes quando houver numero menor que potencia de dois equipes, para iniciar sem confrontos ficticios.
48. Como organizador, quero escolher byes por ordem manual, sorteio ou prioridade associada ao desempenho, para controlar o inicio do chaveamento.
49. Como organizador, quero avancar automaticamente uma equipe que recebeu bye para a fase seguinte, para nao exigir registro de partida ficticia.
50. Como organizador, quero registrar o vencedor de uma partida de mata-mata diretamente, sem placar, para lidar com modalidades sem placar.
51. Como organizador, quero registrar o placar opcional de uma partida de mata-mata, mas exigir um vencedor, para manter o resultado inequivoco.
52. Como organizador, quero impedir placar empatado em mata-mata, para garantir que apenas uma equipe avance.
53. Como organizador, quero impedir que uma partida seja finalizada sem vencedor no mata-mata, para manter a continuidade da chave.
54. Como organizador, quero que o vencedor avance automaticamente para a partida seguinte no mata-mata, para atualizar o chaveamento.
55. Como organizador, quero impedir alteracoes em um resultado do mata-mata apos uma partida subsequente iniciar ou ocorrer, para preservar a integridade da chave.
56. Como organizador, quero editar uma partida em pontos corridos antes ou depois de concluida quando o torneio estiver em andamento, para corrigir erros.
57. Como organizador, quero que uma correcao em pontos corridos recalcule estatisticas e classificacao imediatamente, para manter a tabela consistente.
58. Como organizador, quero corrigir resultados registrados de um torneio encerrado sem mudar automaticamente seu status para em andamento, para preservar o encerramento.
59. Como organizador, quero impedir alteracoes de pontuacao, criterios, estatisticas ou estrutura apos o inicio do torneio, para evitar reinterpretacao de partidas passadas.
60. Como organizador, quero configurar todas as regras antes de iniciar, mas manter apenas correcoes de resultados apos o inicio, para separar planejamento e operacao.
61. Como organizador, quero iniciar um torneio quando houver pelo menos duas equipes, para garantir uma competicao valida.
62. Como organizador, quero impedir o inicio de mata-mata quando o chaveamento nao puder ser gerado corretamente, para evitar partidas incompletas.
63. Como organizador, quero ver uma confirmacao com formato e participantes antes de iniciar, para revisar a decisao.
64. Como organizador, quero que o inicio feche automaticamente novas inscricoes, para preservar a lista de participantes.
65. Como organizador, quero que o inicio genere as partidas e mude o status para em andamento, para executar o campeonato.
66. Como organizador, quero manter datas e locais como opcionais nas partidas, para servir campeonatos sem agendamento detalhado.
67. Como organizador, quero filtrar partidas por rodada ou fase e por status, para localizar jogos pendentes e concluidos.
68. Como organizador, quero ver equipes, placar ou vencedor e status em cada item de partida, para identificar rapidamente o resultado.
69. Como organizador, quero abrir o formulario de uma partida, para registrar ou corrigir o resultado.
70. Como organizador, quero marcar uma partida como concluida somente quando existir resultado valido, para evitar estados incompletos.
71. Como organizador, quero ver partidas concluidas e pendentes separadas ou filtraveis, para acompanhar o progresso.
72. Como organizador, quero encerrar um torneio somente depois que todas as partidas aplicaveis estiverem concluidas, para nao finalizar com pendencias.
73. Como organizador, quero ver mensagens claras quando a exclusao, inicio, finalizacao ou registro nao cumprir uma validacao, para saber como corrigir.
74. Como organizador, quero ver a classificacao em pontos corridos com posicao, equipe, jogos, vitorias, empates, derrotas e pontos, para acompanhar o campeonato.
75. Como organizador, quero destacar a coluna de pontos em negrito, para facilitar a leitura do resultado principal.
76. Como organizador, quero adicionar uma coluna na classificacao para cada estatistica configurada, para comparar criterios positivos e negativos.
77. Como organizador, quero que a classificacao aplique os criterios na ordem configurada pelo usuario, para respeitar as regras do torneio.
78. Como organizador, quero que, se todos os criterios empatarem, o nome da equipe seja usado em ordem alfabetica como desempate final automatico, para obter uma ordem deterministica.
79. Como organizador, quero ver que a ordenacao alfabetica foi usada como desempate final, para entender a posicao na tabela.
80. Como organizador, quero destacar o lider da classificacao somente depois que o torneio de pontos corridos estiver encerrado, para identificar o campeao sem anuncio prematuro.
81. Como organizador, quero destacar o vencedor da partida final ao encerrar um mata-mata, para identificar o campeao.
82. Como organizador, quero visualizar o progresso do mata-mata em fases, para acompanhar os avancos de cada etapa.
83. Como organizador, quero listar torneios por atividade recente, nome, formato e status, para priorizar o trabalho atual.
84. Como organizador, quero buscar torneios pelo nome e filtrar por status, para encontrar uma competicao rapidamente.
85. Como organizador, quero ver na pagina inicial nome, modalidade, formato, status, quantidade de equipes e datas do torneio, para comparar as competicoes.
86. Como organizador, quero usar uma pagina separada de equipes com busca e botoes de criar, editar e excluir, para administrar o cadastro global.
87. Como organizador, quero ver na pagina de equipes quais torneios a equipe participa, para entrar no contexto correto.
88. Como organizador, quero abrir a aba de equipes de um torneio, para consultar participantes e realizar inscricoes.
89. Como organizador, quero que a aba de partidas de um torneio mostre partidas futuras e concluidas, para acompanhar o calendario.
90. Como organizador, quero que a aba de classificacao apareca em pontos corridos e apos o inicio, para acompanhar as posicoes.
91. Como organizador, quero usar uma navegacao simples em celular, para realizar todas as tarefas em tela pequena.
92. Como organizador, quero que o app mantenha todas as informacoes em um arquivo JSON local, para persistir sem banco de dados.
93. Como organizador, quero que o aplicativo nao exija login, para permitir uso direto por qualquer pessoa no dispositivo.
94. Como organizador, quero que a interface use HTML renderizado no servidor e CSS proprio, para manter uma experiencia simples.
95. Como organizador, quero que JavaScript nao seja necessario para as interacoes principais, para manter o app simples e acessivel.

## Implementation Decisions

- Os torneios terao uma lista central na pagina inicial e uma visao detalhada em contexto.
- Um torneio tera nome unico, modalidade livre opcional, formato, datas opcionais, status, configuracao de pontuacao e configuracao de criterios de desempate.
- Os estados funcionais do torneio serao rascunho, em andamento e encerrado.
- Rascunho significa configuracao sem partidas iniciadas ou resultados. Ele permite editar dados, regras e inscricoes.
- As equipes serao entidades globais reutilizaveis entre torneios.
- Uma equipe tera nome unico, sigla opcional ou gerada, cor opcional e observacoes.
- A sigla automatica usara ate tres letras, em maiusculas, sem diacriticos e removendo pontuacao, preservando a possibilidade de siglas repetidas.
- Uma equipe podera participar de varios torneios, mas aparecera uma unica vez em cada torneio.
- A inscricao sera fechada automaticamente no inicio do torneio.
- Partidas conterao equipes, rodada ou fase, data opcional, local opcional, status, vencedor opcional e placar opcional.
- No mata-mata, vencedor sera obrigatorio e o placar, quando informado, nao podera representar empate.
- Nos pontos corridos, um resultado podera ser registrado por placar ou por resultado direto. Empate sera permitido.
- Ao registrar um placar incompleto, o sistema recusara o resultado.
- Estatisticas configuradas serao numericas por equipe e por partida.
- Uma estatistica vazia nao sera convertida em zero.
- Pontos corridos poderao ser turno unico ou ida e volta.
- Pontos corridos gerarao partidas por round robin, com descansos automaticos para numero impar de equipes.
- Mata-mata gerara fases e partidas automaticamente a partir da lista inicial, usando byes quando necessario.
- O inicio permitira escolher manualmente por ordem, sorteio ou outra regra para byes.
- Mata-mata nao podera iniciar sem chaveamento valido e equipes suficientes.
- O vencedor avanca imediatamente para a partida seguinte.
- Correcoes de partidas de pontos corridos recalculem a classificacao.
- A classificacao aplicara pontos e criterios de desempate na ordem configurada.
- Os criterios terao nome, valor numerico agregado por equipe e direcao positiva ou negativa.
- O criterio positivo favorece valores maiores; o negativo favorece valores menores.
- Ordem alfabetica do nome sera o desempate final automatico.
- A tabela mostrara posicao, equipe, jogos, vitorias, empates, derrotas e pontos em negrito, seguidos pelas estatisticas configuradas.
- O usuario podera alterar apenas resultados apos o inicio; pontuacao, criterios, estatisticas e estrutura ficam travados.
- O torneio encerrado pode receber correcoes de resultados sem mudar seu status.
- Uma correcao no mata-mata sera bloqueada quando uma partida subsequente ja tiver ocorrido.
- O encerramento exigira todas as partidas aplicaveis concluidas.
- Em pontos corridos, o lider sera destacado como campeao apenas ao encerrar.
- Em mata-mata, o vencedor da partida final sera destacado ao encerrar.
- O aplicativo usara persistencia exclusiva em um arquivo JSON local.
- A interface sera composta por HTML renderizado no servidor com Jinja2, CSS proprio e responsividade mobile-first.
- Nao sera utilizado framework JavaScript ou biblioteca de interface.

## Use Cases

Os Use Cases abaixo agrupam as responsabilidades derivadas das User Stories. Cada caso sera independente de Flask e HTTP e recebera suas dependencias por interfaces definidas na camada de regras.

1. **Criar torneio**
   - Valida nome unico sem diferenciar maiusculas, minusculas ou acentos.
   - Cria o torneio em estado de rascunho com dados gerais e formato.
   - Cobre as User Stories 1, 6 e 7.

2. **Editar torneio**
   - Permite alterar dados gerais e configuracoes enquanto o torneio estiver em rascunho.
   - Revalida o nome unico e impede alteracoes estruturais apos o inicio.
   - Cobre as User Stories 3 e 59.

3. **Excluir torneio**
   - Exclui o torneio apos confirmacao e remove suas inscricoes e partidas relacionadas.
   - Cobre as User Stories 4 e 5.

4. **Listar torneios**
   - Lista torneios por atividade recente e permite busca por nome e filtro por status.
   - Cobre as User Stories 2, 83 e 84.

5. **Consultar torneio**
   - Retorna dados gerais, participantes, partidas, status e resultado disponivel do torneio.
   - Cobre as User Stories 85 e 88 a 90.

6. **Criar equipe**
   - Valida nome unico e gera automaticamente uma sigla de ate tres letras quando ela nao for informada.
   - Cobre as User Stories 8 a 12.

7. **Editar equipe**
   - Atualiza nome, sigla, cor e observacoes.
   - Mantem o nome unico e permite siglas duplicadas.
   - Cobre as User Stories 13 e 18.

8. **Excluir equipe**
   - Permite exclusao apenas quando a equipe nao estiver inscrita em um torneio iniciado.
   - Cobre a User Story 19.

9. **Listar e consultar equipes**
   - Permite busca por nome, consulta dos dados da equipe e de seus torneios associados.
   - Cobre as User Stories 14 a 17.

10. **Adicionar equipe ao torneio**
    - Inscreve uma equipe existente em um torneio em rascunho.
    - Bloqueia equipe inexistente, duplicada ou inscricao apos o inicio.
    - Cobre as User Stories 21, 23 e 24.

11. **Criar equipe e inscrever no torneio**
    - Cria a equipe global e a inscreve imediatamente no torneio em rascunho.
    - Cobre a User Story 20.

12. **Remover equipe do torneio**
    - Remove uma inscricao enquanto o torneio estiver em rascunho.
    - Cobre a User Story 22.

13. **Configurar pontos corridos**
    - Define turno unico ou ida e volta, pontos de vitoria, empate e derrota e criterios de desempate.
    - Exige pelo menos um criterio e a relacao vitoria maior que empate maior que derrota.
    - Cobre as User Stories 25, 27, 28, 32 a 37 e 60.

14. **Configurar mata-mata**
    - Define a ordem inicial, a estrategia de byes e prepara o chaveamento para inicio.
    - Cobre as User Stories 26, 45 a 48.

15. **Configurar estatisticas da partida**
    - Cria os campos estatisticos numericos do torneio e define seu uso como criterio positivo ou negativo.
    - Cobre as User Stories 38, 39 e 76.

16. **Gerar partidas de pontos corridos**
    - Gera uma partida por par no turno unico ou confrontos em ambos os sentidos na ida e volta.
    - Representa automaticamente rodadas de descanso para numero impar de equipes.
    - Cobre as User Stories 29 a 31.

17. **Gerar chave de mata-mata**
    - Gera fases e partidas a partir da ordem das equipes.
    - Completa o chaveamento com byes por ordem manual, sorteio ou desempenho.
    - Cobre as User Stories 47 a 49 e 62.

18. **Iniciar torneio**
    - Valida participantes e configuracao, gera o calendario ou chaveamento e fecha novas inscricoes.
    - Transforma o torneio em estado em andamento.
    - Cobre as User Stories 61 a 65.

19. **Consultar partidas do torneio**
    - Lista partidas por rodada ou fase e por status, incluindo participantes e resultados.
    - Cobre as User Stories 67, 68, 71 e 89.

20. **Registrar resultado de partida**
    - Valida placar completo ou ausente, resultado direto, vencedor e estatisticas da partida.
    - Permite empate em pontos corridos e exige vencedor em mata-mata.
    - Cobre as User Stories 40 a 44 e 50 a 53.

21. **Corrigir resultado de partida**
    - Permite correcoes em pontos corridos em andamento e no torneio encerrado.
    - Recusa correcao no mata-mata quando uma partida subsequente ja tiver ocorrido.
    - Cobre as User Stories 55, 56, 58 e 69.

22. **Calcular classificacao de pontos corridos**
    - Atualiza jogos, vitorias, empates, derrotas, pontos e estatisticas agregadas.
    - Aplica criterios positivos e negativos na ordem configurada e o nome alfabetico como desempate final.
    - Cobre as User Stories 57, 74 a 79.

23. **Avancar vencedor no mata-mata**
    - Insere o vencedor na partida seguinte e impede vencedor ausente ou empate.
    - Cobre as User Stories 54 e 62.

24. **Encerrar torneio**
    - Impede encerramento com partidas pendentes.
    - Em pontos corridos destaca o lider apenas ao encerrar; em mata-mata destaca o vencedor da partida final.
    - Cobre as User Stories 72, 80 e 81.

25. **Consultar pagina inicial e navegacao**
    - Prepara dados resumidos dos torneios para listagem, busca e filtros.
    - Cobre as User Stories 83 a 86 e 91 a 95.

## Testing Decisions

- A principal seam de teste sera o modulo de regras das listas, independente de Flask, HTTP, templates e persistencia.
- Os testes serao unitarios em pytest e externalizarao o comportamento por entradas e resultados das operacoes de dominio.
- Seams existentes ou novas serao concentradas no modulo de regras, nao espalhadas entre controllers e interface.
- Os testes devem cobrir operacoes validas e invalidas, nao verificar detalhes internos de implementacao.
- A operacao de criar torneio deve ser testada com nomes validos, nomes duplicados, maiusculas e nomes com acentos normalizados.
- A operacao de criar ou editar equipes deve cobrir nome vazio, nome duplicado e geracao de sigla automatica.
- As inscricoes devem cobrir equipe repetida, equipe inexistente, remocao em rascunho e bloqueio apos o inicio.
- As regras de inicio devem validar quantidade minima de equipes e configuracao valida para o formato.
- Os testes de pontos corridos devem cobrir turno unico, ida e volta, numero par e impar de equipes e descanso.
- Os testes de pontuacao devem cobrir configuracoes invalidas, valores sugeridos e a relacao vitoria maior que empate maior que derrota.
- Os criterios de desempate devem cobrir criterio positivo, criterio negativo, ordem de aplicacao e empate final alfabetico.
- Estatisticas de partida devem cobrir preenchimento, ausencia e agregacao por equipe.
- Os testes de partida devem cobrir placar completo, placar incompleto, empate em pontos corridos, empate em mata-mata e vencedor direto sem placar.
- Os testes de mata-mata devem cobrir chaveamento manual, sorteio, byes, numero par e impar de participantes e avancos entre fases.
- A correcao de partidas deve cobrir recalcificacao em pontos corridos e bloqueio apos partida subsequente no mata-mata.
- Os testes de encerramento devem cobrir partidas pendentes, todas concluidas e destaque do campeao.
- Os testes devem validar que configuracoes estruturais ficam bloqueadas apos o inicio e que correcoes continuam permitidas.
- O estado persistido nao deve ser exigido nesses testes: fakes ou repositorios em memoria podem substituir o repositorio concreto.
- A persistencia em arquivo JSON e os testes HTTP podem ser cobertos separadamente, mas nao sao a principal seam das regras de negocio.

## Out of Scope

- Login, contas de usuario, permissoes e autenticacao.
- Banco de dados SQL ou NoSQL.
- API publica ou integracao com terceiros.
- Cadastro de atletas ou pessoas dentro das equipes.
- Posicoes, funcoes ou elenco.
- Suporte obrigatorio a formatos alem de pontos corridos e mata-mata simples.
- Grupos, classificacao por grupos e segunda fase composta.
- Repescagem, playoff adicional ou regiao de rebaixamento.
- Desempate em mata-mata por prorrogacao, penalidades ou critico especial alem do vencedor informado.
- Notificacoes, e-mail, SMS ou compartilhamento externo.
- Aplicativo nativo ou framework JavaScript.
- Sincronizacao entre dispositivos.
- Exportacao, importacao ou backup de arquivos fora da persistencia JSON local.
- Configuracao cosmética avancada de temas ou branding.

## Further Notes

- A especificacao deve ser implementada em uma arquitetura com separacao entre regras de dominio, casos de uso, adaptadores e interface.
- O modulo central de regras deve ser testavel sem Flask, servidor HTTP ou arquivos reais.
- Os textos da interface devem estar em portugues.
- Os nomes de conceito devem seguir o mesmo vocabulario desta especificacao: torneio, equipe, partida, inscricao, rascunho, em andamento, encerrado, pontos corridos, mata-mata, criterio de desempate e campeao.
- Esta especificacao representa as decisoes funcionais do gerenciamento inicial. Detalhes visuais, como tipografia, cor exata e espacamento, devem ser definidos posteriormente sem alterar o modelo descrito.
