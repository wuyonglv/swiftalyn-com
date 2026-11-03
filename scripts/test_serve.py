from email.message import Message
import unittest
from unittest.mock import patch

from serve import PreviewHandler


class PreviewTests(unittest.TestCase):
    def handler(self, path):
        handler = object.__new__(PreviewHandler)
        handler.path = path
        handler.headers = Message()
        handler.headers['If-Modified-Since'] = 'old value'
        handler.headers['If-None-Match'] = 'old value'
        return handler

    def test_refresh_rebuilds_before_serving_and_removes_cache_conditions(self):
        for path in ['/', '/index.html?preview=1']:
            handler = self.handler(path)
            order = []
            with patch('serve.build', side_effect=lambda: order.append('build')), patch(
                'serve.SimpleHTTPRequestHandler.do_GET', side_effect=lambda: order.append('serve')
            ):
                handler.do_GET()
            self.assertEqual(order, ['build', 'serve'])
            self.assertNotIn('If-Modified-Since', handler.headers)
            self.assertNotIn('If-None-Match', handler.headers)

    def test_asset_does_not_trigger_rebuild(self):
        with patch('serve.build') as build, patch('serve.SimpleHTTPRequestHandler.do_GET'):
            self.handler('/data/products.js').do_GET()
        build.assert_not_called()

    def test_build_error_is_reported_instead_of_serving_stale_page(self):
        handler = self.handler('/')
        with patch('serve.build', side_effect=ValueError('invalid content')), patch.object(
            handler, 'send_error'
        ) as error, patch.object(handler, 'log_error'), patch('serve.SimpleHTTPRequestHandler.do_GET') as serve:
            handler.do_GET()
        self.assertEqual(error.call_args.args[0], 500)
        serve.assert_not_called()
