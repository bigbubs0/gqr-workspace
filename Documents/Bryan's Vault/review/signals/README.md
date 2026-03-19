# Signal Review Outputs

This folder is the review-first landing zone for the signal intelligence stack.

- `daily/` - dated morning radar briefs
- `urgent/` - one memo per urgent same-day trigger
- `opportunities/` - signal-to-search matching tables
- `weekly/` - Monday market boards
- `catalysts/` - Monday catalyst boards and JSON caches

Naming rule: start every generated file with an ISO date so manual review stays sortable.

Guardrails:
- No outreach sends
- No Notion record creation when matching is ambiguous
- If a source is missing or conflicting, add a `## Blockers` section instead of guessing
