"""Regenerate the static CV preview after updating files/Zhuoqing_Zhong_CV.pdf.

Requires Poppler's pdftoppm, Pillow, and pypdf. Run from any directory:
    python scripts/render_cv_preview.py

Only preview images and the marked section of cv.html are written. The PDF is
never modified. Text is extracted from that same PDF for an accessible version.
"""
from hashlib import sha256
from html import escape
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'files' / 'Zhuoqing_Zhong_CV.pdf'
DEST = ROOT / 'assets' / 'img' / 'cv'
HTML = ROOT / 'cv.html'
PDF_URL = 'files/Zhuoqing_Zhong_CV.pdf'


def main():
    digest = sha256(PDF.read_bytes()).hexdigest()
    renderer = shutil.which('pdftoppm')
    if not renderer:
        raise SystemExit('pdftoppm is required to render the preview.')
    reader = PdfReader(PDF)
    count = len(reader.pages)
    DEST.mkdir(parents=True, exist_ok=True)
    figures = []
    text_pages = []
    with tempfile.TemporaryDirectory(prefix='cv-preview-') as temp:
        prefix = Path(temp) / 'page'
        subprocess.run([renderer, '-r', '180', '-png', str(PDF), str(prefix)], check=True)
        rendered = sorted(Path(temp).glob('page-*.png'), key=lambda p: int(p.stem.rsplit('-', 1)[1]))
        if len(rendered) != count:
            raise SystemExit('Rendered page count differs from the source PDF.')
        for number, (source, pdf_page) in enumerate(zip(rendered, reader.pages), 1):
            filename = f'page-{number}.webp'
            with Image.open(source) as image:
                width, height = image.size
                image.convert('RGB').save(DEST / filename, 'WEBP', lossless=True, method=6)
            loading = 'eager' if number == 1 else 'lazy'
            figures.append(f'''      <figure class="cv-page">
        <a class="cv-page-link" href="{PDF_URL}#page={number}" target="_blank" rel="noopener" aria-label="Curriculum vitae, page {number} of {count}. Open the PDF in a new tab.">
          <img class="cv-page-image" src="assets/img/cv/{filename}?v={digest[:10]}" width="{width}" height="{height}" alt="Curriculum vitae, page {number} of {count}" loading="{loading}" decoding="async">
        </a>
        <figcaption>Page {number} of {count}</figcaption>
      </figure>''')
            text = escape('\n'.join(line.rstrip() for line in (pdf_page.extract_text() or '').splitlines()))
            text_pages.append(f'      <section class="cv-text-page"><h2>Page {number} of {count}</h2><p>{text}</p></section>')
    noun = 'page' if count == 1 else 'pages'
    content = f'''    <section class="cv-preview" aria-label="Curriculum vitae preview" data-zoomed="false">
      <div class="cv-toolbar">
        <span>PDF preview · {count} {noun}</span>
        <button class="cv-zoom" type="button" aria-pressed="false" aria-controls="cv-pages"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6M7 10h6M10 7v6"/></svg><span>Enlarge preview</span></button>
      </div>
      <div class="cv-sheet-viewport" id="cv-pages" tabindex="0" aria-label="CV pages. When enlarged, scroll horizontally to read the full page.">
{chr(10).join(figures)}
      </div>
    </section>
    <details class="cv-text-version">
      <summary>Read as text</summary>
{chr(10).join(text_pages)}
    </details>'''
    document = HTML.read_text(encoding='utf-8')
    document, replacements = re.subn(r'(?<=<!-- CV_PREVIEW_START -->).*?(?=    <!-- CV_PREVIEW_END -->)', lambda _: '\n' + content + '\n', document, count=1, flags=re.S)
    if replacements != 1:
        raise SystemExit('CV preview markers not found; cv.html was not changed.')
    document = re.sub(
        r'href="' + re.escape(PDF_URL) + r'(?:\?v=[a-f0-9]+)?(?=["#])',
        lambda _: f'href="{PDF_URL}?v={digest[:10]}', document)
    HTML.write_text(document, encoding='utf-8')
    assert sha256(PDF.read_bytes()).hexdigest() == digest, 'Source PDF was unexpectedly changed.'
    print(f'Rendered {count} CV page(s); source PDF unchanged ({digest[:12]}).')


if __name__ == '__main__':
    main()
