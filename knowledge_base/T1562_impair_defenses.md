# T1562 Impair Defenses

## What it is
Attackers disable, tamper with, or evade security tools so they can operate without being detected. Examples include stopping antivirus or EDR services, adding exclusions, disabling the firewall, clearing or stopping logging, and changing security policy.

## Common indicators
- Security services or agents stopped, uninstalled, or crashing
- Antivirus exclusions added for broad paths such as whole drives or temp folders
- Commands such as Set-MpPreference -DisableRealtimeMonitoring or netsh advfirewall set allprofiles state off
- Tamper protection alerts
- A gap in logs or a host that stopped reporting to the SIEM or EDR
- Event log clearing (Windows event 1102 or 104)

## How to tell benign from malicious
- Benign: IT staff adding an exclusion for a business application or temporarily stopping a service for troubleshooting, with a ticket and an admin account, and the change is later reverted.
- Malicious: no ticket, an unfamiliar account, tampering by a script, or the change happening just before other suspicious actions.

## Recommended triage steps
1. Identify who or what made the change and through which tool.
2. Check for a matching change ticket or admin confirmation.
3. Restore the security setting and confirm the agent is healthy.
4. Review all activity on the host from the hour before the change.
5. If unexplained, treat the host as possibly compromised and isolate it.

## Severity guidance
- Medium: unexplained exclusion or setting change with no other activity.
- High: defenses disabled by a script or non-admin account.
- Critical: defenses disabled followed by backup deletion or mass file changes (possible ransomware).
