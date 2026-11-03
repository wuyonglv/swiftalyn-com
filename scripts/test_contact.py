import copy
import json
import re
import unittest
from build import ROOT, render
from contact import validate, update_widgets, update_form


class ContactTests(unittest.TestCase):
    def setUp(self):
        self.contact = json.loads((ROOT / 'content/contact.json').read_text())

    def test_contact_edits_reach_html_and_all_widget_props(self):
        c = self.contact
        c.update(title='Reach us', infoTitle='New team', company='New company',
                 email='new@example.com', formTitle='Write to us', mapAddress='New map address',
                 latitude=40.5, longitude=-74.1, zoom=11)
        c['hours'][0].update(open='10:30', close='18:00', closed=False)
        page = render((ROOT / 'index.html').read_text(),
                      json.loads((ROOT / 'content/home.json').read_text()),
                      json.loads((ROOT / 'content/products.json').read_text()), c)
        for text in ['Reach us', 'New team', 'New company', 'mailto:new@example.com',
                     'New map address', '10:30 – 18:00']:
            self.assertIn(text, page)
        self.assertEqual(page.count('Write to us'), 3)
        for element in ['bs-2', 'bs-3', 'bs-4']:
            self.assertEqual(page.count(f'id="{element}"'), 1)
        source = (ROOT / 'js/script.js').read_text()
        updated = update_widgets(source, c)
        props = {}
        for match in re.finditer(r'''elId:'(bs-[234])'.*?props:JSON.parse\(("(?:\\.|[^"\\])*")\)''', updated):
            props[match[1]] = json.loads(json.loads(match[2]))
        self.assertEqual(props['bs-2']['structuredHours'][0]['hour']['openTime'], '10:30')
        self.assertEqual(props['bs-3']['formTitle'], 'Write to us')
        self.assertIn('New company', props['bs-3']['info'])
        self.assertEqual(props['bs-4']['lat'], '40.5')
        self.assertEqual(props['bs-4']['address'], 'New map address')
        context = next(l for l in source.splitlines() if "window.wsb['context-bs-1']=" in l)
        self.assertIn(context, updated)

    def test_recipient_and_subject_are_encoded_as_safe_js_strings(self):
        self.contact.update(recipientEmail='recipient@example.com', subject='Hello "world"\nNew line')
        source = update_form((ROOT / 'js/formsubmit.js').read_text(), self.contact)
        self.assertIn('https://formsubmit.co/recipient@example.com', source)
        match = re.search(r'subjectField.value = ("(?:\\.|[^"\\])*");', source)
        self.assertEqual(json.loads(match[1]), self.contact['subject'])

    def test_contact_text_cannot_inject_html(self):
        self.contact['company'] = '<img src=x onerror=alert(1)>'
        page = render((ROOT / 'index.html').read_text(),
                      json.loads((ROOT / 'content/home.json').read_text()),
                      json.loads((ROOT / 'content/products.json').read_text()), self.contact)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', page)
        self.assertNotIn('<img src=x onerror=alert(1)>', page)

    def test_invalid_settings_fail_the_build(self):
        for field, value in [('email', 'bad'), ('recipientEmail', 'a@b.com\nInjected'),
                             ('latitude', 91), ('longitude', 181), ('zoom', 21)]:
            contact = copy.deepcopy(self.contact)
            contact[field] = value
            with self.assertRaises(ValueError):
                validate(contact)
        self.contact['hours'][0]['open'] = '25:00'
        with self.assertRaises(ValueError):
            validate(self.contact)


if __name__ == '__main__':
    unittest.main()
