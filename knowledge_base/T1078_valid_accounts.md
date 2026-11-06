# T1078 Valid Accounts

## What it is
An attacker logs in with real credentials they stole, guessed, bought, or found, instead of breaking in with malware. Because the login is legitimate on paper, it blends in with normal activity. It covers domain, local, cloud, and default accounts.

## Common indicators
- Login from a new country, device, or hosting-provider IP (impossible travel)
- Login at unusual hours for that user
- Account suddenly accessing systems or data it never touched before
- MFA prompts the user did not trigger, or a new MFA device being registered
- Dormant or former-employee accounts becoming active
- Windows event 4624 (successful logon) with unusual logon types or source hosts

## How to tell benign from malicious
- Benign: an employee traveling or using a VPN, a new laptop, an admin working a scheduled maintenance window.
- Malicious: activity that does not match the person's role or normal hours, sign-ins from two distant locations within minutes, or a login right after a phishing report or password-spray alert.

## Recommended triage steps
1. Confirm with the user (through a separate channel) whether they logged in.
2. Review the source IP, device, location, and time.
3. Look at what the session did after login: mailbox rules, file downloads, new accounts, privilege changes.
4. If unconfirmed, reset the password, revoke active sessions, and review MFA devices.
5. Check whether the same credentials were used elsewhere.

## Severity guidance
- Low: unusual location confirmed by the user as legitimate.
- Medium: unexplained login with no sensitive actions seen.
- High: unexplained login plus data access, mail forwarding rules, or privileged account involvement.
