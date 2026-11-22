# 02: Cadastro completo de equipes

**What to build:** Um usuário consegue criar, buscar, consultar, editar e excluir equipes em uma página própria. A sigla ausente é gerada automaticamente sem impedir siglas duplicadas.

**Blocked by:** 01 Fundação persistente do MatchManager

**Status:** ready-for-agent

- [ ] Uma equipe exige nome único sem diferenciar maiúsculas e minúsculas.
- [ ] A sigla manual é opcional e aceita siglas duplicadas.
- [ ] Quando a sigla não é informada, o sistema gera até três letras, em maiúsculas e sem diacríticos ou pontuação.
- [ ] A página permite buscar, abrir, editar e excluir equipes.
- [ ] A exclusão é bloqueada enquanto a equipe pertence a um torneio iniciado.
- [ ] Os casos de nome, sigla e exclusão são cobertos por testes independentes de Flask e HTTP.

