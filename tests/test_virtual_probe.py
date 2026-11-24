#!/usr/bin/env python3
"""How tests/test_virtual.py reads a probe, offline.

The external-href gate fails on a definite answer that the link is wrong and
only warns when the host does not answer. This replaces urlopen with a stub
and checks each case: 2xx is ok; a timeout, a DNS failure, a refused or reset
connection, a TLS failure, a malformed response and a 5xx warn; 404, 410 and
the other 4xx fail; VIRTUAL_STRICT turns every warning into a failure.

Run: python3 tests/test_virtual_probe.py
"""
import http.client
import socket
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import test_virtual as V  # noqa: E402

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


class Response:
    def __init__(self, status: int):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(url: str, code: int, reason: str) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, code, reason, {}, None)


BASE = "https://upstream.example"

# url -> what urlopen does, per method. A callable raises; an int answers.
CASES = {
    f"{BASE}/ok": {"HEAD": 200},
    f"{BASE}/head-refused": {"HEAD": 405, "GET": 206},
    f"{BASE}/timeout": {"HEAD": TimeoutError("timed out")},
    f"{BASE}/connect-timeout": {
        "HEAD": urllib.error.URLError(TimeoutError("timed out"))},
    f"{BASE}/dns": {"HEAD": urllib.error.URLError(
        socket.gaierror(-2, "Name or service not known"))},
    f"{BASE}/refused": {"HEAD": urllib.error.URLError(
        ConnectionRefusedError(111, "Connection refused"))},
    f"{BASE}/reset": {"HEAD": ConnectionResetError(
        104, "Connection reset by peer")},
    f"{BASE}/disconnected": {"HEAD": http.client.RemoteDisconnected(
        "Remote end closed connection without response")},
    f"{BASE}/bad-status": {"HEAD": http.client.BadStatusLine("garbage")},
    f"{BASE}/tls": {"HEAD": urllib.error.URLError(
        ssl.SSLError(1, "[SSL: WRONG_VERSION_NUMBER] wrong version number"))},
    f"{BASE}/unavailable": {"HEAD": 503},
    f"{BASE}/gateway": {"HEAD": 504},
    f"{BASE}/gone": {"HEAD": 410},
    f"{BASE}/missing": {"HEAD": 404},
    f"{BASE}/missing-after-get": {"HEAD": 405, "GET": 404},
    f"{BASE}/forbidden": {"HEAD": 403, "GET": 403},
}

WARN = {"timeout", "connect-timeout", "dns", "refused", "reset",
        "disconnected", "bad-status", "tls", "unavailable", "gateway"}
FAIL = {"gone", "missing", "missing-after-get", "forbidden"}
PASS = {"ok", "head-refused"}
assert WARN | FAIL | PASS == {u.rsplit("/", 1)[1] for u in CASES}

REASONS = {200: "OK", 206: "Partial Content", 403: "Forbidden",
           404: "Not Found", 405: "Method Not Allowed", 410: "Gone",
           503: "Service Unavailable", 504: "Gateway Timeout"}


def fake_urlopen(request, timeout=None):
    url, method = request.full_url, request.get_method()
    if url not in CASES:
        raise AssertionError(f"the stub was asked for {url}: no network here")
    outcome = CASES[url][method]
    if isinstance(outcome, BaseException):
        raise outcome
    if outcome >= 400:
        raise http_error(url, outcome, REASONS[outcome])
    return Response(outcome)


def name(url: str) -> str:
    return url.rsplit("/", 1)[1]


real_urlopen = urllib.request.urlopen
urllib.request.urlopen = fake_urlopen
try:
    hrefs = {url: f"collection.json rel:via {name(url)}" for url in CASES}
    lenient = V.check_hrefs(hrefs, strict=False)
    strict = V.check_hrefs(hrefs, strict=True)
    detail = {url: V.probe_detail(url) for url in CASES}
finally:
    urllib.request.urlopen = real_urlopen

# The classification itself.
check(V.classify(200) == V.OK, "200 is ok")
check(V.classify(206) == V.OK, "206 is ok")
check(V.classify(0) == V.UNREACHABLE, "no answer is unreachable")
check(V.classify(503) == V.UNREACHABLE, "503 is unreachable")
check(V.classify(404) == V.BROKEN, "404 is broken")
check(V.classify(410) == V.BROKEN, "410 is broken")
check(V.classify(403) == V.BROKEN, "403 is broken")
check(V.classify(301) == V.BROKEN, "a redirect that ends nowhere is broken")

# probe_detail reports the status and names the error.
check(detail[f"{BASE}/ok"] == (200, ""), f"ok: {detail[f'{BASE}/ok']}")
check(detail[f"{BASE}/head-refused"] == (206, ""),
      f"a 405 on HEAD retries with GET: {detail[f'{BASE}/head-refused']}")
check(detail[f"{BASE}/missing"] == (404, "HTTP 404 Not Found"),
      f"missing: {detail[f'{BASE}/missing']}")
check(detail[f"{BASE}/timeout"] == (0, "TimeoutError: timed out"),
      f"timeout: {detail[f'{BASE}/timeout']}")
check(detail[f"{BASE}/connect-timeout"] == (0, "TimeoutError: timed out"),
      f"connect timeout: {detail[f'{BASE}/connect-timeout']}")
check(detail[f"{BASE}/dns"][0] == 0
      and "gaierror" in detail[f"{BASE}/dns"][1],
      f"dns: {detail[f'{BASE}/dns']}")
check(detail[f"{BASE}/tls"][0] == 0
      and "SSLError" in detail[f"{BASE}/tls"][1],
      f"tls: {detail[f'{BASE}/tls']}")

# The gate: outages warn, definite answers fail, 2xx passes.
errs, warns, answered = lenient
check(answered == len(PASS), f"{answered} answered, want {len(PASS)}")
for url in CASES:
    in_errs = any(url in e for e in errs)
    in_warns = any(url in w for w in warns)
    if name(url) in WARN:
        check(in_warns and not in_errs, f"{name(url)} warns, not fails")
    elif name(url) in FAIL:
        check(in_errs and not in_warns, f"{name(url)} fails")
    else:
        check(not in_errs and not in_warns, f"{name(url)} passes")
timeout_warning = [w for w in warns if w.startswith(
    "collection.json rel:via timeout:")]
check(timeout_warning == [
    "collection.json rel:via timeout: https://upstream.example/timeout "
    "answers nothing (TimeoutError: timed out)"],
      f"the warning names the URL and the error: {timeout_warning}")
check(any("HTTP 404 Not Found" in e and f"{BASE}/missing " in e
          for e in errs), f"the 404 error names the URL and code: {errs}")

# VIRTUAL_STRICT: the outages fail as well.
errs, warns, answered = strict
check(not warns, f"strict mode warns about nothing: {warns}")
check(len(errs) == len(WARN) + len(FAIL),
      f"strict mode fails {len(errs)} href(s), want {len(WARN) + len(FAIL)}")
check(answered == len(PASS), "strict mode still passes the 2xx hrefs")

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)
print(f"OK: {len(CASES)} stubbed probes classified: {len(PASS)} ok, "
      f"{len(WARN)} warn, {len(FAIL)} fail; strict fails all {len(WARN) + len(FAIL)}")
