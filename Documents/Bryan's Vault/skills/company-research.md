# Skill: Company Research

## Purpose
Research a biotech/pharma company and assess recruiting opportunity signals.

## Research Checklist
1. **Notion first** - Search Company Core, Funding, Layoffs, Positive Data, Job Alerts for existing data
2. **Funding** - Last round, amount, lead investor, date
3. **Pipeline** - Active clinical trials, phases, therapeutic areas
4. **Leadership** - Current CMO, VP Clinical, Head of Reg Affairs - any recent departures?
5. **Hiring signals** - Open roles on careers page, LinkedIn job postings
6. **News** - Last 90 days: data readouts, FDA decisions, partnerships, layoffs
7. **Headcount** - LinkedIn employee count, growth trend

## Job Alert Sweep Addendum
Use this section when the task is to scan career sites or capture open roles.

### Scope
- Only process Company Core companies with a Careers Page URL.
- Sweep order:
  1. Tier 1 - current clients
  2. Tier 2 - hot/warm prospects with funding in the last 90 days
  3. Tier 3 - all others
- Only consider these job families:
  - Clinical Development
  - Drug Safety/PV
  - Clinical Data Management
  - Biostatistics
  - Statistical Programming
  - Medical Affairs
  - Regulatory Affairs

### Save Criteria
- Open the live posting for every candidate role.
- Save only if the live posting explicitly shows a US location.
- Accept:
  - `United States`
  - `USA` or `U.S.`
  - a verified US city/state
  - `Remote - United States`
  - `Remote, USA`
  - hybrid with a verified US office
- Reject:
  - non-US locations
  - `Remote` with no US restriction
  - `Global`, `worldwide`, `international`, `EMEA`, `APAC`, `EU`, `UK`, `Canada`, `LATAM`
  - ambiguous or unverifiable locations

### Required Validation
Before any save, confirm all of the following:
1. The Job URL opens to the live posting.
2. The page title matches the job title.
3. The Job URL is a direct posting URL, not a generic careers page.
4. The location is copied from the live posting.
5. The role is explicitly US-eligible.
6. The Job URL does not already exist in Job Alerts.

Create this internal validation record before deciding to save:

```json
{
  "job_title": "",
  "company": "",
  "job_url": "",
  "location_raw": "",
  "location_type": "onsite|hybrid|remote|unknown",
  "us_eligible": true,
  "eligibility_reason": "",
  "duplicate_found": false,
  "save_to_notion": true
}
```

Rules:
- `save_to_notion = true` only if `us_eligible = true`, `duplicate_found = false`, and the direct Job URL is verified.
- If any field is uncertain, set `save_to_notion = false`.
- Extraction first. Judgment second. Write last.

### Blocker Mode
- Follow `docs/plans/2026-03-09-us-only-job-alerts-rollout.md` as the canonical spec.
- If `Job Alerts` is still unresolved in `config/notion-databases.json`, do not write to Notion.
- In blocker mode, produce a local review note and do not update `Jobs Last Checked`.

## ICP Scoring (1-5)
- [ ] Phase 1+ biotech company?
- [ ] Scaling clinical development teams?
- [ ] Recent funding event or positive data readout?
- [ ] Growing clinical dev, drug safety/PV, biometrics, or clinical ops?
- [ ] Likely to use external search firms?

## Output Format
Save as: `/recruiting/companies/YYYY-MM-DD-companyname.md`

Include:
- Company name, HQ, website, LinkedIn URL
- Stage (preclinical / Phase 1 / Phase 2 / Phase 3 / commercial)
- Funding summary
- Pipeline snapshot (table)
- Leadership team (names + LinkedIn)
- ICP Score (X/5)
- Recruiting opportunity assessment (1 paragraph)
- Recommended next action
