# TOOLS.md - Environment & Tools

## Workspace Structure

```
/inbox/       - Bryan drops raw files here (CVs, JDs, voice notes, articles)
/review/      - Agent drops finished work here for approval
/skills/      - Agent skills (.md) - load before starting any task
/config/      - Tool configurations (.json) - check before API calls
/memory/      - Daily session notes (YYYY-MM-DD.md)
/recruiting/  - Deliverables (companies/, outreach/, candidates/, interview-prep/)
/bryan/       - Content workspace (linkedin/, recruitrx/, recruit-ai/, dashboards/)
/assets/      - Brand assets, logos, templates
/archive/     - Completed/dead items moved here
```

---

## Connected Tools

### Notion (Source of Truth)
- **Purpose:** All business intelligence - companies, signals, candidates, active searches
- **Architecture:** Hub-and-spoke with Company Core as central node
- **Database IDs:** See `/config/notion-databases.json`
- **Key databases:** Company Core, Funding (5-50M + Megaround), Layoffs, Positive Data, Active Searches, Candidates, Job Alerts
- **Rules:** Always search before creating. Strip company name suffixes when searching. Use data source IDs for page creation.

### LinkedIn
- **Purpose:** Primary sourcing and outreach channel
- **Usage:** Candidate identification, InMail outreach, company research, thought leadership
- **Rules:** All outreach goes through `/review/` first. Use outreach-drafter skill.

### HubSpot
- **Purpose:** CRM operations
- **Usage:** Contact management, deal tracking, activity logging
- **Access:** Via MCP tools

### Bullhorn
- **Purpose:** Applicant Tracking System (ATS)
- **Usage:** Format candidate output for Bullhorn import when relevant (CSV, standard fields)

### Airtable
- **Purpose:** Secondary tracking (GQR Candidate Tracking)
- **Usage:** Supplementary pipeline data

### Make.com
- **Purpose:** Automation scenarios and webhooks
- **Config:** See `/config/make-scenarios.json`
- **Usage:** Automated workflows connecting tools

### Codex Scheduled Automations
- **Purpose:** Recurring research and synthesis tasks that write review-first outputs
- **Config:** See `/config/signal-automations.json` and `/config/signal-health-manifest.json`
- **Usage:** Morning signal radar, urgent account alerts, opportunity matching, weekly market board

### Google Drive
- **Purpose:** Document storage and retrieval
- **Usage:** Client deliverables, shared documents, CV storage

### Clay / Explorium
- **Purpose:** Prospecting and company enrichment
- **Usage:** Data enrichment for target companies and candidates

### ClinicalTrials.gov
- **Purpose:** Pipeline research
- **Usage:** Trial phase transitions, investigator identification, company pipeline verification
- **When:** Researching a company's clinical programs or verifying trial status

### PubMed
- **Purpose:** Scientific literature
- **Usage:** Thought leadership research, drug safety topics, clinical development trends

---

## MCP Server Connections

The following MCP servers are available in the Claude Code environment:
- **Notion** (ec70e152) - Full Notion workspace access
- **HubSpot** (310934d6) - CRM operations
- **Make.com** (ebd8430c) - Automation scenarios, data stores, connections
- **Airtable** (via MCP_DOCKER) - Secondary tracking
- **Playwright** (browser automation) - Web scraping and research
- **Context7** - Library documentation lookup
- **Perplexity** (via MCP_DOCKER) - Web research and reasoning

---

## Config Files

- `/config/notion-databases.json` - All Notion database IDs and data source URLs
- `/config/make-scenarios.json` - Make.com scenario IDs and webhook URLs (populate as built)
- `/config/sync-manifest.json` - Weekly green/red audit rules for sync workflows
- `/config/signal-automations.json` - Signal automation registry, schedules, and output paths
- `/config/signal-health-manifest.json` - Weekly green/red audit rules for signal automations

## API & Security Notes
- Never store API keys or secrets in markdown files
- Store credentials in `/config/` JSON files only
- Notion database IDs are not sensitive but keep organized in config
