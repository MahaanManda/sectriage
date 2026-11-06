# T1053 Scheduled Task/Job

## What it is
Attackers create or modify scheduled tasks (Windows Task Scheduler, cron, at) to run malicious code repeatedly, at startup, or at a set time. It is used for persistence, execution, and sometimes privilege escalation or lateral movement.

## Common indicators
- New task created with schtasks.exe or via the Task Scheduler (Windows events 4698 task created, 4702 task updated)
- Tasks that run scripts or executables from temp, AppData, or ProgramData paths
- Task names that mimic legitimate Windows or vendor tasks
- Tasks running as SYSTEM that were created by a standard user session
- Tasks created remotely on another host
- New cron entries or at jobs on Linux hosts

## How to tell benign from malicious
- Benign: tasks created by installers, software updaters, backup agents, and RMM or management tools. They use known names, signed binaries, and standard install paths.
- Malicious: odd names, scripts in user-writable folders, encoded commands in the action, tasks created right after a suspicious login or phishing event, or creation by an unexpected account.

## Recommended triage steps
1. Record the task name, action, trigger, run-as account, and creator.
2. Check the executable or script: path, signature, hash, and contents.
3. Compare with known software on the host and with other hosts in the fleet.
4. Look at what happened just before creation (logon, script, download).
5. If malicious, disable and remove the task, then hunt for the dropped files and similar tasks elsewhere.

## Severity guidance
- Low: known vendor task from a standard install.
- Medium: unusual task, unsigned binary, no sign of harm yet.
- High: task runs encoded commands, downloads content, or was created remotely or by a compromised account.
