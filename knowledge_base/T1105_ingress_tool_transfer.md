# T1105 Ingress Tool Transfer

## What it is
Attackers bring tools or payloads into a compromised environment from outside, for example by downloading them from a server they control. Built-in tools are often used to avoid dropping obvious malware.

## Common indicators
- certutil -urlcache, bitsadmin, curl, wget, or PowerShell downloading files
- Downloads from unusual or newly registered domains and raw IP addresses
- Executables, DLLs, or scripts written to temp, ProgramData, or Public folders
- A process connecting out and then launching the downloaded file
- Downloads of unusual file types from services such as paste sites or file-sharing platforms
- Proxy or DNS logs showing a rare external destination

## How to tell benign from malicious
- Benign: patching and software updates from vendor domains, admin downloads of known tools, and package managers fetching from known repositories.
- Malicious: an Office or script process doing the download, a rare destination, a file executed immediately afterward, or a download by an account that does not normally install software.

## Recommended triage steps
1. Record the URL or IP, the process doing the download, and the file path.
2. Check the destination reputation and how many hosts contacted it.
3. Hash and analyze the downloaded file, or search for it in an intelligence source.
4. See whether the file executed and what it did next.
5. Block the destination and isolate the host if malicious.

## Severity guidance
- Low: known vendor update.
- Medium: unknown destination, file not executed.
- High: downloaded file executed, or download started by a document or script.
