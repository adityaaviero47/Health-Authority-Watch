"""Collectors: one per kind of source. Each returns a list of Items or raises CollectError.

The network layer is a single `fetch()` so tests can feed saved responses instead.
"""
import json
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from defusedxml import ElementTree as ET

from .items import Item, normalise

UA = "HealthAuthorityWatch/1.0 (+https://github.com/adityaaviero47/Health-Authority-Watch)"


class CollectError(RuntimeError):
    pass


def fetch(url, params=None, retries=3, timeout=30):
    """GET with retries and exponential backoff; raises CollectError with the last reason."""
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": UA})
            if r.status_code == 200:
                r.encoding = r.encoding or r.apparent_encoding
                return r.text
            last = f"HTTP {r.status_code}"
            if r.status_code in (400, 401, 403, 404):
                break
        except requests.RequestException as e:
            last = type(e).__name__
        time.sleep(2 ** attempt)
    raise CollectError(f"{url}: {last}")


def render(url, wait_ms=4000):
    """Load a page in headless Chromium so content built by JavaScript is present."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise CollectError("playwright not installed") from e
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=UA)
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(wait_ms)
        html = page.content()
        browser.close()
    return html


def iso(dt_text):
    """Best-effort date parse to YYYY-MM-DD (RFC 822, ISO 8601 or YYYYMMDD)."""
    if not dt_text:
        return ""
    t = dt_text.strip()
    for f in (lambda x: parsedate_to_datetime(x),
              lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")),
              lambda x: datetime.strptime(x, "%Y%m%d"),
              lambda x: datetime.strptime(x, "%d/%m/%Y")):
        try:
            return f(t).date().isoformat()
        except (ValueError, TypeError, IndexError):
            continue
    return ""


# ---------------------------------------------------------------- parsers (pure, unit-tested)

def parse_openfda(text, src):
    data = json.loads(text)
    items = []
    for r in data.get("results", []):
        title = f"{r.get('classification', '')} recall: {normalise(r.get('product_description', ''))[:160]}"
        items.append(Item(
            source_id=src["id"], authority=src["authority"], language=src["language"],
            url=f"https://api.fda.gov/drug/enforcement.json?search=recall_number:\"{r.get('recall_number', '')}\"",
            title=title, published=iso(r.get("report_date", "")), summary=normalise(r.get("reason_for_recall", "")),
            extra={"native_id": r.get("recall_number", ""), "fda_class": r.get("classification", ""),
                   "firm": r.get("recalling_firm", "")},
            watch={"status": r.get("status", ""), "classification": r.get("classification", ""),
                   "termination_date": r.get("termination_date", "")}))
    return items


def parse_govuk(text, src):
    data = json.loads(text)
    items = []
    for r in data.get("results", []):
        link = r.get("link", "")
        items.append(Item(
            source_id=src["id"], authority=src["authority"], language=src["language"],
            url=urljoin("https://www.gov.uk", link), title=normalise(r.get("title", "")),
            published=iso(r.get("public_timestamp", "")), updated=r.get("public_timestamp", ""),
            summary=normalise(r.get("description", "")),
            extra={"native_id": link, "format": r.get("format", "") or r.get("content_store_document_type", "")}))
    return items


def parse_rss(text, src):
    """RSS 2.0 or Atom."""
    try:
        root = ET.fromstring(text.encode("utf-8") if isinstance(text, str) else text)
    except ET.ParseError as e:
        raise CollectError(f"feed did not parse: {e}") from e
    ns = {"a": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}
    items = []
    for it in root.iter("item"):
        g = lambda tag: (it.findtext(tag) or "").strip()
        desc = BeautifulSoup(g("description"), "lxml").get_text(" ") if g("description") else ""
        items.append(Item(source_id=src["id"], authority=src["authority"], language=src["language"],
                          url=g("link"), title=normalise(g("title")), published=iso(g("pubDate") or it.findtext("dc:date", "", ns)),
                          summary=normalise(desc)[:600], extra={"native_id": g("guid") or g("link")}))
    for e in root.iter("{http://www.w3.org/2005/Atom}entry"):
        link = e.find("a:link", ns)
        items.append(Item(source_id=src["id"], authority=src["authority"], language=src["language"],
                          url=link.get("href", "") if link is not None else "", title=normalise(e.findtext("a:title", "", ns)),
                          published=iso(e.findtext("a:published", "", ns) or e.findtext("a:updated", "", ns)),
                          updated=e.findtext("a:updated", "", ns) or "",
                          summary=normalise(BeautifulSoup(e.findtext("a:summary", "", ns) or "", "lxml").get_text(" "))[:600],
                          extra={"native_id": e.findtext("a:id", "", ns)}))
    return items


DATE_RE = re.compile(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{4}|\d{4}-\d{2}-\d{2})\b")


def row_date(t):
    """'12.03.2026', '12-03-2026', '12/03/2026' (day first) or '2026-03-12' -> ISO date."""
    return t if re.match(r"\d{4}-", t) else iso(re.sub(r"[.-]", "/", t))


def parse_html_links(html, src):
    """Generic list-page extractor: keep links matching the source's pattern, take the row text as title."""
    soup = BeautifulSoup(html, "lxml")
    for bad in soup(["script", "style", "nav", "header", "footer"]):
        bad.decompose()
    pat = re.compile(src.get("link_pattern", r"\.pdf($|\?)"), re.I)
    seen, items = set(), []
    for a in soup.find_all("a", href=True):
        href = urljoin(src["url"], a["href"].strip())
        if not pat.search(href) or href in seen or href.rstrip("/") == src["url"].rstrip("/"):
            continue
        row = a.find_parent(["tr", "li"]) or a
        text = normalise(row.get_text(" "))
        title = normalise(a.get_text(" ")) or text
        if len(title) < 8 or title.lower() in {"download", "view", "pdf", "click here"}:
            title = text
        if len(title) < 8:
            continue
        m = DATE_RE.search(text)
        seen.add(href)
        items.append(Item(source_id=src["id"], authority=src["authority"], language=src["language"], url=href,
                          title=title[:300], published=row_date(m.group(1)) if m else "",
                          summary=text[:600] if text != title else ""))
    return items


# ---------------------------------------------------------------- collectors (network)

def collect(src, debug_dir=None):
    kind = src["kind"]
    if kind == "openfda":
        since = (datetime.now(timezone.utc) - timedelta(days=src.get("days", 120))).strftime("%Y%m%d")
        text = fetch(src["url"], params={"search": f"report_date:[{since} TO 29991231]",
                                         "sort": "report_date:desc", "limit": src.get("limit", 100)})
        return parse_openfda(text, src)
    if kind == "govuk":
        text = fetch(src["url"], params={"filter_organisations": src["organisation"], "order": "-public_timestamp",
                                         "count": src.get("limit", 50),
                                         "fields": "title,link,public_timestamp,description,format,content_store_document_type"})
        return parse_govuk(text, src)
    if kind == "rss":
        text = fetch(src["url"])
        items = parse_rss(text, src)
        if not items and debug_dir:
            (debug_dir / f"{src['id']}.xml").write_text(text, encoding="utf-8")
        return items
    if kind == "html_links":
        html = render(src["url"]) if src.get("render") == "browser" else fetch(src["url"])
        items = parse_html_links(html, src)
        if len(items) < src.get("min_items", 1) and debug_dir:
            (debug_dir / f"{src['id']}.html").write_text(html, encoding="utf-8")
        return items
    raise CollectError(f"unknown kind {kind}")
