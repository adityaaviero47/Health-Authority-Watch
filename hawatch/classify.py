"""Relevance and severity classification: an LLM (Gemini) with reasons, and a keyword baseline to beat.

Output per item: relevance (high/medium/low), severity (1 = most serious .. 3), category, english_title, reason.
"""
import json
import os
import re
import time

import requests

CATEGORIES = ["recall", "safety_alert", "approval", "guidance", "enforcement", "shortage", "other"]
PROMPT = """You triage health-authority publications for a pharma regulatory-intelligence team.
For each item return a JSON object with:
 "id": the item id given,
 "relevance": "high" | "medium" | "low"  (for a team tracking medicines safety and compliance),
 "severity": 1 | 2 | 3  (1 = could cause serious harm or death, 2 = temporary or reversible harm, 3 = unlikely to cause harm),
 "category": one of %s,
 "english_title": the title translated to English (copy it if already English),
 "reason": one short sentence explaining the severity.
Return a JSON array only, one object per item, in the same order.
Items:
%s"""

SEVERE = re.compile(r"death|fatal|life-threatening|serious (adverse|injur|harm)|sterility|steril|contaminat|"
                    r"microbial|bacteria|fung|endotoxin|particulate|glass|overdose|wrong (drug|strength)|"
                    r"mislabel|label mix|undeclared|cgmp|subpotent|superpotent|anaphyla|mortal|grave", re.I)
MINOR = re.compile(r"labeling|labelling|packag|carton|discolor|odor|out of specification.*(appearance|color)|"
                   r"failed dissolution|impurit|stability|degradation|missing (lot|exp)|typo", re.I)


def rule_classify(item):
    """Keyword baseline: the bar the LLM must clear."""
    text = f"{item['title']} {item.get('summary', '')}"
    sev = 1 if SEVERE.search(text) and not MINOR.search(text) else 3 if MINOR.search(text) else 2
    cat = "recall" if re.search(r"recall|retirada", text, re.I) else "safety_alert" if re.search(r"safety|seguridad|alert", text, re.I) else "other"
    rel = "high" if sev == 1 else "medium" if sev == 2 else "low"
    return {"id": item["item_id"], "relevance": rel, "severity": sev, "category": cat,
            "english_title": item["title"], "reason": "keyword rule", "by": "rules"}


def pick_model(key):
    """Use GEMINI_MODEL if set, else the newest available flash-lite / flash model."""
    if os.environ.get("GEMINI_MODEL"):
        return os.environ["GEMINI_MODEL"]
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models", params={"key": key}, timeout=30)
    names = [m["name"].split("/")[-1] for m in r.json().get("models", [])
             if "generateContent" in m.get("supportedGenerationMethods", [])]
    for want in ("flash-lite-latest", "flash-latest", "flash-lite", "flash"):
        hit = [n for n in names if n.endswith(want) or want in n]
        if hit:
            return sorted(hit)[-1]
    raise RuntimeError("no Gemini flash model available for this key")


def llm_classify(items, key, model=None, batch=20, pause=4.5):
    """Classify in batches; on any failure for a batch, fall back to the rule baseline for that batch."""
    model = model or pick_model(key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    out = []
    for i in range(0, len(items), batch):
        chunk = items[i:i + batch]
        lines = "\n".join(json.dumps({"id": it["item_id"], "authority": it["authority"], "language": it["language"],
                                      "title": it["title"], "summary": it.get("summary", "")[:500]}, ensure_ascii=False)
                          for it in chunk)
        body = {"contents": [{"parts": [{"text": PROMPT % (CATEGORIES, lines)}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
        res = None
        for attempt in range(4):
            try:
                r = requests.post(url, params={"key": key}, json=body, timeout=120)
                if r.status_code == 200:
                    res = parse_llm(r.json(), chunk)
                    break
                if r.status_code in (429, 500, 503):
                    time.sleep(10 * (attempt + 1)); continue
                break
            except (requests.RequestException, ValueError, KeyError):
                time.sleep(5)
        out += res if res else [rule_classify(it) for it in chunk]
        time.sleep(pause)
    return out, model


def parse_llm(resp, chunk):
    """Validate the model's JSON: right ids, allowed values; anything malformed falls back to rules."""
    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    arr = json.loads(text)
    by_id = {str(o.get("id")): o for o in arr if isinstance(o, dict)}
    out = []
    for it in chunk:
        o = by_id.get(it["item_id"])
        ok = (o and o.get("relevance") in ("high", "medium", "low") and str(o.get("severity")) in ("1", "2", "3"))
        if not ok:
            out.append(rule_classify(it)); continue
        out.append({"id": it["item_id"], "relevance": o["relevance"], "severity": int(o["severity"]),
                    "category": o.get("category") if o.get("category") in CATEGORIES else "other",
                    "english_title": str(o.get("english_title") or it["title"])[:300],
                    "reason": str(o.get("reason", ""))[:300], "by": "llm"})
    return out
