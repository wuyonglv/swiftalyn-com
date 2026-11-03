#!/usr/bin/env python3
"""Local preview: rebuild CMS content whenever the homepage is refreshed."""
import argparse
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit

from build import OUT, build


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path in ('/', '/index.html'):
            try:
                build()
            except Exception as error:
                self.log_error('Build failed: %s', error)
                self.send_error(500, 'Content build failed; see the preview terminal for details')
                return
        # Avoid serving stale content, even when edits occur within the same second.
        for header in ('If-Modified-Since', 'If-None-Match'):
            if header in self.headers:
                del self.headers[header]
        super().do_GET()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    build()
    # Single-threaded so an asset request cannot race a rebuild of _site.
    server = HTTPServer(('127.0.0.1', args.port), partial(PreviewHandler, directory=str(OUT)))
    print(f'Preview: http://localhost:{args.port}/ (rebuilds on refresh)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
