---
name: recruitrx-draft
description: "Draft RecruitRx newsletter issues on biotech industry intelligence — funding cycles, clinical data readouts, talent market dynamics. Use when Bryan says 'RecruitRx draft', 'recruitrx', 'newsletter draft', 'draft the newsletter', 'NotebookLM questions for [topic]', or supplies a topic plus research data for synthesis. Two-mode skill: generate NotebookLM research questions for a topic, or synthesize Bryan's research into a finished issue."
---

## Load Context First

Before executing this skill, read the following files from the project folder if they exist:

1. **USER.md** — who the user is
2. **BUSINESS.md** — their business and positioning

Use all context silently. Do not reference the files unless asked.

---

# RecruitRx Drafting

Two-mode skill. Mode is auto-detected from input.

| Mode | Trigger | Output |
|------|---------|--------|
| **A — Question Pack** | Topic only, no research data attached | NotebookLM research question set Bryan can paste into NotebookLM |
| **B — Synthesis** | Topic + research findings (pasted text, NotebookLM exports, PDFs, URLs with extracted content) | Finished newsletter draft |

If the input is ambiguous (a topic with light context that could be either), ask ONE question: "Generate NotebookLM questions for this topic, or do you have research ready to synthesize?"

---

## CRITICAL RULES

### Rule 1: Only Publish What the Data Supports
RecruitRx's editorial standard is quality over volume. If the research does not support a claim, cut it. Never fill gaps with general industry knowledge, training-data recall, or plausible-sounding inference. A short, defensible issue beats a long, padded one.

### Rule 2: Voice Mode — Thought Leadership
Apply the Section 3 thought-leadership mode: passionate, contrarian, industry-insider, likable. Bryan is writing as a working biotech executive search consultant who sees the talent market from inside the deals, not as a journalist summarizing headlines.

### Rule 3: Sentence Editor 8 Rules Apply
Every prose sentence must pass: impact endings, define-then-abbreviate, max economy, no repetition, varied word choice, one advanced word per sentence, two-comma max, kill adverbs.

### Rule 4: Biotech Terminology Discipline
- "CV" not "resume"
- "Search Consultant" not "recruiter" in external prose
- "Phase II/III/IV" — never "Phase 1+"
- Hyphen (-), never em dash
- Define acronyms on first use (FDA, NDA, BLA, PV, CDM, CRO, MoA), then abbreviate freely. Skip definitions only for audience-native terms an MD/PhD biotech reader would know cold (Phase II, MoA in a mechanism context).

### Rule 5: No Cross-Brand Leakage
RecruitRx and recruit.ai are separate brands with separate audiences. Never reference recruit.ai workflows, AI-prompt deliverables, or "AI workflows you can steal" tagline inside a RecruitRx draft. RecruitRx readers come for biotech talent market intelligence, not AI tooling.

---

## Inputs

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| topic | string | required | The issue's central question or thesis (e.g. "What does the GLP-1 wave mean for clinical development hiring?") |
| research | string/files | required for Mode B | Pasted NotebookLM output, source articles, PubMed abstracts, ClinicalTrials.gov data, funding reports, layoff trackers |
| angle | string | optional | Bryan's specific take or contrarian framing if he has one in mind |
| length | enum | optional | `short` (~400 words), `standard` (~700 words, default), `deep` (~1100 words) |

---

## Mode A: NotebookLM Question Pack

### When to Run
Bryan provides a topic with no source material attached, or explicitly asks for "NotebookLM questions for [topic]."

### Execution

Build 8-12 questions structured to surface the data RecruitRx needs. Each question must be specific enough that NotebookLM (or any RAG tool) can answer from sources rather than hand-waving.

**Question categories — include at least one from each:**

1. **Quantitative ground truth** — funding totals, headcount changes, trial counts, approval dates, layoff numbers. Specific time windows (last 12 months, YTD, Q4 2025).
2. **Pipeline and clinical context** — which programs advanced, which readouts hit or missed, what mechanisms or modalities are concentrating capital.
3. **Leadership and talent movement** — CMO/VP appointments and departures, headcount shifts at named companies, function-level scaling.
4. **Competitive and structural dynamics** — which therapeutic areas or modalities are absorbing the people, which are shedding them.
5. **Contrarian or counter-narrative angles** — what's the consensus story, what does the data actually show, where does the conventional wisdom break down.

**Question construction rules:**

- Name companies, drugs, indications, or time windows explicitly. "How many Phase II oncology trials launched in 2025?" beats "What's happening in oncology?"
- Force specificity. "Which top-20 pharma companies announced clinical development restructurings between Q3 2025 and Q1 2026?" beats "Are big pharmas downsizing?"
- Include at least one question that tests the contrarian angle if Bryan supplied one.
- Avoid yes/no framing — questions should produce data, not confirmations.

### Output Format (Mode A)

```markdown
# RecruitRx Research Questions — [Topic]

**Working thesis:** [One sentence capturing the issue's central claim. If Bryan supplied an angle, use it. Otherwise, derive from the topic.]

**Paste into NotebookLM after loading sources (suggested sources at bottom).**

## Ground Truth & Numbers
1. [Question]
2. [Question]

## Pipeline & Clinical Context
3. [Question]
4. [Question]

## Talent & Leadership Movement
5. [Question]
6. [Question]

## Competitive Dynamics
7. [Question]
8. [Question]

## Contrarian Probes
9. [Question]
10. [Question]

---

## Suggested Sources to Load in NotebookLM
- BioPharma Dive / Endpoints / Fierce Biotech coverage of [topic] in last 90 days
- ClinicalTrials.gov searches for [relevant indication or sponsor list]
- PubMed abstracts on [mechanism or readout]
- Quarterly funding reports (BIO, SVB, Pitchbook) if topic touches capital
- Layoffs.fyi or company press releases if topic touches restructuring
- 10-Ks or S-1s for named companies if topic touches a specific issuer
```

**File output:** Save to `/bryan/recruitrx/research-questions/YYYY-MM-DD-[topic-slug].md` and confirm location to Bryan in one line.

---

## Mode B: Newsletter Synthesis

### When to Run
Bryan supplies research findings (NotebookLM output, pasted source data, attached PDFs/articles). The synthesis goes from data → finished issue in one pass.

### Pre-Synthesis Check

Before drafting, audit the research for sufficiency:

| Element | Required? | If missing |
|---------|-----------|------------|
| At least 3 specific data points (numbers, named companies, dated events) | Yes | Stop. Tell Bryan: "Research is thin on specifics. Need [X, Y, Z] before drafting." Do NOT pad with generic claims. |
| A clear talent-market angle | Yes | Ask Bryan: "I see the science/funding data but the talent-market through-line isn't obvious. What's the hiring implication you want to land?" |
| At least one company by name | Yes | Stop and request specifics |
| Source attribution traceable (citation, URL, or NotebookLM source ref) | Strongly preferred | Note in draft: claims without traceable sources get flagged for Bryan to verify before publish |

The pre-synthesis check protects the "only publish what the data supports" rule. A weak research pass produces a weak issue — flag it instead of writing through it.

### Execution

Draft the issue using the output format below. Apply these synthesis rules:

1. **Lead with the talent-market read, not the science.** RecruitRx readers come for hiring intelligence. Science context exists to support the talent-market claim, not the other way around.
2. **Quantify everything possible.** Funding totals, headcount, trial counts, approval rates. Numbers earn trust.
3. **Name companies.** Vague "biotech is hiring more biostatisticians" claims are worth nothing. "Apogee, Structure, and IDEAYA each opened biostats requisitions in Q1 2026" is the standard.
4. **One contrarian beat per issue.** What's the consensus story, and where does the data complicate it? This is the RecruitRx differentiator.
5. **Close with a hiring implication.** What does the reader — a biotech operator or talent leader — do with this?

### Output Format (Mode B)

```markdown
# RecruitRx — [Issue Title]
*[Subhead: one-line teaser, ~10 words, lands on the implication.]*

**Date:** [today]
**Length target:** [short / standard / deep]

---

## The Read
[2-3 sentences. The thesis up top. Most important word lands at end of the final sentence. This is the claim everything below defends.]

---

## What the Data Shows

[3-5 paragraphs of evidence. Each paragraph anchors on a specific data point: a number, a named company, a dated event. Cite sources inline where possible — (BioPharma Dive, 3/14/26) or (ClinicalTrials.gov, NCT0XXXXXX). Sentence editor rules apply throughout.]

[If using subsections, use H3 headers — Funding, Pipeline, Talent Flow, etc. Otherwise flow as continuous prose.]

---

## The Contrarian Beat
[1-2 paragraphs. What does the consensus narrative say? What does the data actually show? This is where Bryan's industry-insider voice carries the issue. No hedging. If the data supports a contrarian read, state it directly.]

---

## What This Means for Hiring
[2-4 specific implications for biotech operators and talent leaders. Use a bulleted list if the implications are parallel; use a short paragraph if they build on each other.]

- [Implication tied to a specific function — Clinical Development, Drug Safety/PV, Biometrics, CDM, etc.]
- [Implication tied to a specific company stage or geography]
- [Implication tied to compensation, sourcing strategy, or pipeline timing]

---

## Sources
- [Source 1 with URL or citation]
- [Source 2]
- [...]

[If any claim in the draft is not source-backed, flag it explicitly:
> ⚠️ The claim that [X] is not directly source-backed in the research. Verify before publish.]
```

**File output:** Save to `/review/YYYY-MM-DD-recruitrx-[topic-slug].md` for Bryan's approval. Once Bryan approves, file to `/bryan/recruitrx/issues/YYYY-MM-DD-[topic-slug].md`.

---

## Validation

Run these checks before delivering a Mode B draft:

1. **Source-backing check** — every quantitative claim (numbers, dates, named events) traces to a research input. Flag any that don't.
2. **Named-company check** — at least three named companies appear in the body. Generic "biotech companies" or "many pharmas" doesn't count.
3. **Talent through-line check** — the "What This Means for Hiring" section ties back to at least one claim in "What the Data Shows." No standalone hiring opinions.
4. **Sentence editor pass** — scan for em dashes, "Phase 1+", "resume," adverbs, three-comma sentences, repeated words within paragraphs. Fix before delivery.
5. **Cross-brand check** — no recruit.ai references, no AI-workflow framing, no `{oo}` motif.
6. **Length check** — short ≤450 words, standard 600-800, deep 1000-1200. Trim or expand to land in band.

If any validation fails, fix in-pass before showing Bryan. Do not deliver a draft that knowingly fails a check.

---

## What This Skill Is NOT

- Not a LinkedIn post drafter — that's a separate skill (recruit.ai content is its own pipeline)
- Not a market map or full competitive landscape report
- Not a candidate outreach drafter
- Not a research tool — research is done by Bryan in NotebookLM; this skill prepares the question pack and synthesizes the answers
- Not a publishing tool — output goes to `/review/` for Bryan to approve and publish manually
