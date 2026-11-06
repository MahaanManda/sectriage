# T1566 Phishing

## What it is
An attacker sends a message, usually email, that tricks the recipient into clicking a link, opening an attachment, or handing over credentials. It is a very common way for an attacker to gain initial access.

## Common indicators
- Sender domain that mimics a real one (for example a swapped letter)
- Urgent language about payments, passwords, or account suspension
- Links whose visible text differs from the real destination
- Unexpected attachments, especially Office files with macros, ISO or HTML files
- Reply-to address different from the sender

## How to tell benign from malicious
- Benign: legitimate marketing mail, internal IT notices, and vendor invoices that match a known relationship and pass SPF, DKIM and DMARC checks.
- Malicious: authentication failures, a newly registered domain, a request that bypasses normal process (such as changing bank details), or a link to a login page on an unrelated domain.

## Recommended triage steps
1. Check the sender, authentication results and headers.
2. Inspect links and attachments without opening them on a normal machine.
3. Search for other recipients of the same message.
4. Find out whether anyone clicked or opened it.
5. If so, reset that user's credentials, review their sign-in activity, and isolate the device if an attachment ran.
6. Remove the message from all mailboxes and block the sender and URLs.

## Severity guidance
- Low: no one interacted, message removed.
- Medium: a link was clicked but no credentials were entered.
- High: credentials were entered or an attachment was executed.