import copy
import json
from pathlib import Path
import unittest
from build import ROOT, render


class ContentBuildTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'index.html').read_text()
        self.home = json.loads((ROOT / 'content/home.json').read_text())
        self.catalog = json.loads((ROOT / 'content/products.json').read_text())

    def test_edited_content_reaches_all_responsive_targets(self):
        self.home['hero']['tagline'] = 'Updated hero\nSecond line'
        self.home['about']['title'] = 'Updated About'
        self.home['partners'][1]['text'] = 'Updated reseller'
        self.catalog['title'] = 'Updated products'
        page = render(self.source, self.home, self.catalog)
        self.assertEqual(page.count('Updated hero<br>Second line'), 8)
        for text in ['Updated About', 'Updated reseller', 'Updated products']:
            self.assertIn(text, page)
        self.assertEqual(page.count('data-ux="SectionHeadingHR"'), self.source.count('data-ux="SectionHeadingHR"'))
        start = self.source.index('id="bs-4"')
        end = self.source.index('</button>', start) + len('</button>')
        self.assertIn(self.source[start:end], page)

    def test_content_is_text_not_executable_html(self):
        self.home['partners'][0]['text'] = '<script>alert(1)</script>'
        page = render(self.source, self.home, self.catalog)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', page)
        self.assertNotIn('<script>alert(1)</script>', page)

    def test_changed_layout_fails_instead_of_silently_dropping_content(self):
        with self.assertRaises(ValueError):
            render(self.source.replace('ABOUT_HEADLINE_RENDERED0', 'missing'), self.home, self.catalog)
        self.home['about']['items'].pop()
        with self.assertRaises(ValueError):
            render(self.source, self.home, self.catalog)

    def test_cms_schema_matches_content(self):
        config = json.loads((ROOT / 'admin/config.yml').read_text())
        for entry in config['collections'][0]['files']:
            content = json.loads((ROOT / entry['file']).read_text())
            self.assertEqual({f['name'] for f in entry['fields']}, set(content))
        self.assertEqual(config['backend']['repo'], 'wuyonglv/swiftalyn-com')


if __name__ == '__main__':
    unittest.main()
