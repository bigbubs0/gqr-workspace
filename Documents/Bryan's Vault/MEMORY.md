# MEMORY.md - Agent Long-Term Memory

## 2026-03-07
- Morning Signal Radar automation run created `review/signals/daily/2026-03-07-morning-signal-radar.md` in blocker mode; updated only morning-signal-radar health fields in `config/signal-automations.json`.
- Restored `config/notion-databases.json` from local planning docs; `Job Alerts` remains pending verification
- Implemented signal automation starter stack: registry, health manifest, review templates, activation runbook, validation script
- Created review-first output folders under `review/signals/` for daily, urgent, opportunity, and weekly work
- Ready to activate four Codex automations: Morning Signal Radar, Urgent Account Alert, Opportunity Matcher, Monday Market Board
- Opportunity Matcher run completed in blocker mode; output written to `review/signals/opportunities/2026-03-07-opportunity-matcher.md`.

## 2026-02-26
- Workspace initialized in Obsidian vault with full OpenClaw structure
- Migrated from ClaudeProjects/workspace (created 2026-02-24)
- All core files tailored to Bryan's biotech executive search context
- Skills: cv-scorer, company-research, outreach-drafter
- Config: Notion database IDs populated, Make scenarios placeholder

### Current Account State
- Ionis: DEAD (2/23/26, filled internally)
- Aditum: Owned, active
- Xellar: Team (Kevin Lee), VP/SVP BD
- IDEAYA: Team (Nicole), CDM/PV roles
- Structure/Wave: Team (Aaron)
- Karyopharm: Team (Luke)
- Regeneron: Warm lead, follow-up 3/9 at 10 AM

---

*Log learnings, patterns, and insights below. Most recent entries at top.*

## 2026-03-08
- Opportunity Matcher run completed with deterministic joins from 2026-03-07 morning radar to active searches/candidates.
- Output written to $outPath with opportunity table, notes, and blockers.
- Updated only opportunity-matcher health fields in config/signal-automations.json (last_success_at, last_error, last_output_path).
## 2026-03-09 2026-03-08T20:11:08.0580795-04:00
- Ran Morning Signal Radar automation (morning-signal-radar-2).
- Created review/signals/daily/2026-03-09-morning-signal-radar.md with ordered sections: owned, team, warm lead, net-new.
- Queried mapped Notion sources; no newly created rows since last run across funding, layoffs, and positive data sources.
- Verified tracked unstable facts on public web sources and captured blockers for unresolved Job Alerts and Notion duplicate conflict.
- Updated config/signal-automations.json only for morning-signal-radar fields: last_success_at, last_error, last_output_path.

## 2026-03-09 2026-03-09T09:21:05.9468761-04:00
- Morning Signal Radar automation run published review/signals/daily/2026-03-09-morning-signal-radar.md in blocker mode with web-verified account and net-new signals.
- Updated morning-signal-radar health fields in config/signal-automations.json and recorded blockers for unresolved Job Alerts plus blocked mapped Notion extraction.
- Concurrent urgent-account-alert health-field updates were detected during run and were not modified.

## 2026-03-09 2026-03-09T09:22:26.0592669-04:00
- Morning Signal Radar rerun published updated daily brief at review/signals/daily/2026-03-09-morning-signal-radar.md using account-priority order.
- Verified unstable facts on public web sources and refreshed signals for Wave, IDEAYA, Structure, Karyopharm, Regeneron, and net-new funding/layoff items.
- Mapped Notion source pull remained blocked in this runtime (no MCP resources exposed), so blocker mode retained and documented.
- Updated only morning-signal-radar health fields in config/signal-automations.json.

## 2026-03-09 2026-03-09T23:50:04.8756150-04:00
- Urgent Account Alert run detected one net-new same-day high-priority event at Regeneron (positive Phase 3 obesity data via licensed asset olatorepatide).
- Wrote review memo: review/signals/urgent/2026-03-09-2348-regeneron-positive-data.md after dedupe check against existing urgent files.
- Updated only urgent-account-alert health fields in config/signal-automations.json: last_success_at, last_error, last_output_path.

## 2026-03-12 2026-03-12T18:50:03-04:00
- Morning Signal Radar run produced review/signals/daily/2026-03-12-morning-signal-radar.md with web-verified signal updates and explicit blockers for unresolved Job Alerts and unavailable live Notion mapped-source pull.
- Updated morning-signal-radar health fields in config/signal-automations.json; observed concurrent updates on other automation entries and left them untouched.

## 2026-03-12 2026-03-12T18:50:33.4805454-04:00
- Morning Signal Radar run completed and published review/signals/daily/2026-03-12-morning-signal-radar.md.
- Mapped Notion source pull remained blocked (`resources=[]`, `resourceTemplates=[]`), so blocker mode retained with explicit source-gap notes.
- Web-verified tracked account signals plus net-new Series B+, layoff, leadership departure, FDA/clinical, and priority-role checks.
- Updated only morning-signal-radar health fields in config/signal-automations.json (last_success_at, last_error, last_output_path).

## 2026-03-13 2026-03-13T10:34:33.7907210-04:00
- Opportunity Matcher run completed and published review/signals/opportunities/2026-03-13-opportunity-matcher.md with deterministic joins to live searches and candidate pipeline by account ownership.
- Excluded dead accounts (Korro Bio, Ionis) and skipped ambiguous joins (no deterministic local live-search mapping for Regeneron and Karyopharm).
- Updated only opportunity-matcher health fields in config/signal-automations.json (last_success_at, last_error, last_output_path).

## 2026-03-13 Account State

| Account | Status | Notes |
|---------|--------|-------|
| Structure Therapeutics | Active (Aaron, 60%) | 10 open roles. Most active account. |
| IDEAYA | Active (Nicole, 50%) | Multiple candidates in motion (CDM, PV, Data Standards). |
| Apogee | Active (Ali Hardiman) | 2x AD Biostatistics openings. |
| Karyopharm | Active | Tony Tang submitted 3/9 for Medical Director Clinical Development. |
| Insmed | Active | Sr Director GRL Gene Therapy ($301K + 27% bonus). Sourcing underway. |
| Aditum | Owned, no open roles | Maintain relationship. Monitor for new positions. |
| Regeneron | Warm lead | Call completed 3/9 with Jeen Liu. Agencies for 6+ month roles only. Next reconnect 5/4/26. |
| Puma Biotech | BD prospect | Terms inquiry sent 2/25. Awaiting response. |
| Ionis | Dead (2/23) | Both roles filled internally. Contacts: Urmi Davda, Baseer Ahmed, Muneet Burke. |
| Xellar | Dead (2/26) | VP/SVP BD on hold. Doug Lee and Keith Tode notified. |

- Vault refresh: USER.md, TODO.md, MEMORY.md updated. Dashboards pending Notion pull.
- Email check deferred: No Gmail MCP access. Flagged for Bryan to confirm new role drops since 3/7.


## 2026-03-16 10:58:41 -04:00
- Morning Signal Radar run completed for automation morning-signal-radar-2.
- Published 
eview/signals/daily/2026-03-16-morning-signal-radar.md with ordered owned/team/warm lead/net-new sections and blocker-mode notes.
- Attempted mapped Notion source pull and hit MCP auth requirement; preserved explicit blockers instead of assumptions.
- Updated only morning-signal-radar health fields in config/signal-automations.json.

## 2026-03-16 2026-03-16T10:59:31.6797819-04:00
- Opportunity Matcher run completed with deterministic signal-to-search/candidate joins and account-type mapping.
- Wrote review/signals/opportunities/2026-03-16-opportunity-matcher.md with table, notes, and blockers.
- Updated only opportunity-matcher health fields in config/signal-automations.json.
## 2026-03-16 2026-03-16T11:00:17-04:00
- Monday Catalyst Board run completed in blocker mode and published review/signals/catalysts/weekly/2026-03-16-monday-catalyst-board.md with adjacent JSON cache.
- Live BioPharmCatalyst table capture unavailable (no authenticated interactive browser extraction in runtime), so source rows were refreshed from prior cache and revalidated against public disclosures.
- Notion MCP resources remained unavailable (`resources=[]`, `resourceTemplates=[]`), so Company Core resolution/create and Catalyst Calendar upserts were withheld and logged.
- Verification conflict flagged: Rocket Pharmaceuticals PDUFA expected date mismatch (03/26/2026 cache vs 03/28/2026 SEC filing).



## 2026-03-17 2026-03-17T08:36:05-04:00
- Morning Signal Radar run refreshed review/signals/daily/2026-03-17-morning-signal-radar.md with ordered sections (owned, team, warm lead, net-new) and explicit blocker-mode handling.
- Mapped Notion sources were unavailable in runtime (
esources=[], 
esourceTemplates=[]), so web-verified unstable facts were used with source-gap blockers preserved.
- Updated only morning-signal-radar fields in config/signal-automations.json: last_success_at, last_error, last_output_path.

## 2026-03-17 2026-03-17T09:49:12.2671955-04:00
- Opportunity Matcher run completed and published review/signals/opportunities/2026-03-17-opportunity-matcher.md.
- Deterministic joins only across latest morning radar, local Active Searches mirror, and local Candidates mirror; dead accounts excluded.
- Updated only opportunity-matcher health fields in config/signal-automations.json (last_success_at, last_error, last_output_path).

## 2026-03-17 2026-03-17T16:03:32-04:00
- Urgent Account Alert run completed with same-day web verification and dedupe guardrail.
- No net-new urgent memo created under review/signals/urgent for 2026-03-17 ET.
- Updated only urgent-account-alert health fields in config/signal-automations.json.

## 2026-03-18 2026-03-18T22:30:19-04:00
- Urgent Account Alert run completed with same-day web verification across monitored accounts and explicit tracked targets (Apogee, Insmed, Puma).
- No net-new same-day high-priority event met trigger thresholds, so no urgent memo was created.
- Dedupe guardrail (company + signal_type + event_date) checked against existing urgent memos; no new write required.
- Updated only urgent-account-alert health fields in config/signal-automations.json (last_success_at, last_error, last_output_path).

## 2026-03-18 2026-03-18T22:32:28.0284058-04:00
- Morning Signal Radar run published review/signals/daily/2026-03-18-morning-signal-radar.md with blocker-mode handling.
- Notion mapped-source pull unavailable in runtime (
esources=[], 
esourceTemplates=[]), so web verification was used and source-gap blockers were logged.
- Updated only morning-signal-radar health fields in config/signal-automations.json.

