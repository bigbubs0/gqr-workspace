---
name: sentence-editor
description: "Apply Bryan's 8-rule sentence editing framework to any text. Use when Bryan says 'edit this', 'clean this up', 'sentence editor', 'polish this', 'tighten this', or pastes text that needs revision. Also trigger when any other skill produces written output — all InMails, emails, articles, and posts should pass these rules before delivery."
---

## Load Context First

Before executing this skill, read the following files from the project folder if they exist:

1. **USER.md** — who the user is
2. **BUSINESS.md** — their business and positioning

Use all context silently. Do not reference the files unless asked.

---

# Sentence Editor

Apply all 8 rules to every sentence. Preserve the author's voice and intent. Output the revised version — no explanations, no tracked changes, no rule-by-rule breakdown unless asked.

## The 8 Rules

### 1. Impact Endings
End each sentence on its strongest word. Move weak trailing phrases earlier or cut them.

**Before:** "This role offers significant growth potential for the right candidate."
**After:** "The right candidate inherits significant growth potential."

### 2. Define Before Contract
Spell out acronyms on first use, abbreviate after. Exception: audience-native abbreviations (CRA, CDM, PV for biotech audiences) need no definition.

### 3. Max Economy
Fewest words possible. No filler. Every word must earn its place.

**Before:** "I wanted to reach out to you because I think you might be a great fit."
**After:** "Your background aligns with a role worth discussing."

### 4. No Repetition
Never restate information already conveyed. If a fact appears once, it's done.

### 5. Vary Word Choice
No word appears twice in the same paragraph unless structurally unavoidable (articles, prepositions).

### 6. One Advanced Word Per Sentence Max
Keep language accessible. One precise, elevated word per sentence — not two.

### 7. Two-Comma Max
If a sentence contains 3+ commas, split it. Parenthetical clauses and list structures count.

### 8. Kill Adverbs
Replace adverbs with stronger verbs or adjectives. "Moved quickly" → "sprinted." "Really important" → "critical."

## Execution Rules

- Apply all 8 rules in a single pass. Do not iterate rule by rule.
- Preserve the author's voice. Tighten without flattening.
- If the input is already clean, say so. Do not change text that doesn't need changing.
- Output the revised text only. No preamble, no "here's the edited version," no rule annotations.
- If asked "what did you change," then itemize. Otherwise, just deliver.
