# Playbook: Suspicious PowerShell Activity

## What it is
PowerShell is a legitimate admin tool that attackers also use to run code, download payloads and move around a network. The goal is to separate routine administration from abuse.

## Common indicators
- Encoded commands (`-EncodedCommand`, `-enc`) or long base64 strings
- `-ExecutionPolicy Bypass`, `-WindowStyle Hidden`, `-NoProfile` used together
- Commands that download and run content (`DownloadString`, `Invoke-WebRequest` piped to `Invoke-Expression`)
- PowerShell launched by Word, Excel or a browser rather than by a user or admin tool
- Connections to rarely seen external hosts

## How to tell benign from malicious
- Benign: scripts run by IT management tools, scheduled maintenance, signed scripts from known paths, and activity from an admin account during business hours.
- Malicious: encoded or obfuscated commands, an unusual parent process, a user account that never uses PowerShell, or activity right after a phishing event.

## Recommended triage steps
1. Capture the full command line and the parent process.
2. Decode any encoded content and read what it does.
3. Check the user, host and time against normal behavior.
4. Look for network connections, dropped files and persistence such as scheduled tasks.
5. If malicious, isolate the host, preserve evidence, and reset affected credentials.

## Severity guidance
- Low: signed admin script from a known tool.
- Medium: unusual but unconfirmed, such as unexpected encoded commands on a standard user's machine.
- High: download-and-execute behavior, an Office parent process, or signs of persistence or lateral movement.