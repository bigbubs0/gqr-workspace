# Comet Browser Automation Patterns

## Critical: 0x0 Viewport Issue
Comet browser reports 0x0 viewport even after resize_window calls. This does NOT block most operations but critically affects input.

### What WORKS with 0x0 viewport:
- `form_input` tool (setting values on input fields via ref)
- JavaScript DOM manipulation (innerHTML, textContent, etc.)
- `click` via ref (element reference clicks)
- `navigate` (URL navigation)
- `find` (element search)
- `read_page` (accessibility tree)

### What FAILS with 0x0 viewport:
- `computer` `type` action - text is NOT entered into fields (fails silently!)
- `computer` `screenshot` action - returns "not connected" error
- `computer` `key` action - keyboard events may not reach page elements
- Coordinate-based clicks (no visible viewport to target)

### Outlook Compose Strategy (confirmed working 3/9/26):
1. Open compose via URL: `https://outlook.office.com/mail/deeplink/compose`
2. Use `find` to locate all form elements (To, Subject, Body, Save draft, Send)
3. Set Subject via `form_input` on subject field ref
4. Set Body via JavaScript: insert HTML before signature block using `innerHTML`
5. Set To via `form_input` on To field ref (NOTE: may not trigger autocomplete)
6. Save via clicking Save draft button ref
7. Close compose by navigating to `https://outlook.office.com/mail/`

### To Field Limitation:
`form_input` sets raw text in the To field but does NOT trigger Outlook's contact autocomplete/resolution. Always flag for Bryan to verify recipient manually.

### NEVER click Send button - drafts only.
