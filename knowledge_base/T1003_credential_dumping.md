# T1003 OS Credential Dumping

## What it is
An attacker extracts password hashes or plaintext credentials from a system, most often from LSASS process memory, the SAM database, or the NTDS.dit file on a domain controller. Stolen credentials let them move to other systems and escalate privileges.

## Common indicators
- A non-system process opening or reading LSASS memory (Sysmon event 10)
- Tools such as Mimikatz or ProcDump targeting lsass.exe
- Creation of memory dump files of lsass.exe
- Registry export of the SAM or SYSTEM hives
- Use of ntdsutil or volume shadow copies on a domain controller
- EDR alerts on credential access

## How to tell benign from malicious
- Benign: legitimate security or backup software that touches LSASS or shadow copies, and crash dump collection by IT. These come from known, signed tools in known paths.
- Malicious: unsigned or renamed tools, dumps written to temp folders or user profiles, or activity from an account that has no admin duties.

## Recommended triage steps
1. Identify the process that accessed LSASS and its parent.
2. Check whether the tool is a known, approved security product.
3. Look for dump files and any outbound transfer of them.
4. Assume credentials on that host are exposed: list which accounts were logged in.
5. Isolate the host and reset exposed credentials, starting with privileged accounts.

## Severity guidance
- Low: approved tool confirmed.
- High: unknown tool accessing LSASS.
- Critical: confirmed dump on a server or domain controller, because many accounts may be exposed.
