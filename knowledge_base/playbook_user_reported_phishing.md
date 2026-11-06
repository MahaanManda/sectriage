# Playbook: User-Reported Phishing Email

## What it is
A user reports a suspicious email. The goal is to decide quickly whether it is malicious, find out who else received it, and whether anyone interacted with it.

## Common indicators
- Sender display name that does not match the address
- Failed or missing SPF, DKIM, or DMARC results
- Lookalike or newly registered sender domain
- Links to login pages on unrelated domains
- Attachments with macros, ISO, HTML, or archives
- Request for urgent payment, gift cards, or credentials

## How to tell benign from malicious
- Benign: legitimate marketing mail, vendor notices, and internal messages that look unusual but pass authentication and match a known relationship. Confirm with the apparent sender through a separate channel.
- Malicious: failed authentication, a lookalike domain, a mismatched link destination, or a request that bypasses the normal process.

## Recommended triage steps
1. Analyze headers, authentication results, links, and attachments safely.
2. Check threat intelligence for the sender, domain, and URLs.
3. Search all mailboxes for the same message and remove it.
4. Find out who clicked or opened: use mail, proxy, and EDR logs.
5. For anyone who entered credentials, reset passwords, revoke sessions, and review mailbox rules.
6. For anyone who opened an attachment, treat the device as possibly compromised.
7. Block the sender and URLs, and reply to the reporter.

## Severity guidance
- Low: no interaction and message removed.
- Medium: link clicked, no credentials entered.
- High: credentials entered or attachment executed.
