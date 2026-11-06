# T1021 Remote Services

## What it is
Attackers use valid accounts to log in to other systems through remote access services such as Remote Desktop (RDP), SMB and admin shares, SSH, and WinRM. This is a common way to move laterally across a network.

## Common indicators
- RDP, SSH, or WinRM sessions between hosts that normally never connect
- Windows logon type 3 (network) or 10 (remote interactive) from unusual sources (events 4624, 4625)
- Access to admin shares such as C$ or ADMIN$
- A single account logging in to many hosts in a short time
- Remote service or task creation after a remote login
- RDP exposed to the internet followed by successful logins

## How to tell benign from malicious
- Benign: administrators and helpdesk staff using RDP or remote management on a regular schedule, and RMM tools connecting to endpoints.
- Malicious: workstation-to-workstation RDP, a standard user account reaching servers, off-hours sessions, or a login chain that fans out across hosts.

## Recommended triage steps
1. Map the source host, destination host, account, and time.
2. Check whether the account normally uses this path and whether a ticket or change explains it.
3. Look at what happened after login: tools run, files copied, tasks created.
4. Check how the source host was reached and whether it is already compromised.
5. Contain the source and destination, and reset the account if not explained.

## Severity guidance
- Low: known admin or RMM activity.
- Medium: unusual path with no suspicious follow-up.
- High: fan-out across multiple hosts, or follow-up activity such as credential dumping or tool execution.
