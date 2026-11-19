#!/usr/bin/env python3
"""Zero-dependency CLI (v1.2.0) for SPFGuard RFC 7208 10-Lookup Analyzer & CIDR Flattener (JSON + SARIF v2.1.0)."""
import argparse, json, pathlib, sys, urllib.request

EDGE_URL = "https://specgate.profalexandrezamboni.workers.dev/api/v1/spfguard/analyze"

def main() -> int:
    p = argparse.ArgumentParser(description="SPFGuard RFC 7208 10-Lookup Gate (v1.2.0)")
    p.add_argument("--domain", default="example.com", help="Domain name")
    p.add_argument("--spf", default="", help="Inline SPF TXT string")
    p.add_argument("--spf-file", default="", help="Path to file containing SPF TXT string")
    p.add_argument("--format", choices=("json", "sarif"), default="json", help="Output format: json or OASIS sarif v2.1.0")
    args, _ = p.parse_known_args()
    spf_txt = args.spf or (pathlib.Path(args.spf_file).read_text(encoding="utf-8").strip() if args.spf_file else "")
    payload = {"domain": args.domain, "spf_record": spf_txt or "v=spf1 -all", "resolve_live_dns": not bool(spf_txt), "format": args.format}
    target_url = EDGE_URL + ("?format=sarif" if args.format == "sarif" else "")
    req = urllib.request.Request(target_url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "User-Agent": "spfguard-cli/1.2.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    print(json.dumps(res, indent=2))
    exceeds = (res.get("runs", [{}])[0].get("properties", {}).get("verdict") == "FAIL_PERMERROR_RISK") if args.format == "sarif" else bool(res.get("exceeds_rfc7208_limit"))
    if exceeds:
        print(f"\n[SPFGuard] RFC 7208 10-lookup ceiling exceeded! Automate multi-domain CIDR flattening ($19/mo Starter · $39/mo Team): https://specgate.profalexandrezamboni.workers.dev/#pricing", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
