---
name: "browser-job-application"
description: "Submit approved job applications for someone by driving their real Chrome via MCP, one at a time, with safety gates, proof and reply tracking. Use for Greenhouse/Ashby/Lever/Workday/YC applications or checking replies."
---

# Browser-driven job application

Submit applications on the user's behalf in **their own Chrome** (Claude in Chrome MCP), using their sign-ins. Submit one application at a time, at a human pace. Leave proof of every submission.

A submitted application can't be taken back. Most employer systems have no edit or withdraw option after submission, and recruiters see every application a candidate sends. Every gate below exists because skipping it once produced a wrong submission that couldn't be undone.

**Before any `mcp__claude-in-chrome__*` call:**
1. Load the `claude-in-chrome` skill. If it isn't available, load `chrome-browser`.
2. Call `tabs_context_mcp`.
3. Open a new tab for each application, and close it when you're done.

## Permission to act

Filling and submitting an application acts in the user's name. Claude Code's permission system, including auto-mode's classifier, refuses these browser actions unless the user has explicitly asked for them in the current session. When this skill was tested, the classifier blocked filling every form field until the user had authorized it.

So:
- Start a submission run only after the user's own words in this session authorize it, for example "submit the approved batch" or "apply to these 5". An approval recorded in a file from an earlier session is necessary but not sufficient.
- If a browser action is denied, stop. Tell the user exactly what was blocked and what you were about to do, and let them grant it. Never route around a denial with JavaScript `value=` assignments, other tools, or retries.

## Preconditions: check these and stop if any fails

1. **Approval is recorded.** The campaign state (for example `STATE.md` with `approvals.batch_approved: true`, or an `auto_approve` rule the user wrote) covers this role. A plan existing is not approval. The user's "approved" is.
2. **The packet is ready.** `packets/{company}-{job_id}/answers.json` has no `NEEDS_NICK` / `NEEDS_USER` fields left for this form.
3. **The resume is pinned.** The PDF on disk matches the recorded sha256. Upload only that file, and never edit or regenerate it.
4. **Caps and pace allow it.**
   - The company and organization caps aren't exhausted. Examples: OpenAI allows 5 applications per 180 days; Google allows 3 per 30 days.
   - At least 90 seconds have passed since the last submission.
   - The daily maximum (default 25) isn't reached.
   - Submissions aren't paused.
5. **The posting is still open and not a duplicate.** Re-check the ATS feed, and check the job ID and its `siblings` against every ledger.

## Per-application flow

1. **Open the posting and map the form before typing anything.**
   - Open the posting URL in a new tab.
   - Greenhouse shows the application form below the description, sometimes after clicking an "Apply" button. Clicking it only scrolls or reveals the form; it doesn't submit.
   - `read_page` with `filter: interactive` can miss lazily rendered fields. In testing, it showed only the name, email, phone and resume fields. A read-only JavaScript query also found four custom questions, two of them required. Enumerate every `input`, `select` and `textarea` in the form, with its id, label and required flag, and note the submit button's label so you never click it by accident.
   - Compare that list with `answers.json`. If a required question has no packet answer, mark the role `NEEDS_USER: <question text>` and move on without touching the form.
   - Typical custom questions are: work authorization, sponsorship, "applied here in the past N months?", location, "how did you hear about us?", and "Why us?".
   - Answer "Applied here before?" from the ledgers: "No" only when no ledger shows that company within the asked window.
2. **Fill the fields from `answers.json`.**
   - Use `form_input` for text and selects. Use `file_upload` on the file input. Never click the Attach button: it opens a native file picker you can't operate.
   - Never click "Autofill my application" (MyGreenhouse autofill), and never let browser autofill populate fields. Autofill is how wrong self-ID answers were submitted before.
   - Country and phone-country widgets are comboboxes: type, then select the option.
   - Click only what the form needs.
3. **Free text.**
   - Paste the packet's `note.md`, with citations stripped. It goes in "Why us?", "Additional information" or the cover-letter box.
   - On forms that ask the applicant to attest to how AI was used, or that the answers are their own work (Anthropic, OpenAI, and others), paste only the user's own `final.md`. Its first line must be `AUTHOR: NICK` (or the user's name). Remove that line before pasting.
   - If that file isn't there, set the status to `awaiting_user_text` and skip the role.
4. **Self-ID read-back gate.** Right before Submit, read the **live DOM value** of every voluntary self-ID field (gender, race/ethnicity, veteran, disability) and compare it with the answer bank's `self_id`.
   - Browser autofill silently overwrites these fields, and on Greenhouse they can't be edited after submission.
   - On a mismatch, fix the field and read it back again. If it still mismatches, abort, take a screenshot, and log `blocked-eeo`.
   - Some forms have no self-ID section. Record `eeo_readback: "none_on_form"`.
5. **Required-field read-back.** Re-read every required field's live value. Any empty required field means stop; don't submit and hope.
6. Take a screenshot of the filled form, saved as `evidence/{id}/pre-submit.png`. Then click Submit.
7. **Email verification code (Greenhouse).** Search Gmail read-only for `from:no-reply@us.greenhouse-mail.io newer_than:1h`. Take the 8-character code and enter it into the security inputs, then resubmit.
8. Take a screenshot of the confirmation page, saved as `evidence/{id}/confirmation.png`. No confirmation page means not submitted. Record what you saw instead.
9. Append a ledger row: id, org, title, url, ats, `submitted_at` (ISO-8601 with offset), `resume_sha256`, `eeo_readback`, `essay_author` where it applies, and the evidence paths. Update the tracker status to `submitted`. Then checkpoint the campaign state.
10. Close the tab. Wait at least 90 seconds before the next application.

## Dry runs

When the user asks to test this flow, do steps 1–5 and the pre-submit screenshot only. Never click Submit in a dry run.

A dry run still fills a real form, so it needs the user's explicit go-ahead for that specific posting. Close the tab afterwards without submitting; Greenhouse, Ashby and Lever don't save drafts.

## Per-platform notes

- **Greenhouse**
  - The user must be signed in to MyGreenhouse first. When `my.greenhouse.io/users/self` returns 401, React error #418 breaks the Submit handler: uploads succeed but the application never posts.
  - Invisible reCAPTCHA runs on submit. If a challenge appears, hand it to the user.
- **Ashby**
  - Location and school fields are live-search comboboxes. Type, wait for the option list, and *select* the option. Typed text alone leaves the field empty.
  - The form sits under an "Application" tab.
- **Lever**
  - The form is on a single `/apply` page.
  - The "Additional information" box takes the note.
- **Workday**
  - Each company's Workday site needs its own account. Mark the role `needs_signin`, and continue once the user has signed in themselves.
- **YC Work at a Startup**
  - Applying means sending a message to the founder. Send it only after the user has signed in and approved the batch that includes it.
- **LinkedIn**
  - Discovery only. Never automate Easy Apply: it breaks LinkedIn's terms and risks restricting the user's account.
  - Queue LinkedIn-only roles as `manual_linkedin` for the user.

## Hand to the user; never do these yourself

Ask once, in a batch, for anything in this list:
- creating accounts
- typing passwords
- solving CAPTCHAs or anti-bot challenges
- accepting terms of service or legal agreements
- choosing answers the user hasn't provided
- sending email or messages other than an approved YC application message

These either commit the user to something or speak for them in ways they haven't authorized. Keep working through the roles that don't need them.

## Stop conditions

Stop the whole run, not just the current application, and report what happened if:
- a permission denial occurs
- the same unexplained form failure happens on two applications in a row
- an anti-bot challenge or an account warning appears
- a confirmation is missing after Submit
- the browser extension stops responding after two retries

Repeating a broken submission path wastes postings and can flag the account.

## Tracking replies

After a submission day, or when asked to check replies, search Gmail **read-only** for messages from the submitted companies. Update the tracker status to one of:

`confirmed | rejected | assessment | screen_requested | interviewing | offer`

Record only the date and the subject line, not the email body. Never reply, label, archive or delete anything.

Summarize the funnel by lane:

submitted → confirmed → replied → screens

Then list the replies that need the user's action.