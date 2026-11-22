# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

GitHub Issues and the GitHub CLI (`gh`) are not used for issue tracking, even though
the repository may have a GitHub remote.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Closing an issue

When an issue is completed:

1. Mark every satisfied acceptance criterion with `[x]`.
2. Change the issue's `Status` line to `Status: done`.
3. Ensure the documentation accurately reflects the implemented functionality.

Do not mark an issue complete if all acceptance criteria have not been satisfied.
