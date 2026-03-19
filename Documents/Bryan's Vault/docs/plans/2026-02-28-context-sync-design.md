# Context Sync System Design

**Date:** 2026-02-28
**Status:** Approved
**Scope:** Multi-directional sync between Notion, Google Drive, and Obsidian

## Architecture

Notion as structured data hub. Obsidian as markdown context layer. Google Drive as document store. Make.com orchestrates all sync via scheduled scenarios writing to OneDrive API for Obsidian access.

```
NOTION (structured data) <---> MAKE.COM (orchestrator) <---> OBSIDIAN (OneDrive vault)
       |                            |
       └────────────────────────────┘
                 GOOGLE DRIVE (documents)
```

### Canonical Vault

`C:\Users\bblai\OneDrive\Documents\Bryan's Vault` - OneDrive syncs to all devices. Local `C:\Bryan's Vault` deprecated and removed.

### Ownership Rules

| Content Type | Owner | Direction |
|---|---|---|
| Candidate records, status, pipeline | Notion | Notion -> Obsidian (read mirror) |
| Company/signal structured data | Notion | Notion -> Obsidian (read mirror) |
| Active Searches status | Notion | Notion -> Obsidian (read mirror) |
| CVs, contracts, documents | Google Drive | Drive -> Notion (link reference) |
| Working context files (USER.md, MEMORY.md, etc.) | Obsidian | Obsidian -> everywhere |
| Candidate notes/scratch work | Obsidian | Obsidian -> Notion (on push) |

Conflicts: owner always wins. No ambiguity.

## Sync Scenarios

### Scenario 0: Health Monitor
- **Schedule:** Daily, 7 AM ET
- **Logic:** Calls Make.com API (`/api/v2/scenarios/{id}/logs`) for each sync scenario. Parses most recent execution timestamp and status. If any scenario's last success is >2 hours past expected cadence, compiles alert.
- **Output:** Email alert listing scenario name, last success time, hours overdue, and last status.
- **Note:** Originally designed to use Sync State Tracker data store, but API-based approach proved simpler and eliminated the need for scenarios to write sync state. Data store was never populated and has been deleted.

### Scenario 1: Notion -> Obsidian (Company Intelligence)
- **Schedule:** Every 4 hours
- **Source:** Company Core, filtered to companies with signal activity in last 48h window
- **Output 1:** Markdown files in `recruiting/companies/{company-slug}.md` with frontmatter (status, signals, therapeutic areas) + signal timeline table
- **Output 2:** Dashboard rollup at `bryan/dashboards/signal-feed.md` - last 7 days of signals across all companies, reverse chronological
- **Write via:** OneDrive API

### Scenario 2: Notion -> Obsidian (Active Searches)
- **Schedule:** Hourly
- **Source:** Active Searches DB, filtered to Status = Active or On Hold
- **Output 1:** Per-search files in `recruiting/searches/{role-title-client}.md` with candidates, status, priority, last activity
- **Output 2:** Dashboard rollup at `bryan/dashboards/active-searches.md` - table of all live searches with candidate counts and weighted revenue
- **Write via:** OneDrive API

### Scenario 3: Notion -> Obsidian (Candidate Pipeline)
- **Schedule:** Hourly
- **Source:** Candidates DB, filtered to active statuses (Active, Screening Call Scheduled, Submitted to Client, Interviewing, Offer Extended)
- **Output:** Per-candidate files in `recruiting/candidates/{name-company}.md`
- **Terminal handling:** Candidates entering terminal status (Placed, Not Interested, Archive, etc.) get `terminal: true` + `terminal_date: ISO` added to frontmatter. File stays in `recruiting/candidates/` for 7 days. After 7 days in terminal, file moves to `90_archive/candidates/`.
- **Write via:** OneDrive API

### Scenario 4: Drive -> Notion (New Document Linker)
- **Schedule:** Hourly
- **Watches:** `01_CANDIDATES` and `00_INBOX` folders for new files
- **Matching logic:**
  1. Extract candidate name from filename (strip extensions, dates, prefixes)
  2. Search Notion Candidates DB for match on name
  3. If confident match found: add Drive file link to candidate record
  4. If ambiguous or no match: create stub record with `needs_review: true` flag, status = "New Lead", Drive link attached. Do NOT silently create clean records.
- **Write via:** Notion API

### Scenario 5: Obsidian -> Notion (Context + Notes Sync)
- **Schedule:** Hourly
- **Source 1:** Root context files (`USER.md`, `MEMORY.md`, `TODO.md`) read via OneDrive API
- **Source 2:** Candidate note sections (content below `<!-- SYNC BOUNDARY -->` delimiter) in `recruiting/candidates/` files
- **Logic:** Compare file timestamps against Sync State Tracker. Only process changed files.
- **Output 1:** Updates "Agent Context" page in Notion with latest context file contents
- **Output 2:** Pushes candidate note edits back to corresponding Notion candidate records' notes field (matched via `notion_id` in frontmatter)

### Scenario 6: Obsidian -> Drive (Context Backup)
- **Schedule:** Every 4 hours
- **Source:** `USER.md`, `MEMORY.md`, `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `TOOLS.md` from OneDrive vault
- **Output:** Copies to `91_SYSTEM/agent-context/` in Google Drive
- **Write via:** Drive API

### Schedule Summary

| Scenario | Cadence | Estimated Ops/Run |
|---|---|---|
| 0: Health Monitor | Daily | ~18 (API calls to check each scenario) |
| 1: Company Intelligence | 4 hours | ~50-100 |
| 2: Active Searches | Hourly | ~30-50 |
| 3: Candidate Pipeline | Hourly | ~40-80 |
| 4: Drive Document Linker | Hourly | ~10-20 |
| 5: Obsidian Context Sync | Hourly | ~15-30 |
| 6: Context Backup | 4 hours | ~10 |

**Estimated daily ops:** ~2,500-4,500 (well within Make.com Pro tier limits)

## Data Store

### Sync State Tracker (REMOVED)
- **Original purpose:** Track last-synced timestamps per scenario, per content item
- **Status:** Deleted 2026-02-28. Never populated by any scenario.
- **Reason:** Health Monitor uses Make.com API logs directly (`/api/v2/scenarios/{id}/logs`), which proved simpler than maintaining a separate state store. Individual scenarios use file timestamps and Notion `last_edited_time` for change detection instead of a centralized tracker.

## Obsidian Vault Structure

```
Bryan's Vault/
├── AGENTS.md                         # manual - agent definitions
├── HEARTBEAT.md                      # manual - system health
├── IDENTITY.md                       # manual - AI agent identity
├── MEMORY.md                         # manual - session memory (syncs to Notion + Drive)
├── SOUL.md                           # manual - core directives
├── TODO.md                           # manual - task tracking (syncs to Notion)
├── TOOLS.md                          # manual - tool registry
├── USER.md                           # manual - Bryan's profile (syncs to Notion + Drive)
│
├── bryan/
│   ├── dashboards/
│   │   ├── active-searches.md        # SYNCED - Scenario 2
│   │   ├── pipeline-summary.md       # SYNCED - Scenario 3
│   │   └── signal-feed.md            # SYNCED - Scenario 1
│   ├── linkedin/
│   ├── recruit-ai/
│   └── recruitrx/
│
├── recruiting/
│   ├── candidates/
│   │   └── {name-company}.md         # SYNCED - Scenario 3 (notes section syncs back)
│   ├── companies/
│   │   └── {company-slug}.md         # SYNCED - Scenario 1
│   ├── searches/
│   │   └── {role-title-client}.md    # SYNCED - Scenario 2
│   ├── interview-prep/              # manual only
│   └── outreach/                    # manual only
│
├── skills/
│   ├── company-research.md
│   ├── cv-scorer.md
│   └── outreach-drafter.md
│
├── config/
│   └── sync-manifest.json            # local sync state mirror
│
├── docs/
│   └── plans/                        # design docs
│
├── 90_archive/
│   └── candidates/                   # terminal candidates after 7-day grace
│
├── inbox/                            # manual capture
├── review/                           # manual capture
├── assets/
└── memory/
```

## Synced File Formats

### Company File
```markdown
---
source: notion
notion_id: {page_id}
last_synced: 2026-02-28T14:00:00Z
client_status: Active Client
therapeutic_areas: [Oncology]
most_recent_signal: Funding
most_recent_signal_date: 2026-02-15
---
# {Company Name}

**Status:** {client_status} | **Country:** {country} | **Headcount:** {band}

## Active Searches
- {role title} ({priority}, {fee_structure})

## Signal Timeline
| Date | Type | Summary |
|---|---|---|
| {date} | {type} | {summary} |
```

### Search File
```markdown
---
source: notion
notion_id: {page_id}
last_synced: 2026-02-28T14:00:00Z
client: {company}
status: Active
priority: Hot
fee_structure: Owned 100%
---
# {Role Title} - {Client}

**Status:** {status} | **Priority:** {priority} | **Fee:** {fee}
**Intake Date:** {date} | **Target Fill:** {date}

## Candidates ({count})
| Name | Status | Last Activity |
|---|---|---|
| {name} | {status} | {date} |
```

### Candidate File
```markdown
---
source: notion
notion_id: {page_id}
last_synced: 2026-02-28T14:00:00Z
status: Interviewing
current_company: {company}
current_title: {title}
terminal: false
---
# {Candidate Name}

**Status:** {status} | **Company:** {company}
**Title:** {title} | **Location:** {location}
**LinkedIn:** {url}

## Linked Searches
- {search title}

## Key Skills
{skills}

<!-- SYNC BOUNDARY - edits below sync back to Notion -->

```

### Signal Feed Dashboard
```markdown
---
source: notion
last_synced: 2026-02-28T14:00:00Z
---
# Signal Feed - Last 7 Days

| Date | Company | Signal Type | Summary |
|---|---|---|---|
| {date} | {company} | {type} | {summary} |

**Totals:** {n} funding | {n} positive data | {n} layoffs
```

## Conflict Resolution

| Scenario | Resolution |
|---|---|
| Structured data edited in both Notion and Obsidian | Notion wins. Frontmatter overwritten. Notes below SYNC BOUNDARY preserved. |
| New CV in Drive, candidate already in Notion | Match found -> link file to existing record. No duplicate. |
| New CV in Drive, no candidate match | Create stub with `needs_review: true`. Do not create clean "New Lead" records. |
| Company deleted from Notion | Markdown file moved to `90_archive/companies/` (retained 30 days). |
| Candidate enters terminal status | `terminal: true` + `terminal_date` added to frontmatter. File stays in place 7 days. Archived after grace period. |
| Obsidian vault offline when sync fires | Make writes to OneDrive cloud. Files sync down when device comes online. |
| Make scenario fails mid-sync | Make.com logs failure. Health Monitor detects via API. Failed items retry next cycle. |
| Duplicate candidate filenames | Filename format: `{name}-{company}.md`. If still ambiguous, append Notion ID slug. |

## Staleness Protection

- Every synced file: `last_synced` timestamp in frontmatter
- Scenario 0: daily health check, push alert if any scenario >2 hours overdue
- Dashboard files: `stale: true` flag added if source scenario hasn't run in 48+ hours

## Prerequisites

1. Create OneDrive connection in Make.com (personal OneDrive app)
2. ~~Create Sync State Tracker data store in Make.com~~ (removed - not needed, see Data Store section)
3. Create "Agent Context" page in Notion (for Scenario 5 output)
4. Consolidate vaults: copy any unique content from `C:\Bryan's Vault` to OneDrive vault, then remove local vault
5. Create `90_archive/candidates/` and `90_archive/companies/` folders in vault

## Implementation Order

1. Vault consolidation + folder structure setup
2. OneDrive Make.com connection (Sync State Tracker data store removed - not needed)
3. Scenario 0 (Health Monitor) - validates infrastructure
4. Scenario 2 (Active Searches) - highest value, tests Notion -> OneDrive pipeline
5. Scenario 3 (Candidate Pipeline) - extends the pattern
6. Scenario 1 (Company Intelligence + Signal Feed)
7. Scenario 5 (Obsidian -> Notion context sync)
8. Scenario 4 (Drive -> Notion document linker)
9. Scenario 6 (Context Backup)
