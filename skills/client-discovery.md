---
name: client-discovery
description: "Use when Bryan says 'discovery prep', 'INTEL prep', 'research [company]', 'client meeting prep', 'BD prep [company]', 'get me ready for [company]', or asks to prepare for a new business call or first meeting with a hiring contact. Also trigger when Bryan mentions 'new account research', 'prospecting research', or provides a company name and asks for background intel. Generates client call prep packages. This skill MUST be read before generating any discovery prep."
---

## Load Context First

Before executing, silently load:

1. **Voice DNA** — Use Mode 2 (Client Relationship) for all output. Consultative, strategic softening, measured emotion.
2. **ICP** — Hiring manager persona (Sarah) for pain point mapping
3. **Business Profile** — GQR positioning, service offerings, competitive differentiators
4. **Notion Company Core** — If the company exists in Notion, pull existing data first. Do not duplicate research.
5. **Notion Jobs Database** — Pull any currently posted roles at this company. Bryan should walk into a discovery call already knowing their open headcount.

Do not reference these files. Use them silently.

---

# Client Discovery — Call Prep Package

## Purpose

Research a target company, map the contact's likely pain points, and produce a structured discovery call guide using the INTEL framework. Output is a document Bryan can reference on-screen during the call.

---

## CRITICAL RULES

### Rule 1: No Narration

Do not explain what you're about to do. Do not print phase labels. Execute and deliver.

### Rule 2: Sentence Editor Rules Apply

Every sentence must pass all 8 rules:

1. Impact endings — end on the strongest word
2. Define before contract — spell out acronyms on first use, abbreviate after
3. Max economy — fewest words possible
4. No repetition — never restate information already conveyed
5. Vary word choice — no word appears twice in the same paragraph
6. One advanced word per sentence max
7. Two-comma max — split if 3+ commas
8. Kill adverbs — replace with stronger verbs

### Rule 3: Never Guess Compensation Data

Compensation ranges, fee structures, and budget details must come from Bryan or verified sources. If unknown, flag: "[VERIFY with TA contact]" — do not estimate.

### Rule 4: Cite Sources Where Possible

Company intel claims must note the source: SEC filing, press release, ClinicalTrials.gov, LinkedIn, Notion, etc. If a claim is inferred rather than sourced, mark it "[INFERRED]."

### Rule 5: EQSC Responses Must Sound Like Bryan

Objection handling scripts use Bryan's voice — direct, scientific-literate, zero sales-speak. Not a playbook. A conversation.

### Rule 6: No "Phase 1+" Language

Use "Phase II/III" or "Phase II through commercial" or the specific phases.

### Rule 7: Pull Existing Notion Data First

If this company already exists in Notion Company Core, start from that record. Don't regenerate data Bryan already has - build on it.

### Rule 8: Anti-Slop Filter

Before producing final output, silently apply the 3-pass anti-slop filter:
1. Load `skills/anti-slop/kill-list.json` and scan for banned phrases - replace or delete per the kill list
2. Compress output using max economy and no-repetition principles
3. Scan for Voice DNA violations (never_sounds_like categories, business_jargon_replacements, em dashes)
Do not narrate. Output only the clean version.
For full filter spec, see `skills/anti-slop/SKILL.md`.

---

## Input

Bryan provides:

- Company name (required)
- Contact name and title (optional but improves pain point mapping)
- LinkedIn URL, JD, or specific questions Bryan wants answered (optional)
- Meeting context: "first BD call," "they reached out to us," "follow-up from conference," etc. (optional)

If the company name is ambiguous (e.g., "Vertex" could be Vertex Pharmaceuticals or Vertex Inc.), ask one clarifying question.

---

## Output: Discovery Call Prep Package

### Header

```
DISCOVERY PREP: [Company Name]
Contact: [Name, Title] (or "TBD" if not provided)
Meeting Type: [First BD Call / Follow-Up / Inbound Inquiry / Referral]
Prepared: [Date]
```

### Section 1: Company Intel

```
STAGE: [Preclinical / Phase I / Phase II / Phase III / Commercial / Multi-stage]
THERAPEUTIC AREAS: [Primary and secondary TAs]
LEAD PROGRAMS: [Drug name, indication, phase — top 2-3 programs]
RECENT MILESTONES: [Funding, data readouts, FDA actions, partnerships — last 6 months]
HEADCOUNT: [Approximate employee count — source: LinkedIn, press, SEC filing]
HEADCOUNT TRAJECTORY: [Growing / Stable / Contracting — based on job posting volume and recent news]
KEY LEADERSHIP: [CEO, CMO, CHRO, VP HR/TA — names and tenure where available]
FUNDING STATUS: [Last round, amount, lead investor, date — or "Public: [ticker]"]
LOCATION: [HQ and key sites. Note onsite/hybrid policy if known.]
```

**Sources:** Cite each data point. If web search is available, pull from company website, press releases, SEC filings, ClinicalTrials.gov. If not available, use Notion data and flag: "MANUAL RESEARCH RECOMMENDED: [specific items to verify]."

### Section 2: Open Roles — Current Hiring Footprint

Pull from Notion Jobs Database and/or web search:

| Role | Source | Days Posted | Functional Area |
|---|---|---|---|
| [Title] | [Company site / LinkedIn / Indeed] | [Approx age] | [Clinical Ops / Biometrics / PV / etc.] |

**Analysis:** Pattern the openings. Are they building a clinical ops team? Replacing departures? Scaling biometrics for a Phase III readout? This tells Bryan what pain they're hiring against.

If no roles found: "No current postings identified — may be using internal TA or have not yet posted. Discovery call should probe hiring plans."

### Section 3: Contact Profile

If a contact name/title was provided:

```
NAME: [Full name]
TITLE: [Current title]
TENURE: [Time at company — if findable on LinkedIn]
LIKELY PAIN POINTS: [Mapped from ICP persona Sarah — 3-5 specific pain points this person probably feels based on their role, company stage, and hiring footprint]
DECISION-MAKING AUTHORITY: [Likely authority level — can they sign an agency agreement, or do they need TA/procurement approval?]
PRIOR AGENCY EXPERIENCE: [If discoverable — have they worked with agencies before? Any signals?]
```

If no contact provided: "Contact TBD — generic hiring manager pain points applied. Update after identifying the decision-maker."

### Section 4: INTEL Framework Call Guide

#### I — Intro / Agenda (Mode 2 voice — consultative, warm, professional)

Opening script (2-3 sentences Bryan can adapt):

```
"[Name], appreciate you making time. I focus on [relevant functional areas] hiring for [stage]-stage biotechs — companies like [2-3 similar-stage comparables, not competitors]. Wanted to learn about what you're building and see if there's a fit."
```

**Agenda framing:** Position as a two-way evaluation, not a sales pitch. Bryan is assessing whether this is a good account, not begging for business.

#### N — Needs / Current Situation

Discovery questions (5-7, ordered from broad to specific):

1. "What does your [functional area] team look like today — headcount, structure?"
2. "Where are you in your hiring plan for [current year]?"
3. "Are you using agencies now, or has this been internal TA?"
4. [Questions tailored to open roles identified in Section 2]
5. [Questions tailored to company stage — e.g., "With [drug] moving into Phase III, how is the biometrics team scaling?"]
6. "What's been the hardest role to fill in the last 12 months?"
7. "What does your interview process look like — rounds, timeline, decision-makers?"

#### T — Threats / Pain Points

Probing questions to surface what's not working:

1. "What's your biggest hiring bottleneck right now?"
2. "How long are your open positions staying open on average?"
3. "Have you lost candidates late in process — and if so, what happened?"
4. [If they use agencies]: "What's worked and what hasn't with your current recruiting partners?"
5. [If they don't use agencies]: "What's kept you from using external recruiters?"

#### E — Explain Solutions

GQR positioning tailored to the pain points most likely for this company:

**For stretched internal TA:** "We don't send blast submittals. I specialize in [functional area] — my candidates understand [specific technical context]. You'll get 3-5 curated profiles, not 30 resumes to sort through."

**For slow time-to-fill:** "Speed is the differentiator. First InMails go out within 48 hours. I source sponsor-side candidates who understand [company stage] pace."

**For bad agency experiences:** "I get it — most agencies treat biotech like IT staffing. I can explain your clinical trial structure without a glossary. That's why my candidates don't need to be re-explained the science."

**For competitive market:** "The candidates you want are not on job boards. They're passive, employed, and getting 10 InMails a week. I know how to cut through because I speak their language."

Select the 2-3 most relevant positioning statements based on company intel.

#### L — Leadership Sign-Off / Next Steps

Close strategy options:

```
CASINO CLOSE (for hot leads — they have immediate pain):
"You mentioned [specific pain point]. I have candidates in my network right now who fit [role]. Can I send 2-3 profiles this week so you can see the caliber?"

INVESTMENT CLOSE (for warm leads — building the relationship):
"Even if timing isn't today, I'd like to stay connected. Can I send you a candidate every few weeks when I see someone who fits your pipeline stage? No commitment — just proof of concept."

INFORMATION CLOSE (for cold leads — planting the seed):
"I publish a newsletter on biopharma hiring trends — RecruitRx. Happy to add you. When timing makes sense, you'll know where to find me."
```

Recommend which close to use based on company stage and meeting type.

### Section 5: Objection Playbook

Top 3 likely objections with EQSC responses:

```
OBJECTION 1: "[Most likely objection based on company profile]"

EMPATHY: [Acknowledge without agreeing — "I hear that a lot from companies at your stage."]
QUESTION: [Probe deeper — "When you say [objection], what specifically has gone wrong?"]
SELL: [Position GQR's differentiator against the specific concern]
CLOSE: [Micro-close — "Would it help if I showed you what a curated slate looks like for a role like [their open role]?"]
```

Repeat for objections 2-3. Common objections by profile:

- **No agency budget:** "We handle everything internally"
- **Bad past experience:** "Last agency sent unqualified candidates"
- **Exclusivity demand:** "We only work with exclusive partners"
- **Fee sensitivity:** "Your fees are too high"
- **Timing:** "We're not hiring right now"

Select the 3 most probable for this company and contact.

### Section 6: Account Classification

```
RECOMMENDED CLASSIFICATION: [Owned / Team / Monitor]

REVENUE PROJECTION:
- Estimated annual placements: [X roles based on hiring footprint and company stage]
- Average fee per placement: [$XX,XXX based on role seniority and comp ranges]
- Commission rate: [100% owned / 50% team]
- Projected annual revenue to Bryan: $[XX,XXX]

DECISION FACTORS:
- [Strategic fit — does this match Bryan's ICP?]
- [Revenue threshold — owned account worthwhile at this volume?]
- [Relationship depth — is Bryan the primary contact or is this team-sourced?]
- [Time investment — discovery + ramp time vs. expected payoff timeline]

RECOMMENDATION: [1-2 sentences on why owned, team, or monitor-only]
```

### Section 7: Next Skill

- "Discovery call went well? New role identified? → Run: rapid-source [role title] at [company]"
- "Need to formalize the account? → Add to Notion Company Core with classification"
- "Ready to submit a candidate? → Run: candidate-submission [candidate] for [company]"

---

## Output Mode Toggle

**Full Package:** Default. Everything above.

**Quick Brief:** If Bryan says "quick" or "short version" — deliver Sections 1, 4 (INTEL questions only), and 6 (classification). Skip objection playbook and detailed contact profile.

---

## What This Skill Is NOT

- Not a market map. If Bryan wants competitive landscape across a therapeutic area, that's a separate request.
- Not a pitch deck. This is a call prep document, not a slide presentation.
- Not a CRM entry. Notion updates happen after the call, not before.
- Not a place to be generic. Every question, every positioning statement, every objection response must reference this specific company's situation.
