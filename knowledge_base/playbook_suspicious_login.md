# Playbook: Suspicious Login or Impossible Travel

## What it is
An identity or VPN system flags a sign-in as unusual, such as a new country, an impossible travel pattern, or an unfamiliar device. The goal is to tell a real traveler from an account takeover.

## Common indicators
- Two sign-ins from far-apart locations within a short time
- Sign-in from a hosting provider, anonymizer, or unusual country
- New device or browser never seen for that user
- MFA fatigue: many prompts followed by an approval
- Successful login after multiple failures
- Immediately after sign-in: mailbox rules, forwarding, or file downloads

## How to tell benign from malicious
- Benign: VPN or mobile-carrier IPs that appear to be in another location, a user traveling, a corporate proxy, or a new phone. Often confirmed by the user and consistent with calendar or travel.
- Malicious: the user denies the login, MFA was approved without the user's action, or the session performed actions the user normally does not.

## Recommended triage steps
1. Contact the user through a separate channel and ask whether they signed in.
2. Review IP, location, device, user agent, and timing.
3. Review what the session did: mail rules, forwarding, file access, new MFA methods.
4. If unconfirmed, revoke sessions, reset the password, and require MFA re-registration.
5. Check whether the same IP touched other accounts.
6. Document the outcome.

## Severity guidance
- Low: confirmed legitimate.
- Medium: unconfirmed with no actions taken in the session.
- High: unconfirmed with mailbox rules, data access, or privileged account involved.
