---
name: signal-to-brief
description: "Log a biotech signal to Notion and generate a full intelligence brief combining Perplexity research with Notion data. Use when Bryan says 'signal to brief', 'process this signal', 'log and brief', 'signal intel', 'full intel', 'brief me on', or provides a biotech signal (funding, layoff, positive data) and wants both logging and a research brief. Also trigger when Bryan pastes a news snippet and says 'what do we know' or 'dig into this'. This skill chains signal intake, deep research, and client brief into one autonomous workflow."
---

# Signal-to-Brief

Log a biotech signal to the correct Notion database, run deep company research via Perplexity, pull all existing Notion intelligence, and synthesize everything into one actionable brief.

---

## CRITICAL RULES

### Rule 1: No Mid-Execution Questions
All inputs are parsed from the initial message. If signal type or company name is genuinely ambiguous, ask ONE question covering all gaps before starting. Once execution begins, run to completion without stopping.

### Rule 2: No Narration
Do not print phase labels, progress updates, or status messages between steps. Execute silently. The only outputs Bryan sees are:
1. A one-line confirmation that the signal was logged (with Notion link)
2. The full intelligence brief

### Rule 3: Graceful Degradation

| Tool | If unavailable |
|------|----------------|
| `mcp__ec70e152-*` (Notion) | Skip Notion intake + data pull. Note "Notion unavailable" in brief. Run Perplexity research only. |
| `mcp__MCP_DOCKER__perplexity_research` | Skip research section. Note "Perplexity unavailable" in brief. Run Notion-only brief. |
| Both down | Tell Bryan both tools are unavailable. Display extracted signal fields for manual logging. |

### Rule 4: Sentence Editor Rules Apply
All prose sections (Hiring Implications, Recommended Actions) must pass Bryan's 8 rules: impact endings, max economy, no repetition, varied word choice, one advanced word per sentence, two-comma max, kill adverbs. Tables and data fields are exempt.

---

## Inputs

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| signal_input | string | required | - | Natural language, news snippet, URL, or structured data describing the signal |
| company_name | string | auto-parsed | extracted from signal_input | Company name |
| signal_type | string | auto-parsed | extracted from signal_input | funding / layoff / positive data |
| signal_date | date | auto-parsed | today | Date of the signal event |

**Accepted input formats:**
- Natural language: "Arvinas raised $200M Series D on Feb 15"
- News snippet pasted from an article
- URL (extract company + signal from context)
- Company name + description: "Disc Medicine positive Phase 2 data for bitopertin in EPP"
- Multiple signals: process each sequentially, one brief per company

---

## Execution

### Step 1: Parse Input

**Action:** Extract structured fields from raw input.

Extract:
- **Company name** (strip suffixes for matching: Therapeutics, Pharmaceuticals, Inc, Pharma, Bio, Biosciences)
- **Signal type:** funding ($5-50M or >=50M based on amount), layoff/restructuring, positive data/milestone
- **Signal date** (default to today)
- **Signal-specific fields:**

| Signal Type | Fields to Extract |
|-------------|-------------------|
| Funding $5-50M | Amount, round/series, lead investors, use of proceeds |
| Funding >=50M | Amount, round/series, lead investors, use of proceeds |
| Layoffs | Event type, country, reason, scale/headcount impact, source |
| Positive Data | Readout type, outcome, therapeutic areas, modality, conference/venue, likely next step |

**Expected output:** Structured data ready for Notion entry creation.

**Fallback:** If signal type is ambiguous, infer from keywords (raised/funding/Series = funding; layoff/restructuring/RIF/cut = layoffs; Phase/data/readout/approval/FDA = positive data). If still unclear, ask Bryan once.

---

### Step 2: Signal Intake (Notion)

**Action:** Log the signal to Notion.

#### 2a: Check for duplicates
- Tool: `mcp__ec70e152-d1ab-4c0f-8c87-a66e35b1513f__notion-search`
- Search the target signal database for the company name
- If entry exists with same date: update it, do not duplicate
- If no match: proceed to create

#### 2b: Create signal entry
- Tool: `mcp__ec70e152-d1ab-4c0f-8c87-a66e35b1513f__notion-create-pages`
- Target data source by signal type:

| Signal Type | Data Source |
|-------------|-----------|
| Funding $5-50M | `collection://9490e7cc-0504-4412-85ad-32b2ad7e906e` |
| Funding >=50M | `collection://927267bf-ec5b-4b20-9829-2b9d6371ba23` |
| Layoffs | `collection://21cf7674-0da8-4812-8708-04b65a252cac` |
| Positive Data | `collection://c5a4112f-cd39-479f-a90f-3165a1ec7a60` |

- Title field: `Company` = company name
- Populate all signal-specific fields from Step 1

#### 2c: Link to Company Core
- Tool: `mcp__ec70e152-d1ab-4c0f-8c87-a66e35b1513f__notion-search`
- Search Company Core (`collection://f371c4ed-be14-468e-a197-822154951845`) for company name
- Try exact match first, then strip suffixes
- If found: set `Company Core` relation on the signal entry
- If NOT found: create new Company Core entry, then link

#### 2d: Update Company Core metadata
- Tool: `mcp__ec70e152-d1ab-4c0f-8c87-a66e35b1513f__notion-update-page`
- Set `Most recent signal type` = `Funding`, `Positive data`, or `Layoffs`
- Set `Most recent signal date` = signal date

**Expected output:** Signal logged, linked, Company Core updated. Capture Notion page URL.

**Fallback:** If Notion MCP fails, log the failure and continue to Step 3. Note in brief that signal was NOT logged and needs manual entry.

---

### Step 3: Deep Research (Perplexity)

**Action:** Run comprehensive company research.

- Tool: `mcp__MCP_DOCKER__perplexity_research`

**Research query (adapt based on signal type):**

```
Research [COMPANY NAME] biotech/pharmaceutical company. Provide:

1. LEADERSHIP TEAM: Current CEO, CMO, VP/SVP Clinical Development, VP/SVP Drug Safety or Pharmacovigilance, Head of Biometrics/Biostatistics, VP Clinical Operations. Include names and approximate tenure.

2. CLINICAL PIPELINE: Active clinical trials - drug name, indication, current phase, expected milestones in next 12 months. Recent data readouts or regulatory submissions.

3. RECENT NEWS (last 90 days): Funding, partnerships, regulatory actions, leadership changes, conference presentations, layoffs. Exclude: [THE SIGNAL ALREADY KNOWN].

4. COMPETITIVE LANDSCAPE: 2-3 direct competitors in same therapeutic area or modality. Recent talent movement between these companies.

5. HIRING SIGNALS: Recent job postings (clinical development, drug safety, biometrics, clinical ops, medical affairs), LinkedIn headcount trends, team expansions or new sites.

6. COMPANY BASICS: Headquarters, approximate headcount, founding year, public/private, total funding, therapeutic focus.
```

**Expected output:** Structured research data with citations.

**Fallback:** If `perplexity_research` fails, try `mcp__MCP_DOCKER__perplexity_ask` with shorter query (leadership + pipeline + news only). If both fail, skip and generate Notion-only brief.

---

### Step 4: Pull Existing Notion Intel

**Action:** Search all Notion databases for existing company data.

#### 4a: Company Core profile
- Tool: `mcp__ec70e152-d1ab-4c0f-8c87-a66e35b1513f__notion-search` then `mcp__ec70e152-d1ab-4c0f-8c87-a66e35b1513f__notion-fetch` for full page
- Capture: Client Status, Country, Therapeutic areas, Headcount band, Last Contact Date, Last Submission, ATS Type

#### 4b: Historical signals (search each DB for company name)
- Layoffs: `collection://21cf7674-0da8-4812-8708-04b65a252cac`
- Positive Data: `collection://c5a4112f-cd39-479f-a90f-3165a1ec7a60`
- Funding 5-50M: `collection://9490e7cc-0504-4412-85ad-32b2ad7e906e`
- Funding >=50M: `collection://927267bf-ec5b-4b20-9829-2b9d6371ba23`
- Sort by date, most recent first

#### 4c: Job Alerts
- `collection://e83b1888-f65a-486d-bc1f-c0071623f9af` - job family, level, status

#### 4d: Active Searches
- `collection://a9ad56d9-0459-44c3-a914-5bfeaa8617bf` - role title, status, priority, fee structure, candidates count

#### 4e: Candidate Pipeline
- `collection://3841a478-62d3-4e5d-8265-d429375bd314` - candidates linked to this company

**Expected output:** Full picture of GQR's existing relationship with this company.

**Fallback:** If any individual DB search fails, note it in that section and continue.

---

### Step 5: Synthesize Intelligence Brief

**Action:** Combine all data from Steps 1-4.

**Leadership mapping** - match Perplexity findings to Bryan's placeable roles:
- CMO / Chief Medical Officer -> placeable
- VP/SVP Clinical Development -> placeable
- VP/SVP Drug Safety / Pharmacovigilance -> placeable
- Head/Director+ Biometrics / Biostatistics -> placeable
- VP/SVP Clinical Data Management -> placeable
- Medical Directors -> placeable
- VP Clinical Operations -> placeable
- CEO -> BD context, not a placement target

**Hiring Implications** - cross-reference:
- Signal type (funding = hiring; positive data = scaling; layoff = talent source, NOT client target)
- Pipeline stage (Phase 2+ = drug safety/PV; Phase 3 = biometrics; NDA/BLA = regulatory + medical affairs)
- Headcount band (<200 = building first dedicated functions)
- Existing job alerts (confirm or expand)

**Recommended Actions** - 2-3 concrete next steps based on:
- GQR relationship status (new = BD outreach; existing client = check-in; active search = pipeline update)
- Signal implications (funding = timing play; positive data = expansion play; layoff = talent sourcing play)
- Intel gaps (no contact = first touch; stale contact = re-engage)

---

### Step 6: Display Brief

Output the formatted brief per the Output Format section below.

---

## Output Format

```markdown
> Signal logged: [signal type] for [Company Name] ([date]) - [Notion link]

---

## [Company Name] - Intelligence Brief
Generated: [today's date] | Signal: [signal type + one-line summary]

### Company Profile
| Field | Value |
|-------|-------|
| **Headquarters** | [city, state/country] |
| **Founded** | [year] |
| **Public/Private** | [status + ticker if public] |
| **Headcount** | [band or estimate] |
| **Total Funding** | [amount if known] |
| **Therapeutic Focus** | [areas] |
| **GQR Client Status** | [from Notion or "Not in system"] |
| **Last GQR Contact** | [date or "No record"] |
| **Last Submission** | [date or "None"] |

### Signal Summary
**New Signal:** [Full details of the signal just logged]

**Historical Signals:**
| Date | Type | Details |
|------|------|---------|
| [date] | [type] | [one-line summary] |
[If none: "No prior signals logged"]

### Leadership Team
| Name | Title | Tenure | Placeable Role? |
|------|-------|--------|-----------------|
| [name] | [title] | [since year or ~duration] | [Yes/No] |
[From Perplexity. If unavailable: "Leadership data unavailable - Perplexity research failed"]

### Clinical Pipeline
| Drug/Candidate | Indication | Phase | Next Milestone |
|---------------|------------|-------|----------------|
| [name] | [indication] | [phase] | [event + timeline] |
[From Perplexity. If unavailable: "Pipeline data unavailable"]

### Hiring Implications
[2-4 sentences. Specific role types this company likely needs based on signal + pipeline + headcount. Sentence editor rules apply.]

### Active Job Alerts
| Role | Family | Level | Status |
|------|--------|-------|--------|
[From Notion. If none: "No active job alerts"]

### Existing GQR Relationship
- **Active Searches:** [count + role titles, or "None"]
- **Candidates in Pipeline:** [count + statuses, or "None"]
- **Prior Submissions:** [status or "None on record"]

### Competitive Landscape
| Competitor | Therapeutic Overlap | Recent Activity |
|-----------|-------------------|-----------------|
[From Perplexity. 2-3 max. If unavailable: "Competitive data unavailable"]

### Recommended Actions
1. [Specific, actionable next step with rationale]
2. [Specific, actionable next step]
3. [Optional third if warranted]
```

**File type:** Displayed in conversation only (not saved to disk or Notion by default)

---

## Validation

1. **Signal logged check:** Confirm the `notion-create-pages` or `notion-update-page` call returned successfully. If failed, confirmation line must say "FAILED - manual logging needed" instead of a fake link.

2. **Brief completeness check:** Every section header must be present (Company Profile, Signal Summary, Leadership Team, Clinical Pipeline, Hiring Implications, Active Job Alerts, Existing GQR Relationship, Competitive Landscape, Recommended Actions). Sections with no data must say so explicitly - never silently omit a section.

3. **No hallucinated names:** Every person in Leadership Team must come from the Perplexity response. Every candidate in Existing GQR Relationship must come from Notion results. Do not infer or guess names.

---

## What This Skill Is NOT

- Not a replacement for `/signal-intake` - that remains available standalone for quick logging without research
- Not a replacement for `/client-brief` - that remains available standalone for existing companies without a new signal
- Not an outreach drafter - Bryan handles outreach separately via `/outreach:draft`
- Not a market map - full competitive landscape analysis is a separate request
- Not a Notion page writer - the brief displays in conversation only
