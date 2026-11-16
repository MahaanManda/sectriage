# Harbor Logistics: Asset Tiers and Severity Policy

Synthetic example policy for the fictional company Harbor Logistics.

## Asset tiers
- Tier 0 (identity and trust): DC01, DC02, PKI01, ADFS01.
- Tier 1 (business-critical servers and sensitive users): FS01, FS02, SQL01, BACKUP01, RMM01, JUMP01, NESS01, and all Finance workstations (names starting FIN-).
- Tier 2: all other workstations and servers.

## Sensitive users
Executives and Finance department staff are sensitive users. Privileged accounts are all adm_ and svc_ accounts.

## Severity for true positives (apply the first rule that matches)
1. Critical:
   - likely malicious activity on or targeting a Tier 0 asset
   - ransomware indicators on any host: shadow copy deletion outside backup tooling, mass file encryption, ransom notes
   - confirmed theft of regulated or customer data
2. High:
   - likely malicious activity on a Tier 1 asset
   - any malicious activity that uses a privileged account
   - compromise of an executive or Finance user account
3. Medium:
   - likely malicious activity on a Tier 2 host or standard user account
   - an unapproved remote-access tool running on any host
   - an upload of more than 500 MB to unapproved cloud storage
   - a successful sign-in from an unexpected country for a standard user
   - an approved tool acting outside its window with no valid ticket in the change register
4. Low: policy violation with no sign of compromise, such as unapproved software with no remote access or network exposure.

Benign activity is Informational. When a true positive meets several rules, use the highest.

## Handling by severity
- Critical: page the on-call analyst immediately and isolate the asset.
- High: respond within 1 hour.
- Medium: respond the same business day.
- Low: handle in the weekly review.
