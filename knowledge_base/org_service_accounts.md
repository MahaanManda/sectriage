# Harbor Logistics: Service Account Expected Behavior

Synthetic example policy for the fictional company Harbor Logistics.

## General rules
- Service accounts (names starting svc_) never log on interactively (console, RDP) and never sign in over VPN or to cloud apps.
- Service accounts do not browse the internet. Their only outbound internet traffic is the destination listed below, if any.
- Administrator accounts (names starting adm_) belong to named technicians: adm_jkhan and adm_tpatel. They log on to servers only from JUMP01 and RMM01.

## Accounts
| Account | Purpose | Allowed logon type | Allowed targets | Expected activity |
|---|---|---|---|---|
| svc_backup | Veeam backup | Network, from BACKUP01 only | FS01, FS02, SQL01 | Nightly 23:00 to 03:00 UTC. Reads files, creates and resizes shadow copies. Uploads to S3 bucket harbor-backup-prod. |
| svc_scan | Nessus credentialed scans | Network, from NESS01 only | All internal hosts | Wednesdays 03:00 to 05:00 UTC. Many logons across many hosts are normal in that window. |
| svc_sql | SQL Server and maintenance | Service logon on SQL01 only | SQL01 | Runs the scheduled task DBMaint (C:\Scripts\dbmaint.ps1) nightly at 02:00. It creates no other scheduled tasks. |
| svc_rmm | PatchPilot server | Network, from RMM01 only | All managed hosts | Pushes scripts during maintenance windows or approved changes. |

## Warning signs
- A service account logging on interactively, from a workstation, or from a source host not in the table.
- A service account touching a host outside its allowed targets, especially a Tier 0 asset.
- A service account creating scheduled tasks, services or files outside its normal role.
- A service account sending data to any destination not listed.
