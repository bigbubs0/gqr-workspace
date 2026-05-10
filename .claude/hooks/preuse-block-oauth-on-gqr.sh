#!/usr/bin/env bash
# Reads JSON from stdin (canonical Claude Code hook protocol).
# Blocks Edit / Write / Bash that combine OAuth-style work with GQR / Outlook /
# Graph context. Cites program.md §9 + feedback_gqr_auth_workaround.md.

set -euo pipefail

PAYLOAD="$(cat)"
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.tool_name // ""')

case "$TOOL_NAME" in
  Edit)
    HAYSTACK="$(echo "$PAYLOAD" | jq -r '
      [(.tool_input.file_path // ""), (.tool_input.new_string // ""), (.tool_input.old_string // "")] | join("\n")
    ')"
    ;;
  Write)
    HAYSTACK="$(echo "$PAYLOAD" | jq -r '
      [(.tool_input.file_path // ""), (.tool_input.content // "")] | join("\n")
    ')"
    ;;
  Bash)
    HAYSTACK="$(echo "$PAYLOAD" | jq -r '.tool_input.command // ""')"
    ;;
  *)
    exit 0
    ;;
esac

# OAuth-style indicators (case-insensitive)
oauth_re='oauth|access[_-]?token|refresh[_-]?token|authorization[_-]?code|client[_-]?secret|graph\.microsoft\.com|login\.microsoftonline\.com|/oauth2/|MSAL|msal[._-]|admin[_ -]?consent'

# GQR / Outlook / Graph context indicators
gqr_re='gqr\.com|GQR|outlook|graph\.microsoft|tenant[_ -]?admin|sweep[_ -]?producer|bryan\.blair@gqr'

if echo "$HAYSTACK" | grep -qiE "$oauth_re" \
   && echo "$HAYSTACK" | grep -qiE "$gqr_re"; then
  cat >&2 <<'MSG'
BLOCK: This tool call combines OAuth-style auth with GQR / Outlook / Graph context.

Per program.md §9 + feedback_gqr_auth_workaround.md, the GQR Microsoft 365
tenant admin-approval wall makes every OAuth path unusable. The chosen
approach is:
  - Comet (browser automation) for live Outlook reads
  - Local Classic Outlook COM producer (~/.claude/sweep-producer/producer.py)
    for sweep data
  - Make.com scenario 4847631 was DELETED 2026-04-24

Do NOT propose or implement OAuth, MSAL, Graph API, or admin-consent flows
on GQR-adjacent infrastructure. If you genuinely need to override this for
this one task, ask Bryan first and update program.md afterward.
MSG
  exit 2
fi

exit 0
