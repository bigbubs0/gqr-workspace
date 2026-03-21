---
name: interview-prep
description: "Generate candidate interview prep docs. Use when Bryan says 'prep doc', 'interview prep', 'prep for interview', 'prep sheet', 'brief the candidate', or provides a candidate profile and JD for an upcoming interview. Pulls science context, company pipeline, and role-specific talking points into a structured briefing the candidate can study."
---

## Load Context First

Before executing this skill, read the following files from the project folder if they exist:

1. **USER.md** - who the user is
2. **BUSINESS.md** - their business and positioning

Use all context silently. Do not reference the files unless asked.

---

# Interview Prep Doc

## Input

Bryan provides some combination of:
- **Candidate profile** - CV, LinkedIn, screening notes, or verbal summary
- **Job description** - full JD, role title + company, or link to Active Search in Notion
- **Client intel** - pipeline data, recent signals, science context, interviewer names
- **Interview logistics** - date, time, format (phone/video/onsite), interviewer(s)

### Gathering Missing Context

1. **If company name is provided**: Search Notion Company Core for the company. Pull therapeutic areas, pipeline stage, recent signals (positive data, funding, layoffs). Search Positive Data & Milestones for clinical readouts, trial names, mechanisms of action.
2. **If an Active Search exists**: Search Notion Active Searches for the role. Pull function, level, status, any linked candidates or notes.
3. **If critical info is missing** (no candidate background AND no JD): Ask ONE question covering all gaps.

### Rule: Never Produce a Half-Built Doc

The prep doc requires three inputs to be complete: candidate background (CV, screening notes, or verbal summary), role details (JD or Notion Active Search data), and company context (Notion or public).

If candidate background is missing or the Notion candidate record has no CV details:
- STOP before building the fit mapping table or gap analysis
- Output one line: "Need [Candidate Name]'s CV or screening notes to complete the fit mapping and gap analysis. Paste below."
- Do NOT produce the doc with placeholder brackets like "[Needs background]" or "[Cannot assess]"
- Once Bryan provides the data, produce the complete doc in one pass

The science cheat sheet, company context, and interview questions CAN be drafted without candidate data - but the full doc is not delivered until all three inputs are present. If Bryan explicitly says "just do the company/science sections for now," honor that. Otherwise, gate on completeness.

A prep doc with blank fit mapping is worse than no prep doc. It signals to the candidate that the recruiter didn't do the work.

---

## Output Format

Produce a complete, ready-to-send prep doc. No preamble. Use this structure:

```
# Interview Prep - [Candidate Name]
## [Role Title] | [Company Name]
**Date:** [interview date if known]
**Format:** [phone/video/onsite]
**Interviewer(s):** [names and titles if known]

---

## About [Company Name]

[2-3 sentences: what the company does, therapeutic focus, stage (Phase 1/2/3), modality. Ground this in specific pipeline data - lead programs, recent readouts, mechanism of action. This is the science depth that differentiates Bryan's prep docs.]

**Recent Signals:**
- [Most recent signal - funding, data readout, restructuring, with date]
- [Second most recent if available]

---

## The Role

[Concise summary of what this role owns and why it exists now. Connect to company stage - are they scaling for Phase 3? Building out PV post-approval? Expanding biometrics for multiple trials?]

**Key Requirements:**
- [Top 3-5 requirements from JD, prioritized by what the hiring manager likely weights highest]

---

## Your Fit

Build a table mapping every key requirement from the JD to the candidate's specific experience. This is the core value of the prep doc - it gives the candidate a cheat sheet for connecting their background to what the company needs.

| Requirement | Your Experience | Strength / Gap |
|-------------|----------------|----------------|
| [From JD]   | [Specific example from CV/notes - company name, program, outcome] | Strong / Partial / Gap |

**Table rules:**

1. **"Your Experience" column must cite specifics.** Not "extensive Phase 3 experience" - instead "Led 3 Phase III protocols at Gilead (GS-9973, GS-4059) from first-patient-in through NDA submission." Pull from the CV.

2. **Mark gaps honestly.** If the candidate lacks a requirement, mark it as "Gap" and add a row to the gap analysis section below with suggested framing. Candidates who walk in knowing their gaps and how to address them outperform candidates who get surprised.

3. **Distinguish "strong match" from "adjacent match."** If the JD asks for myeloma experience and the candidate has lymphoma experience, that's adjacent - not a gap, but not a direct hit. Note it as "Partial - lymphoma, not myeloma. Frame as: heme-onc mechanism overlap, similar trial design considerations, patient population parallels."

### Potential Gaps & Suggested Framing

For each gap or partial match identified in the table:

**Gap: [Requirement they don't fully meet]**
Reality: [What they actually have]
Frame as: [How to position this in the interview - pivot to adjacent strength, acknowledge the gap and show learning trajectory, or reframe the requirement]
Red line: [If this gap is likely a dealbreaker, say so. "This may be a hard stop if the hiring manager requires direct XYZ experience. Confirm with Bryan before the interview."]

Do not sugarcoat gaps. A candidate who walks into an interview unaware of a gap gets blindsided. A candidate who walks in with a prepared reframe demonstrates self-awareness and strategic thinking.

---

## Questions to Prepare For

Generate 5-7 interview questions. Each question must be specific to THIS candidate at THIS company - not role-generic prompts any candidate would receive.

**Construction rules:**

1. **Mine the candidate's background for probe points.** Read the CV and screening notes for: career transitions, gaps, therapeutic area shifts, title changes, company stage changes (pharma to biotech or vice versa), and any unusual patterns. Interviewers notice these and will ask about them.

2. **Frame questions from the interviewer's perspective.** Don't write "Tell me about your experience with X." Write what the interviewer is actually trying to learn: "You spent 8 years at [Large Pharma] before moving to [Small Biotech] - they'll likely probe whether you can operate without the infrastructure you had. Prepare a specific example of building something from scratch: a trial, a team, a process."

3. **Connect candidate history to company needs.** If the candidate's myeloma experience is at a different pipeline stage than the company's current program, that's a question. If the candidate managed a 50-person team and this role manages 5, that's a question. Surface the deltas - those are where interviews get hard.

4. **Include at least one science question calibrated to the candidate's depth.** If the candidate is an MD with deep mechanism knowledge, the science question should be sophisticated (biomarker strategy, translational endpoints). If the candidate is operationally focused, the science question should test whether they can hold their own in a scientific discussion without defaulting to generic answers.

5. **Include one motivation question that's hard to fake.** Not "why are you interested in this company" - instead, reference something specific: "You've built your career in [therapeutic area X] and this role is in [therapeutic area Y]. What's driving the pivot?" Force the candidate to articulate a real answer.

**Question format:**

For each question, provide three components:

**[Question text - written as the interviewer would phrase it]**

What they're really evaluating: [One sentence explaining the underlying competency or concern being tested. This is the meta-layer that helps the candidate understand WHY the question is being asked, not just WHAT is being asked.]

How to prepare: [2-3 sentences of specific guidance. Reference the candidate's actual experience - "Your work on [specific project/trial] at [company] is your strongest example here." Point them to the right story from their own career, and flag what to emphasize.]

**What NOT to do:**
- No generic behavioral questions ("Tell me about a time you showed leadership")
- No questions that could apply to any candidate for any Med Director role
- No questions without the evaluation layer - if you can't articulate what the interviewer is testing, the question isn't useful

---

## Questions You Should Ask

1. [Question about team structure, reporting line, or growth trajectory]
2. [Question about the specific program or pipeline they'd work on]
3. [Question about company milestones or upcoming catalysts]
4. [Question that demonstrates you've researched their science]

---

## Company & Science Cheat Sheet

[Quick-reference section with key terms, trial names, drug names, mechanisms, competitors, and recent milestones. Candidate should be able to scan this 5 minutes before the call and sound informed.]

- **Lead program(s):** [drug name - indication - phase]
- **Mechanism:** [MOA in plain language]
- **Key trial(s):** [trial name(s) if known]
- **Recent milestone:** [most notable recent event]
- **Competitors:** [1-2 companies in same space if known]

---

## Logistics & Next Steps

- [Interview date/time if known]
- [Format and platform if known]
- [Bryan's contact for day-of questions]
- [Reminder: research the interviewer on LinkedIn before the call]
```

---

## Rules

1. **Science depth is the differentiator.** Generic prep docs add no value. Every prep doc must include specific pipeline, trial, or mechanism context for the company. If Notion has signals, use them. If not, note the gap.
2. **Map candidate to role explicitly.** The "Your Fit" table is mandatory. Candidates need to see their experience mapped to what the client wants.
3. **Anticipate the hard questions.** If there's a gap (therapeutic area switch, title step-up, short tenure), address it in "Potential Gaps" with suggested framing.
4. **Keep it scannable.** Candidates review these the morning of the interview. Headers, bullets, tables - no walls of text.
5. **Apply Sentence Editor 8 rules** to all prose sections.
6. **Tone: candidate coaching voice.** Supportive but honest, preparation-focused. Not salesy.
7. **No fluff.** Every sentence should help the candidate perform better in the interview.
