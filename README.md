\# cert-expiry-watchdog



A small Python tool that checks TLS certificate expiry dates for a list of hosts and warns you \*\*before\*\* a certificate expires and takes a site down.



Uses only Python's standard library (`ssl`, `socket`), so there's nothing to install.



\## Why



An expired TLS certificate is one of the most avoidable outages there is: the date is known months in advance, yet it still catches teams out. This tool turns that date into an early warning.



\## How it works



1\. Reads hosts from `sites.txt` (one per line, `#` for comments)

2\. Opens a TLS connection to each host and reads its certificate

3\. Calculates the days left and assigns a status

4\. Prints a report and exits with code `1` if any host needs attention, so it can be dropped into a scheduled job or pipeline



| Status | Meaning |

|---|---|

| `OK` | More than 30 days left |

| `WARNING` | 8 to 30 days left |

| `CRITICAL` | 7 days or fewer left |

| `INVALID` | Certificate expired, self-signed or wrong host |

| `ERROR` | Could not connect (DNS failure, timeout) |



One failing host never stops the run. Every host always gets a result.



\## Usage



```bash

python watchdog.py

```



\## Example output



```

\[OK      ] github.com                          62 days left (expires 2026-11-29)

\[OK      ] google.com                          66 days left (expires 2026-12-03)

\[INVALID ] expired.badssl.com                  certificate has expired

\[ERROR   ] this-host-does-not-exist.example    could not connect (\[Errno 11001] getaddrinfo failed)



Checked 4 hosts: 2 need attention

```



\## Future improvements



\- Send WARNING and CRITICAL results to Slack or Teams

\- Run on a schedule with GitHub Actions or cron

\- JSON output for log aggregators

\- Configurable thresholds per host

