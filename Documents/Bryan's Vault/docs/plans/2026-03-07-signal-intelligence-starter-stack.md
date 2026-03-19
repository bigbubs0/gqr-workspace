# Signal Intelligence Starter Stack

## Goal

Ship a review-first signal operating layer for Bryan's biotech search workflow. The stack surfaces new signals, urgent account events, search-linked opportunities, a Monday market board, and a Monday catalyst board without sending outreach.

## Implemented Files

- `config/notion-databases.json` - Restored source map with blocker state for `Job Alerts`
- `config/signal-automations.json` - Automation registry and schedules
- `config/signal-health-manifest.json` - Weekly green/red audit rules
- `review/signals/` - Output folders and templates
- `review/weekly-signal-automation-audit-template.md` - Audit format
- `scripts/validate-signal-automation-stack.ps1` - Local validation

## Source Rules

1. Read `USER.md` first for account ownership, warm leads, and dead accounts.
2. Read `TODO.md` for upcoming follow-ups and urgent priorities.
3. Read `config/notion-databases.json` for the current source map.
4. Use Notion as the structured source of truth when IDs are available.
5. Verify unstable facts on the web before citing them.
6. If `Job Alerts` remains unverified, write a blocker and continue with public job-posting verification only.

## Automation Specs

### Morning Signal Radar

- Schedule: daily at 6:30 AM ET
- Output: `review/signals/daily/YYYY-MM-DD-morning-signal-radar.md`
- Required sections: owned, team, warm lead, net-new, blockers
- Required signal types:
  - Series B or larger funding
  - layoffs
  - positive clinical data
  - Phase 2 to Phase 3 transitions
  - FDA milestones
  - CMO or VP-level departures
  - priority job postings

### Urgent Account Alert

- Schedule: hourly
- Output: `review/signals/urgent/YYYY-MM-DD-HHMM-company-signal.md`
- Scope: Aditum, Xellar, IDEAYA, Structure, Wave, Karyopharm, Regeneron, and explicitly tracked targets
- Trigger threshold: only same-day material events
- Dedupe key: `company + signal_type + event_date`

### Opportunity Matcher

- Schedule: daily at 6:45 AM ET
- Output: `review/signals/opportunities/YYYY-MM-DD-opportunity-matcher.md`
- Join fresh signals to:
  - active searches
  - candidate pipeline
  - account ownership
- Required columns:
  - company
  - signal
  - account type
  - linked search
  - candidate angle
  - BD angle
  - priority
  - next move

### Monday Market Board

- Schedule: Monday at 7:00 AM ET
- Output: `review/signals/weekly/YYYY-MM-DD-monday-market-board.md`
- Cover:
  - prior 7 days of signals
  - stalled searches
  - candidates with no activity over 7 days
  - warm lead follow-ups
  - blockers

### Monday Catalyst Board

- Schedule: Monday at 10:00 AM ET
- Output: `review/signals/catalysts/weekly/YYYY-MM-DD-monday-catalyst-board.md`
- Cache: `review/signals/catalysts/weekly/YYYY-MM-DD-monday-catalyst-board.json`
- Source strategy:
  - BioPharmCatalyst FDA and PDUFA calendar URLs first
  - public-source verification and enrichment second
- Required sections:
  - tracked companies first
  - catalysts in the next week
  - PDUFA catalysts in the next 90 days
  - new Company Core records
  - verification conflicts
  - blockers
- Notion behavior:
  - upsert live catalyst rows into `Catalyst Calendar`
  - relate rows to `Company Core`
  - create missing `Company Core` companies as `Prospect`

## Health And Audit

- Audit manifest: `config/signal-health-manifest.json`
- Audit template: `review/weekly-signal-automation-audit-template.md`
- Weekly audit owner: Bryan + Codex
- Green rule: recent success evidence, output exists, and no unresolved blocking config
- Red rule: stale, failed, missing output, or blocked by missing config

## Manual Activation Checklist

1. Verify the `Job Alerts` data source ID in Notion and update `config/notion-databases.json`.
2. Create the five Codex scheduled automations using the registry schedules.
3. Run `scripts/validate-signal-automation-stack.ps1`.
4. Trigger one manual run for Morning Signal Radar and confirm a dated file lands in `review/signals/daily/`.
5. Trigger Opportunity Matcher against that same morning run and confirm the output table is populated.
6. Trigger Urgent Account Alert twice against the same event and confirm no duplicate memo is created.
7. Run the Monday Market Board against a seeded week of signals and confirm stalled-search and no-activity sections are present.
8. Run the Monday Catalyst Board against the logged-in catalyst source and confirm both screenshot-style sections plus the JSON cache are present.

## Acceptance Tests

- Known signal test - a recent public funding, job posting, or positive data event appears in the morning radar.
- Dedupe test - the urgent alert does not create a second memo for the same event.
- Priority test - owned accounts sort above team accounts and dead accounts are excluded.
- Match test - at least one fresh signal joins to a live search with a concrete candidate or BD angle.
- Failure test - removing a source ID produces a blocker section instead of fabricated output.
- Catalyst dedupe test - rerunning the same catalyst board updates an existing row instead of creating a duplicate.
