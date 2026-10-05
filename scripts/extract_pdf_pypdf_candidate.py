"""Create a separate page-wise PyPDF text candidate for comparison with PyMuPDF.

Does not overwrite laws_pages.jsonl. Run from the project root:
    py scripts/extract_pdf_pypdf_candidate.py --pdf data/raw/ifab_laws_2026_27_ar.pdf \
        --out data/extracted/laws_pages_pypdf_candidate.jsonl \
        --qa data/eval/pypdf_candidate_qa.json
"""
from __future__ import annotations
import argparse, json, re, statistics
from pathlib import Path
from pypdf import PdfReader


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--pdf', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--qa', type=Path, required=True)
    a = p.parse_args()
    reader = PdfReader(str(a.pdf))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.qa.parent.mkdir(parents=True, exist_ok=True)
    lengths, issues = [], []
    replacement_total = 0
    with a.out.open('w', encoding='utf-8') as target:
        for i, page in enumerate(reader.pages):
            text = (page.extract_text() or '').replace('\r', '\n')
            text = re.sub(r'[\t ]+', ' ', text)
            text = re.sub(r'\n{3,}', '\n\n', text).strip()
            replacement = text.count('\ufffd')
            arabic = len(re.findall(r'[\u0600-\u06ff]', text))
            replacement_total += replacement
            lengths.append(len(text))
            if len(text) < 100 or replacement:
                issues.append({'pdf_page': i+1, 'chars': len(text), 'arabic_chars': arabic,
                               'replacement_character_count': replacement})
            target.write(json.dumps({
                'source_id': 'IFAB-LOTG-2026-27-AR',
                'source_title': 'Laws of the Game 2026/27 (Arabic)',
                'season': '2026/27', 'pdf_page': i+1, 'text': text,
                'extractor': 'pypdf_candidate', 'char_count': len(text),
                'arabic_char_count': arabic,
            }, ensure_ascii=False) + '\n')
    a.qa.write_text(json.dumps({
        'source': str(a.pdf), 'extractor': 'pypdf candidate; comparison only',
        'page_count': len(reader.pages), 'total_characters': sum(lengths),
        'median_characters_per_page': statistics.median(lengths) if lengths else 0,
        'replacement_character_total': replacement_total,
        'pages_under_100_chars': sum(n < 100 for n in lengths),
        'pages_flagged': issues,
        'warning': 'This is an alternative extraction candidate, not a verified correction. Compare wording with the rendered official PDF before indexing; it does not perform OCR.',
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Candidate pages: {len(reader.pages)} | replacement glyphs: {replacement_total} | report: {a.qa}')

if __name__ == '__main__':
    main()
