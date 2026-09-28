import ssl
import socket
import sys
from datetime import datetime, timezone

WARNING_DAYS = 30
CRITICAL_DAYS = 7


def get_cert_expiry(host, port=443, timeout=5):
    """Connect to a host over TLS and return its certificate expiry date."""
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls:
            cert = tls.getpeercert()
    expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
    return expiry.replace(tzinfo=timezone.utc)


def classify(days_left):
    """Turn days-left into a status, like a ticket priority."""
    if days_left <= CRITICAL_DAYS:
        return "CRITICAL"
    if days_left <= WARNING_DAYS:
        return "WARNING"
    return "OK"


def check_host(host):
    """Check one host and always return a result, even if the check fails."""
    try:
        expiry = get_cert_expiry(host)
        days_left = (expiry - datetime.now(timezone.utc)).days
        return {
            "host": host,
            "status": classify(days_left),
            "detail": f"{days_left} days left (expires {expiry:%Y-%m-%d})",
        }
    except ssl.SSLCertVerificationError as e:
        # Expired, self-signed or wrong-host certificates all land here
        return {"host": host, "status": "INVALID", "detail": e.verify_message}
    except (socket.timeout, socket.gaierror, ConnectionError, OSError) as e:
        return {"host": host, "status": "ERROR", "detail": f"could not connect ({e})"}


def load_hosts(path="sites.txt"):
    with open(path) as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


if __name__ == "__main__":
    results = [check_host(h) for h in load_hosts()]

    for r in results:
        print(f"[{r['status']:<8}] {r['host']:<35} {r['detail']}")

    problems = [r for r in results if r["status"] != "OK"]
    print(f"\nChecked {len(results)} hosts: {len(problems)} need attention")
    sys.exit(1 if problems else 0)