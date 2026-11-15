#!/usr/bin/env python3
"""Zero-dependency CLI for SPFGuard RFC 7208 10-Lookup Analyzer & CIDR Flattener."""
import argparse, json, pathlib, sys, urllib.request

EDGE_URL = "https://specgate.profalexandrezamboni.workers.dev/api/v1/spfguard/analyze"

def main() -> int:
    p = argparse.ArgumentParser(description="SPFGuard RFC 7208 10-Lookup Gate")
    p.add_argument("--domain", default="example.com", help="Domain name")
    p.add_argument("--spf", default="", help="Inline SPF TXT string")
    p.add_argument("--spf-file", default="", help="Path to file containing SPF TXT string")
    args, _ = p.parse_known_args()
    spf_txt = args.spf or (pathlib.Path(args.spf_file).read_text(encoding="utf-8").strip() if args.spf_file else "")
    payload = {"domain": args.domain, "spf_record": spf_txt or "v=spf1 -all", "resolve_live_dns": not bool(spf_txt)}
    req = urllib.request.Request(EDGE_URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "User-Agent": "spfguard-cli/1.1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    print(json.dumps(res, indent=2))
    if res.get("exceeds_rfc7208_limit"):
        print(f"\n[SPFGuard] RFC 7208 10-lookup ceiling exceeded! Automate multi-domain CIDR flattening ($19/mo Starter · $39/mo Team): https://specgate.profalexandrezamboni.workers.dev/#pricing", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
