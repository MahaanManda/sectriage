# Harbor Logistics: Approved Tools and Trusted Sources

Synthetic example policy for the fictional company Harbor Logistics. It is used to test whether triage can use environment-specific context.

## Approved management and security tools
Only these tools may perform administration, remote control, scanning or backup in the environment. Anything else doing the same job is unapproved.

| Purpose | Approved tool | Expected install path | Runs as | Source host |
|---|---|---|---|---|
| RMM / patching | PatchPilot agent (ppagent.exe) | C:\Program Files\PatchPilot\ppagent.exe | SYSTEM | RMM01 (10.20.5.10) |
| Remote support | PatchPilot Remote only | C:\Program Files\PatchPilot\ | technician adm_ account | RMM01 |
| Endpoint security | SentinelGuard (sgservice.exe) | C:\Program Files\SentinelGuard\sgservice.exe | SYSTEM | n/a |
| Backup | Veeam, run from BACKUP01 | C:\Program Files\Veeam\ | svc_backup | BACKUP01 (10.20.5.30) |
| Vulnerability scanning | Nessus scanner NESS01 | n/a | svc_scan | NESS01 (10.20.5.15) |
| Admin jump host | JUMP01 | n/a | adm_ accounts | JUMP01 (10.20.5.20) |

- PatchPilot launching PowerShell or cmd with -EncodedCommand is normal behavior for this agent.
- SentinelGuard reading LSASS memory is normal, but only from its install path. The same file name running from any other folder (for example C:\ProgramData or a user profile) is not SentinelGuard.
- PsExec is approved only when run from JUMP01 by an adm_ account. PsExec from any other host is unapproved.

## Not approved
- Remote-access tools other than PatchPilot Remote: AnyDesk, TeamViewer, ScreenConnect, Splashtop, and similar. A user installing one is a policy violation and may be attacker access.
- Personal cloud storage and transfer services: personal Dropbox, Google Drive, MEGA, WeTransfer. rclone is not approved on any machine.
- Any scanner, port sweep or network mapping from a host other than NESS01.

## Approved data destinations
- Microsoft 365 tenant harbor-logistics (SharePoint and OneDrive).
- AWS S3 bucket harbor-backup-prod, written only by svc_backup from BACKUP01 or the file and database servers it protects.
- GitHub organization harbor-logistics.
- Any other S3 bucket name, including look-alikes such as harbor-backup-stage or harbor-backups, is not approved.

## Identity expectations
- All staff are in the United States or Canada. Sign-ins from those two countries with MFA on a known device are normal.
- A successful sign-in from any other country, with no travel notice on file, is unexpected.
- Office egress range 198.51.100.0/24 and VPN pool 10.99.0.0/24 are trusted.
