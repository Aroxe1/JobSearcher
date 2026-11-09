# Application tracking

Tracking lives in the profile file, section "Tracked applications", as a Markdown table so the user can read and edit it by hand.

```
| Company | Role | Link | Date | Status | Next action | Due |
|---------|------|------|------|--------|-------------|-----|
| Acme | Marketing apprentice | https://… | 2026-11-09 | Applied | Follow up by email | 2026-11-18 |
```

- **Date** = date of the last status change (ISO format YYYY-MM-DD, unambiguous across countries).
- **Due** = when the next action should happen (empty if none).

## Statuses
`To apply` → `Applied` → `Followed up` → `Interview` → `Offer` / `Rejected` / `No answer` / `Withdrawn`

Write statuses in the profile's language (e.g. French: `À postuler`, `Postulé`, `Relancé`, `Entretien`, `Offre`, `Refus`, `Sans réponse`, `Abandonné`) and keep them consistent within one file. Translating an existing status to that language is not a status change. For an offer the user pasted (no URL), put "pasted by user" plus the contact email in Link.

A status changes only when the user confirms the action happened. A drafted but unsent follow-up keeps the current status; set Next action to "Send follow-up (draft ready)" with Due = today.

Defaults:
- `Applied` → next action "Follow up", due +7 to +10 days
- `Followed up` → second follow-up +14 days, then `No answer`
- `Interview` → "Send thank-you note" same/next day, then "Follow up" +7 days
- `Rejected` → optional "Ask for feedback"; keep the row (history helps spot patterns)

## At the start of each session
1. Compare **Due** dates with today's date.
2. Mention overdue/due-today actions first ("2 follow-ups are due: Acme, Globex — want me to draft them?").
3. If many rows are `No answer` or `Rejected`, gently suggest reviewing the CV/targeting rather than just sending more.

## Updating
- Add rows only for offers the user wants to track (not every search result).
- Update the profile's "Last updated" date.
- If the user uses another tool (spreadsheet, Notion…), offer the table as copy-pasteable text instead of duplicating.
