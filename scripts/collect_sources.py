"""Download official IFAB sources listed in data/sources_manifest.csv.

Run where outbound HTTPS is available:
    python scripts/collect_sources.py

The script does not treat failures as successful downloads. It saves each web
page/PDF, extracts searchable text, and writes a collection report.
"""
from __future__ import annotations

import csv
import hashlib
from html.parser import HTMLParser
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import fitz


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sources_manifest.csv"
RAW_WEB = ROOT / "data" / "raw" / "web"
RAW_DOCS = ROOT / "data" / "raw" / "supplementary"
EXTRACTED = ROOT / "data" / "extracted" / "supplementary"
REPORT = ROOT / "data" / "eval" / "source_collection_report.json"


def safe_name(source_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", source_id)


def fetch(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": "FootballLawsRAGCapstone/0.1 (educational source collection)"})
    with urlopen(request, timeout=45) as response:
        return response.read(), response.headers.get("Content-Type", "")


class ArticleTextParser(HTMLParser):
    """Small stdlib-only parser that keeps main/article text and drops UI chrome."""

    SKIP = {"script", "style", "nav", "footer", "header", "aside", "noscript", "svg"}
    BLOCKS = {"p", "h1", "h2", "h3", "h4", "li", "section", "article", "main", "br"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.main_depth = 0
        self.has_main = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP:
            self.skip_depth += 1
        if tag in {"main", "article"}:
            self.has_main = True
            self.main_depth += 1
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"main", "article"} and self.main_depth:
            self.main_depth -= 1
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth == 0 and (not self.has_main or self.main_depth > 0):
            value = data.strip()
            if value:
                self.parts.append(value)


def extract_html(payload: bytes) -> str:
    parser = ArticleTextParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    text = "\n".join(parser.parts)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def extract_pdf(path: Path, source: dict[str, str]) -> list[dict[str, object]]:
    doc = fitz.open(path)
    pages = []
    for page_index, page in enumerate(doc):
        text = re.sub(r"\n{3,}", "\n\n", page.get_text("text", sort=False)).strip()
        pages.append({
            "source_id": source["id"],
            "source_title": source["title"],
            "url": source["url"],
            "season": source["season"],
            "language": source["language"],
            "pdf_page": page_index + 1,
            "text": text,
        })
    return pages


def main() -> None:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    results: list[dict[str, object]] = []
    for source in rows:
        source_id = source["id"]
        if source["status"].startswith("downloaded"):
            results.append({"source_id": source_id, "status": "already_local", "local_filename": source["local_filename"]})
            continue

        name = safe_name(source_id)
        try:
            payload, content_type = fetch(source["url"])
            digest = hashlib.sha256(payload).hexdigest()
            if source["format"].upper() == "PDF" or "pdf" in content_type.lower() or payload.startswith(b"%PDF"):
                path = RAW_DOCS / f"{name}.pdf"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                pages = extract_pdf(path, source)
                text_path = EXTRACTED / f"{name}.jsonl"
                text_path.parent.mkdir(parents=True, exist_ok=True)
                with text_path.open("w", encoding="utf-8") as out:
                    for page in pages:
                        out.write(json.dumps(page, ensure_ascii=False) + "\n")
                local = str(path.relative_to(ROOT))
                extracted = str(text_path.relative_to(ROOT))
                page_count = len(pages)
            else:
                path = RAW_WEB / f"{name}.html"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                text = extract_html(payload)
                if len(text) < 150:
                    raise ValueError(f"Extracted page text too short ({len(text)} chars)")
                text_path = EXTRACTED / f"{name}.txt"
                text_path.parent.mkdir(parents=True, exist_ok=True)
                text_path.write_text(text, encoding="utf-8")
                local = str(path.relative_to(ROOT))
                extracted = str(text_path.relative_to(ROOT))
                page_count = None

            source["status"] = "downloaded_and_extracted"
            source["local_filename"] = local
            source["notes"] = (source.get("notes", "") + f" SHA256={digest}; extracted={extracted}").strip()
            results.append({"source_id": source_id, "status": "downloaded_and_extracted", "local_filename": local, "extracted_filename": extracted, "sha256": digest, "pdf_page_count": page_count})
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            results.append({"source_id": source_id, "status": "failed", "error": f"{type(error).__name__}: {error}"})
        time.sleep(0.25)

    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_count": len(rows),
        "downloaded_and_extracted": sum(r["status"] == "downloaded_and_extracted" for r in results),
        "already_local": sum(r["status"] == "already_local" for r in results),
        "failed": sum(r["status"] == "failed" for r in results),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sources: {len(rows)} | report: {REPORT}")


if __name__ == "__main__":
    main()
