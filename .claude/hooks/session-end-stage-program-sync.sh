#!/usr/bin/env bash
# Stages a marker file so the next program-sync run knows this session ended.
# Does NOT write to program.md directly (that would clobber on every quit).

set -euo pipefail

STAGE_DIR="$HOME/.claude/sweep/program-sync"
mkdir -p "$STAGE_DIR/processed"

PAYLOAD="$(cat)"
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
TS=$(date -u +%FT%TZ)
SAFE_TS="${TS//:/-}"

cat > "$STAGE_DIR/pending-${SAFE_TS}-${SESSION_ID}.json" <<EOF
{
  "session_id": "$SESSION_ID",
  "ended_at": "$TS",
  "transcript_path": $(echo "$PAYLOAD" | jq '.transcript_path // null'),
  "cwd": $(echo "$PAYLOAD" | jq '.cwd // null'),
  "reason": $(echo "$PAYLOAD" | jq '.reason // null')
}
EOF

exit 0
