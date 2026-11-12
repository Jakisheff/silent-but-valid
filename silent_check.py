#!/usr/bin/env python3
"""silent_check: advisory detector of silent-but-valid signals.

Checks places where agent pipelines report success while being wrong:
zero dispersion across a run series (quiet default), zero CI runs after a
push (merge-ref conflict looks like calm), and test files touched by a diff
(a weakened check looks like a passed check). Advisory only: a hit means
"signal is absent here", not "defect is present".
"""
import json
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def check_dispersion(paths, keys):
    series = {}
    for p in sorted(Path(paths).glob("*.json")):
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            return {"status": "error", "reason": f"{p}: {e}"}
        for key in keys:
            def dig(d, parts):
                for part in parts.split("."):
                    if isinstance(d, list) and part == "-":
                        d = d[-1] if d else None
                    elif isinstance(d, dict):
                        d = d.get(part)
                    else:
                        return None
                    if d is None:
                        return None
                return d
            value = dig(data, key)
            if value is None or isinstance(value, (list, dict)):
                continue
            series.setdefault(key, []).append((p.name, value))
    findings = []
    for key, values in series.items():
        distinct = {v for _, v in values}
        if len(values) >= 3 and len(distinct) == 1:
            findings.append({
                "check": "zero-dispersion", "metric": key,
                "runs": len(values), "distinct_values": list(distinct)[:1],
                "reading": "all runs report the identical value; a quiet "
                           "default or a frozen configuration is likely",
            })
    return {"status": "hit" if findings else "clean", "findings": findings}


def check_runs(repo, branch):
    ref = run(["gh", "api", f"repos/{repo}/git/ref/heads/{branch}",
               "--jq", ".object.sha"])
    if ref.returncode != 0:
        return {"status": "error", "reason": ref.stderr.strip()[:200]}
    sha = ref.stdout.strip()
    r = run(["gh", "api",
             f"repos/{repo}/commits/{sha}/check-runs",
             "-H", "Accept: application/vnd.github+json"])
    if r.returncode != 0:
        return {"status": "error", "reason": r.stderr.strip()[:200]}
    total = json.loads(r.stdout).get("total_count", 0)
    if total == 0:
        r2 = run(["gh", "api", f"repos/{repo}/compare/main...{branch}",
                  "--jq", ".status, .ahead_by, .behind_by"])
        return {"status": "hit", "findings": [{
            "check": "zero-runs", "repo": repo, "branch": branch, "sha": sha[:10],
            "reading": "no check runs exist for this head; for merge-ref CI "
                       "this usually means the branch conflicts with the "
                       "base and workflows never started",
            "compare": r2.stdout.strip() or "unavailable",
        }]}
    return {"status": "clean", "check_runs": total}


def check_touched(base="main"):
    r = run(["git", "diff", "--name-only", f"{base}...HEAD"])
    if r.returncode != 0:
        return {"status": "error", "reason": r.stderr.strip()[:200]}
    files = [f for f in r.stdout.split() if f]
    testish = [f for f in files if any(mark in f.lower() for mark in
               ("test", "spec", "__snapshots__", ".features"))]
    if testish:
        return {"status": "hit", "findings": [{
            "check": "tests-touched", "files": testish,
            "reading": "this diff modifies test material; verify the checks "
                       "were strengthened, not relaxed",
        }]}
    return {"status": "clean", "changed_files": len(files)}


def main(argv):
    usage = ("usage: silent_check.py dispersion <dir> <metric-key...>\n"
             "       silent_check.py runs <owner/repo> <branch>\n"
             "       silent_check.py touched [base]")
    if len(argv) < 2:
        print(usage, file=sys.stderr)
        return 2
    mode = argv[1]
    if mode == "dispersion" and len(argv) >= 4:
        report = check_dispersion(argv[2], argv[3:])
    elif mode == "runs" and len(argv) == 4:
        report = check_runs(argv[2], argv[3])
    elif mode == "touched" and len(argv) in (2, 3):
        report = check_touched(argv[2] if len(argv) == 3 else "main")
    else:
        print(usage, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=1))
    return 0 if report.get("status") == "clean" else (
        2 if report.get("status") == "error" else 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
