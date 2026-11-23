# 02: Cadastro completo de equipes

**What to build:** Um usuário consegue criar, buscar, consultar, editar e excluir equipes em uma página própria. A sigla ausente é gerada automaticamente sem impedir siglas duplicadas.

**Blocked by:** 01 Fundação persistente do MatchManager

**Status:** done

- [x] Uma equipe exige nome único sem diferenciar maiúsculas e minúsculas.
- [x] A sigla manual é opcional e aceita siglas duplicadas.
- [x] Quando a sigla não é informada, o sistema gera até três letras, em maiúsculas e sem diacríticos ou pontuação.
- [x] A página permite buscar, abrir, editar e excluir equipes.
- [x] A exclusão é bloqueada enquanto a equipe pertence a um torneio iniciado.
- [x] Os casos de nome, sigla e exclusão são cobertos por testes independentes de Flask e HTTP.


## Comments

**2026-11-23, decisões de implementação (confirmadas com o usuário):**

- O nome da equipe é único ignorando maiúsculas **e acentos** ("Grêmio" = "gremio"), a mesma regra dos torneios. É mais restritivo que a US9, que menciona só maiúsculas.
- A sigla automática usa as **três primeiras letras** do nome, ignorando acentos, pontuação, dígitos e espaços ("São Paulo" → "SAO", "E.C. Bahia" → "ECB"). Um nome sem letras fica sem sigla. A sigla manual é mantida como digitada; deixá-la vazia na edição gera uma nova a partir do nome.
- O bloqueio de exclusão é feito pela interface `TeamParticipationQuery` do core e testado com um fake. Como as inscrições só existem a partir da issue 04, a aplicação usa `NoRegistrationsParticipationQuery`, que sempre responde que a equipe não participa de torneio iniciado. **A issue 04 precisa substituir esse stub** por uma implementação baseada nas inscrições persistidas.
- Cor opcional no formato `#rrggbb` (salva em minúsculas). A lista de equipes fica em ordem alfabética.
