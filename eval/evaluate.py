"""Accuracy test for the severity classifier, using FDA's official recall class as the ground truth.

Pulls drug recalls reported in the last 365 days, samples N per class (Class I / II / III), hides the class,
and asks both the keyword baseline and the LLM to predict severity (1/2/3) from the product and reason text.
Writes eval/results.json and eval/predictions.csv.   Usage: python eval/evaluate.py [--per-class 50]
"""
import argparse, csv, json, os, random, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hawatch.collectors import fetch, parse_openfda   # noqa: E402
from hawatch import classify                           # noqa: E402

CLASS_TO_SEV = {"Class I": 1, "Class II": 2, "Class III": 3}


def metrics(y, p):
    acc = sum(a == b for a, b in zip(y, p)) / len(y)
    f1s, per = [], {}
    for k in (1, 2, 3):
        tp = sum(a == k and b == k for a, b in zip(y, p)); fp = sum(a != k and b == k for a, b in zip(y, p))
        fn = sum(a == k and b != k for a, b in zip(y, p))
        prec = tp / (tp + fp) if tp + fp else 0.0; rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        f1s.append(f1); per[k] = {"precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3)}
    conf = {f"true{a}": {f"pred{b}": sum(x == a and z == b for x, z in zip(y, p)) for b in (1, 2, 3)} for a in (1, 2, 3)}
    return {"accuracy": round(acc, 3), "macro_f1": round(sum(f1s) / 3, 3), "per_class": per, "confusion": conf}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--per-class", type=int, default=50); a = ap.parse_args()
    src = {"id": "fda_recalls", "authority": "US FDA", "language": "en"}
    since = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y%m%d")
    rng = random.Random(42)
    sample = []
    for cls in CLASS_TO_SEV:
        text = fetch("https://api.fda.gov/drug/enforcement.json",
                     params={"search": f'report_date:[{since} TO 29991231] AND classification:"{cls}"', "limit": 1000})
        items = parse_openfda(text, src)
        uniq = {i.item_id: i for i in items}.values()
        sample += rng.sample(list(uniq), min(a.per_class, len(uniq)))
    rows = []
    for it in sample:
        d = it.to_dict()
        d["title"] = d["title"].split(" recall: ", 1)[-1]          # hide the class that the title carries
        rows.append(d)
    y = [CLASS_TO_SEV[r["extra"]["fda_class"]] for r in rows]
    rule = [classify.rule_classify(r)["severity"] for r in rows]
    out = {"n": len(rows), "per_class": a.per_class, "window_days": 365, "rules": metrics(y, rule)}
    key = os.environ.get("GEMINI_API_KEY")
    llm = None
    if key:
        labels, model = classify.llm_classify(rows, key)
        llm = [l["severity"] for l in labels]
        out["llm"] = metrics(y, llm); out["model"] = model
        out["llm_fallback_items"] = sum(1 for l in labels if l["by"] != "llm")
    (ROOT / "eval" / "results.json").write_text(json.dumps(out, indent=2))
    with open(ROOT / "eval" / "predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["recall_number", "fda_class", "rule_severity", "llm_severity", "product", "reason"])
        for i, r in enumerate(rows):
            w.writerow([r["extra"]["native_id"], r["extra"]["fda_class"], rule[i], llm[i] if llm else "", r["title"][:200], r["summary"][:300]])
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
