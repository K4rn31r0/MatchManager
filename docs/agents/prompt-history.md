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
