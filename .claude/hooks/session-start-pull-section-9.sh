#!/usr/bin/env bash
# Pulls §9 from a dedicated Notion page and splices into program.md between markers.
# Idempotent: empty fetch / network error -> no-op (never blocks session start).

set -euo pipefail

# === REQUIRED ENV - set in your shell rc OR ~/.claude/settings.json env block ===
# TODO: Set NOTION_TOKEN to your Notion integration secret (secret_xxx).
# TODO: Set NOTION_SECTION_9_PAGE_ID to the Notion page ID for the dedicated §9 page
#       (32-char hex from the URL, with or without dashes).
NOTION_TOKEN="${NOTION_TOKEN:-}"
NOTION_SECTION_9_PAGE_ID="${NOTION_SECTION_9_PAGE_ID:-}"

PROGRAM_MD="${PROGRAM_MD:-$HOME/.claude/CLAUDE.md}"
BEGIN_MARKER="<!-- §9:BEGIN auto-synced from Notion -->"
END_MARKER="<!-- §9:END auto-synced from Notion -->"
LOG="$HOME/.claude/logs/session-start-pull-section-9.log"

mkdir -p "$(dirname "$LOG")"
exec >>"$LOG" 2>&1
echo "--- $(date -u +%FT%TZ) session-start sync ---"

if [[ -z "$NOTION_TOKEN" || -z "$NOTION_SECTION_9_PAGE_ID" ]]; then
  echo "Skipping §9 sync: NOTION_TOKEN or NOTION_SECTION_9_PAGE_ID not set."
  exit 0
fi

NOTION_API="https://api.notion.com/v1"
NOTION_VERSION="2022-06-28"
TMP_BLOCKS="$(mktemp)"
trap 'rm -f "$TMP_BLOCKS" "$TMP_BLOCKS.new" 2>/dev/null || true' EXIT

cursor=""
echo "[]" > "$TMP_BLOCKS"

while :; do
  url="$NOTION_API/blocks/$NOTION_SECTION_9_PAGE_ID/children?page_size=100"
  [[ -n "$cursor" ]] && url="${url}&start_cursor=${cursor}"
  resp=$(curl -sS --fail-with-body \
    -H "Authorization: Bearer $NOTION_TOKEN" \
    -H "Notion-Version: $NOTION_VERSION" \
    "$url") || { echo "Notion fetch failed (network/auth). Leaving program.md untouched."; exit 0; }

  echo "$resp" | jq -e '.results' >/dev/null 2>&1 || { echo "Notion response missing .results; leaving program.md untouched."; exit 0; }

  jq -s '.[0] + (.[1].results)' "$TMP_BLOCKS" <(echo "$resp") > "$TMP_BLOCKS.new"
  mv "$TMP_BLOCKS.new" "$TMP_BLOCKS"

  has_more=$(echo "$resp" | jq -r '.has_more // false')
  cursor=$(echo "$resp" | jq -r '.next_cursor // ""')
  [[ "$has_more" == "true" && -n "$cursor" ]] || break
done

# Block-to-markdown converter. Extend for any block types you actually use in §9.
# TODO: If you use callouts, toggles, or columns in §9, add cases here.
MARKDOWN=$(jq -r '
  def rich(arr): (arr // []) | map(.plain_text) | join("");
  def cells(arr): (arr // []) | map(map(.plain_text) | join("")) | join(" | ");
  map(
    if   .type == "heading_1"          then "# "   + rich(.heading_1.rich_text)
    elif .type == "heading_2"          then "## "  + rich(.heading_2.rich_text)
    elif .type == "heading_3"          then "### " + rich(.heading_3.rich_text)
    elif .type == "paragraph"          then rich(.paragraph.rich_text)
    elif .type == "bulleted_list_item" then "- "   + rich(.bulleted_list_item.rich_text)
    elif .type == "numbered_list_item" then "1. "  + rich(.numbered_list_item.rich_text)
    elif .type == "to_do"              then "- [" + (if .to_do.checked then "x" else " " end) + "] " + rich(.to_do.rich_text)
    elif .type == "code"               then "```" + (.code.language // "") + "\n" + rich(.code.rich_text) + "\n```"
    elif .type == "quote"              then "> "   + rich(.quote.rich_text)
    elif .type == "divider"            then "---"
    elif .type == "table_row"          then "| " + cells(.table_row.cells) + " |"
    else ""
    end
  ) | map(select(. != "")) | join("\n\n")
' "$TMP_BLOCKS")

if [[ -z "$MARKDOWN" ]]; then
  echo "Notion §9 fetch returned empty content; leaving program.md untouched."
  exit 0
fi

if ! grep -qF "$BEGIN_MARKER" "$PROGRAM_MD"; then
  echo "Markers not found in $PROGRAM_MD; appending §9 block at end."
  {
    echo
    echo "$BEGIN_MARKER"
    echo "$MARKDOWN"
    echo "$END_MARKER"
  } >> "$PROGRAM_MD"
  exit 0
fi

# In-place replacement using awk (portable across macOS / Linux / Git-Bash).
TMP_OUT="$(mktemp)"
awk -v begin="$BEGIN_MARKER" -v endm="$END_MARKER" -v body="$MARKDOWN" '
  $0 == begin { print; print body; in_block=1; next }
  $0 == endm  { in_block=0; print; next }
  !in_block   { print }
' "$PROGRAM_MD" > "$TMP_OUT" && mv "$TMP_OUT" "$PROGRAM_MD"

echo "§9 synced from Notion ($(echo "$MARKDOWN" | wc -l) lines)."
exit 0
