#!/usr/bin/env python3
"""
server.py  —  Minimal lab web server for the Cybervoid Saga cache-smuggling demo.

Serves two things on http://127.0.0.1:8099 :
  /                 the SIMULATED lure page (index.html) with an <img> that
                    forces the browser to cache the "asset"
  /cached_asset.jpg the BENIGN smuggled file, sent with Content-Type: image/jpeg
                    and long cache headers -- the exact server-side trick.

Everything served is harmless. This only demonstrates that a browser will
cache a non-image file that is *labelled* as an image.
"""
import http.server
import os
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8099


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def do_GET(self):
        if self.path.startswith("/cached_asset.jpg"):
            path = os.path.join(HERE, "cached_asset.jpg")
            with open(path, "rb") as f:
                body = f.read()
            self.send_response(200)
            # THE TRICK: claim it's a JPEG so the browser caches it as an image.
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            # A benign stand-in for the attacker's custom "find me" header.
            self.send_header("X-Lab-Tag", "cybervoid-saga-demo")
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def log_message(self, fmt, *args):
        print("[server]", self.address_string(), fmt % args)


if __name__ == "__main__":
    os.chdir(HERE)
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"[server] lab server on http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
        httpd.serve_forever()
