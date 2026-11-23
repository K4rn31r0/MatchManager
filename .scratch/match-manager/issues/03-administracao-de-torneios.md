# 03: Administração de torneios

**What to build:** Um usuário consegue criar, editar, listar, buscar, filtrar, consultar e excluir torneios pela interface. A visão principal apresenta o contexto necessário para continuar cada torneio.

**Blocked by:** 01 Fundação persistente do MatchManager

**Status:** done

- [x] A página inicial lista torneios por atividade recente e permite busca por nome.
- [x] Os torneios podem ser filtrados por rascunho, em andamento e encerrado.
- [x] Um torneio em rascunho pode ser editado e excluído com confirmação.
- [x] O nome duplicado é recusado sem diferenciar maiúsculas, minúsculas ou acentos.
- [x] A exclusão remove inscrições e partidas relacionadas.
- [x] O resumo exibido apresenta nome, modalidade, formato, status, participantes e datas.
- [x] Cadastro, busca, edição, exclusão e consultas são cobertos por testes de regras independentes de HTTP.


## Comments

A exclusão com confirmação está disponível nos três status e remove inscrições e partidas. A edição continua limitada aos rascunhos. Validação concluída com 95 testes passando.
