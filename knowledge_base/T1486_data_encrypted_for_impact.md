# T1486 Data Encrypted for Impact

## What it is
This is ransomware behavior. Attackers encrypt files to make them unusable and demand payment for recovery. They often first steal data and delete backups to raise the pressure.

## Common indicators
- Many files rapidly renamed or given a new extension
- Ransom notes (text or HTML files) appearing in many folders
- Commands that delete shadow copies or backups (vssadmin delete shadows, wbadmin delete, bcdedit changes to disable recovery)
- Sudden high disk activity and CPU use
- Security tools being stopped just before the activity
- File server or shared drives suddenly inaccessible

## How to tell benign from malicious
- Benign: a backup or archive job, a legitimate encryption product rolling out, or bulk file renames by a known sync tool. These are scheduled, signed, and expected.
- Malicious: unexpected mass changes, ransom notes, recovery being disabled, or activity at night or on weekends.

## Recommended triage steps
1. Isolate affected machines from the network immediately, without powering them off if possible, to preserve memory evidence.
2. Identify the earliest affected host and the time it started.
3. Check backups for integrity and whether they are reachable by the attacker.
4. Escalate to incident response and leadership.
5. Look for earlier signs: phishing, credential dumping, remote access.

## Severity guidance
- Critical in nearly all confirmed cases. Treat early indicators (shadow copy deletion, mass renames) as high until proven otherwise.