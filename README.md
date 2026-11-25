# MatchManager

Organizador de competições e partidas esportivas.

Aplicação web em Python e Flask para organizar torneios de qualquer modalidade. O usuário cadastra equipes, cria torneios em **pontos corridos** ou **mata-mata**, inscreve as equipes, registra os resultados e acompanha a classificação ou o chaveamento até o campeão. Os dados ficam num arquivo JSON local, sem login e sem banco de dados.

## Como executar

Requer Python 3.11 ou superior.

```bash
pip install -r requirements.txt
flask --app server.app run
```

Acesse http://127.0.0.1:5000. Os dados ficam em `instance/matchmanager.json`, criado automaticamente no primeiro cadastro.

## Testes

```bash
pytest
```

## Estilo de código (PEP 8)

O código segue a PEP 8, com linhas de até 79 caracteres. A formatação e a verificação usam o [Ruff](https://docs.astral.sh/ruff/), configurado em [`ruff.toml`](ruff.toml):

```bash
pip install ruff
ruff format .     # formata o código
ruff check .      # verifica as regras da PEP 8
```

---

## Arquitetura: Clean Architecture

O código está dividido nas quatro camadas da Clean Architecture. A **regra de dependência** é seguida à risca: as importações sempre apontam para dentro, em direção ao `core`.

```text
┌──────────────────────────────────────────────────────────────────┐
│ Frameworks & Drivers                                             │
│ Flask (server/app.py) · Jinja2/CSS (client/) · JSON (infra/db)   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Interface Adapters                                         │  │
│  │ controllers · presenters                                   │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ Use Cases  (CreateTeam, StartTournament, ...)        │  │  │
│  │  │ + interfaces que o core exige (TeamRepository, ...)  │  │  │
│  │  │  ┌────────────────────────────────────────────────┐  │  │  │
│  │  │  │ Entities  (Tournament, Team, Match)            │  │  │  │
│  │  │  └────────────────────────────────────────────────┘  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
        As dependências apontam sempre para o centro.
        Os repositórios JSON implementam as interfaces do core.
```

| Camada | Pasta | Responsabilidade | Exemplos |
|---|---|---|---|
| **Entities** | [`server/core/entities/`](server/core/entities/) | Conceitos e regras do domínio, sem nenhuma dependência externa | `Tournament`, `Team`, `Match`, regras de nome em `names.py`, montagem do chaveamento em `knockout_bracket.py` |
| **Use Cases** | [`server/core/use_cases/`](server/core/use_cases/) | Uma operação do sistema por classe, coordenando entidades e interfaces | `CreateTeam`, `StartTournament`, `RecordRoundRobinResult`, `CalculateRoundRobinStandings` |
| **Interface Adapters** | [`server/api/controllers/`](server/api/controllers/), [`server/api/presenters/`](server/api/presenters/), [`server/core/interfaces/`](server/core/interfaces/) | Converter HTTP em chamadas de use case e resultados em dados de tela; definir os contratos que o core exige | `team_controller.py`, `tournament_presenter.py`, `TeamRepository` |
| **Frameworks & Drivers** | [`server/infrastructure/`](server/infrastructure/), [`server/app.py`](server/app.py), [`client/`](client/) | Flask, templates Jinja2, CSS e persistência em JSON | `JsonTeamRepository`, `JsonFileStorage` |

**O core é independente de framework.** Nenhum arquivo em `server/core/` importa Flask, Werkzeug, `server.api` ou `server.infrastructure`. Para verificar:

```bash
grep -rnE "^\s*(from|import) (flask|werkzeug|server\.(infrastructure|api))" server/core
```

O comando não retorna nada.

**Raiz de composição.** [`server/app.py`](server/app.py) é o único lugar que conhece as implementações concretas. Ele cria os repositórios JSON, instancia os use cases injetando essas dependências e registra os blueprints do Flask.

### Exemplo de fluxo: criar uma equipe

1. O formulário envia `POST /teams/`. O **controller** ([`team_controller.py`](server/api/controllers/team_controller.py)) lê os campos e monta um `TeamData`, sem nenhuma regra de negócio.
2. O **use case** [`CreateTeam`](server/core/use_cases/create_team.py) verifica se o nome está disponível (ignorando maiúsculas e acentos) e cria a entidade.
3. A **entidade** [`Team`](server/core/entities/team.py) valida suas regras: nome obrigatório, cor no formato `#rrggbb` e sigla gerada automaticamente quando não é informada.
4. O use case salva a equipe através da **interface** [`TeamRepository`](server/core/interfaces/team_repository.py). Ele não sabe que existe JSON.
5. Em produção, essa interface é implementada por [`JsonTeamRepository`](server/infrastructure/db/json_team_repository.py), que grava no arquivo. Nos testes, é substituída por um repositório em memória.
6. Se uma regra for violada, o core lança um `DomainError` com mensagem em português, e o controller a devolve ao usuário com status 400.

---

## Princípios SOLID

### S — Responsabilidade única

Cada classe tem um único motivo para mudar:

- **Um use case por operação:** [`CreateTeam`](server/core/use_cases/create_team.py), [`UpdateTeam`](server/core/use_cases/update_team.py), [`DeleteTeam`](server/core/use_cases/delete_team.py), [`ListTeams`](server/core/use_cases/list_teams.py) e [`GetTeam`](server/core/use_cases/get_team.py) são classes separadas, em vez de um único "TeamService".
- **Papéis separados:** o controller só traduz HTTP, o presenter ([`team_presenter.py`](server/api/presenters/team_presenter.py)) só formata para a tela, e o repositório só persiste.
- **Regras de texto num só lugar:** a comparação de nomes (sem maiúsculas e sem acentos) fica em [`names.py`](server/core/entities/names.py) e é reutilizada por torneios e equipes.

### O — Aberto/fechado

O **início de torneio** é aberto para novos formatos sem modificar o fluxo existente. [`StartTournament`](server/core/use_cases/start_tournament.py) não conhece os formatos: ele recebe um mapa `formato → estratégia` (padrão *Strategy*, contrato `TournamentStarter`) e delega a ela. As estratégias são registradas em [`server/app.py`](server/app.py):

```python
start_tournament = StartTournament(
    tournament_repository,
    {
        TournamentFormat.ROUND_ROBIN: StartRoundRobinTournament(
            tournament_repository,
            generate_round_robin_calendar,
        ),
        TournamentFormat.KNOCKOUT: start_knockout_tournament,
    },
)
```

Para suportar um novo formato, basta criar outra estratégia e registrá-la. `StartTournament` não muda.

O mesmo vale para os **critérios de desempate** dos pontos corridos: eles são dados configurados pelo usuário (nome e direção positiva ou negativa), e o cálculo da classificação ([`calculate_round_robin_standings.py`](server/core/use_cases/calculate_round_robin_standings.py)) os aplica de forma genérica. Um critério novo não exige alterar código.

### L — Substituição de Liskov

As implementações de cada contrato são intercambiáveis sem alterar o comportamento dos use cases:

- Os mesmos use cases rodam com os repositórios JSON no app e com os repositórios em memória de [`tests/fakes.py`](tests/fakes.py) nos testes (`InMemoryTeamRepository`, `InMemoryTournamentRepository`, `InMemoryMatchRepository`, `InMemoryRegistrationRepository`).
- Os repositórios JSON têm seus próprios testes em [`tests/infrastructure/`](tests/infrastructure/), que verificam que eles cumprem o contrato: o que é gravado volta igual numa nova instância.

### I — Segregação de interfaces

As interfaces são pequenas e feitas para quem as consome:

- [`TeamParticipationQuery`](server/core/interfaces/team_participation_query.py) tem **um único método**, `is_in_started_tournament`. É tudo que o [`DeleteTeam`](server/core/use_cases/delete_team.py) precisa para saber se pode excluir uma equipe, sem depender de todo o repositório de inscrições.
- Repositórios de torneios, equipes, inscrições e partidas são contratos separados ([`server/core/interfaces/`](server/core/interfaces/)), em vez de um único repositório genérico.

### D — Inversão de dependência

Os módulos de alto nível (use cases) dependem de abstrações, nunca de implementações:

- Os use cases recebem as interfaces pelo construtor. Exemplo: `CreateTeam(repository: TeamRepository, id_generator)`.
- Até **relógio e gerador de ids** são injetados (`clock`, `id_generator`). Por isso os testes usam `FakeClock` e `SequentialIdGenerator` e são determinísticos.
- As interfaces ficam no **core** ([`server/core/interfaces/`](server/core/interfaces/)) e a infraestrutura as implementa. É a infraestrutura que depende do core, nunca o contrário.

---

## Testes

São 220 testes automatizados com pytest, organizados por camada:

| Pasta | O que testa | Quantidade |
|---|---|---|
| [`tests/entities/`](tests/entities/) | Regras das entidades, como a geração de sigla | 28 |
| [`tests/use_cases/`](tests/use_cases/) | Regras de negócio de cada use case | 159 |
| [`tests/infrastructure/`](tests/infrastructure/) | Gravação e leitura no JSON, com arquivo temporário | 13 |
| [`tests/api/`](tests/api/) | Rotas Flask de ponta a ponta | 20 |

**Os testes de use case são isolados da infraestrutura:** usam os repositórios em memória de [`tests/fakes.py`](tests/fakes.py), sem Flask, sem servidor e sem arquivo em disco. Cobrem tanto o caminho de sucesso quanto as falhas, como nome duplicado, placar parcial, empate em mata-mata e encerramento com partidas pendentes.

---

## Uso de Inteligência Artificial

A IA foi usada como **ferramenta de implementação dentro de um processo controlado pelo grupo**, e não para gerar o projeto de uma vez. A estratégia foi o **desenvolvimento orientado a especificação** (*Spec-Driven Development*): os requisitos e as regras do projeto foram fixados por escrito antes de qualquer código, e cada passo da IA foi limitado e verificado.

### Etapas

1. **Regras do projeto para os agentes.** O [`AGENTS.md`](AGENTS.md) descreve para qualquer assistente de IA os requisitos do enunciado, a Clean Architecture, os princípios SOLID, os padrões de código e de testes, e o processo de issues. Por isso ferramentas diferentes produziram código no mesmo padrão.
2. **Especificação.** Com a skill `to-spec` foi escrita a [especificação](.scratch/match-manager/spec.md), com 95 histórias de usuário, decisões de implementação, casos de uso e o que fica fora do escopo.
3. **Divisão em issues.** Com a skill `to-tickets`, a spec foi quebrada em [10 issues](.scratch/match-manager/issues/), cada uma uma fatia vertical com critérios de aceitação, organizadas num [grafo de dependências](.scratch/match-manager/dag.md).
4. **Implementação com TDD.** Cada issue foi implementada numa branch própria com a skill `tdd`: primeiro o teste que falha, depois o código mínimo para passar. Os pontos de teste eram combinados com o grupo antes.
5. **Pessoas decidem as regras de negócio.** Quando a spec era ambígua, a IA tinha que perguntar em vez de inventar. Exemplos de decisões tomadas pelo grupo: como gerar a sigla automática, se nomes iguais com acentos diferentes contam como duplicados, e se a data de término pode ser anterior à de início.
6. **Revisão humana e por PR.** Cada issue entrou na `main` por Pull Request. As revisões encontraram problemas que a IA tinha deixado passar. O principal: depois das issues 05 e 06, um torneio de pontos corridos não podia ser iniciado pelo app, embora os testes unitários passassem. Isso foi corrigido na issue 09.
7. **Rastreabilidade.** Cada ação relevante está registrada em [`docs/agents/prompt-history.md`](docs/agents/prompt-history.md), com o prompt usado, as decisões tomadas e o resultado. Cada issue tem seus critérios de aceitação marcados.

### Ferramentas

| Ferramenta | Uso |
|---|---|
| Claude Code (Claude Opus 5.5) | Issues 01, 02, 09 e 10; revisões de arquitetura e documentação |
| Codex | Issues 03 e 04 |
| GitHub Copilot | Issues 05 a 08 |

As skills usadas (`to-spec`, `to-tickets`, `tdd`, `implement`, `grill-me` e `code-review`) estão em [`.github/skills/`](.github/skills/).

### Por que essa estratégia

- **Escopo controlado:** com a spec e os critérios de aceitação escritos antes, a IA implementa o que foi pedido, nem mais nem menos, e cada issue tem uma definição objetiva de "pronto".
- **Arquitetura preservada:** as regras do `AGENTS.md` mantiveram as camadas e os princípios SOLID mesmo com três ferramentas e várias pessoas trabalhando.
- **Resultado verificável:** com TDD, cada regra de negócio tem um teste. O que a IA produz é conferido por execução, não por confiança.
- **Pessoas no controle:** regras de negócio, revisão e merge ficaram com o grupo. A revisão comprovou ser necessária, já que encontrou falhas reais que os testes não mostravam.
