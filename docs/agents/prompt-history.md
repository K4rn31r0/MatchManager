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
**Branch:** issues-05-e-06-pontos-corridos

**Prompt:**

> a issue 05 (.scratch\match-manager\issues\05-pontos-corridos-configuracao-calendario.md). Antes de começar, leia a issue e os arquivos que ela referencia.

**Decisões confirmadas com o usuário antes da implementação:** os seams principais são o caso de uso de configurar pontos corridos e o gerador de calendário, testados com repositórios em memória, independentemente de Flask e HTTP.

**O que foi feito:** Implementei no core os modos turno único e ida e volta, pontuação padrão de vitória 3, empate 1 e derrota 0, critérios de desempate positivos ou negativos e campos estatísticos. A configuração valida a relação entre os pontos, exige pelo menos um critério e bloqueia alterações fora do rascunho. O gerador circular cria um confronto por par, repete os confrontos nos dois sentidos na ida e volta e representa descansos válidos para número ímpar de equipes. A configuração e os confrontos são persistidos no JSON local e estão conectados à interface do torneio. Foram adicionados testes unitários, teste de serialização da configuração e compatibilidade ASCII no armazenamento JSON. Resultado: 114 testes passando na suíte completa. A issue 05 foi marcada como concluída.

Após a revisão obrigatória do commit inicial, completei os casos de borda de critérios inválidos, equipes insuficientes e descanso em ida e volta com número ímpar. O modelo passou a representar os campos estatísticos por tipo próprio, a interface permite configurar até três critérios na ordem e o conteúdo foi validado novamente com 118 testes passando.

## 007 — Implementação da issue 06: Pontos corridos, resultados e classificação

**Data:** 2026-11-23
**Ferramenta:** Copilot SDK no VS Code
**Branch:** issues-05-e-06-pontos-corridos

**Prompt:**

> a issue 06 (.scratch\match-manager\issues\06-pontos-corridos-resultados-classificacao.md). Antes de começar, leia a issue e os arquivos que ela referencia, e tenha certeza de que a issue 05 esteja devidamente validada. Se houver alguma regra de negócio importante em aberto, pare e me avise.

**Decisões confirmadas com o usuário antes da implementação:** o placar só é aceito quando ambos os valores estiverem preenchidos; placar parcial é recusado. As interfaces principais cobrem registro de resultado, cálculo da classificação e encerramento.

**O que foi feito:** A issue 05 foi confirmada como concluída e validada pela suíte atual com 118 testes antes desta implementação. Adicionei ao domínio de partida resultado direto, placar opcional, estatísticas por equipe e estado concluído. Implementei casos de uso independentes de Flask para registrar ou corrigir resultados, calcular jogos, vitórias, empates, derrotas, pontos e estatísticas agregadas, ordenar por critérios positivos ou negativos e usar o nome normalizado como desempate final. Adicionei o encerramento que rejeita partidas pendentes e expõe o líder apenas como campeão após o status encerrado. A persistência JSON passou a ler, atualizar e listar partidas completas ou legadas. A interface passou a listar partidas, registrar placares e estatísticas, mostrar a tabela em destaque e encerrar o torneio. Resultado: 128 testes passando. A issue 06 foi marcada como concluída.

Após a revisão obrigatória, corrigi o encerramento para rejeitar também partidas marcadas como concluídas sem resultado válido, centralizei a validação de placar parcial na entidade da partida e passei a informar na interface quando o desempate alfabético foi aplicado.

## 008 — Implementação da issue 07: Mata-mata, chaveamento

**Data:** 2026-11-24
**Ferramenta:** Copilot
**Branch:** `main`

**Prompt:**

> Implement ONLY local issue 07, in the current repository and current branch. The coordinator verified the issue order against `.scratch/match-manager/dag.md`: dependencies 03 and 04 are done; issue 08 is blocked by 07 and must not be started until this agent completes. The issue title is “07: Mata-mata: chaveamento”. User confirmed these TDD seams: (1) the bracket-generation use case with fake repositories, covering manual order, draw, performance-based bye distribution, and valid rounds/matches; (2) web flow for bracket display/validation, including rounds, automatic bye advancement, and rejecting tournament start with an invalid bracket.
>
> First read the complete issue file `.scratch/match-manager/issues/07-mata-mata-chaveamento.md` and report its title in your progress/output before implementation. Also read repository `AGENTS.md`, `.scratch/match-manager/dag.md`, relevant domain/ADR docs, `docs/agents/issue-tracker.md`, and current code/tests relevant to the feature. Respect Clean Architecture and existing patterns. Work test-first in vertical red→green slices at the two confirmed seams. Do not invent business rules: if an acceptance criterion leaves a consequential rule ambiguous that cannot be resolved from existing specs/code, stop and report the precise question without making changes or committing.
>
> Implement all acceptance criteria and directly related docs. Update that issue only when every criterion is implemented and verified: mark all satisfied checkboxes `[x]` and Status `done`. Add a sequential entry to `docs/agents/prompt-history.md` recording the user's exact prompt/task and a concise factual implementation summary. Run focused tests during each TDD slice and relevant type/lint checking if established; do not run the full suite (the coordinator will do it once after both issues). After issue 07 is fully validated, create one commit on the current branch with exactly the subject `07: Mata-mata: chaveamento (issue 07)` (include the required Copilot co-author trailer). Do not begin issue 08. Before committing, inspect the diff and ensure no unrelated changes are included. Return the commit hash, test commands/results, changes, and any remaining caveats. If you cannot complete the issue fully, stop before committing and report the blocker; do not mark it done or begin another issue.

**Esclarecimento confirmado pelo usuário:**

> Regra de negócio esclarecida pelo usuário: “Use a ordem inicial fornecida pelo usuário como ranking de desempenho; equipes melhor posicionadas recebem os byes primeiro. Em empate, preserve a ordem inicial.” Continue exclusivamente a issue 07, mantendo os demais requisitos do seu prompt; não inicie a issue 08.

**O que foi feito:** Implementados os valores de domínio do chaveamento e partidas com posições futuras, a geração independente de Flask para ordem manual ou sorteada e byes escolhidos manualmente, sorteados ou priorizados pelo ranking inicial. A ordem de ranking prioriza byes e é preservada; byes avançam sem criar partidas fictícias. O fluxo persiste e apresenta fases, equipes e partidas, e valida o chaveamento antes de iniciar o torneio. A issue 07 foi marcada como concluída após 49 testes focados e regressões relacionadas passarem. O pycodestyle passou nos módulos novos e, nos módulos existentes alterados, nas verificações que excluíram avisos preexistentes E501/W503. A suíte completa não foi executada, conforme solicitado.

## 009 — Implementação da issue 08: Mata-mata, resultados e avanços

**Data:** 2026-11-24
**Ferramenta:** Copilot
**Branch:** `main`

**Prompt:**

> Implement ONLY local issue 08 on the current repository/current branch. The coordinator verified the issue order against `.scratch/match-manager/dag.md`; blocker issue 07 is now `done` and committed as 7cdca522ac6d157ddab0f8851832122a830dbdb1. The issue title is “08: Mata-mata: resultados e avanços”. The user confirmed these TDD seams: (1) result/advancement use case with fake repositories, covering direct winner, valid/optional score, rejecting draw/partial score/missing winner, and advancement into the next match; (2) web flow displaying progress through the final and champion.
>
> First read the complete `.scratch/match-manager/issues/08-mata-mata-resultados-avancos.md` and report its title in your progress/output before implementation. Also read `AGENTS.md`, `.scratch/match-manager/dag.md`, relevant domain/ADR docs, `docs/agents/issue-tracker.md`, issue 07 and the implementation/tests relevant to the feature. Respect Clean Architecture and project patterns. Work test-first in vertical red→green slices at the two confirmed seams. Do not invent business rules: if an acceptance criterion leaves a consequential rule ambiguous that cannot be resolved from existing specs/code, stop and report the precise question without making changes or committing.
>
> Implement all acceptance criteria and directly related docs. Update issue 08 only after every criterion is implemented and verified: mark all criteria `[x]`, set Status `done`, and append a factual comment if useful. Append sequential entry 009 to `docs/agents/prompt-history.md`, including the exact user request that generated this issue work and a concise summary (preserve existing file contents). Run focused tests during each TDD slice and relevant type/lint checking if established; do NOT run the full suite (the coordinator will run it once after this issue). After full issue validation, make one commit on the current branch with exactly the subject `08: Mata-mata: resultados e avanços (issue 08)` and required Copilot co-author trailer. Do not touch any other issue. Before committing, inspect the diff and ensure no unrelated changes are included. Return commit hash, test commands/results, changes, and caveats. If you cannot complete the issue fully, stop before committing and report the blocker; do not mark done.

**O que foi feito:** Implementei casos de uso independentes de Flask para registrar resultados do mata-mata, exigir um vencedor, validar placar opcional sem empate e avançar ou corrigir a equipe na posição correspondente da partida seguinte; uma correção é recusada se uma partida posterior já foi concluída. A interface apresenta os formulários de resultado, a evolução até a final e o campeão somente após o encerramento válido do torneio. A issue 08 foi marcada como concluída após 42 testes focados e regressões relacionadas passarem, além do pycodestyle com as exclusões E501/W503 já adotadas no repositório. A suíte completa não foi executada, conforme solicitado.

## 010 — Implementação da issue 09: Ciclo, correções e encerramento

**Data:** 2026-11-25
**Ferramenta:** Claude Code (Claude Opus 5.5)
**Branch:** `issues-09-e-10-ciclo-e-mobile`

**Prompt:**

> Sim, vamos ter que fazer as issues 9 e 10, depois dar push e commit e e testar se a aplicação está funcionando. Pode ir.
>
> Vamos focar na 9 antes da 10

**O que foi feito:** Criado o caso de uso `StartTournament`, que inicia qualquer torneio delegando a uma estratégia por formato (Strategy/OCP): `StartRoundRobinTournament` (novo, pois pontos corridos não tinham início) valida rascunho, configuração e pelo menos duas equipes, gera o calendário completo e muda o status para em andamento; o mata-mata reutiliza `StartKnockoutTournament`. A entidade `Tournament` ganhou `start()` e `ensure_accepts_results()`, usado pelos dois casos de uso de resultado, permitindo correções em torneios em andamento ou encerrados sem mudar o status. No mata-mata, o bloqueio de correção passou a considerar apenas a partida subsequente que depende do resultado, o que permite corrigir a final de um torneio encerrado. A interface ganhou a página de confirmação de início com formato, regras e participantes. Testes novos cobrem início, bloqueios de configuração e inscrição, correções, recálculo da classificação e encerramento com fakes, além do fluxo web; a suíte completa passou (196 testes).

## 011 — Implementação da issue 10: Experiência completa mobile

**Data:** 2026-11-25
**Ferramenta:** Claude Code (Claude Opus 5.5)
**Branch:** `issues-09-e-10-ciclo-e-mobile`

**Prompt:**

> Sim, vamos ter que fazer as issues 9 e 10, depois dar push e commit e e testar se a aplicação está funcionando. Pode ir.

**O que foi feito:** A página do torneio passou a ter abas (Partidas, Classificação, Equipes e Configuração/Regras) sem JavaScript, usando âncoras com `:target` e `:has()` como melhoria progressiva. Foram criados os casos de uso `ListTournamentMatches` (filtro por rodada/fase e status, comum aos dois formatos) e `ScheduleMatch` (data e local opcionais, independentes do resultado), com a entidade `Match` ganhando `schedule()` e a persistência JSON os novos campos. Um presenter de partidas formata placar, vencedor, status e nomes de fase. A interface ganhou navegação com seção atual marcada, links de retorno, estados vazios, confirmação de encerramento com `<details>`, formulários que reabrem com os valores digitados em caso de erro e CSS mobile-first com tabela rolável. A suíte completa passou (220 testes) e a aplicação foi testada ponta a ponta no servidor real, incluindo capturas de tela em largura de celular e desktop.
