# Playbook: Ransomware Early Warning Indicators

## What it is
Ransomware usually gives warning signs hours or days before files are encrypted. This playbook helps decide whether an alert is part of that early stage.

## Common indicators
- Initial access: phishing, exposed remote desktop, or a stolen VPN login
- Discovery: network scanning, account and domain enumeration
- Credential theft: LSASS access, new admin accounts
- Lateral movement: remote logins and remote service creation across many hosts
- Defense evasion: antivirus or EDR being disabled
- Backup tampering: shadow copy or backup deletion
- Large outbound data transfers before encryption

## How to tell benign from malicious
- Benign: authorized vulnerability scans, IT admins working across many hosts during maintenance, and backup software changes announced in advance.
- Malicious: several of the signs above on one host or account within a short time, especially outside business hours or from an account that does not normally do this.

## Recommended triage steps
1. Collect the alerts for the same host and account over the last 48 hours and look for a chain.
2. Confirm any admin activity with the person or change ticket.
3. If two or more stages appear together, isolate the host and disable the account.
4. Protect backups: disconnect or lock them from the network.
5. Escalate to incident response.

## Severity guidance
- Low: one isolated indicator with a known explanation.
- High: two or more stages seen together.
- Critical: backup tampering or active encryption.