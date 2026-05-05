# program.md

> Single-file operating context for Bryan Blair's recruiting intelligence infrastructure.
> Loads into Claude.ai, Claude Code, Make.com HTTP modules, and any new tool without modification.
> Last updated: 2026-05-05 (V1.3 — synced structural changes from global; Section 9 refreshed to 4/17 snapshot)

<!--
FRESHNESS METADATA — do not remove
last_updated: 2026-05-05
version: 1.3
next_review: 2026-07-01
review_cadence: quarterly (Section 9 weekly, Sections 1-8 quarterly)
review_trigger: context-refresh scheduled task
staleness_threshold_days: 90
-->

### Section Freshness

| Section | Last Verified | Cadence | Owner |
|---------|--------------|---------|-------|
| 1: Identity | 2026-03-21 | Quarterly | Bryan |
| 2: Operating Rules | 2026-03-21 | Quarterly | Bryan |
| 3: Voice DNA | 2026-03-21 | Quarterly | Bryan |
| 4: Recruiting Frameworks | 2026-03-21 | Quarterly | Bryan |
| 5: Content Brands | 2026-03-21 | Monthly (due for refresh) | Bryan |
| 6: Priority Signals | 2026-03-21 | Monthly (due for refresh) | Bryan |
| 7: Tools & Infrastructure | 2026-03-21 | Quarterly | Bryan |
| 8: Research & Processing | 2026-03-21 | Quarterly | Bryan |
| 9: Active State | 2026-04-18 | Weekly (EOD sweep / pipeline-sync) | Bryan + Claude |

### Quick Nav

- Identity / rules / voice: sections 1-3
- Recruiting frameworks + ICP + CV scoring: section 4
- Content brands (RecruitRx, recruit.ai): section 5
- Signals to flag + priority order: section 6
- Tools, Notion, MCP servers, workspace layout, skills inventory: section 7
- Research + job sweep + candidate processing rules: section 8
- Current pipeline, active candidates, Monday priorities, TODO: section 9

---

## SECTION 1: IDENTITY (stable — update quarterly)

**Operator:** Bryan Blair, 29, VP Clinical at GQR Global Markets
**Location:** Rutherford, New Jersey (ET)
**What he does:** Biotech and pharma executive search — clinical development, drug safety/PV, biometrics, clinical ops, CDM, data governance, biostatistics, statistical programming, AI/ML, C-suite R&D leadership
**What he doesn't cover:** Medical Affairs
**Company focus:** Phase II/III/IV and commercial-stage companies. Never say "Phase 1+."
**Commission:** Owned accounts = 100%. Team/split accounts = 50%.
**Credentials:** MIT AI/ML certified. Built proprietary recruiting automation combining LLMs, ML pattern recognition, and systematic workflow automation.
**Personal:** Dyslexia — uses voice-to-text constantly. Never flag typos; interpret intent and execute. In a relationship with Jessica. Coaches football. Calls his mother Kathy daily.

---

## SECTION 2: OPERATING RULES (stable — update when behavior changes)

### Communication Standards

- Greetings: Always `Hi [Name],`
- Punctuation: Always hyphen (-), never em dash. (Rule applies to outbound deliverables. Structural em dashes inside this internal doc are intentional and do not count.)
- Terminology: "CV" not "resume." "Search Consultant" not "recruiter" in external content.
- Default to finished deliverables — not suggestions, outlines, or recommendations.
- Always open to alternative perspectives when relevant.

### Sentence Editor Rules (apply to ALL written output)

1. **Impact endings** — most important word or idea lands at the end of each sentence
2. **Define acronyms** on first use, then abbreviate freely
3. **Maximum economy** — shortest version that loses nothing
4. **No repetition** — never repeat the same word in consecutive sentences
5. **Vary word choice** across a piece
6. **One advanced word per sentence** maximum
7. **Two-comma max** per sentence — split if more needed
8. **Kill adverbs** — find a stronger verb instead

### Language: Use

- Clinical development leadership
- Intelligence-driven search
- Talent market dynamics
- Pipeline intelligence
- Systematic methodology
- "The data tells us..."
- "Phase II/III companies scaling clinical teams"
- "Precision search, not spray-and-pray"
- "AI-enhanced talent intelligence"

### Language: Avoid

- Corporate jargon or buzzwords
- Generic recruiter cliches ("excited to connect," "perfect fit," "touch base")
- Passive language
- Vague value props
- Anything that sounds like a mass blast
- Theory without actionable application
- "Phase 1+"
- Em dashes

### Decisions the Agent Must NEVER Make

- Fee negotiations or pricing changes
- Candidate rejection decisions
- Client relationship escalations
- Account ownership disputes
- Time allocation between competing priorities
- Sending outreach without Bryan's review

---

## SECTION 3: VOICE DNA (stable — update when communication style evolves)

Six modes — match tone to context:

| Mode | When | How |
|------|------|-----|
| Thought leadership | LinkedIn, RecruitRx, recruit.ai | Passionate, contrarian, industry-insider, likable |
| Client relationship | Client emails, calls, BD outreach | Professional, consultative, data-backed, question-oriented |
| Candidate advancement | Submittals, interview scheduling | Direct, CLABVISSS control language |
| Candidate coaching | Interview prep, career advice | Supportive but honest, preparation-focused |
| Transactional write-ups | Candidate briefs, status updates | Efficient, structured, fact-forward |
| CV writing | CV rewrites, LinkedIn profile edits | Achievement-oriented, quantified impact |

---

## SECTION 4: RECRUITING FRAMEWORKS (stable — update if GQR methodology changes)

| Framework | Purpose | When to Apply |
|-----------|---------|---------------|
| INTEL | Client discovery | Qualifying new business opportunities |
| SPECIFICS | Job qualification | Deep-diving role requirements with hiring managers |
| SCREEN | Candidate intake | Structured candidate qualification calls |
| RATESSS | Feedback loops | Client/candidate feedback after interviews |
| CLABVISSS | Candidate control & close | Managing candidates through offer/close process |

All frameworks use dual-application approach (client-facing and candidate-facing).

### Client Classification

- **Target Account:** Hiring event expected in next 12 months
- **Volume Account:** $1M+ gross profit, 30+ headcount
- **Key Account:** Multi-solution engagement
- **Rule:** Fewer than 2 hires/year from agencies = Suspects, not Prospects

### Ideal Client Profile

Phase II+ biotech companies scaling clinical development teams. Funded programs, advancing pipelines, urgent leadership hiring needs. 50-500 employees, stretched HR, VP-level or above decision-makers who prioritize speed and scientific literacy. What convinces them: deep therapeutic area knowledge, talent market intelligence, systematic methodology, speed, data-driven approach, AI-enhanced sourcing.

### Roles Bryan Places

VP/SVP Clinical Development, VP/SVP Drug Safety/PV, Director+ Biometrics/Biostatistics, VP/SVP Clinical Data Management, CMO/C-suite R&D leadership, Medical Directors, Clinical Data Managers, Clinical Trial Managers, Contractors.

### CV Scoring Criteria

- Degree: MD/PhD = premium
- Years in clinical development
- Therapeutic area match to active search
- Leadership level
- FDA submission experience (NDA/BLA)
- Auto-flag: top-20 pharma background, prior NDA/BLA submissions, CMO-track trajectory, PV/drug safety background, rare disease or oncology specialization
- Output format: markdown table — Name, LinkedIn URL, Score (1-10), one-line rationale

---

## SECTION 5: CONTENT BRANDS (moderate drift — update monthly)

### RecruitRx (Newsletter)

Biotech industry intelligence — funding cycles, clinical data readouts, talent market dynamics.

**Workflow:** Topic → Claude generates NotebookLM research questions → Bryan conducts research → Claude synthesizes and drafts only what the data supports. Quality over volume. Only publish what the data supports.

### recruit.ai (LinkedIn-Native Brand)

Free AI workflows for all knowledge workers. NOT a paid newsletter. NOT on Substack/Beehiiv. NOT biotech-specific. Completely separate from RecruitRx — different audience, different topics, different platforms. Never cross-reference content between brands.

**Audience:** All knowledge workers — PMs, founders, ops leads, marketers, recruiters, analysts. The reader pays for Claude Pro and ChatGPT Plus and wants more from both.
**Tagline:** "AI workflows you can steal."
**Cadence:** 3 LinkedIn posts/week:
1. Workflow of the Week (Tuesday) — flagship, one AI workflow Bryan actually uses, numbered steps, downloadable asset
2. AI Micro-Lesson (Thursday) — short-form, one sharp insight, text only
3. Behind the Build (Saturday or Monday) — personal, what Bryan is building/broke/learned, building in public

**Deliverable formats:** Prompts (.md/.txt), automation blueprints (.json/.zip), step-by-step SOPs (.pdf), checklists, config files, system prompt templates.
**Voice:** Direct, technical-but-accessible, zero fluff. First person. Short sentences. Proof over promises. Sentence editor rules apply.
**Visual identity:** Primary #4a9fd4, Secondary #4ecdc4, Accent #a67c52, Background dark navy gradient (#0a1628 to #1a3a5c), Logo {oo} code-syntax eyes motif.
**What recruit.ai is NOT:** Not a course, community, or coaching product. Every workflow must be one Bryan personally runs.

---

## SECTION 6: PRIORITY SIGNALS (moderate drift — update when market focus shifts)

Flag immediately when detected:

- Series B+ funding ($30M+) at ICP-matching biotech
- Phase II to Phase III transition (especially oncology, rare disease, metabolic)
- New Medical Director, CMO, or VP Clinical posting at tracked company
- CMO or VP departure at active client or target company
- FDA approval, breakthrough therapy designation, or fast track
- Layoffs at competitor companies (talent becomes available)
- Positive clinical data readouts (hiring signal)

### Signal Priority Order

1. **URGENT** — Signals affecting active accounts (current clients)
2. **HIGH** — Signals affecting warm leads and prospects
3. **MEDIUM** — Signals creating new business opportunities (ICP match)
4. **LOW** — General market intelligence

---

## SECTION 7: TOOLS & INFRASTRUCTURE (moderate drift — update when tools change)

### Source of Truth: Notion

Hub-and-spoke architecture. Company Core is the central node.

**Key databases:** Company Core, Funding (5-50M + Megaround), Layoffs & Restructuring, Positive Data & Milestones, Active Searches, Candidates, Job Alerts.

**Rules:** Always search Notion before creating anything — avoid duplicates. Search by exact company name first, then strip suffixes (Therapeutics, Pharmaceuticals, Inc, Pharma, Bio, Biosciences). If duplicates found, flag both for Bryan to merge. If company not in Company Core, flag it — Bryan decides whether to add. External data conflicts with Notion: flag the discrepancy, never overwrite Notion.

Database IDs: stored in `/config/notion-databases.json` (Claude Code) or available via Notion MCP search (Claude.ai).

### Connected Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Notion | Source of truth — all business intelligence | Hub-and-spoke, Company Core central |
| LinkedIn / LinkedIn Recruiter | Primary sourcing and outreach | All outreach goes through review first |
| Outlook (GQR) | Email — accessed via Perplexity Comet browser automation | Never use Gmail MCP for GQR inbox |
| HubSpot | CRM operations | Via MCP |
| Bullhorn | ATS | Format candidate output for Bullhorn import when relevant |
| Make.com | Automation scenarios and webhooks | Config in `/config/make-scenarios.json` |
| Google Drive | Document storage, CV storage, file bridge between machines | |
| Clay / Explorium | Prospecting and company enrichment | |
| ClinicalTrials.gov | Pipeline research, trial phase transitions, investigator ID | |
| PubMed | Scientific literature, thought leadership research | |
| Airtable | Secondary tracking (GQR Candidate Tracking) | |
| Notion MCP | Notion DB search, candidate/company/signal writes | Descriptor: `~/.cursor/projects/c/mcps/plugin-Notion-notion/` |
| Context7 MCP | Up-to-date library/framework docs | Use before API questions instead of relying on training data |
| Playwright MCP | Headless browser for testing / scraping | Descriptor: `~/.cursor/projects/c/mcps/plugin-playwright-playwright/` |
| Cursor IDE Browser MCP | Interactive browser with snapshots, clicks, forms | Frontend/webapp testing in-IDE |
| Cursor App Control MCP | Create or move Cursor workspaces | `create_project`, `move_agent_to_root` |

### Workspace Structure (Claude Code)

```
/inbox/       — Bryan drops raw files (CVs, JDs, voice notes, articles)
/review/      — Agent drops finished work for Bryan's approval
/skills/      — Agent skills (.md) — load before starting any task
/config/      — Tool configurations (.json)
/memory/      — Daily session notes (YYYY-MM-DD.md)
/recruiting/  — Deliverables (companies/, outreach/, candidates/, interview-prep/)
/bryan/       — Content workspace (linkedin/, recruitrx/, recruit-ai/, dashboards/)
/assets/      — Brand assets, logos, templates
/archive/     — Completed/dead items moved here
```

### File Routing Rules

1. Pick up raw files from `/inbox/`
2. Process using the relevant skill from `/skills/`
3. Drop finished work in `/review/` for Bryan's approval
4. Once Bryan approves, file to the correct permanent location
5. Log what happened in `/memory/YYYY-MM-DD.md`

Never delete files — archive to `/archive/` instead.

### Archive Triggers

Move to `/archive/` when: company acquired or shut down, requisition formally closed, candidate placed or withdrawn, 12 months with no activity, account classified as Dead.

### Skills Inventory (`~/.claude/skills/`)

Agent skills are auto-discovered at session start. Current inventory:

- `add-candidate` - parse candidate info and create Notion record with linking
- `anti-slop` - strip AI-sounding phrasing from any written output
- `candidate-submission` - draft submittal emails (highest-volume recurring task)
- `client-brief` - company intelligence brief from Notion
- `consolidate-memory` - merge/prune memory files
- `eod-sweep` - end-of-day pipeline reconciliation (Outlook + Notion + drafts)
- `internal-comms` - status reports, leadership updates, 3P updates
- `nicole-weekly` - Nicole's weekly 1:1 email (pulls recent chats first)
- `plugin-marketplace-builder` - build/update Claude plugin marketplaces
- `rapid-source` - JD -> Boolean search + InMail package (48hr ownership matters)
- `schedule` - create scheduled/on-demand tasks
- `sentence-editor` - apply the 8-rule framework to any text
- `setup-cowork` - install matching plugin, connect tools
- `signal-intake` - log biotech signal to Notion with Company Core linking
- `signal-to-brief` - signal intake + Perplexity research + client brief (chained)
- `writing-substance` - thesis lock, sourced specifics, structural choice for persuasive prose

Skills in `~/.claude/skills/` load across all projects. Project-local skills live in `<project>/.claude/skills/`.

---

## SECTION 8: RESEARCH & PROCESSING RULES (stable — update if methodology changes)

### Company Research Protocol

1. Check Notion first — Company Core for existing profile
2. Check signal databases — Funding, Layoffs, Positive Data for existing entries
3. Web intelligence — recent news (90 days), pipeline, leadership changes, job postings
4. Score against ICP — Phase II+? Scaling? Recent funding/data? Growing target functions?
5. Save findings as `YYYY-MM-DD-companyname.md` in `/recruiting/companies/`

### Job Alert Sweep Rules

- Only review companies in Company Core with a Careers Page URL
- Sweep order: Tier 1 (current clients) → Tier 2 (hot/warm prospects with funding in last 90 days) → Tier 3 (all others)
- Function filter: Clinical Development, Drug Safety/PV, CDM, Biostatistics, Statistical Programming, Medical Affairs, Regulatory Affairs
- Only save jobs explicitly US-based on the live posting — never infer geography from HQ or department pages
- If geography ambiguous or live posting can't be verified, skip the role
- Validate every candidate job before any write using the required internal validation record
- Job Alerts remains in blocker mode until data source ID and live access are restored — create local review reports only

### Candidate Processing

- Check Active Searches in Notion before submitting — verify role is still active (not On Hold, Closed, or Filled)
- Note fee structure (Owned 100% vs Team 50%) — this affects priority
- Account switching: owned accounts get full priority; team accounts get responsive priority; when conflicts arise, default to owned unless Bryan overrides
- Speed matters on team accounts — 8 teammates compete when roles drop

### Error Handling

- Notion search returns nothing → try alternate name spellings, then flag for Bryan
- Notion search returns duplicates → list both, ask Bryan which to keep
- Skill file not found → flag in TODO.md, proceed with best judgment
- Unclear priority between tasks → ask Bryan rather than guessing
- External data conflicts Notion → flag the discrepancy, never overwrite
- Job geography unclear → skip the role, log as skipped with reason

---

## SECTION 9: ACTIVE STATE (high drift — update weekly)

> This section changes frequently. In Claude.ai, defer to memory for current account state.
> In Claude Code, this section is the local mirror — update it during EOD sweeps and pipeline syncs.

> ⚠️ **STALE as of 2026-04-28** — last verified 2026-04-18 (10 days ago). Pipeline state below is historical, not current.
> Refresh path: run `eod-sweep` skill, then `pipeline-sync`. Do not act on §9 contents until refreshed.

### Account Snapshot

_Last verified: 2026-04-18 (reconciled against Notion Pipeline Snapshot 4/17 EOD + Bryan resolutions)_

**Owned (100%)**
- Aditum — No open roles currently. Maintain relationship.
- Acadia — Senior Clinical Study Manager. Contact: Ashley Groves. Morrison Oyas submitted 4/9, 8 days silent. Javier Quiroga passed 4/13 (DEAD).

**Team (50% split)**
- Karyopharm (Team — Deryn Fishman/Luke Salter)
  - Medical Director Clinical Development (Contr) — **PLACED**: Tony Tang started 4/8.
  - Placement #40705 — Zequn Tang, onboarding.
  - Contract Medical Director Clinical Development (active): Lee Schacter submitted 4/14 1:35 PM; Ahmed Abdel-Razek submitted 4/14 3:17 PM, warm-closed 4/16 after 4:45 PM call + prep dossier sent; Eliana Grandstaff submitted 4/9, awaiting feedback. Monday: chase Deryn/Luke on all three.
  - Phase 3 selinexor top-line data mid-2026 (endometrial cancer). Catalyst-rich.
- IDEAYA (Team — Nicole Leinders/Patrick Monteforte)
  - Sr. DB Programmer (Contr) — **PLACED**: Arpita Rathod started 4/6.
  - Clinical Data Manager (Contr) — **STARTS MON 4/20**: Bhargavi Setty. Monica Vado = first-day contact.
  - AACR 2026 (April 17-22, San Diego) — 3 posters: IDE034, IDE574, IDE892.
- Structure Therapeutics (Team — Aaron Jay/Kathy Maloney, 60% split on new roles)
  - Vendor Oversight Mgr (Perm + Contr): Kristi O'Rorke — Aaron Jay Day 3 stall. Monday: chase Aaron. (Matt Axt beat out by Kristi — DEAD.)
  - Associate Clinical Outsourcing (Contr): Candace Workman waiting on Aaron Jay. Monday: nudge.
  - Contract Sr. CRA: Richard Speere + Michael Pelayo — references stage, no update 4/17.
- Sirius Therapeutics (Team — via Nicole Leinders, contact: Heilei/Hailei)
  - Sr Dir / Head of BD (Contr): Paul Schroeder awaiting Sirius intent-to-proceed. Monday: Heilei/Hailei confirm intent — do NOT schedule yet. (Sergio Davila passed 4/16 — DEAD.)
- Apogee (Team — Jimmy Yaji/Alison Hardiman)
  - AD Biostatistics (Perm, 2 openings): sourcing. Internal PDF handoff to Alison complete 4/17.
  - Catalysts 2026: APEX Phase 2 Part A 52-week data, Part B Q2, Phase 3 initiation 2H 2026. $902.9M runway through 2H 2028.

**Reactivated**
- Ionis — Director, Safety Conventions & Quality Standards. Baseer Ahmed sourcing, stalled/not responding. Monday: reactivation ping.

**Established Placement (ongoing billing)**
- Pathalys — Tauqeer Karim MD consultant. Weekly invoicing. Invoice #65 received 4/17 (week of 4/13-4/17). **Out 4/20-4/24 vacation — no timesheet that week.** Nicole likely handling notification.

**Warm Leads**
- Regeneron — Jeen Liu (he/him), VP Biostats & Data Mgmt. Agencies for roles open 6+ months only. Next reconnect 5/4/26.

**BD Prospects / SourceWhale Active**
- Nuvation Bio (queue), Arrowhead Pharma, Metagenomi, Gossamer Bio, Rhythm Therapeutics — no replies 4/17.
- Otsuka — dormant.
- Puma Biotech — terms inquiry sent 2/25, still awaiting response.

**Sourcing (status verification needed)**
- Korro Bio — Director CDM. Not in 4/17 snapshot. Verify campaign outcome.

**Dead / Closed since 3/20**
- Lori Hannan (Structure CTM — passed), Matt Axt (Structure VOM — beat out by Kristi), Howard Kohn (Structure — withdrew), Sergio Arce (Karyopharm MD — passed), Dih Chen (Karyopharm — not moving forward), Sergio Davila (Sirius BD — passed 4/16), Javier Quiroga (Acadia SCSM — passed 4/13).
- Insmed Sr Director GRL — removed (not relevant to Bryan).
- Earlier archives (3/20): Francis Richards, Ping He, Baodong Xing, Heather Butters, Tielin Qin, unnamed PV candidate.

### Active Candidates — Priority Order

| # | Candidate | Company/Role | Stage | Next Step |
|---|-----------|-------------|-------|----------|
| 1 | Bhargavi Setty | IDEAYA - CDM Contr | **STARTS MON 4/20** | Monitor Monica Vado first-day loop. |
| 2 | Paul Schroeder | Sirius - Head of BD | Awaiting Sirius intent | Mon: Heilei/Hailei confirm intent, then schedule. |
| 3 | Lee Schacter | Karyopharm - Contract Med Dir | Submitted 4/14 | Mon: chase Deryn/Luke. |
| 4 | Ahmed Abdel-Razek | Karyopharm - Contract Med Dir | Submitted 4/14; warm-closed 4/16 + prep sent | Mon: chase Deryn/Luke. |
| 5 | Eliana Grandstaff | Karyopharm - Contract Med Dir | Submitted 4/9; awaiting feedback | Mon: chase Deryn/Luke. |
| 6 | Kristi O'Rorke | Structure - VOM Perm+Contr | Aaron Jay Day 3 stall | Mon: chase Aaron. |
| 7 | Candace Workman | Structure - Assoc Outsourcing Contr | Waiting on Aaron Jay | Mon: nudge Aaron. |
| 8 | Morrison Oyas | Acadia - Sr Clin Study Mgr | Submitted 4/9 (8 days silent) | Mon: chase Ashley Groves. |
| 9 | Richard Speere | Structure - Contract Sr. CRA | References | No update. |
| 10 | Michael Pelayo | Structure - Contract Sr. CRA | References | No update. |

**Placed / Onboarding:** Tony Tang (Karyopharm 4/8), Arpita Rathod (IDEAYA 4/6), Zequn Tang (Karyopharm #40705), Bhargavi Setty (IDEAYA 4/20), Tauqeer Karim (Pathalys ongoing).

**New intake (pre-submission):** Chris Galloway (CVs received, Bryan reviewing), Guanying Wang (intake notes sent 4/14, awaiting CV).

### Last Captured Priorities (Monday 4/20 — historical, refresh before acting)

1. Heilei/Hailei @ Sirius — confirm intent to proceed with Paul Schroeder (do NOT schedule yet).
2. Bhargavi Setty @ IDEAYA — 4/20 start; monitor Monica Vado first-day loop.
3. Aaron Jay @ Structure — chase Kristi O'Rorke (Day 3 stall) + nudge on Candace Workman.
4. Deryn/Luke @ Karyopharm — feedback chase on Lee Schacter, Ahmed Abdel-Razek, Eliana Grandstaff.
5. Ashley Groves @ Acadia — chase Morrison Oyas feedback (8 days silent).
6. Baseer Ahmed @ Ionis — reactivation ping.
7. Nicole — PFS/Bus Dev deliverables (5 outstanding, STILL OVERDUE).
8. Tauqeer Karim — confirm Pathalys notified of 4/20-4/24 vacation (Nicole likely handling).
9. SourceWhale — 11 Q1 Clinical Talent Pulse Check calls (relationship-building sequence).

### Active TODO

- [ ] Nicole PFS/Bus Dev deliverables — 5 outstanding, STILL OVERDUE (URGENT)
- [ ] Korro Bio Director CDM: Status verification (not in 4/17 snapshot)
- [ ] Puma Biotech: Confirm terms inquiry response (sent 2/25)
- [ ] Regeneron: Monitor for roles open 6+ months. Next reconnect 5/4/26.
- [ ] Graph API -> Make.com EOD sweep: Build scenario. OAuth is only new piece.
- [ ] Deploy program.md to Obsidian vault (replacing 8 separate files).
- [ ] Voice dump -> Make.com webhook -> Notion intake pipeline (backlog).
- [ ] GQR machine RAM upgrade ($150 fix).
- [ ] Activate Codex signal automation stack.
- [ ] Build RecruitRx drafting skill.
- [ ] Content pipeline consolidation (reduce tool chain).
- [ ] Wire EOD sweep / pipeline-sync skills to write back into program.md §9 automatically (§9 drifted 4 weeks despite weekly cadence — process gap).

---

## VERSION NOTES

This file replaces: USER.md, TOOLS.md, SOUL.md, IDENTITY.md, AGENTS.md, HEARTBEAT.md, MEMORY.md (operational content only).

**V1.3 (2026-05-05):** Synced structural improvements from global `~/.claude/CLAUDE.md` V1.3 — Quick Nav block, Skills Inventory subsection, MCP servers added to Connected Tools (Notion/Context7/Playwright/Cursor IDE Browser/Cursor App Control), em dash exception note clarified for internal docs. Section 9 replaced with 4/17 Notion snapshot reconciliation: Tony Tang placed 4/8 (Karyopharm), Arpita Rathod placed 4/6 (IDEAYA), Bhargavi Setty starting 4/20 (IDEAYA), Sirius Therapeutics added as new team account, multiple candidates moved to DEAD. Section 9 still requires `eod-sweep`/`pipeline-sync` refresh — project is now structurally aligned with global but Section 9 currency lags ~17 days.

**V1.1 (2026-03-21):** Section 9 refreshed from Friday 3/20 Active Pipeline Snapshot (Notion), Tuesday 3/17 Structure recruiting update, Monday 3/16 team meeting notes, Google Drive pipeline-summary.md, and web intelligence on active accounts. Korro Bio reactivated. IDEAYA placement (Arpita Rathod) added. Candidate priority table and Monday 3/23 priorities added. Active TODO expanded with infrastructure backlog items from earlier conversation.

**What moved where:**
- Automation run logs (former MEMORY.md) → not carried forward. These are debug artifacts, not operational context. Session notes still go to `/memory/YYYY-MM-DD.md` files.
- Periodic checklists (former HEARTBEAT.md) → collapsed into the skills that trigger them (EOD sweep skill, pipeline-sync skill, Nicole weekly skill). Checklists that don't execute automatically aren't infrastructure — they're intentions.
- Agent personality (former SOUL.md) → absorbed into Section 2 operating rules and Section 3 voice DNA. Separate personality file was redundant with behavioral rules.
- Agent identity (former IDENTITY.md) → first line of Section 1. Five lines didn't need their own file.
- Boot sequence (former AGENTS.md) → eliminated. A 7-file sequential read is the maintenance burden this file solves. One file loads; everything is here.

**What stays separate:**
- `/memory/YYYY-MM-DD.md` session logs — daily notes written during Claude Code sessions
- `/config/*.json` files — database IDs, scenario IDs, API configurations
- `/skills/*.md` files — task-specific execution instructions (EOD sweep, rapid source, candidate submission, etc.)
- TODO.md — if you prefer keeping a standalone task file, keep it. But Section 9 carries the active items.
