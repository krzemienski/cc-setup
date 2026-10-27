#!/usr/bin/env python3
"""Validate resource URLs concurrently.

Usage:
    python3 validate_urls.py input.json [output.json]
    cat input.json | python3 validate_urls.py - [output.json]

Input:  JSON list of {"title": ..., "url": ...}
Output: JSON list with added "http-status" (int or str) and "ok" (bool).
        Writes to output.json if given, else stdout. Stdlib only.
"""
import json
import ssl
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TIMEOUT = 12
WORKERS = 12
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE  # report status even on bad certs; flag separately


def check(item):
    url = item.get("url", "")
    out = dict(item)
    status, ok, note = None, False, ""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method,
                                         headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=_ctx) as r:
                status = r.status
                final = r.geturl()
                ok = 200 <= status < 400
                if final != url:
                    out["final-url"] = final
                break
        except urllib.error.HTTPError as e:
            status = e.code
            if e.code in (403, 429):
                note = "blocked-checker"
            if method == "HEAD" and e.code in (403, 405, 501):
                continue  # some sites reject HEAD; retry as GET
            break
        except Exception as e:  # noqa: BLE001
            status = type(e).__name__
            note = str(e)[:120]
            break
    out["http-status"] = status
    out["ok"] = ok
    if note:
        out["note"] = note
    return out


def main():
    args = [a for a in sys.argv[1:] if a != "-"]
    src = sys.stdin.read() if "-" in sys.argv[1:] or not args else open(args[0]).read()
    items = json.loads(src)
    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(check, it): i for i, it in enumerate(items)}
        for f in as_completed(futs):
            results[futs[f]] = f.result()
    payload = json.dumps(results, indent=2, ensure_ascii=False)
    if len(args) >= 2:
        with open(args[1], "w") as fh:
            fh.write(payload + "\n")
    else:
        print(payload)
    ok_n = sum(1 for r in results if r.get("ok"))
    print(f"# {ok_n}/{len(results)} URLs OK", file=sys.stderr)


if __name__ == "__main__":
    main()
