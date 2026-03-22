---
name: Browser Resilience During Sweeps
description: Do not fall back to Notion-only mode from transient browser issues - retry clicks, adjust coordinates, use keyboard nav. Per-email fallback only.
type: feedback
---

Windows-MCP can click, scroll, type, and snapshot inside the Comet browser. Do NOT fall back to "screenshot-only" or "subject-line-only" mode from a single failed click.

**Why:** On 3/19/26, the agent declared the browser "broken" after a few misclicks on Outlook email items and switched the entire sweep to Notion-only mode. The browser was working fine — the clicks just needed coordinate adjustments or keyboard navigation.

**How to apply:**
- "Disconnected" = Snapshot returns nothing or errors 3 consecutive times. That's the only threshold.
- A misclick, slow load, or element not found = transient. Retry with adjusted coords, try double-click, try keyboard nav (Tab/Enter/arrows), try Ctrl+L address bar navigation.
- Fallback is per-email (log as FAILED TO READ after 2 attempts), never per-sweep.
- Rule 8 in the eod-sweep SKILL.md codifies this.

**Three escape routes that are permanently closed (added 3/19/26):**
1. **Stale memory citations** — Do NOT cite "0x0 viewport" or past session failures as reasons not to click. Every session is fresh. Try it now.
2. **Window management ≠ browser failure** — Edge stealing focus, Start menu opening, overlapping windows are OS problems. Fix them and retry. Don't count them as browser failures.
3. **Delegating clicks to Bryan** — NEVER offer "you manually click." Bryan is not your hands. Exhaust the 5-technique escalation ladder, then log FAILED TO READ and move on.
