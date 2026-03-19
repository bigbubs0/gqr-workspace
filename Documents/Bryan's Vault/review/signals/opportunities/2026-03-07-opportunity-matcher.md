# Opportunity Matcher - 2026-03-07

| Company | Signal | Account Type | Linked Search | Candidate Angle | BD Angle | Priority | Next Move |
|---|---|---|---|---|---|---|---|
| Aditum | No verified signal loaded | Owned (100%) | Ambiguous - no deterministic company key in local active-search mirror | Do not route candidates without a real trigger event | Hold outreach until signal source is restored | Low | Re-run matcher after next successful signal ingestion |
| Xellar | No verified signal loaded | Team (50%) | Ambiguous - no deterministic company key in local active-search mirror | Hold candidate packaging until a verified signal appears | Keep warm only; no outbound motion yet | Low | Re-scan first when signal feed is healthy |
| IDEAYA | No verified signal loaded | Team (50%) | Ambiguous - no deterministic company key in local active-search mirror | Hold candidate packaging until a verified signal appears | Keep warm only; no outbound motion yet | Low | Re-scan first when signal feed is healthy |
| Structure/Wave | No verified signal loaded | Team (50%) | Ambiguous - no deterministic company key in local active-search mirror | Hold candidate packaging until a verified signal appears | Keep warm only; no outbound motion yet | Low | Re-scan first when signal feed is healthy |
| Karyopharm | No verified signal loaded | Team (50%) | Ambiguous - no deterministic company key in local active-search mirror | Hold candidate packaging until a verified signal appears | Keep warm only; no outbound motion yet | Low | Re-scan first when signal feed is healthy |
| Regeneron | No verified signal loaded | Warm lead | No linked live search in local mirror | Keep pipeline in standby; prep only for known call context | Focus on 2026-03-09 call prep, not signal-based pitch | Medium | Run focused refresh before call prep window |

## Notes
- Primary signal input read: `review/signals/daily/2026-03-07-morning-signal-radar.md`.
- Morning radar confirms signal feed gap from local mirror (`bryan/dashboards/signal-feed.md` empty), so this run stays in blocker mode.
- Local mirrors read: `recruiting/searches` (22 active records) and `recruiting/candidates` (24 pipeline records).
- Dead accounts excluded: Korro Bio and Ionis.

## Blockers
- No verified fresh signal rows are available to join, so opportunity matching cannot proceed beyond account-level hold actions.
- Search mirror records are role-centric and often lack a normalized company field, which blocks deterministic search linking when signal data is absent.
- `Job Alerts` data source remains unresolved in `config/notion-databases.json` (`data_source_id: null`).
