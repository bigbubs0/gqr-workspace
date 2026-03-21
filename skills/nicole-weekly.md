---
name: nicole-weekly
description: "Draft Nicole's weekly 1-on-1 email. Use when Bryan says 'Nicole email', 'Nicole 1-on-1', 'weekly update for Nicole', '1:1 prep', or any reference to drafting his weekly internal update for his manager. This skill MUST pull recent chats first — never guess or reconstruct from memory."
---

## Load Context First

Before executing this skill, read the following files from the project folder if they exist:

1. **USER.md** — who the user is

Use all context silently. Do not reference the files unless asked.

---

# Nicole Weekly 1-on-1 Email

## Purpose

Produce a weekly working note from Bryan to Nicole (his manager) that reconstructs the week from actual conversations, covers every active account with real activity, and surfaces items that need Nicole's input or action.

---

## CRITICAL RULES — Non-Negotiable

### Rule 1: Pull Recent Chats First

Before writing a single word, pull the last 7 days of conversation history using the recent chats tool. Paginate through all available conversations for the period. This is the primary source material.

Every submittal Bryan writes goes through Claude first. Every interview prep, every feedback email, every BD outreach. The receipts are in the chat history. Use them.

If a detail isn't in the chat history, Notion, or Bryan's current-session context, it does not go in the email. Do not guess. Do not reconstruct from memory.

### Rule 2: No Account Ownership Labels

Never write "owned account," "team account," "50% split," "60% split," "Aaron's account," "Ali's account," or any variation. Nicole knows the account structure. These labels make the email read like a pipeline report to a stranger instead of a working note between colleagues.

### Rule 3: Working Note Tone

This is not a formal report. Not an executive summary. It reads like a sharp, direct update between two people who share full context. Bryan's natural voice — no corporate stiffness, no over-explanation.

### Rule 4: Nicole Already Has Context

Bryan and Nicole communicate throughout the week via Teams. By the time this email lands, Nicole already knows many of the details. The email confirms shared understanding, synthesizes the week, and surfaces action items — it does not re-explain things Nicole already lived through.

**This means:** If Bryan and Nicole already discussed a candidate situation in detail during the week, the email line can be short — even one sentence. The email is a reference document for Monday's call, not a first-time briefing.

### Rule 5: Paragraph Density Scales With Novelty

- **New intel Nicole hasn't seen** → full paragraph (2-4 sentences). Interview results, new submittals, strategic bottlenecks, candidate control updates.
- **Status Nicole already knows from Teams** → one line. "Heather Butters — fingers crossed they extend an offer."
- **Waiting on someone else** → one line with the ask. "Peter Kim — still no read from Ekaterina. Can you follow up?"

Do not pad short statuses into full paragraphs. Do not compress genuinely complex updates into one line. Match the density to the novelty.

### Rule 6: No Narration

Do not print "searching chats..." or "reconstructing the week..." or any status updates. Pull the data, build the email, deliver it.

### Rule 7: Sentence Editor Rules Apply

All 8 rules apply to every sentence:

1. Impact endings
2. Define before contract
3. Max economy
4. No repetition
5. Vary word choice
6. One advanced word per sentence max
7. Two-comma max
8. Kill adverbs

---

## Execution Sequence

### Step 1: Gather

1. Pull last 7 days of recent chats (use recent_chats tool, paginate with n=20 and date filters until the full week is covered)
2. Search for any account-specific conversations that may have been missed (use conversation_search for active account names)
3. Check Notion Pipeline Snapshot for current state if Notion MCP is connected
4. Note Bryan's current-session context for anything he's mentioned today

### Step 2: Reconstruct

From the gathered material, extract:

- Submittals sent — candidate name, role, company, date
- Interviews scheduled or completed — candidate, company, role, date, outcome
- Feedback received or pending — what came back, what's outstanding
- Offers, rejections, or candidate control situations
- BD activity — outreach, responses, new leads, new roles
- Placements or starts — fee implications
- Dead processes — anything that died this week and why
- Items needing Nicole's input

### Step 3: Draft

Use the email format below. Read through once for Sentence Editor compliance before delivering.

---

## Email Format

```
Subject: 1:1 Prep - [Date of next 1:1, e.g., 3/17]

Hi Nicole,

Ahead of [day].

[COMPANY NAME]

[Candidate/role updates. One paragraph per candidate situation. Short
statuses get one line. Complex situations get 2-4 sentences. Lead with
what changed this week and what happens next.]

[Next COMPANY NAME — repeat for each company with activity this week.
Order by activity level, most active first.]

[OTHER ITEMS — optional section for activity that doesn't fit under a
company header: BD warm leads, cross-team shoutouts, tool wins, market
observations. Only include if there's something worth mentioning.]

What I Need From You

- [Specific ask — name + what you need Nicole to do]
- [Specific ask]
- [Specific ask]

Bryan
```

---

## Section Rules

**Company sections:**
- Only include companies where something happened this week (submittal, interview, feedback, offer, new role, BD response, candidate movement)
- Do not include companies with zero activity just to show they exist
- Within each company, organize by candidate — most actionable first
- One paragraph per candidate situation unless it's a one-liner

**Candidate paragraphs — what to include:**
- Current status and what changed this week
- What happens next (interview date, feedback pending, offer timeline)
- Candidate control intel when relevant (competing offers, decision variables, enthusiasm level, risk of losing them)
- Strategic context when it matters ("She's the archetype that moves fast when excited and cools quickly when stalled")

**Candidate one-liners — when to use:**
- Nicole already knows the full context from Teams
- Status is simply "waiting" with nothing new
- Status is binary (submitted, no feedback yet)

**Team callouts:**
- Reference colleagues naturally when relevant ("Want to shout out Ali — she's been very helpful getting relevant info for this search")
- Never label their role or account ownership
- Patrick, Aaron, Ali, and other names flow as context, not org chart entries

**Other Items section:**
- BD activity that doesn't belong under an active account (Regeneron warm lead, new prospect outreach)
- Cross-team wins or collaboration notes
- Tool or process wins worth flagging
- Market observations relevant to pipeline strategy
- Skip this section entirely if nothing falls outside the company headers

**What I Need From You:**
- Dashes or numbers — either format works
- Each item: name + specific action Nicole can take or decision she can make
- Not "let's discuss Structure" — instead "Ekaterina's feedback on Peter Kim"
- Include enough context that Nicole can prepare a response before the call
- 2-5 items typical. If the week was clean, this section can be short

**What to exclude:**
- Accounts with no activity this week
- Candidates Bryan has already marked as dead or archived (unless they died THIS week)
- Routine administrative tasks unless they're blocking something
- Details Nicole already received via separate email this week (unless there's a new development)
- Confidence scores, BITA counts, signal analysis, or any system-generated metadata

---

## Quality Check Before Delivery

1. Every candidate name must trace to a chat from the last 7 days, Notion, or Bryan's current-session context
2. Every status claim must match what actually happened — no upgrading "Bryan mentioned he might submit" to "submitted"
3. No account ownership labels anywhere
4. Short statuses are genuinely short (one line). Complex updates are genuinely detailed. No middle-ground padding
5. "What I Need From You" items are actionable — Nicole can do something with each one
6. Full Sentence Editor pass on the complete email

---

## What This Skill Is NOT

- Not a pipeline dashboard. Nicole has Notion for that.
- Not a first-time briefing. Nicole lives in this pipeline daily.
- Not a performance review. Skip self-assessment unless Bryan asks for it.
- Not a daily log. Synthesize the week into what matters for Monday.
- Not a place to pad. Quiet week = short email. That's fine.
