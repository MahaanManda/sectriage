# T1547 Boot or Logon Autostart Execution

## What it is
Attackers configure a program to launch automatically when the system boots or a user logs in. Common methods are Run and RunOnce registry keys, the Startup folder, and services. This gives them persistence after reboots.

## Common indicators
- New values under HKCU or HKLM Software\Microsoft\Windows\CurrentVersion\Run or RunOnce
- New files in the Startup folder
- New or modified Windows services pointing to unusual paths
- Autostart entries pointing to temp folders, user profiles, or scripts
- Entries with random-looking names
- EDR persistence alerts

## How to tell benign from malicious
- Benign: normal applications adding startup entries during install (chat clients, VPN clients, printer software, RMM and security agents).
- Malicious: an entry created by PowerShell, cmd, or an Office app, pointing to a script or a binary in a user-writable folder, or matching a recent suspicious download.

## Recommended triage steps
1. Identify which process created the entry and when.
2. Inspect the target file: location, signature, hash, reputation.
3. Check whether the entry exists on other machines (a common software pattern is benign).
4. Review activity around that time for the initial access.
5. Remove the persistence, quarantine the file, and scan the host.

## Severity guidance
- Low: known application startup entry.
- Medium: unknown entry, unsigned file, no further evidence.
- High: entry created by a script or Office process, or paired with other suspicious activity.
