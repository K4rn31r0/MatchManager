
---
name: solid-review
description: "Review a codebase's architecture against the five SOLID principles (SRP, OCP, LSP, ISP, DIP). Uses five parallel sub-agents to independently inspect the codebase, identify evidence-backed design violations, and suggest refactorings. Does not modify code. Use when the user requests a SOLID review, architecture review focused on SOLID, or an assessment of design quality."
---

# SOLID Review

Evaluate the codebase against the five SOLID principles:

- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)

The objective is to identify meaningful design problems and recommend improvements, NOT to mechanically enforce design patterns.

**This is a read-only review. Never edit, create, delete, or refactor source files.**

## 1. Establish the review scope

The default scope is the entire relevant codebase.

The user may instead specify:
- A directory or module.
- A particular feature or architectural layer.
- A Git diff or range of commits.

If the scope is ambiguous, ask one clarifying question.

Identify the project's language, frameworks, architecture, and major modules.

## 2. Gather architectural context

Before reviewing:

1. Read the applicable AGENTS.md and other agent instructions.
2. Read CODING_STANDARDS.md and CONTRIBUTING.md if present.
3. Inspect architecture documentation, ADRs, and domain documentation.
4. Identify existing architectural patterns and conventions.
5. Map the major dependencies and boundaries between modules.

The repository's documented architectural decisions take precedence over generic design preferences.

Do not assume that a particular architectural style or design pattern is required.

## 3. Spawn five parallel sub-agents

Run all five reviews in parallel.

Start every sub-agent with a fresh context window.

Each agent must independently inspect the relevant code and architectural context.

### SRP Agent — Single Responsibility Principle

Investigate whether classes, modules, and functions have multiple unrelated responsibilities or multiple independent reasons to change.

Look for:
- Classes handling unrelated business rules or technical concerns.
- Modules combining orchestration, persistence, validation, and presentation without a clear reason.
- Unrelated responsibilities tightly coupled through shared state.
- Changes to one concern repeatedly requiring changes to another.

Do not flag classes merely because they have many methods or lines of code.

### OCP Agent — Open/Closed Principle

Investigate whether existing behavior can be extended without unnecessarily modifying stable code.

Look for:
- Repeated conditional logic for handling new variants of the same behavior.
- Centralized registries or dispatch logic that must constantly be modified.
- New features requiring invasive changes across unrelated modules.
- Missing extension points where variability is a demonstrated requirement.

Do not suggest abstractions for hypothetical future requirements. Simple conditionals are often appropriate.

### LSP Agent — Liskov Substitution Principle

Investigate whether subtypes can genuinely substitute their base types without breaking expected behavior.

Look for:
- Overridden methods that change expected semantics.
- Subclasses that reject inputs accepted by their parent.
- Subclasses that violate expected postconditions or invariants.
- Unexpected exceptions or behavior that callers cannot reasonably anticipate.
- Implementations that violate interface contracts.

Consider behavioral contracts, not merely inheritance syntax.

### ISP Agent — Interface Segregation Principle

Investigate whether consumers are forced to depend on methods or capabilities they do not need.

Look for:
- Large interfaces with unrelated responsibilities.
- Implementations containing empty, unsupported, or meaningless methods.
- Consumers depending on broad abstractions unnecessarily.
- Interfaces combining capabilities that vary independently.

Do not split interfaces simply to minimize their number of methods.

### DIP Agent — Dependency Inversion Principle

Investigate whether high-level policies depend unnecessarily on low-level implementation details.

Look for:
- Business logic directly coupled to infrastructure implementations.
- Domain logic depending on frameworks, databases, or external services.
- Concrete dependencies making unit testing unnecessarily difficult.
- Abstractions placed in inappropriate layers.
- Dependency injection that exists only superficially while coupling remains.

Do not introduce interfaces or dependency injection everywhere. Direct dependencies are acceptable when they are stable and appropriate.

## 4. Sub-agent reporting requirements

Each agent must report:

1. Findings, if any.
2. The exact file and line range.
3. A short code excerpt demonstrating the issue.
4. Which principle is affected and why.
5. The practical consequences of leaving the design unchanged.
6. A concrete refactoring suggestion.
7. Severity: High, Medium, or Low.
8. Confidence: High, Medium, or Low.

Use these severity definitions:

- High: Significant architectural weakness with substantial maintenance, testing, or extension consequences.
- Medium: Meaningful design weakness with a limited but identifiable negative impact.
- Low: Potential improvement with relatively minor consequences.

A finding must be supported by actual code evidence.

Do not invent hypothetical problems, assume requirements that were never established, or report every deviation from an idealized design as a violation.

If no meaningful violations are found, explicitly report that.

Under 500 words per sub-agent.

## 5. Aggregate the results

Present the five reports under separate headings:

## SRP
## OCP
## LSP
## ISP
## DIP

Preserve the findings from each agent. Do not artificially create findings to fill a section.

Consolidate duplicate findings only when they describe the same underlying issue. Preserve their relationship to multiple principles when applicable.

Do not modify the codebase.

## 6. Final recommendations

After presenting the findings, provide a prioritized refactoring plan.

For each recommended improvement, include:
- Related finding(s).
- Proposed architectural change.
- Expected benefit.
- Relative implementation effort: Low, Medium, or High.
- Dependencies on other refactorings, if any.

Prioritize improvements that address multiple findings without introducing unnecessary abstractions.

Do not generate patches or implement the recommendations unless the user explicitly requests a separate implementation task.

Finish with a brief summary of the number of findings per principle and the highest-severity issues.
