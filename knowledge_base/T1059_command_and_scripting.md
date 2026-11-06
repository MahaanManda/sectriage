# T1059 Command and Scripting Interpreter

## What it is
Attackers use built-in interpreters to run commands and scripts: PowerShell, Windows Command Shell (cmd.exe), VBScript, JavaScript, Python, and Unix shells. These tools are already on the machine, so no malware file is needed. Related sub-techniques include T1059.001 (PowerShell) and T1059.003 (Windows Command Shell).

## Common indicators
- cmd.exe or PowerShell launched by Office apps, browsers, or PDF readers
- Long, obfuscated, or encoded command lines
- Scripts run from temp or user-download folders
- Commands that download files, disable security tools, or enumerate the network
- wscript.exe or cscript.exe running scripts from email attachments
- Windows event 4688 or EDR process-creation logs showing unusual parent-child chains

## How to tell benign from malicious
- Benign: admin scripts from a management tool, login scripts, build and deployment tasks, and developers running scripts on their own workstations.
- Malicious: an unusual parent process, a script run by a user who never scripts, obfuscation with no business reason, or activity shortly after an email click.

## Recommended triage steps
1. Capture the full command line, parent process, user, and host.
2. Decode or deobfuscate the content and read what it does.
3. Check whether the script file is signed or from a known path.
4. Look for follow-on activity: network connections, downloaded files, new services or tasks.
5. If malicious, isolate the host and preserve evidence.

## Severity guidance
- Low: known script from a known tool.
- Medium: unusual but unconfirmed activity from a standard user.
- High: download-and-execute behavior, Office parent process, or evidence of persistence.
