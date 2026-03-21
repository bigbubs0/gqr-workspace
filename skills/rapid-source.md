---
name: rapid-source
description: Generates Boolean search strings and Voice DNA-aligned InMails from a pasted job description for biotech/pharma recruiting. Use this skill whenever Bryan says "rapid source", "source this", "build me a search", "Boolean string", "InMail for this role", "sourcing package", "search package", or pastes a JD and asks for sourcing help. Also trigger when Bryan mentions needing to source fast, get InMails out, build a LinkedIn Recruiter project, or any combination of Boolean + outreach for a specific role. First InMail = 48hr ownership at GQR - speed matters. This skill MUST be read before generating any sourcing package.
---

# Rapid Source

## Purpose

Paste a JD. Get Boolean search strings + InMail templates calibrated to Bryan's voice, biotech expertise, and 30% acceptance rate methodology. Output is copy-paste ready for LinkedIn Recruiter.

---

## CRITICAL RULES

### Rule 1: No Narration

Do not explain what you're about to do. Do not print phase labels. Do not summarize the JD back to Bryan. Execute and deliver.

### Rule 2: Sentence Editor Rules Apply to All InMail Output

Every sentence in every InMail must pass all 8 rules:

1. **Impact endings** — end each sentence on the strongest word
2. **Define before contract** — spell out acronyms on first use, abbreviate after
3. **Max economy** — fewest words possible, no filler
4. **No repetition** — never restate information already conveyed
5. **Vary word choice** — no word appears twice in the same paragraph unless unavoidable
6. **One advanced word per sentence max** — keep language accessible
7. **Two-comma max** — if a sentence has 3+ commas, split it
8. **Kill adverbs** — replace with stronger verbs or adjectives

### Rule 3: Never Name the Client in InMails

All InMails refer to the company as "a [stage] [therapeutic area] biotech" or similar. Never reveal the company name — that's the phone call hook.

### Rule 4: Biotech-Native Language

Use abbreviations appropriate for specialist audiences: CRA, CTM, CDM, PV, CDISC, SDTM, ADaM, TFLs, BOIN, GCP, ICH, IND, NDA, BLA, EDC, CTMS, IRT, CRO, etc. Do not define these in InMails — the candidates know them. Only define in Boolean strings where LinkedIn profiles may use the spelled-out version.

### Rule 5: No "Phase 1+" Language

Bryan does not use this term. Use "Phase II/III" or "Phase II through commercial" or the specific phases relevant to the role.

### Rule 6: Respect the NOT Block

Boolean strings must include a NOT block to exclude misaligned seniority levels. If the role is Associate/Manager level, exclude Director/VP/SVP/Head. If the role is Director level, exclude VP/SVP/Chief/Associate/Coordinator.

### Rule 7: CRO Exclusion Is Context-Dependent

Do NOT blanket-exclude CRO in Boolean strings. Apply this logic:

- **Clinical Operations roles** (CRA, CTM, Clinical Outsourcing, etc.): EXCLUDE CRO. These roles require sponsor-side CRO *oversight* experience. Candidates currently at CROs are on the wrong side of the table.
- **PV / Drug Safety / Regulatory roles**: DO NOT exclude CRO. PV physicians and safety scientists transfer cleanly between sponsor and CRO. Many strong candidates spent time at IQVIA, Labcorp Drug Development, or PV-focused CROs before going sponsor-side. Excluding CRO kills a significant portion of the qualified pool.
- **Biometrics / Statistical Programming / CDM roles**: DO NOT exclude CRO. Same logic as PV - technical skills transfer directly.
- **When in doubt**: Leave CRO in. Bryan can filter manually in LinkedIn Recruiter. A false positive is better than a missed candidate.

### Rule 8: Disclose Onsite Requirements in InMails

If the role requires 3+ days onsite per week, the InMail must mention this. PV physicians, biostatisticians, and senior-level candidates have strong remote preferences post-COVID. If they read the full InMail, get interested, then learn it's 4-day onsite on the call - that's a wasted screen for both sides.

**Format:** One short clause in the value proposition section. Examples:
- "Based in South San Francisco, four days onsite."
- "Hybrid from their San Diego office - four days per week."
- "Remote-eligible with quarterly onsites."

Do NOT bury location at the end or omit it entirely. Do NOT soften it ("flexible hybrid" when the JD says 4 days). State it factually and move on. Candidates who self-select out on location save Bryan a screening call.

### Rule 9: Output Formatting and CTA Construction

**No em dashes anywhere in output.** Use a colon as the separator in Boolean angle labels and template section headers.

Correct: `CORE MATCH: Sponsor-side clinical outsourcing leaders with Phase II/III depth`
Wrong: `CORE MATCH — Sponsor-side clinical outsourcing leaders with Phase II/III depth`

**CTA sentences must end on a high-weight word.** The final word of the call-to-action is what the reader retains. Never end a CTA on "it," "week," "you," "there," or "out." End on the role descriptor, the experience term, or the outcome.

Correct: "Worth 15 minutes if you have Phase II/III outsourcing experience."
Correct: "Happy to share the full brief if you're open to a call."
Wrong: "Your CV and 15 minutes would be worth it."
Wrong: "Open to a brief call this week?"

---

## Input

Bryan pastes a JD (or describes a role verbally). May include:

- Full JD document text
- Role title + company + key requirements (shorthand)
- Additional hiring manager requirements not in the JD
- Specific constraints (location, visa, comp, contract vs perm)

If critical information is missing, ask ONE question covering all gaps. Do not ask multiple sequential questions.

---

## Output Structure

Deliver in this exact order, no headers beyond what's shown:

### 1. BOOLEAN STRINGS

Generate 3 variations. Each targets a different sourcing angle.

**Format per string:**

```
[ANGLE NAME] — [one-line description of who this catches]

[Boolean string]
```

**Construction rules:**

- Title cluster: 3-5 title variations including adjacent titles candidates may hold. Cast wider than the exact JD title.
- Skill/experience cluster: 4-6 must-have technical keywords from the JD, OR'd together in logical groups.
- Industry filter: ("biotech" OR "pharmaceutical" OR "biopharma" OR "biopharmaceutical") — apply Rule 7 for CRO inclusion/exclusion logic based on role type.
- Therapeutic/indication cluster: if the role requires specific TA experience, include disease area terms. If TA-agnostic, omit this block entirely.
- NOT block: seniority exclusions based on role level.
- No `site:` operators, no `-` operators, no quotes around single words.
- Every Boolean string must be runnable in LinkedIn Recruiter as-is.

**Angle selection guidance (pick 3 from these patterns):**

- **Core match** — tightest alignment to JD requirements
- **Adjacent title** — people doing this work under a different title
- **Sponsor-side from CRO** — catches people with CRO oversight experience on the sponsor side (if applicable)
- **Big pharma breakout** — catches people at large pharma who might want a biotech move
- **Therapeutic specialist** — leads with disease area or modality expertise over title
- **System/tool specialist** — leads with specific platform experience (Veeva, Medidata, IRT vendor, etc.)

### 2. INMAIL TEMPLATES

Generate 2 InMail templates. Each uses a different hook but follows the same structural framework.

**InMail structural framework:**

```
Subject: [6 words max — specific to the role, not generic]

[Hook — 1-2 sentences. Why you're reaching out. Reference something specific about the role that would attract this type of candidate. Do NOT open with "I came across your profile" or "Hope this finds you well."]

[Value proposition — 2-3 sentences. What makes this role worth a conversation. Include: stage of company, therapeutic area (without naming the company), what the candidate would own, why timing matters. Quantify where possible (pipeline stage, team size, growth trajectory).]

[CTA — 1-2 sentences. Ask for a brief call. Request CV if appropriate for the role level. Keep it low-friction.]

Bryan Blair
VP, Biotech & Pharma Recruiting
GQR Global Markets
```

**Template A angle:** Technical depth hook — leads with a specific skill or experience from the JD that signals Bryan understands what the work actually involves. This is the "I'm not a generic recruiter" signal.

**Template B angle:** Career trajectory hook — leads with what this role represents as a career move (scope expansion, ownership, pipeline stage upgrade, title bump, biotech transition from pharma). This is the "here's why you should care" signal.

**InMail rules:**

- Max 120 words per InMail body (excluding signature). LinkedIn truncates after ~300 characters in preview — front-load the hook.
- No exclamation points.
- No "exciting opportunity" or "thrilling" or "amazing" or any generic recruiter language.
- Hyphens, not em dashes.
- "CV" not "resume."
- One question max per InMail. Either ask for a call OR ask for a CV — not both in the same message.

### 3. FOLLOW-UP MESSAGE

One short follow-up message (40-60 words) to send 3-5 days after the initial InMail if no response. Different angle than the original. No guilt language ("just following up", "bumping this"). Add one new piece of information or reframe the value prop.

### 4. SOURCING NOTES (optional)

Only include if there's something Bryan should know that isn't obvious from the output:

- If the Boolean will return thin results, say why and suggest loosening strategy
- If the role has a known sourcing challenge (rare skill combo, location constraint, comp misalignment), flag it
- If a specific company or competitor is a prime poaching target, name it
- If the JD has contradictions or unclear requirements, flag them

Keep to 2-3 bullet points max. If nothing noteworthy, skip this section entirely.

---

## Example Interaction

**Bryan:** [pastes JD for Associate Clinical Outsourcing role at Structure]

**Claude:** [immediately outputs 3 Boolean strings, 2 InMails, 1 follow-up, and sourcing notes — no preamble, no JD summary, no narration]

---

## What This Skill Is NOT

- Not a JD rewriter. The JD is input, not output.
- Not a candidate evaluation tool. That's the submission email skill.
- Not a market map. If Bryan wants a competitive landscape, that's a separate request.
- Not a place to be cautious. Bryan knows biotech recruiting — write for an expert audience.
