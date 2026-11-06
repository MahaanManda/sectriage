# T1070 Indicator Removal

## What it is
Attackers delete or alter evidence of their activity, such as clearing event logs, deleting files they dropped, or modifying timestamps, to hinder investigation.

## Common indicators
- Windows security log cleared (event 1102) or system log cleared (event 104)
- wevtutil cl or Clear-EventLog commands
- Deletion of dropped tools or scripts shortly after use
- Command history cleared on Linux hosts
- Log forwarding gaps or missing time ranges
- File timestamps that do not match the file's apparent history

## How to tell benign from malicious
- Benign: log rotation, scheduled cleanup jobs, disk-space maintenance, and approved reinstalls.
- Malicious: logs cleared by an interactive user or script, no maintenance ticket, or clearing that follows other suspicious activity.

## Recommended triage steps
1. Find who cleared the log, when, and from which session.
2. Check whether central logs (SIEM, EDR) still hold the missing data.
3. Review the activity just before the clearing, since it is probably what they wanted hidden.
4. Confirm with admins whether any maintenance occurred.
5. Treat the host as suspect and isolate it if unexplained.

## Severity guidance
- Medium: log cleared with a plausible maintenance explanation.
- High: unexplained log clearing.
- Critical: log clearing together with credential theft, defense impairment, or ransomware indicators.
