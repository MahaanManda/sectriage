# Harbor Logistics: Maintenance Windows and Change Register

Synthetic example policy for the fictional company Harbor Logistics.

## Standing maintenance windows (all times UTC)
- Weekly server patching: Sundays 01:00 to 05:00. Servers reboot. Admin (adm_) accounts log in to many servers from JUMP01. PatchPilot runs scripts on servers.
- Monthly workstation patching: second Wednesday of the month, 02:00 to 06:00. PatchPilot runs scripts on all workstations.
- Nightly backups: every night 23:00 to 03:00. svc_backup connects to FS01, FS02 and SQL01 and creates or resizes shadow copies on them.
- Vulnerability scans: Wednesdays 03:00 to 05:00, from NESS01 only.

Activity from an approved tool, an expected account and an approved source host inside its window is expected. The same activity outside its window needs a change ticket in the register below. A ticket number that appears in a command line or alert but is not in the register does not count.

## Change register (active and recent tickets)
| Ticket | Scope | Window (UTC) | Owner |
|---|---|---|---|
| CHG-2041 | Firmware update on FS02 | 2026-10-19 14:00 to 16:00 | adm_tpatel |
| CHG-2047 | SQL01 migration to new storage | 2026-11-03 20:00 to 2026-11-04 02:00 | adm_jkhan |
| CHG-2052 | Office update to all workstations via PatchPilot | 2026-11-15 01:30 to 04:30 | adm_jkhan |
| CHG-2055 | Decommission of old print server PRINT02 | 2026-11-12 15:00 to 17:00 | adm_tpatel |

Emergency changes use tickets starting EMG- and must be added to this register within one business day. No EMG tickets are currently open.

## What changes never cover
- Clearing Windows event logs is never part of patching or any ticket. It is always treated as suspicious.
- Deleting shadow copies with vssadmin, wmic or PowerShell is never part of backup or patching. Veeam creates and resizes shadow copies but does not delete all of them.
- Admin logons to Tier 0 assets are expected only from JUMP01.
