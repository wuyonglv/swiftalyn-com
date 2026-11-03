#!/usr/bin/env python3
"""Build the static site from Decap's JSON content using Python's standard library."""
import html
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import contact as contact_content

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def render(source, home, catalog, contact=None):
    values = {
        'HEADER_TAGLINE_RENDERED': [home['hero']['tagline']] * 2,
        'ABOUT_SECTION_TITLE_RENDERED': [home['about']['title']],
        'CONTENT_WELCOME_TITLE_RENDERED': [p['title'] for p in home['partners']],
        'CONTENT_WELCOME_DESCRIPTION_RENDERED': [p['text'] for p in home['partners']],
        'PRODUCT_GROUP_TITLE_RENDERED': [catalog['title']],
        'FOOTER_COPYRIGHT_RENDERED': [home['footer']['copyright']],
    }
    raw_values = {}
    if contact is not None:
        contact_content.validate(contact)
        values.update(contact_content.text_targets(contact))
        raw_values = contact_content.html_targets(contact)
        values.update({key: [value] for key, value in raw_values.items()})
    if len(home['about']['items']) != 3 or len(home['partners']) != 2:
        raise ValueError('The current layout requires exactly 3 About items and 2 partners')
    for i, item in enumerate(home['about']['items']):
        values[f'ABOUT_HEADLINE_RENDERED{i}'] = [item['title']]
        values[f'ABOUT_DESCRIPTION_RENDERED{i}'] = [item['text']]

    class Editor(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.lines = source.splitlines(keepends=True)
            self.stack = []
            self.edits = []
            self.counts = {}

        def position(self):
            line, col = self.getpos()
            return sum(map(len, self.lines[:line - 1])) + col

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            aid = attrs.get('data-aid')
            value = None
            if aid in values:
                index = self.counts.get(aid, 0)
                value = values[aid][index]
                self.counts[aid] = index + 1
            if attrs.get('data-ux') == 'scaler' and attrs.get('data-scaler-id', '').startswith('scaler-tagline-container-'):
                value = home['hero']['tagline']
            # Preserve the decorative heading separator by replacing only its text span.
            if tag == 'span' and self.stack and self.stack[-1]['aid'] in {
                'ABOUT_SECTION_TITLE_RENDERED', 'PRODUCT_GROUP_TITLE_RENDERED', 'CONTACT_SECTION_TITLE_REND'
            }:
                value = self.stack[-1]['value']
                self.stack[-1]['value'] = None
            if attrs.get('class') == 'local-products-message':
                value = catalog['emptyMessage']
            if tag not in VOID:
                self.stack.append({'tag': tag, 'aid': aid, 'value': value,
                                   'start': self.position() + len(self.get_starttag_text())})

        def handle_endtag(self, tag):
            if not self.stack or self.stack[-1]['tag'] != tag:
                return
            node = self.stack.pop()
            if node['value'] is not None:
                text = node['value'] if node['aid'] in raw_values else html.escape(node['value']).replace('\n', '<br>')
                self.edits.append((node['start'], self.position(), text))

    editor = Editor()
    editor.feed(source)
    for aid, entries in values.items():
        if editor.counts.get(aid) != len(entries):
            raise ValueError(f'Missing or changed template target: {aid}')
    for start, end, value in sorted(editor.edits, reverse=True):
        source = source[:start] + value + source[end:]
    return source


def build():
    home = json.loads((ROOT / 'content/home.json').read_text())
    catalog = json.loads((ROOT / 'content/products.json').read_text())
    contact = json.loads((ROOT / 'content/contact.json').read_text())
    for product in catalog['products']:
        if not product['name'].strip() or not isinstance(product['price'], (int, float)) or product['price'] < 0:
            raise ValueError('Products require a name and a nonnegative numeric price')
        if product.get('image') and not (ROOT / product['image']).is_file():
            raise ValueError(f"Missing product image: {product['image']}")
    page = render((ROOT / 'index.html').read_text(), home, catalog, contact)
    # A new URL forces browsers to load changed CSS even after an older cached preview.
    css_version = hashlib.sha256((ROOT / 'css/styles.css').read_bytes()).hexdigest()[:12]
    page = page.replace('href="css/styles.css"', f'href="css/styles.css?v={css_version}"')
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for folder in ['admin', 'css', 'js', 'fonts', 'images']:
        shutil.copytree(ROOT / folder, OUT / folder)
    (OUT / 'js/script.js').write_text(contact_content.update_widgets((ROOT / 'js/script.js').read_text(), contact))
    (OUT / 'js/formsubmit.js').write_text(contact_content.update_form((ROOT / 'js/formsubmit.js').read_text(), contact))
    for name in ['script.js', 'formsubmit.js']:
        version = hashlib.sha256((OUT / 'js' / name).read_bytes()).hexdigest()[:12]
        page = page.replace(f'src="js/{name}"', f'src="js/{name}?v={version}"')
    (OUT / 'data').mkdir()
    products = json.dumps(catalog['products'], ensure_ascii=True).replace('<', '\\u003c')
    (OUT / 'data/products.js').write_text('window.SWIFTALYN_PRODUCTS = ' + products + ';\n')
    (OUT / 'index.html').write_text(page)
    for name in ['privacy-policy.html', 'terms-and-conditions.html', 'manifest.webmanifest', 'CNAME']:
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, OUT / name)
    (OUT / '.nojekyll').touch()
    print(f'Built {OUT}')


if __name__ == '__main__':
    build()
