# Playbook: Possible Data Exfiltration

## What it is
Large or unusual transfers of data out of the environment may mean an attacker is stealing information. The goal is to decide what was sent, where, and whether it was authorized.

## Common indicators
- Large outbound transfers to a rare destination or personal cloud storage
- Use of archiving tools (zip, 7z, rar) just before the transfer
- Data sent to file-sharing services, paste sites, or unusual ports
- Use of tools like rclone, WinSCP, or MEGA clients
- Transfers at unusual hours or from servers that do not normally upload
- Access to many files or a database dump just before the transfer

## How to tell benign from malicious
- Benign: approved backups and cloud syncs, software updates, large business file shares with known partners, and developers pushing to approved repositories.
- Malicious: unapproved destinations, personal accounts, staging of data in a temp folder, or transfers right after credential theft or lateral movement.

## Recommended triage steps
1. Identify the source host, account, destination, volume, and time.
2. Confirm whether the destination and the transfer are approved.
3. Determine what data was involved and how sensitive it is.
4. Block the destination and disable the account or session if unexplained.
5. Look for earlier compromise: credential theft, remote access, tools dropped.
6. Escalate to incident response and, if sensitive data is involved, to legal or compliance.

## Severity guidance
- Low: approved transfer confirmed.
- Medium: unexplained but small, non-sensitive.
- High: large or sensitive data to an unapproved destination.
- Critical: confirmed theft of sensitive or regulated data.
