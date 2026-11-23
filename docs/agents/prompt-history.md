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

## 005 — Implementação da issue 04

**Data:** 2026-11-23
**Ferramenta:** Codex
**Branch:** `issue-04-inscricao-de-equipes`

**Prompt:**

> Só inicie a implementação da issue 04 depois de concluir e validar a 03. Se houver um bloqueio ou uma regra importante em aberto, pare e me avise.

**O que foi feito:** Depois de validar e registrar a issue 03 no commit `e1f7cd1`, criei a branch da issue 04 a partir desse commit. Implementei a aba Equipes com listas de inscritos e disponíveis, inscrição de equipes existentes, criação com inscrição na mesma gravação JSON e remoção antes do início. Conectei a consulta real de participação ao bloqueio de exclusão da equipe global e removi as inscrições quando uma equipe de rascunho é excluída. Os oito critérios foram conferidos e o ticket foi marcado como concluído após a suíte passar com 102 testes.

## 006 — Implementação da issue 05: Pontos corridos, configuração e calendário

**Data:** 2026-11-23
**Ferramenta:** Copilot SDK no VS Code
**Branch:** atual

**Prompt:**

> a issue 05 (.scratch\match-manager\issues\05-pontos-corridos-configuracao-calendario.md). Antes de começar, leia a issue e os arquivos que ela referencia.

**Decisões confirmadas com o usuário antes da implementação:** os seams principais são o caso de uso de configurar pontos corridos e o gerador de calendário, testados com repositórios em memória, independentemente de Flask e HTTP.

**O que foi feito:** Implementei no core os modos turno único e ida e volta, pontuação padrão de vitória 3, empate 1 e derrota 0, critérios de desempate positivos ou negativos e campos estatísticos. A configuração valida a relação entre os pontos, exige pelo menos um critério e bloqueia alterações fora do rascunho. O gerador circular cria um confronto por par, repete os confrontos nos dois sentidos na ida e volta e representa descansos válidos para número ímpar de equipes. A configuração e os confrontos são persistidos no JSON local e estão conectados à interface do torneio. Foram adicionados testes unitários, teste de serialização da configuração e compatibilidade ASCII no armazenamento JSON. Resultado: 114 testes passando na suíte completa. A issue 05 foi marcada como concluída.

Após a revisão obrigatória do commit inicial, completei os casos de borda de critérios inválidos, equipes insuficientes e descanso em ida e volta com número ímpar. O modelo passou a representar os campos estatísticos por tipo próprio, a interface permite configurar até três critérios na ordem e o conteúdo foi validado novamente com 118 testes passando.
