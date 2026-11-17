"""Change detection: compare this run's items with the saved state and label each NEW, REVISED or UNCHANGED."""
import json
from pathlib import Path

NEW, REVISED, UNCHANGED = "new", "revised", "unchanged"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def save(path: Path, state: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def diff(items, state: dict, now: str, baseline: bool = False):
    """Return [(status, item)] and update `state` in place.

    baseline=True (a source's first run) records items without flagging them as new,
    so onboarding a source does not flood the report with its whole back catalogue.
    """
    out, seen = [], set()
    for it in items:
        iid, fp = it.item_id, it.fingerprint()
        if iid in seen:                        # duplicate within one run (same link listed twice)
            continue
        seen.add(iid)
        old = state.get(iid)
        if old is None:
            status = UNCHANGED if baseline else NEW
            state[iid] = {"fp": fp, "title": it.title, "url": it.url, "source": it.source_id,
                          "first_seen": now, "last_changed": now, "revisions": 0}
        elif old["fp"] != fp:
            status = REVISED
            old.update(fp=fp, title=it.title, last_changed=now, revisions=old.get("revisions", 0) + 1)
        else:
            status = UNCHANGED
        state[iid]["last_seen"] = now
        out.append((status, it))
    return out
