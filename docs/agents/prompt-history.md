# Histórico de prompts

Registro sequencial das ações significativas realizadas com apoio de IA, com o prompt que originou cada uma.

## 001 — Implementação da issue 01: Fundação persistente

**Data:** 2026-11-23
**Ferramenta:** Claude Code (Claude Opus 5.5)
**Branch:** `issue-01-fundacao-persistente`

**Prompt:**

> agr, seguindo o padrao do enunciado e o que foi especificado nos mds do repo, precisaria implementar issue 01 e 02. Vamos fazer com calma, uma por uma em branches separadas

**Decisões confirmadas com o usuário antes da implementação:** nome e formato obrigatórios; modalidade e datas opcionais; data de término anterior à de início é recusada; seams de teste em `CreateTournament`, `ListTournaments` (com repositório fake em memória) e `JsonTournamentRepository` (com arquivo temporário).

**O que foi feito:** Implementada a primeira fatia vertical seguindo Clean Architecture e TDD (red → green por seam). No core foram criados a entidade imutável `Tournament` (com `TournamentFormat`, `TournamentStatus` e invariantes de nome e datas), a regra de domínio `normalize_name` (compara nomes ignorando maiúsculas, acentos e espaços externos), a interface `TournamentRepository`, os erros de domínio e os casos de uso `CreateTournament` e `ListTournaments`, que recebem dependências por injeção (repositório, gerador de ids e relógio). Na infraestrutura, `JsonFileStorage` grava um único arquivo JSON de forma atômica e `JsonTournamentRepository` implementa o contrato do core. Na camada de adaptadores, o controller Flask converte o formulário em entrada do caso de uso e traduz erros em mensagens em português, e o presenter formata rótulos e datas. `server/app.py` é a raiz de composição. Foram adicionados `requirements.txt`, configuração do pytest, templates Jinja2 e CSS próprio mínimo. Resultado: 20 testes passando e código conforme PEP-8 (`pycodestyle`).

## 002 — Implementação da issue 02: Cadastro completo de equipes

**Data:** 2026-11-23
**Ferramenta:** Claude Code (Claude Opus 5.5)
**Branch:** `issue-02-cadastro-de-equipes` (criada a partir do commit da issue 01)

**Prompt:**

> agr, seguindo o padrao do enunciado e o que foi especificado nos mds do repo, precisaria implementar issue 01 e 02. Vamos fazer com calma, uma por uma em branches separadas

**Decisões confirmadas com o usuário antes da implementação:** nome da equipe único ignorando maiúsculas e acentos; sigla automática com as três primeiras letras do nome; bloqueio de exclusão por meio de uma interface no core com stub até a issue 04; seams de teste nos casos de uso (repositórios fake), na entidade `Team` (novo diretório `tests/entities/`) e em `JsonTeamRepository` (arquivo temporário, incluindo convivência com torneios no mesmo JSON).

**O que foi feito:** Implementada a segunda entidade do domínio, `Team`, imutável, com invariantes de nome e cor, geração automática de sigla, comparação de nomes e busca. As funções de texto (`remove_accents`, `normalize_name`, `optional_text`) foram centralizadas em `names.py` e reaproveitadas por `Tournament`. Foram criados os casos de uso `CreateTeam`, `ListTeams`, `GetTeam`, `UpdateTeam` e `DeleteTeam`, que dependem das abstrações `TeamRepository` e `TeamParticipationQuery`, com a regra de nome único compartilhada entre criação e edição. Na infraestrutura, `JsonTeamRepository` usa a chave `teams` do mesmo arquivo JSON, e `NoRegistrationsParticipationQuery` atende à consulta de participação até a issue 04. Na interface, a página "Equipes" ganhou busca, criação, detalhe, edição e exclusão com página de confirmação, sem JavaScript, e um 404 em português para equipe inexistente. Resultado: 84 testes passando (28 de entidade, 46 de casos de uso e 10 de infraestrutura) e código conforme PEP-8.

## 003 — Verificação inicial das issues 03 e 04

**Data:** 2026-11-23
**Ferramenta:** Codex
**Branch:** `issue-03-administracao-de-torneios`

**Prompt:**

> seguindo o padrao do enunciado e o que foi especificado nos mds do repo, precisaria implementar issue 03 e 04. Vamos fazer com calma, uma por uma em branches separadas. A branch da issue 03 já está criada.
>
> 1. Confira a ordem em .scratch/match-manager/dag.md e verifique se as dependências estão implementadas na branch atual. Leia AGENTS.md e .scratch/match-manager/spec.md antes de começar.
> 2. Implemente a issue completa, incluindo o fluxo pela interface. Rode pytest, confira cada critério de aceitação e atualize o ticket local. Marque como done apenas quando todos os critérios forem atendidos. Registre o prompt e o resultado em docs/agents/prompt-history.md.
> 3. Só inicie a implementação da issue 04 depois de concluir e validar a 03. Se houver um bloqueio ou uma regra importante em aberto, pare e me avise.

**O que foi feito:** Conferi o DAG, a especificação, os tickets locais e o código existente. A branch da issue 03 contém a fundação persistente da issue 01 e o cadastro de equipes da issue 02. A implementação parou antes de alterar código ou tickets. A especificação pede preservar o nome exatamente como digitado, mas o teste vigente exige remover espaços nas extremidades. Também ficou pendente definir se a exclusão com confirmação se estende a torneios iniciados ou encerrados, pois o critério da issue 03 menciona rascunhos e a especificação descreve exclusão sem restrição explícita de status.

## 004 — Implementação da issue 03

**Data:** 2026-11-23
**Ferramenta:** Codex
**Branch:** `issue-03-administracao-de-torneios`

**Prompt:**

> sim e sim

> Sim, faça o commit da 03

**O que foi feito:** Implementei consulta, busca, filtros, ordenação, edição em rascunho e exclusão confirmada nos três status, incluindo remoção de inscrições e partidas no mesmo arquivo JSON. O nome continua preservando grafia, acentos e espaços internos, com remoção dos espaços nas extremidades. A interface exibe os dados gerais e a contagem de equipes. Conferi os sete critérios e marquei o ticket como concluído após 95 testes passarem.
