# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root, or
- **`GLOSSARY-MAP.md`** at the repo root if it exists: it points at one `GLOSSARY.md` per context. Read each one relevant to the topic.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Do not flag their absence or suggest creating them upfront.

## File structure

This is a single-context repository:

```
/
├── GLOSSARY.md
├── docs/adr/
└── src/
```

The project structure may differ while the same documentation layout is used. The exact domain paths must remain at the root:

- `GLOSSARY.md`
- `docs/adr/`

## Use the glossary's vocabulary

When an output names a domain concept, use the term as defined in `GLOSSARY.md`. Do not drift to synonyms the glossary explicitly avoids.

If the concept needed is not in the glossary yet, reconsider whether the project already uses another term or note the gap for later domain modeling.

## Flag ADR conflicts

If an output contradicts an existing ADR, surface it explicitly rather than silently overriding the decision.
