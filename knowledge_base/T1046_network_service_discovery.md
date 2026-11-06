# T1046 Network Service Discovery

## What it is
Attackers scan the network to find hosts, open ports, and services they can attack next. It happens early after getting a foothold, and is often followed by lateral movement.

## Common indicators
- One host connecting to many IPs on the same port in a short time
- One host connecting to many ports on one target
- Use of nmap, masscan, advanced IP scanner, or built-in tools
- Spikes in failed connections or firewall denies from one internal host
- Scans from a workstation that is not an IT or security machine
- IDS signatures for port scans

## How to tell benign from malicious
- Benign: approved vulnerability scanners, network monitoring and inventory tools, and RMM discovery jobs. These run from known hosts and often on a schedule.
- Malicious: scanning from a user workstation, a server that never scans, scanning at unusual times, or scanning right after other suspicious activity on the same host.

## Recommended triage steps
1. Identify the source host, tool, account, and scan scope.
2. Compare against the scanner inventory and the vulnerability scan schedule.
3. Check the host for what launched the scanner and for earlier compromise signs.
4. Look for follow-up activity against discovered services.
5. Isolate the host if unexplained.

## Severity guidance
- Low: approved scanner or known tool.
- Medium: unexplained scan from a standard host.
- High: scan followed by remote login attempts, exploit traffic, or credential theft.
