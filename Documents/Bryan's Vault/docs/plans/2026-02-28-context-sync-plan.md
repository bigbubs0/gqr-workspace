# Context Sync System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a multi-directional sync system between Notion, Google Drive, and Obsidian via Make.com scenarios, keeping all three platforms current with recruiting intelligence.

**Architecture:** Notion owns structured data (companies, candidates, searches). Obsidian (OneDrive vault) owns unstructured context and working notes. Google Drive owns documents (CVs, contracts). Make.com orchestrates hourly/4-hourly sync via OneDrive API, Notion API, and Drive API.

**Tech Stack:** Make.com scenarios, OneDrive `uploadAFile`/`downloadAFile` modules, Notion API, Google Drive API, Make.com data stores

> **2026-02-28 Update:** All "Data Store: Update Record" and "Data Store: Search Records" steps
> throughout this plan are obsolete. The Sync State Tracker data store was never populated and has
> been deleted. Health Monitor uses Make.com API logs directly. Individual scenarios use file
> timestamps and Notion `last_edited_time` for change detection. Task text preserved for history.

---

## Phase 1: Infrastructure Setup

### Task 1: Consolidate Obsidian Vaults

**Context:** Two identical vaults exist. OneDrive vault is the superset (has community plugins). Local vault can be safely removed.

**Step 1: Remove local vault from Obsidian registry**
Open Obsidian settings, remove `C:\Bryan's Vault` from the vault switcher. Do NOT delete files yet - just unregister.

**Step 2: Verify OneDrive vault works**
Open `C:\Users\bblai\OneDrive\Documents\Bryan's Vault` in Obsidian. Confirm all files, plugins, and settings load correctly.

**Step 3: Delete local vault**
Run:
```bash
rm -rf "/c/Bryan's Vault"
```
Expected: Directory removed. OneDrive vault is now the single source.

**Step 4: Create missing folders in OneDrive vault**
```bash
mkdir -p "/c/Users/bblai/OneDrive/Documents/Bryan's Vault/90_archive/candidates"
mkdir -p "/c/Users/bblai/OneDrive/Documents/Bryan's Vault/90_archive/companies"
mkdir -p "/c/Users/bblai/OneDrive/Documents/Bryan's Vault/bryan/dashboards"
```
Expected: Archive and dashboard directories created.

**Step 5: Commit checkpoint**
This is a file-system-only change (no git repo here). Verify OneDrive syncs the new folders to cloud.

---

### Task 2: Create OneDrive Connection in Make.com

**Context:** Make.com has an `onedrive` app (v2) but no connection exists yet. Need an Azure OAuth connection with `Files.ReadWrite` scope.

**Step 1: Create the connection**
In Make.com UI (us2.make.com):
1. Go to Connections > Create a connection
2. Select "Microsoft OneDrive" (personal)
3. Authenticate with Bryan's Microsoft account (the one backing OneDrive)
4. Grant `Files.ReadWrite` permissions

Note: This step requires browser-based OAuth - cannot be fully automated via API. Bryan must click through the auth flow.

**Step 2: Verify the connection works**
Use Make.com MCP to test. Create a test tool that uses `onedrive:searchFilesFolders` to list files in `/Documents/Bryan's Vault`. If it returns the vault files, the connection is live.

```
Module: onedrive:searchFilesFolders (v2)
Parameters: { "__IMTCONN__": <new_connection_id> }
Mapper: {
  "select": "my",
  "select1": "no",
  "itemType": "file",
  "folder": "/Documents/Bryan's Vault",
  "searchInHiddenFolders": false,
  "limit": 10
}
```
Expected: Returns list including USER.md, MEMORY.md, etc.

**Step 3: Record connection ID**
Save the connection ID for use in all subsequent scenarios.

---

### Task 3: Create Sync State Tracker Data Store

**Step 1: Create the data structure**
```
Name: "Sync State Schema"
Team ID: 200002
Strict: true
Spec:
  - name: "scenario_id", type: "text", required: true
  - name: "content_key", type: "text", required: true
  - name: "last_synced", type: "text", required: true
  - name: "last_hash", type: "text"
  - name: "status", type: "text", required: true
```
Use: `mcp__ebd8430c...data-structures_create`

**Step 2: Create the data store**
```
Name: "Sync State Tracker"
Team ID: 200002
Data Structure ID: <from step 1>
Max Size: 5 MB
```
Use: `mcp__ebd8430c...data-stores_create`

**Step 3: Verify**
Use `data-stores_get` to confirm the store exists and is empty.

---

### Task 4: Create "Agent Context" Page in Notion

**Step 1: Create the page**
Use Notion MCP `notion-create-pages`:
```json
{
  "pages": [{
    "properties": { "title": "Agent Context - Synced" },
    "content": "# Agent Context\n\nThis page is auto-updated by the Context Sync System.\nLast synced: never\n\n## USER.md\n_Pending first sync_\n\n## MEMORY.md\n_Pending first sync_\n\n## TODO.md\n_Pending first sync_"
  }]
}
```
No parent specified - creates as a private workspace page.

**Step 2: Record the page ID**
Save the page ID for Scenario 5 configuration.

---

## Phase 2: Core Notion -> Obsidian Pipeline

### Task 5: Scenario 2 - Active Searches Sync (Highest Value)

**Why first:** This is the most immediately useful scenario and establishes the Notion -> OneDrive write pattern used by Scenarios 1 and 3.

**Step 1: Get module instructions for Notion search**
Verify the Notion query pattern for Active Searches:
```
Data Source: collection://a9ad56d9-0459-44c3-a914-5bfeaa8617bf
Filter: Status IN ("Active", "On Hold")
Properties needed: Role Title, Client, Status, Priority, Fee Structure,
  Candidates, Intake Date, Last Activity Date, Target Fill Date
```

**Step 2: Build the scenario blueprint**
Create scenario in Make.com (team 200002):

Module chain:
1. **Notion: Search Objects** - Query Active Searches data source for Status = Active or On Hold
2. **Iterator** - Loop through results
3. **Text Aggregator** - For each search, format markdown using the Search File template:
```markdown
---
source: notion
notion_id: {{item.id}}
last_synced: {{now}}
client: {{item.properties.Client}}
status: {{item.properties.Status}}
priority: {{item.properties.Priority}}
fee_structure: {{item.properties["Fee Structure"]}}
---
# {{item.properties["Role Title"]}} - {{item.properties.Client}}

**Status:** {{item.properties.Status}} | **Priority:** {{item.properties.Priority}} | **Fee:** {{item.properties["Fee Structure"]}}
**Intake Date:** {{item.properties["Intake Date"]}} | **Target Fill:** {{item.properties["Target Fill Date"]}}

## Candidates
{{candidateList}}

<!-- SYNC BOUNDARY - edits below sync back to Notion -->

```
4. **OneDrive: Upload a File** - Write each file to `/Documents/Bryan's Vault/recruiting/searches/`
```
Module: onedrive:uploadAFile (v2)
Mapper: {
  "enter": "path",
  "select": "my",
  "select1": "no",
  "folder": "/Documents/Bryan's Vault/recruiting/searches",
  "filename": "{{slugify(item.properties['Role Title'])}}-{{slugify(item.properties.Client)}}.md",
  "data": "{{markdownContent}}",
  "conflictBehavior": "replace"
}
```
5. **Text Aggregator** - Build the dashboard rollup `active-searches.md`:
```markdown
---
source: notion
last_synced: {{now}}
---
# Active Searches

| Role | Client | Priority | Fee | Candidates | Last Activity |
|---|---|---|---|---|---|
{{#each searches}}
| {{Role Title}} | {{Client}} | {{Priority}} | {{Fee Structure}} | {{candidateCount}} | {{Last Activity Date}} |
{{/each}}

**Pipeline:** {{activeCount}} active | {{holdCount}} on hold
```
6. **OneDrive: Upload a File** - Write dashboard to `/Documents/Bryan's Vault/bryan/dashboards/active-searches.md`
7. **Data Store: Update Record** - Update Sync State Tracker with scenario_id "scenario_2", last_synced = now, status = "success"

**Schedule:** Every 60 minutes

**Step 3: Create the scenario**
Use `mcp__ebd8430c...scenarios_create` with the blueprint.

**Step 4: Test run**
Use `mcp__ebd8430c...scenarios_run` to execute once. Check:
- Files appear in OneDrive vault `recruiting/searches/` folder
- Dashboard appears in `bryan/dashboards/active-searches.md`
- Sync State Tracker has an entry

**Step 5: Verify in Obsidian**
Open Obsidian, check that the synced files are visible with correct frontmatter and content.

**Step 6: Activate the scenario**
Use `mcp__ebd8430c...scenarios_activate` to enable the hourly schedule.

---

### Task 6: Scenario 3 - Candidate Pipeline Sync

**Step 1: Build the scenario blueprint**
Same pattern as Task 5 but for Candidates:

Module chain:
1. **Notion: Search Objects** - Query Candidates data source `collection://3841a478-62d3-4e5d-8265-d429375bd314`
   - Filter: Candidate Status IN ("Active", "Screening Call Scheduled", "Submitted to Client", "Interviewing", "Offer Extended")
   - Properties: Candidate Name, Current Company, Current Title, Email, LinkedIn URL, Quick Summary, Key Skills, Location, Candidate Status, Last Contact, Next Follow-Up
2. **Iterator** - Loop through results
3. **Router** - Two paths:
   - Path A (active candidates): Format markdown using Candidate File template, upload to `/Documents/Bryan's Vault/recruiting/candidates/`
   - Path B (terminal check): Query data store for candidates with `terminal: true` and `terminal_date` > 7 days ago. For those, use OneDrive `moveAFileFolder` to move from `recruiting/candidates/` to `90_archive/candidates/`
4. **OneDrive: Upload a File** - Write each candidate file
```
filename: "{{slugify(candidateName)}}-{{slugify(currentCompany)}}.md"
folder: "/Documents/Bryan's Vault/recruiting/candidates"
conflictBehavior: "replace"
```
5. **OneDrive: Upload a File** - Write pipeline dashboard to `bryan/dashboards/pipeline-summary.md`
6. **Data Store: Update Record** - Sync State Tracker update

**Terminal status handling:**
- When a previously-active candidate's Notion status changes to terminal (Placed, Not Interested, Archive, Withdrew, Passed, Not Qualified):
  - Add `terminal: true` and `terminal_date: {{now}}` to frontmatter
  - Keep file in `recruiting/candidates/` for 7 days
  - After 7 days: OneDrive `moveAFileFolder` to `90_archive/candidates/`
  - Remove from Sync State Tracker

**Step 2: Create, test, verify, activate**
Same workflow as Task 5 Steps 3-6.

---

### Task 7: Scenario 1 - Company Intelligence + Signal Feed

**Step 1: Build the scenario blueprint**

This scenario queries multiple Notion databases and merges the data.

Module chain:
1. **Notion: Search Objects** - Query Company Core `collection://f371c4ed-be14-468e-a197-822154951845`
   - Filter: `Most recent signal date` >= {{addDays(now, -2)}} (48h window)
   - Properties: Company, Client Status, Country, Therapeutic areas, Most recent signal type, Most recent signal date, Headcount (band)
2. **Iterator** - Loop through companies
3. **For each company - Notion: Search Objects** - Query each signal DB for matching company:
   - Layoffs: `collection://21cf7674-0da8-4812-8708-04b65a252cac` filtered by Company Core relation
   - Positive Data: `collection://c5a4112f-cd39-479f-a90f-3165a1ec7a60` filtered by Company Core relation
   - 5-50M Funding: `collection://9490e7cc-0504-4412-85ad-32b2ad7e906e` filtered by Company Core relation
   - Megaround: `collection://927267bf-ec5b-4b20-9829-2b9d6371ba23` filtered by Company Core relation
4. **Aggregator** - Merge signal data into timeline for each company
5. **Text Formatter** - Generate company markdown using Company File template
6. **OneDrive: Upload a File** - Write to `/Documents/Bryan's Vault/recruiting/companies/{{company-slug}}.md`
7. **Array Aggregator** - Collect last 7 days of signals across all companies
8. **Text Formatter** - Generate signal feed dashboard
9. **OneDrive: Upload a File** - Write to `/Documents/Bryan's Vault/bryan/dashboards/signal-feed.md`
10. **Data Store: Update Record** - Sync State Tracker

**Schedule:** Every 240 minutes (4 hours)

**Step 2: Create, test, verify, activate**
Same workflow as Task 5 Steps 3-6.

---

## Phase 3: Reverse Sync (Obsidian/Drive -> Notion)

### Task 8: Scenario 5 - Obsidian -> Notion Context Sync

**Step 1: Build the scenario blueprint**

Module chain:
1. **OneDrive: Download a File** - Read `USER.md` from `/Documents/Bryan's Vault/USER.md`
```
Mapper: {
  "enter": "path",
  "choose": "map",
  "select": "my",
  "select1": "no",
  "file": "/Documents/Bryan's Vault/USER.md",
  "format": false
}
```
2. **OneDrive: Download a File** - Read `MEMORY.md` (same pattern)
3. **OneDrive: Download a File** - Read `TODO.md` (same pattern)
4. **Data Store: Get Record** - Check Sync State Tracker for last hash of each file
5. **Filter** - Only proceed if file content hash differs from stored hash
6. **Notion: Update Page** - Update "Agent Context" page with new content
   - Use the page ID from Task 4
   - Replace content sections for each changed file
7. **OneDrive: Search Files/Folders** - List files in `/Documents/Bryan's Vault/recruiting/candidates/`
8. **Iterator** - Loop through candidate files
9. **OneDrive: Download a File** - Read each candidate file
10. **Text Parser** - Extract content below `<!-- SYNC BOUNDARY - edits below sync back to Notion -->` delimiter
11. **Filter** - Only proceed if notes section has content AND content hash differs from stored
12. **Notion: Update Page** - Push notes to corresponding Notion candidate record (matched via `notion_id` from frontmatter YAML parse)
13. **Data Store: Update Record** - Update hashes and timestamps

**Schedule:** Every 60 minutes

**Step 2: Create, test, verify, activate**

---

### Task 9: Scenario 4 - Drive -> Notion Document Linker

**Step 1: Build the scenario blueprint**

Module chain:
1. **Google Drive: Watch Files in a Folder** - Watch `01_CANDIDATES` folder (ID: `19p0p8_aZKRRhHjvjZSJXxIIzuOcFfOTk`) for new files
   - Also watch `00_INBOX` folder (ID: `1tOJh8IPPhsKTa706Xk5cei6lA14DHVK_`)
2. **Text Parser** - Extract candidate name from filename
   - Strip file extension (.pdf, .docx, .doc)
   - Strip common prefixes (CV_, Resume_, Confidential_)
   - Strip dates (YYYY-MM-DD, MM-DD-YYYY patterns)
   - Split remaining text on underscores, hyphens, spaces
   - Result: best-guess candidate name
3. **Notion: Search Objects** - Search Candidates DB for matching name
   - Query: extracted candidate name
   - Data Source: `collection://3841a478-62d3-4e5d-8265-d429375bd314`
4. **Router** - Two paths:
   - **Path A (match found, confidence high):** Update Notion candidate record - add Google Drive file link to the record
   - **Path B (no match or ambiguous):** Create new Notion candidate page:
     ```json
     {
       "parent": { "data_source_id": "3841a478-62d3-4e5d-8265-d429375bd314" },
       "pages": [{
         "properties": {
           "Candidate Name": "{{extractedName}}",
           "Candidate Status": "New Lead"
         },
         "content": "**needs_review:** true\n**Source file:** [{{filename}}]({{webViewLink}})\n\nAuto-created by Context Sync - name extracted from filename. Verify candidate identity and merge if duplicate."
       }]
     }
     ```
5. **Data Store: Update Record** - Log to Sync State Tracker

**Schedule:** Every 60 minutes (but uses Watch trigger, so only fires when new files appear)

**Step 2: Create, test, verify, activate**

---

### Task 10: Scenario 6 - Context Backup to Drive

**Step 1: Build the scenario blueprint**

Module chain:
1. **OneDrive: Download a File** - Read each context file:
   - `/Documents/Bryan's Vault/USER.md`
   - `/Documents/Bryan's Vault/MEMORY.md`
   - `/Documents/Bryan's Vault/IDENTITY.md`
   - `/Documents/Bryan's Vault/SOUL.md`
   - `/Documents/Bryan's Vault/AGENTS.md`
   - `/Documents/Bryan's Vault/TOOLS.md`
2. **Google Drive: Upload a File** - Write each to `91_SYSTEM/agent-context/` folder (ID: `1RCy7odDH5Rk677KLxaVuPp7-qvQW90rp` - need to create subfolder first)
   - Filename: same as source
   - Conflict behavior: overwrite existing
3. **Data Store: Update Record** - Sync State Tracker

**Schedule:** Every 240 minutes (4 hours)

**Pre-step: Create `agent-context` subfolder in `91_SYSTEM`**
Use Google Drive MCP to create folder:
```
mcp__ebd8430c...s4155743_create_google_drive_folder
folderName: "agent-context"
parentFolderId: "1RCy7odDH5Rk677KLxaVuPp7-qvQW90rp"
```

**Step 2: Create, test, verify, activate**

---

## Phase 4: Monitoring

### Task 11: Scenario 0 - Health Monitor

**Step 1: Build the scenario blueprint**

Module chain:
1. **Data Store: Search Records** - Query Sync State Tracker for all records where `scenario_id` starts with "scenario_"
2. **Iterator** - Loop through each scenario's last sync record
3. **Filter/Router** - For each scenario, compare `last_synced` against expected cadence:
   - Scenarios 2, 3, 4, 5: alert if >2 hours since last success
   - Scenarios 1, 6: alert if >6 hours since last success
   - Scenario 0 itself: skip
4. **Aggregator** - Collect all overdue scenarios into a single alert message
5. **Filter** - Only proceed if at least one scenario is overdue
6. **Email: Send an Email** - Send alert to bryanblairjr@gmail.com
   - Subject: "[Context Sync] {{count}} scenario(s) overdue"
   - Body: Table of overdue scenarios with name, last success, hours overdue

**Schedule:** Daily at 7:00 AM ET

**Step 2: Create, test, verify, activate**

---

## Phase 5: Cleanup & Validation

### Task 12: End-to-End Validation

**Step 1: Trigger all scenarios manually**
Run each scenario once via `scenarios_run` in order: 0, 1, 2, 3, 5, 6. (Scenario 4 requires a new file in Drive to trigger.)

**Step 2: Verify Obsidian vault**
Open Obsidian. Check:
- `recruiting/searches/` has files for all active searches
- `recruiting/candidates/` has files for active pipeline candidates
- `recruiting/companies/` has files for recently-signaled companies
- `bryan/dashboards/active-searches.md` shows current table
- `bryan/dashboards/signal-feed.md` shows last 7 days of signals
- `bryan/dashboards/pipeline-summary.md` shows candidate counts
- All files have correct YAML frontmatter with `source: notion`, `notion_id`, `last_synced`

**Step 3: Verify Notion**
Check "Agent Context" page has USER.md, MEMORY.md, TODO.md content.

**Step 4: Verify Drive**
Check `91_SYSTEM/agent-context/` has copies of all 6 context files.

**Step 5: Test bi-directional candidate notes**
1. Open a candidate file in Obsidian
2. Add a note below the `<!-- SYNC BOUNDARY -->` line
3. Wait for Scenario 5 to run (or trigger manually)
4. Check the corresponding Notion candidate record - notes should appear

**Step 6: Test Drive -> Notion linker**
1. Drop a test CV into `01_CANDIDATES` in Drive
2. Wait for Scenario 4 to trigger
3. Check Notion Candidates DB - should have a new stub with `needs_review: true`

**Step 7: Verify Sync State Tracker**
Check data store has entries for all scenarios with recent timestamps and status = "success".

---

### Task 13: Update Memory & Config

**Step 1: Update vault config files**
Write `config/sync-manifest.json` to the vault with scenario IDs, schedules, and connection references.

**Step 2: Update MEMORY.md**
Add Context Sync scenario IDs and data store ID to Bryan's MEMORY.md for future Claude sessions.

**Step 3: Update CLAUDE.md project memory**
Add sync system reference to `C:\Users\bblai\.claude\projects\C--\memory\MEMORY.md` so future Claude Code sessions know the sync exists.
