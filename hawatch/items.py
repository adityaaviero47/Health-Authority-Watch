"""The common record every collector produces, plus text normalisation and content hashing."""
import hashlib
import re
import unicodedata
from dataclasses import dataclass, field, asdict


@dataclass
class Item:
    source_id: str
    authority: str
    language: str
    url: str
    title: str
    published: str = ""          # ISO date when the source gives one
    updated: str = ""            # source's own "last updated" marker, if any
    summary: str = ""
    extra: dict = field(default_factory=dict)   # source-specific fields (e.g. FDA recall class)
    watch: dict = field(default_factory=dict)   # extra fields whose change counts as a revision (e.g. status)

    @property
    def item_id(self) -> str:
        """Stable identity: the source plus its own id (recall number) or canonical URL."""
        key = self.extra.get("native_id") or canonical_url(self.url)
        return f"{self.source_id}:{key}"

    def fingerprint(self) -> str:
        """Hash of the content that matters; a change means the item was revised."""
        parts = [normalise(self.title), normalise(self.summary), self.updated,
                 *[f"{k}={normalise(str(v))}" for k, v in sorted(self.watch.items())]]
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]

    def to_dict(self):
        d = asdict(self)
        d["item_id"] = self.item_id
        return d


def normalise(text: str) -> str:
    """Unicode NFC, collapse whitespace, drop zero-width characters: so cosmetic edits are not revisions."""
    text = unicodedata.normalize("NFC", text or "")
    text = re.sub(r"[​-‍﻿]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def canonical_url(url: str) -> str:
    url = (url or "").strip()
    url = re.sub(r"#.*$", "", url)
    url = re.sub(r"[?&](utm_[^=&]+|source)=[^&]*", "", url)
    return url.rstrip("/").replace("http://", "https://", 1)
