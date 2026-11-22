# AGENTS.md

# 1. Project Overview

This project is a sports tournament management system.

Users should be able to:

- Create and manage tournaments.
- Create and manage teams.
- Associate teams with tournaments.
- Configure and manage different tournament formats, such as round-robin (league) and knockout (elimination).
- Manage matches, results, and tournament progression.

The backend is developed using Python and Flask. Automated tests are written using Pytest.

The project is developed as an academic software engineering project and must comply with the architectural and quality requirements specified for the assignment.

# 2. Mandatory Technologies and Requirements

The following technologies are mandatory:

- Python: application development language.
- Flask: backend web framework.
- Pytest: automated testing framework.
- Git: version control.
- GitHub: remote repository hosting and collaboration.

The following requirements must be satisfied throughout development:

1. Implement at least four complete user stories.
2. Implement at least two domain entities.
3. Follow Clean Architecture, with clear separation between:
   - Entities
   - Use Cases
   - Interface Adapters
   - Frameworks and Drivers
4. Explicitly apply SOLID principles in the design and implementation of classes and methods.
5. Implement unit tests for use cases, testing business logic independently of infrastructure.

Do not consider a requirement fulfilled merely because its corresponding files or classes exist. Functionality must be implemented and tested.

# 3. Project Structure

The current project structure is:

```text
.
├── client/
│   └── templates/
├── server/
│   ├── api/
│   │   ├── controllers/
│   │   └── presenters/
│   ├── core/
│   │   ├── entities/
│   │   ├── interfaces/
│   │   └── use_cases/
│   └── infrastructure/
│       ├── db/
│       └── gateways/
└── tests/
    └── use_cases/
```

Respect the existing directory organization.

New directories may be introduced when justified by architectural or functional requirements. Avoid unnecessary restructuring.

# 4. Clean Architecture Guidelines

Follow the Dependency Rule of Clean Architecture:

**Source code dependencies must always point inward, toward higher-level policies.**

The innermost layer must remain independent of external frameworks, databases, and delivery mechanisms.

## 4.1. Entities

Location: `server/core/entities/`

Entities represent the fundamental business concepts of the application.

Examples:

- Tournament
- Team
- Match

Guidelines:

- Encapsulate domain rules and invariants.
- Represent meaningful business concepts and their behavior.
- Remain independent of Flask, databases, ORMs, and HTTP.
- Avoid exposing unrestricted state mutations.
- Use explicit methods to represent meaningful domain operations.

At least two domain entities must be implemented.

## 4.2. Use Cases

Location: `server/core/use_cases/`

Use cases implement application-specific business workflows.

Examples:

- CreateTournament
- CreateTeam
- RegisterTeamInTournament
- GenerateTournamentSchedule
- RecordMatchResult

Guidelines:

- Coordinate entities and repository interfaces.
- Implement application-level business rules.
- Receive dependencies through dependency injection.
- Return results independently of HTTP response formats.
- Never access Flask request contexts or database implementations directly.
- Remain independently testable without starting a Flask application.

Each use case should have a clear responsibility.

## 4.3. Interface Adapters

Locations:

- `server/api/controllers/`
- `server/api/presenters/`
- `server/core/interfaces/`

Interface adapters translate data between the external world and the application's core.

### Controllers

Guidelines:

- Handle incoming HTTP requests.
- Extract request parameters and payloads.
- Perform input validation at the API boundary.
- Invoke the appropriate use cases.
- Translate application errors into appropriate HTTP responses.
- Never contain business rules or directly access database implementations.

### Presenters

Guidelines:

- Transform use case outputs into representations suitable for external clients.
- Handle response formatting and serialization.
- Avoid exposing internal implementation details.
- Never implement business rules.

### Interfaces

Guidelines:

- Define contracts for dependencies required by the core.
- Use Python abstract base classes or typing.Protocol when appropriate.
- Define repository and gateway contracts according to application needs.
- Never depend on concrete infrastructure implementations.

## 4.4. Frameworks and Drivers

Location: `server/infrastructure/`

This layer contains concrete implementations of external technologies and services.

### Database

Location: `server/infrastructure/db/`

Guidelines:

- Handle database configuration, connections, and persistence.
- Implement repository interfaces defined in the core.
- Keep database models separate from domain entities whenever appropriate.
- Handle conversion between persistence models and domain entities.
- Never expose database-specific details to the core.

### Gateways

Location: `server/infrastructure/gateways/`

Guidelines:

- Implement integrations with external services.
- Adapt external systems to interfaces defined by the core.
- Keep third-party dependencies isolated from business rules.

### Flask Application

Flask initialization and dependency wiring should be handled at the application composition root.

The composition root is responsible for:

- Initializing the Flask application.
- Configuring infrastructure dependencies.
- Instantiating use cases with their required dependencies.
- Registering controllers and routes.

Avoid placing application initialization or dependency wiring inside domain entities or use cases.

# 5. SOLID Principles

Apply SOLID principles explicitly and pragmatically.

## 5.1. Single Responsibility Principle (SRP)

Each class and method should have one clear responsibility.

- Entities should focus on domain behavior.
- Use cases should represent specific application operations.
- Controllers should handle HTTP interactions.
- Repositories should handle persistence operations.
- Presenters should handle output formatting.

Avoid classes that combine unrelated responsibilities.

## 5.2. Open/Closed Principle (OCP)

Software components should be open for extension but closed for modification.

- Prefer abstractions and polymorphism when multiple behaviors are expected.
- Tournament formats should be extensible without requiring extensive modifications to existing tournament workflows.
- Avoid large conditional structures that grow whenever a new tournament format is introduced.

## 5.3. Liskov Substitution Principle (LSP)

Implementations of an abstraction must be interchangeable without breaking expected behavior.

- Concrete repository implementations must respect their interface contracts.
- Different tournament format implementations must preserve the behavior expected by their common abstraction.
- Avoid subclasses that violate the assumptions of their parent classes.

## 5.4. Interface Segregation Principle (ISP)

Prefer small, cohesive interfaces over large interfaces containing unrelated operations.

- Define interfaces according to the specific needs of their consumers.
- Avoid forcing implementations to provide methods they do not need.
- Separate unrelated repository or gateway responsibilities when appropriate.

## 5.5. Dependency Inversion Principle (DIP)

High-level modules must not depend directly on low-level implementations.

- Use cases must depend on abstractions rather than concrete repositories.
- Infrastructure implementations must fulfill contracts defined by the core.
- Use dependency injection to connect abstractions to concrete implementations.
- The core must never import Flask or infrastructure modules.

Do not introduce abstractions solely to demonstrate SOLID. Apply each principle where it improves maintainability, extensibility, or testability.

# 6. Domain Rules

Tournament-related business rules must reside in the core layer, within the appropriate entities or use cases.

Examples of rules that may apply:

- A team cannot be registered in the same tournament more than once.
- Tournament capacity restrictions must be respected, if configured.
- A tournament must satisfy its minimum team requirements before starting.
- Round-robin tournaments must generate valid fixtures.
- Knockout tournaments must follow valid elimination rules.
- Match results must respect the tournament's current state.

These are examples, not assumptions about finalized requirements. Verify the intended business rules before implementing them.

Different tournament formats should have clearly separated behavior.

Consider using the Strategy pattern when appropriate to support different tournament formats without coupling their logic to the Tournament entity.

Avoid implementing all tournament behavior through large conditional structures.

# 7. User Stories and Functional Requirements

The application must implement at least four complete user stories.

Guidelines:

- Each user story should represent meaningful functionality from the user's perspective.
- Implement the complete workflow required by the story.
- Keep business logic in the appropriate core components.
- Expose functionality through the API when required.
- Include automated tests for the associated use cases.
- Do not consider a user story complete merely because its controller or endpoint exists.

When implementing a user story:

1. Understand its requirements and acceptance criteria.
2. Identify the affected entities and business rules.
3. Identify the required use cases and interfaces.
4. Implement the necessary infrastructure adapters.
5. Expose the functionality through the API when applicable.
6. Write tests covering expected behavior and relevant failure scenarios.
7. Verify that existing functionality remains operational.

Do not invent missing acceptance criteria or business rules. Ask for clarification when an important requirement is ambiguous.

# 8. Coding Standards

- Use Python 3 and follow PEP 8.
- Use English for class names, function names, variables, modules, and comments.
- Use descriptive and meaningful identifiers.
- Apply type hints to function parameters, return values, and important attributes.
- Use docstrings when they provide meaningful context.
- Prefer small, cohesive classes and functions.
- Avoid unnecessary abstractions and premature generalization.
- Avoid global mutable state.
- Handle exceptions explicitly.
- Do not silently swallow errors.
- Follow the existing coding style when modifying established modules.

User-facing messages and interface content should be written in Portuguese.

# 9. Testing Guidelines

Use Pytest for all automated tests.

## 9.1. Test Organization

Tests must be located under `tests/`.

Organize tests according to the components they validate.

Suggested structure:

```text
tests/
├── entities/
├── use_cases/
├── api/
└── infrastructure/
```

The current `tests/use_cases/` directory should be preserved.

New test directories should be introduced as the corresponding components are implemented.

## 9.2. Unit Testing

Unit tests for use cases are mandatory.

Guidelines:

- Test use cases independently of Flask.
- Test business logic independently of database implementations.
- Use mocks, fakes, or stubs to replace external dependencies.
- Verify that dependencies are called with the expected arguments.
- Test successful execution and relevant failure scenarios.
- Test domain invariants and validation rules.
- Keep tests deterministic and independent of execution order.

Use cases must not require a real database connection or a running web server to be unit tested.

## 9.3. Test Naming

Use descriptive test names that communicate the expected behavior.

Prefer names such as:

```python
def test_create_tournament_with_valid_data():
    ...

def test_register_team_rejects_duplicate_registration():
    ...

def test_record_match_result_rejects_invalid_tournament_state():
    ...
```

## 9.4. Test Execution

Run the complete test suite using:

```bash
pytest
```

Run a specific test module using:

```bash
pytest tests/use_cases/test_create_tournament.py
```

All existing tests must continue to pass after modifications.

Never modify or remove tests merely to make an implementation pass.

# 10. Git and GitHub Guidelines

Use Git for version control and GitHub as the remote repository.

Guidelines:

- Make commits that represent coherent changes.
- Use descriptive commit messages.
- Avoid committing generated files, temporary files, and environment-specific configuration.
- Never commit secrets, credentials, or API keys.
- Preserve the existing Git history.
- Never rewrite shared history or force-push without explicit authorization.
- Do not commit changes unless explicitly requested.

# 11. Development Workflow

Before implementing a feature:

1. Inspect the relevant files and understand the existing architecture.
2. Identify the user story and its acceptance criteria.
3. Identify the relevant entities and business rules.
4. Determine which use cases and interfaces are required.
5. Implement the core functionality independently of external frameworks.
6. Implement or update infrastructure adapters.
7. Connect the functionality through controllers and presenters.
8. Write automated tests.
9. Run the relevant tests and, when practical, the complete test suite.
10. Review the implementation for Clean Architecture and SOLID compliance.

Before modifying existing code:

- Understand its current responsibilities and dependencies.
- Reuse existing abstractions whenever appropriate.
- Avoid rewriting working components without a concrete reason.
- Preserve existing behavior unless the requested feature explicitly requires a change.

# 12. Important Restrictions

- Never place business logic in Flask controllers.
- Never import Flask or infrastructure modules into the core.
- Never execute database queries directly from entities or use cases.
- Never couple domain entities to database schemas or serialization formats.
- Never bypass repository interfaces to access persistence implementations.
- Never introduce circular dependencies between architectural layers.
- Never duplicate business rules across multiple layers.
- Never sacrifice testability for implementation convenience.
- Never introduce unnecessary design patterns or abstractions.

When an architectural decision is unclear, prioritize simplicity, separation of concerns, testability, and consistency with the existing architecture.

When requirements are incomplete, ask for clarification instead of inventing business rules.

# 13. Local Issue Tracking

## 13.1. Issue Tracker

The project uses a **local Markdown-based issue tracker**.

- Issue specifications and tracking files must be stored locally under `.scratch/`.
- Do not use GitHub Issues to create, retrieve, update, or close issues.
- Do not use the GitHub CLI (`gh`) for issue tracking operations.
- These restrictions apply even if the Git remote points to a GitHub repository.
- GitHub remains the remote repository hosting platform, but it is not used as the project's issue tracker.

## 13.2. Issue Documentation

Follow the conventions documented in:

`docs/agents/issue-tracker.md`

This document defines how issues are structured, organized, updated, and closed.

Before creating or modifying issues:
1. Read `docs/agents/issue-tracker.md`.
2. Inspect the existing files under `.scratch/`.
3. Follow the established naming and organization conventions.
4. Avoid duplicating existing issues.

## 13.3. Issue Lifecycle

When working on an existing issue:
- Read its description and acceptance criteria before implementing changes.
- Keep the issue documentation synchronized with implementation progress.
- Do not mark an issue as complete if its acceptance criteria have not been satisfied.

When an issue is completed:
1. Mark all satisfied acceptance criteria with `[x]`.
2. Update its `Status` field to `done`.
3. Ensure the documentation accurately reflects the implemented functionality.

Never mark an issue as complete merely because the implementation has been started or because its tests have been written.

## 13.4. Scope and Restrictions

- Issue tracking is local and file-based.
- Do not migrate local issues to GitHub Issues.
- Do not assume that GitHub Pull Requests or GitHub Projects are part of the issue-tracking workflow.
- Do not delete issue history unless explicitly requested.

## Agent skills

### Issue tracker

Issues e specs ficam em arquivos Markdown locais em `.scratch/`. Consulte `docs/agents/issue-tracker.md`.

### Domain docs

Repositório de contexto único, com `GLOSSARY.md` na raiz e `docs/adr/`. Consulte `docs/agents/domain.md`.

Qualquer ação significativa deve ser documentada, no formato de um pequeno parágrafo, em um arquivo sequencial `/docs/agents/prompt-history.md`. 
Inclua o prompt que gerou a ação junto da documentação do que foi feito (em uma entrada no arquivo prompt-history.md).