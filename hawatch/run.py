"""Entry point.  python -m hawatch.run [--validate-only] [--source ID]

One run: collect every source -> validate -> detect new/revised -> classify the changes -> write report,
state and health. Exits 1 if any source is unhealthy, after saving everything, so the scheduled job
shows red and GitHub notifies the owner.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import classify, state as st
from .collectors import CollectError, collect
from .validate import check

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--source")
    a = ap.parse_args(argv)
    sources = yaml.safe_load(open(ROOT / "sources.yaml"))["sources"]
    if a.source:
        sources = [s for s in sources if s["id"] == a.source]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    debug = ROOT / "debug"; debug.mkdir(exist_ok=True)
    state_path, health_path = ROOT / "state" / "state.json", ROOT / "state" / "health.json"
    state, prev_health = st.load(state_path), st.load(health_path)
    known = {v["source"] for v in state.values()}

    health, changes = [], []
    for src in sources:
        t0 = time.time()
        try:
            items, err = collect(src, debug), None
        except CollectError as e:
            items, err = [], str(e)
        except Exception as e:                      # never let one source kill the run
            items, err = [], f"{type(e).__name__}: {e}"
        h = check(src, items, err)
        h["seconds"] = round(time.time() - t0, 1)
        streak = prev_health.get(src["id"], {}).get("fail_streak", 0)
        h["fail_streak"] = 0 if h["ok"] else streak + 1
        health.append(h)
        print(f"[{'OK ' if h['ok'] else 'BAD'}] {src['id']:<14} {h['items']:>4} items {h['seconds']:>5}s  {'; '.join(h['problems'])}")
        if a.validate_only or not items:
            continue
        baseline = src["id"] not in known
        for status, it in st.diff(items, state, now, baseline=baseline):
            if status != st.UNCHANGED:
                changes.append({"status": status, **it.to_dict()})

    if a.validate_only:
        return 0 if all(h["ok"] for h in health) else 1

    key = os.environ.get("GEMINI_API_KEY")
    model = None
    if changes and key:
        labels, model = classify.llm_classify(changes, key)
    else:
        labels = [classify.rule_classify(c) for c in changes]
    for c, l in zip(changes, labels):
        c["assessment"] = l
    changes.sort(key=lambda c: (c["assessment"]["severity"], {"high": 0, "medium": 1, "low": 2}[c["assessment"]["relevance"]]))

    st.save(state_path, state)
    st.save(health_path, {h["source"]: h for h in health})
    run = {"run_at": now, "model": model or "rules", "health": health, "changes": changes}
    runs = ROOT / "reports" / "runs"; runs.mkdir(parents=True, exist_ok=True)
    (runs / f"{now.replace(':', '')}.json").write_text(json.dumps(run, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "reports" / "latest.md").write_text(render_report(run, len(state)), encoding="utf-8")
    print(f"{len(changes)} new or revised items; {len(state)} items tracked")
    return 0 if all(h["ok"] for h in health) else 1


def render_report(run, tracked):
    L = [f"# Health Authority Watch: run {run['run_at']}", "",
         f"Classifier: `{run['model']}` · items tracked: {tracked}", "", "## Source health", "",
         "| Source | Authority | Items | Time (s) | Status |", "|---|---|---|---|---|"]
    for h in run["health"]:
        status = "OK" if h["ok"] else "FAIL ({}) x{}".format("; ".join(h["problems"]), h["fail_streak"])
        L.append(f"| {h['source']} | {h['authority']} | {h['items']} | {h['seconds']} | {status} |")
    L += ["", f"## New and revised ({len(run['changes'])})", ""]
    if not run["changes"]:
        L.append("Nothing new since the last run.")
    else:
        L += ["| Severity | Relevance | Status | Authority | Title (English) | Why |", "|---|---|---|---|---|---|"]
        for c in run["changes"][:200]:
            a = c["assessment"]
            t = a["english_title"].replace("|", "/")
            L.append(f"| {a['severity']} | {a['relevance']} | {c['status']} | {c['authority']} | [{t}]({c['url']}) | {a['reason'].replace('|', '/')} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
