# Notion Integration Patterns

## Candidate DB
- Data source ID: `3841a478-62d3-4e5d-8265-d429375bd314`
- Parent page: `c88d8909-e7c5-427a-a427-e53f2f267777`

### Valid Candidate Status Values:
New Lead, Active, Screening Call Scheduled, References, Submitted to Client, Interviewing, Offer Extended, Placed, Not Interested, Not Qualified, Withdrew, Passed, Archive - Past Contact

**"Archived" is NOT valid** - use "Archive - Past Contact" instead.

### Key Properties:
- Candidate Name (title)
- Candidate Status (select)
- Submitted For (rich_text)
- Last Contact (date)
- Personal Notes (rich_text)

## Company Core DB
- Database ID: `9e8c123a-23b8-4b1d-9be0-d759b897b61a`
- Data source: `collection://f371c4ed-be14-468e-a197-822154951845`

## Pipeline Snapshot
- Page ID: `125f675e-918b-453f-9c68-b271365cad26`
- Format: plain text, full overwrite with `replace_content`

## Daily Command Center
- Page ID: `2de74761-3c9a-8181-9b76-e658b009b893`
