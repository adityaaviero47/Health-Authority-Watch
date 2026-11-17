"""Source validation: the checks a new source must pass before it is onboarded, and every run after."""
from collections import Counter


def check(src, items, error=None):
    """Return a health record: ok flag plus the reasons it failed."""
    problems = []
    n = len(items)
    if error:
        problems.append(f"collect failed: {error}")
    if n < src.get("min_items", 1):
        problems.append(f"only {n} items (min {src.get('min_items', 1)})")
    if n:
        no_title = sum(1 for i in items if len(i.title) < 8)
        no_url = sum(1 for i in items if not i.url.startswith("http"))
        dated = sum(1 for i in items if i.published)
        dupes = sum(c - 1 for c in Counter(i.item_id for i in items).values() if c > 1)
        if no_title / n > 0.1:
            problems.append(f"{no_title}/{n} items lack a usable title")
        if no_url:
            problems.append(f"{no_url}/{n} items lack a URL")
        if dated / n < 0.5:
            problems.append(f"only {dated}/{n} items carry a date")
        if dupes:
            problems.append(f"{dupes} duplicate ids")
    return {"source": src["id"], "authority": src["authority"], "items": n, "ok": not problems, "problems": problems}
