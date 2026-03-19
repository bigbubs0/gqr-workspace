# US-Only Job Alerts Rollout

## Purpose
Standardize career-site sweeps for Claude and Codex so Job Alerts only captures roles that are explicitly US-based on the live posting. Until `Job Alerts` has a verified Notion data source ID and live access is restored, this workflow stays in blocker mode and produces a local review report only.

## Operating Summary
- Source population: Company Core records with a Careers Page URL
- Sweep order:
  1. Tier 1 - Current clients
  2. Tier 2 - Hot/warm prospects with funding in the last 90 days
  3. Tier 3 - All others
- Target job families:
  - Clinical Development
  - Drug Safety/PV
  - Clinical Data Management
  - Biostatistics
  - Statistical Programming
  - Medical Affairs
  - Regulatory Affairs
- Write rule: save only explicitly US-eligible roles
- Blocker rule: do not write to Notion until `Job Alerts` is verified and live access is restored

## Default Sweep Prompt
Use this as the default sweep prompt.

Check the career sites for all companies in Company Core that have a Careers Page URL.

Your task is to find and log only US-based jobs into the Job Alerts database.

Hard rule:
Only save jobs that are explicitly located in the United States.

Target job families:
- Clinical Development
- Drug Safety/PV
- Clinical Data Management
- Biostatistics
- Statistical Programming
- Medical Affairs
- Regulatory Affairs

For each company:
1. Visit the careers page.
2. Review open jobs in the target job families.
3. Open the direct live posting for each candidate role.
4. Extract:
   - Name: Job title
   - Company: Link to Company Core record
   - Job URL: Direct ATS or direct posting URL
   - Job Family
   - Level: `c_suite`, `evp_svp`, `vp`, `director`, `associate_director`, `manager`, `senior`, `mid_entry`, or `unknown`
   - Location: Exact location text from the live posting
   - First Seen: today's date
   - Status: `New`

US-only eligibility rules:
Accept only if one of these is true:
- The location explicitly states United States, USA, U.S., or a US city/state.
- The role is `Remote - United States` or `Remote, USA`.
- The role is hybrid and tied to a US office.
- The posting lists multiple locations and at least one clearly verified location is in the US.

Reject immediately if any of these is true:
- The posting location is outside the United States.
- The role is remote but geography is global, worldwide, international, EMEA, APAC, EU, UK, Canada, LATAM, or unspecified.
- The posting lists only non-US cities or countries.
- The location cannot be verified from the live posting.

Before saving any row, confirm all of the following:
1. The Job URL opens to the live posting.
2. The page title matches the job title.
3. The Job URL is a direct posting URL, not a generic careers page.
4. The Location is copied from the live posting, not scraped suffix text.
5. The job is explicitly US-eligible.
6. The job does not already exist in Job Alerts based on Job URL.

Decision rule:
- If there is any doubt about geography, do not save the role.
- Skip ambiguous roles rather than risk logging a non-US job.

After scanning, update the Jobs Last Checked date in Company Core for each company reviewed only when live write access is available. In blocker mode, record the review locally and do not update Notion.

## Mandatory Validation Record
Create this internal record for every candidate role before deciding whether to save:

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

Validation rules:
- `save_to_notion = true` only if `us_eligible = true`, `duplicate_found = false`, and the direct Job URL is verified.
- If any field is uncertain, set `save_to_notion = false`.
- Never write first and validate later.
- Extraction first. Judgment second. Write last.

## US Geography Validation Gate
Before saving a new job alert:

7. Confirm the live posting is explicitly US-based.
8. Accept only:
   - United States
   - USA / U.S.
   - US city/state
   - `Remote - United States`
   - Hybrid with a verified US office
9. Reject:
   - Any non-US city or country
   - Remote roles with no explicit US restriction
   - `Global`, `worldwide`, `international`, `EMEA`, `APAC`, `EU`, `UK`, `Canada`, `LATAM` roles
   - Ambiguous or unverified locations
10. If a role fails geography validation, do not save it.
11. If geography is uncertain, skip the role rather than making an assumption.

## Location Interpretation Rules
Accept:
- `Cambridge, MA`
- `Boston, Massachusetts`
- `New York, NY`
- `South San Francisco, CA`
- `Remote - United States`
- `Remote, USA`
- `United States`

Reject:
- `Hyderabad, India`
- `Cairo, Egypt`
- `Tokyo, Japan`
- `Cambridge, UK`
- `Toronto, ON`
- `Remote`
- `Global`
- `Worldwide`
- `EMEA`
- `APAC`
- `EU`
- `UK`
- `Canada`
- Multiple locations with no clearly verified US location

## Public Field Standards
Required job fields:
- `Name`
- `Company`
- `Job URL`
- `Job Family`
- `Level`
- `Location`
- `First Seen`
- `Status`

Level normalization:
- `c_suite`
- `evp_svp`
- `vp`
- `director`
- `associate_director`
- `manager`
- `senior`
- `mid_entry`
- `unknown`

## Notion Schema Checklist
Add or confirm these properties in `Job Alerts`:
- `Country` - Select
  - `United States`
  - `Non-US`
  - `Unknown`
- `US Eligible` - Checkbox
- `Location Verified` - Checkbox
- `Geo Status` - Formula
- `Reject Reason` - Text
- `Review Queue` - Formula or checkbox

Recommended formula for `Geo Status`:

```text
if(
  prop("US Eligible"),
  "Approved - US",
  if(
    prop("Country") == "Non-US",
    "Reject - Non-US",
    "Review - Ambiguous"
  )
)
```

Recommended formula for `Review Queue`:

```text
if(
  and(prop("US Eligible"), prop("Location Verified")),
  "Ready",
  "Needs Review"
)
```

## View Setup
Create these views in Notion:

### Main US Job Alerts
Filters:
- `US Eligible` = checked
- `Location Verified` = checked
- `Geo Status` = `Approved - US`

### Geo Review
Filters:
- `US Eligible` = unchecked
- Or `Location Verified` = unchecked
- Or `Geo Status` = `Review - Ambiguous`

### Rejected Non-US
Filters:
- `Geo Status` = `Reject - Non-US`

These views are quarantine guardrails only. Rejected or ambiguous roles are never intentionally saved to `Job Alerts`.

## Non-Negotiable Agent Rules
- Do not infer geography from company headquarters.
- Do not infer geography from department pages.
- Do not infer geography from search results.
- Only use the exact location shown on the live job posting.
- If the location is not explicitly US-based, skip the role.
- If the live posting is unavailable, skip the role.
- If the direct posting URL cannot be verified, skip the role.

## Blocker Mode
Current blocker status:
- `Job Alerts` data source ID is not verified in `config/notion-databases.json`.
- Live Notion MCP access is not available in this runtime.

Required blocker-mode behavior:
- Run career-site sweeps in verification mode only.
- Produce a local review report with approved candidates, rejected candidates, and reasons.
- Do not write new Job Alerts rows.
- Do not update `Jobs Last Checked` in Company Core.
- Keep rejected and ambiguous roles out of `Job Alerts`.

Exit blocker mode only when all are true:
1. `Job Alerts` data source ID is verified.
2. Required schema properties exist in Notion.
3. Duplicate checks on `Job URL` can run against live data.
4. Company Core updates for `Jobs Last Checked` are available.

## Test Cases
Prompt and unit checks:
- Accept: `Cambridge, MA`
- Accept: `Boston, Massachusetts`
- Accept: `Remote - United States`
- Accept: `Remote, USA`
- Accept: `United States`
- Reject: `Remote`
- Reject: `Global`
- Reject: `Worldwide`
- Reject: `EMEA`
- Reject: `APAC`
- Reject: `EU`
- Reject: `UK`
- Reject: `Canada`
- Reject: `Toronto, ON`
- Reject: `Cambridge, UK`
- Reject: `Hyderabad, India`

Per-role verification checks:
1. Direct URL opens a live posting.
2. Page title matches the job title.
3. URL is not a generic careers page.
4. Location text is copied from the posting body or header.
5. Duplicate detection blocks existing `Job URL`.

End-to-end checks after Notion access is restored:
1. Approved US role writes successfully.
2. Non-US role does not write.
3. Ambiguous role does not write.
4. Duplicate URL does not write.
5. `Jobs Last Checked` updates only for reviewed companies.

## Defaults and Assumptions
- Canonical source lives in local docs first and syncs to Notion later.
- Tier 2 "recent funding" means funding in the last 90 days.
- Tier 1 falls back to current active clients if Company Core lacks explicit tier fields.
- Tier 2 falls back to hot/warm prospects joined to recent funding signals if Company Core lacks explicit tier fields.
- Rejected and ambiguous roles are never intentionally saved to `Job Alerts`.
