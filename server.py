import http.server
import socketserver
import os

PORT = int(os.environ.get("PORT", 8000))

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: *; worker-src 'self' blob:;")
        super().end_headers()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Servidor sirviendo en puerto {PORT} con CSP habilitado para Alpine.js")
    httpd.serve_forever()
