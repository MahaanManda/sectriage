# T1110 Brute Force

## What it is
An attacker guesses passwords repeatedly to get into an account. Variants include trying many passwords against one account, trying one common password against many accounts (password spraying), and reusing credentials leaked from other breaches (credential stuffing).

## Common indicators
- Many failed logins in a short window (Windows event 4625, or failed sign-in logs in a cloud identity provider)
- Failures across many different usernames from one source IP
- A burst of failures followed by one success
- Logins from unusual countries or hosting-provider IPs

## How to tell benign from malicious
- Benign: one user with a recently changed password, a service account with an outdated saved credential, or a mobile device retrying with an old password. These typically repeat from one known device at a steady rhythm.
- Malicious: failures across many accounts, unfamiliar source IPs, off-hours timing, or a success right after a long failure run.

## Recommended triage steps
1. Identify the source IP and the targeted accounts.
2. Check whether any attempt succeeded, and if so, what that account did next.
3. Check whether the source is a known device or user location.
4. If compromise is possible, reset credentials, revoke sessions, and require MFA.
5. Block or rate-limit the source.

## Severity guidance
- Low: failures only, known device, no success.
- Medium: many failures from an unknown source, no success.
- High: a successful login after repeated failures, or any privileged account involved.