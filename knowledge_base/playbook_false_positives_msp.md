# Playbook: Common False Positives in Managed Environments

## What it is
Many alerts come from legitimate IT management and security tools doing their normal job. In environments run by an MSP or an IT team, remote management (RMM), endpoint protection, backup, and monitoring tools all do things that look like attacker behavior. This playbook lists the usual look-alikes so they are not escalated by mistake.

## Common indicators
- PowerShell or cmd launched by an RMM agent, often with long or encoded command lines
- Remote sessions (RDP, remote-control agents) from a technician to many machines
- Admin accounts logging in to many hosts in a short window during patching
- Endpoint security or backup agents reading LSASS memory or creating shadow copies
- Vulnerability scanners and inventory tools sweeping ports and hosts
- Large numbers of agents going offline, or failed connections, during a cloud or vendor outage
- Users with an outdated saved password causing repeated failed logins

## How to tell benign from malicious
- Benign: the activity comes from a known management tool, a signed binary in a standard install path, a known technician or service account, a scheduled maintenance window, or a matching change ticket. The pattern repeats the same way across many machines.
- Malicious: the same behavior from an unfamiliar tool or path, an account that is not an admin or service account, a user workstation instead of a management server, or activity that starts right after a phishing event or odd login.
- During an outage: if many hosts show the same drop in connectivity at the same time, and the vendor reports an incident, it is more likely an outage than an attack. A single host with odd behavior is more suspicious.

## Recommended triage steps
1. Identify the parent process and the account behind the activity.
2. Check whether the tool, path, and signature match known management software.
3. Match against maintenance windows, change tickets, and scheduled jobs.
4. For many-host events, check vendor status pages and whether the pattern is uniform.
5. If any detail does not match, treat it as suspicious and use the technique-specific playbook.
6. Record the benign explanation so the pattern is recognized next time.

## Severity guidance
- Low: confirmed known tool, expected account, expected time.
- Medium: looks like a known tool but one detail is off (path, account, timing).
- High: management-tool behavior from an unknown source, or combined with other suspicious signs.
