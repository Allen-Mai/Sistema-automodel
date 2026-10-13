"""Extract text from a PDF into a UTF-8 text file (for IFA SISTEMA Cookbooks).

Usage: python extract_pdf.py <input.pdf> <output.txt>
"""
import sys

from pypdf import PdfReader


def main():
    src, out = sys.argv[1], sys.argv[2]
    reader = PdfReader(src)
    pages = len(reader.pages)
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write(f"# source: {src}\n# pages: {pages}\n")
        for i, page in enumerate(reader.pages, 1):
            fh.write(f"\n===== PAGE {i} =====\n")
            try:
                fh.write(page.extract_text() or '(no extractable text)')
            except Exception as exc:  # noqa: BLE001
                fh.write(f'(extract failed: {exc})')
    print(f"wrote {out}, {pages} pages")


if __name__ == '__main__':
    main()
