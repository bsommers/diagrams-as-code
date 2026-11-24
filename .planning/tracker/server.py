#!/usr/bin/env python3
"""Local work tracker: live Gantt of agents, progress, key files. stdlib only."""
import glob, json, os, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
CFG = HERE / "agents.json"
OK_EXT = {".svg", ".png", ".md", ".txt", ".json", ".py"}
_cache = {}


def cached(key, ttl, fn):
    now = time.time()
    if key in _cache and now - _cache[key][0] < ttl:
        return _cache[key][1]
    _cache[key] = (now, fn())
    return _cache[key][1]


def sh(args, cwd=None):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return ""


def worktrees(repo):
    out, cur = {}, {}
    for line in sh(["git", "worktree", "list", "--porcelain"], repo).splitlines() + [""]:
        if not line:
            if cur.get("worktree"):
                out[Path(cur["worktree"]).name] = cur
            cur = {}
        else:
            k, _, v = line.partition(" ")
            cur[k] = v
    return out


def agent_state(a, cfg, wts):
    tdir = Path(cfg["tasks_dir"])
    f = tdir / f"{a['id']}.output"
    st = f.stat() if f.exists() else None
    start = getattr(st, "st_birthtime", st.st_ctime) if st else None
    last = st.st_mtime if st else None
    status = a["status"]
    res = {"id": a["id"], "name": a["name"], "model": a["model"], "kind": a["kind"],
           "status": status.upper(), "start": start, "last_activity": last,
           "end": last if status == "done" else None}
    wt = wts.get("agent-" + a["id"][:17]) or wts.get("agent-" + a["id"])
    res["branch"], res["worktree"], res["commits"], res["files"], res["svgs"] = None, None, 0, [], []
    pct = 100 if status == "done" else 0
    if wt:
        path = Path(wt["worktree"])
        res["worktree"] = str(path)
        res["branch"] = wt.get("branch", "").replace("refs/heads/", "")
        res["commits"] = int((sh(["git", "rev-list", "--count", f"{cfg['base']}..HEAD"], path).strip() or 0))
        names = set(sh(["git", "diff", "--name-only", cfg["base"]], path).split())
        for ln in sh(["git", "status", "--porcelain", "-uall"], path).splitlines():
            names.add(ln[3:].strip())
        names = sorted(n for n in names if n and not n.startswith(".claude"))
        res["files"] = names[:60]
        res["svgs"] = [n for n in names if n.endswith(".svg")][:24]
        if status != "done":
            if a["kind"] == "gallery":
                n = len(glob.glob(str(path / "examples" / a["domain"] / "[0-9]*.py")))
                pct = min(95, int(100 * n / a["target"]))
            elif a["kind"] == "primitive":
                hit = sum(1 for c in a["checks"] if glob.glob(str(path / c)))
                pct = min(95, int(100 * hit / len(a["checks"])))
            if res["commits"] and status != "done":
                pct = max(pct, 90)
    res["progress"] = pct
    return res


def state():
    cfg = json.loads(CFG.read_text())
    wts = cached("wt", 5, lambda: worktrees(cfg["repo"]))
    agents = [cached("a" + a["id"], 3, lambda a=a: agent_state(a, cfg, wts)) for a in cfg["agents"]]
    prs = cached("prs", 30, lambda: json.loads(sh(
        ["gh", "pr", "list", "-R", cfg["prs"], "--state", "all", "--limit", "20",
         "--json", "number,title,state,headRefName,url"]) or "[]"))
    return {"now": time.time(), "agents": agents, "key_files": cfg["key_files"], "prs": prs,
            "started_at": min((a["start"] for a in agents if a["start"]), default=time.time())}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        ip = self.client_address[0]
        if not (ip.startswith("192.168.") or ip in ("127.0.0.1", "::1")):
            return self._send(403, b"forbidden: LAN clients only", "text/plain")
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if u.path == "/api/state":
            return self._send(200, json.dumps(state()).encode(), "application/json")
        if u.path == "/file":
            cfg = json.loads(CFG.read_text())
            p = Path(parse_qs(u.query).get("path", [""])[0]).resolve()
            roots = [Path(cfg["repo"]).resolve(), Path(cfg["tasks_dir"]).resolve().parents[0]]
            if p.suffix in OK_EXT and p.is_file() and any(r in p.parents for r in roots):
                ct = {".svg": "image/svg+xml", ".png": "image/png"}.get(p.suffix, "text/plain; charset=utf-8")
                return self._send(200, p.read_bytes(), ct)
        self._send(404, b"not found", "text/plain")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"work tracker on 0.0.0.0:{port} (LAN clients 192.168.x.x only)", flush=True)
    ThreadingHTTPServer((os.environ.get("TRACKER_HOST", "0.0.0.0"), port), H).serve_forever()
