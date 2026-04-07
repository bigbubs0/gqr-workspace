# Power Automate: EOD Email Scan → Make.com

## Purpose
Pulls today's inbox + sent emails from your GQR Outlook at 5:30 PM ET and sends structured data to Make.com webhook for processing into Notion + Google Drive.

## Why Power Automate Instead of Make.com OAuth
GQR's Microsoft 365 admin has not authorized the Make.com OAuth app. Power Automate runs under YOUR Microsoft 365 credentials natively - no admin approval needed for Graph API access to your own mailbox.

## Webhook URL
```
https://hook.us2.make.com/3qkyygxjc6163aup23anr661py7u3ut1
```

## Flow Setup (Step by Step)

### Step 1: Trigger
- **Type:** Recurrence
- **Interval:** 1 day
- **Frequency:** Day
- **At these hours:** 17
- **At these minutes:** 30
- **Time zone:** (UTC-05:00) Eastern Time

### Step 2: Initialize variable - TodayStart
- **Name:** TodayStart
- **Type:** String
- **Value:** `@{formatDateTime(utcNow(), 'yyyy-MM-dd')}T05:00:00Z`

### Step 3: Get Inbox Emails (Office 365 Outlook - Get emails V3)
- **Folder:** Inbox
- **Filter Query:** `receivedDateTime ge @{variables('TodayStart')}`
- **Order By:** receivedDateTime desc
- **Top:** 100
- **Include Attachments:** No

### Step 4: Select - Format Inbox
- **From:** Step 3 output (value)
- **Map:**
  - from: `@{item()?['from']?['emailAddress']?['name']} <@{item()?['from']?['emailAddress']?['address']}>`
  - subject: `@{item()?['subject']}`
  - received: `@{item()?['receivedDateTime']}`
  - preview: `@{take(item()?['bodyPreview'], 300)}`
  - isRead: `@{item()?['isRead']}`

### Step 5: Initialize variable - InboxFormatted
- **Name:** InboxFormatted
- **Type:** String
- **Value:** (empty)

### Step 6: Apply to each - Build inbox markdown
- **Input:** Output of Step 4 (Select)
- **Inside the loop - Append to string variable:**
  - **Name:** InboxFormatted
  - **Value:**
```
## @{items('Apply_to_each')?['received']} - @{items('Apply_to_each')?['from']}
**Subject:** @{items('Apply_to_each')?['subject']}
**Preview:** @{items('Apply_to_each')?['preview']}

```

### Step 7: Get Sent Emails (Office 365 Outlook - Get emails V3)
- **Folder:** Sent Items
- **Filter Query:** `sentDateTime ge @{variables('TodayStart')}`
- **Order By:** sentDateTime desc
- **Top:** 100

### Step 8: Select - Format Sent
- **From:** Step 7 output (value)
- **Map:**
  - to: `@{first(item()?['toRecipients'])?['emailAddress']?['name']} <@{first(item()?['toRecipients'])?['emailAddress']?['address']}>`
  - subject: `@{item()?['subject']}`
  - sent: `@{item()?['sentDateTime']}`
  - preview: `@{take(item()?['bodyPreview'], 300)}`

### Step 9: Initialize variable - SentFormatted
- **Name:** SentFormatted
- **Type:** String
- **Value:** (empty)

### Step 10: Apply to each - Build sent markdown
- **Input:** Output of Step 8 (Select)
- **Inside the loop - Append to string variable:**
  - **Name:** SentFormatted
  - **Value:**
```
## @{items('Apply_to_each_2')?['sent']} - To: @{items('Apply_to_each_2')?['to']}
**Subject:** @{items('Apply_to_each_2')?['subject']}
**Preview:** @{items('Apply_to_each_2')?['preview']}

```

### Step 11: HTTP - Send to Make.com Webhook
- **Method:** POST
- **URI:** `https://hook.us2.make.com/3qkyygxjc6163aup23anr661py7u3ut1`
- **Headers:**
  - Content-Type: application/json
- **Body:**
```json
{
  "scan_date": "@{formatDateTime(utcNow(), 'yyyy-MM-dd')}",
  "scan_time": "@{formatDateTime(utcNow(), 'HH:mm')}",
  "inbox_count": @{length(body('Get_Inbox_Emails')?['value'])},
  "sent_count": @{length(body('Get_Sent_Emails')?['value'])},
  "inbox_formatted": @{variables('InboxFormatted')},
  "sent_formatted": @{variables('SentFormatted')}
}
```

## Testing

After building the flow:
1. Click **Test** → **Manually** in Power Automate
2. Check Make.com scenario 4472273 execution history for the received webhook
3. Verify data appears on Notion EOD Scan Output page and in Google Drive

## Maintenance
- Webhook URL is hardcoded. If the Make.com webhook is recreated, update Step 11.
- Flow runs under your Microsoft 365 credentials. No admin needed.
- If your GQR password changes, Power Automate may need re-authentication.
