# Functional Area Taxonomy - Canonical Values

> Last updated: 2026-04-07
> Applies to: Company Core, Candidates, Active Searches, Job Alerts
> Note: Active Searches still has legacy "Function" (select) property pending Make.com scenario 4260680 update.

## 20 Canonical Values

| # | Value | Replaces | Notes |
|---|-------|----------|-------|
| 1 | Clinical Development | - | Core Bryan function |
| 2 | Clinical Operations | - | Core Bryan function |
| 3 | Drug Safety/PV | Pharmacovigilance, Drug Safety | |
| 4 | Biostatistics | Biometrics/Stats, Statistical Analysis, Statistics, Biometrics | |
| 5 | Statistical Programming | Programming | |
| 6 | Clinical Data Management | Data Management | |
| 7 | Medical Affairs | - | Exists for candidate background tagging; Bryan does NOT recruit FOR Med Affairs |
| 8 | MSL | Scientific Liaison | Medical Science Liaison |
| 9 | Regulatory Affairs | Regulatory | Full name, Title Case |
| 10 | CMC/Manufacturing | CMC | |
| 11 | Research & Development | Research and Development, R&D Liaison, R&D/Discovery | Ampersand, not "and" |
| 12 | Quality Assurance | Quality | |
| 13 | Clinical Outsourcing | Vendor Mgmt, Vendor Oversight, Vendor Selection, Vendor Outsourcing, Outsourcing | Matches Structure Therapeutics role family |
| 14 | Program Management | - | |
| 15 | Project Management | - | |
| 16 | Publications/Medical Writing | Publications | |
| 17 | Business Development | - | |
| 18 | Commercial | Sales, Marketing | |
| 19 | Executive Leadership | - | C-suite candidates |
| 20 | Alliance Management | - | |

## Removed Values

| Value | Reason |
|-------|--------|
| Medical Director | Title, not function - candidates belong in Clinical Development |
| Scientific Partnerships | Too niche |
| Account Management | Not a placement function |
| Recruitment / Talent Acquisition | Not a placement function |
| Procurement | Not a placement function |
| Market Research | Not a placement function |
| Contract Management / Contracts Management / Contracting | Not a placement function |
| Governance | Not a placement function |
| Financial Management | Not a placement function |

## Pending Cleanup

- [ ] Update Make.com scenario 4260680 (context_sync_active_searches) to read "Functional Areas" instead of "Function"
- [ ] Verify hourly sync runs clean
- [ ] Delete old "Function" property from Active Searches

## Rules

- Title Case always
- Multi-select on all databases (Candidates, Active Searches, Job Alerts, Company Core)
- Drug Safety/PV uses forward slash (not "Drug Safety & PV" or "Drug Safety and PV")
- Research & Development uses ampersand (not "Research and Development")
