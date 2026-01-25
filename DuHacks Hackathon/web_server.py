"""
Simple HTTP Server for Music AI Web Interface
Serves HTML/CSS/JS files and integrates with Python backend
"""

import http.server
import socketserver
import os
import json
from pathlib import Path
from urllib.parse import urlparse

PORT = 9000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with CORS headers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Serve index.html for root path
        if parsed_path.path == '/':
            self.path = '/index.html'
        
        return super().do_GET()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.end_headers()


class ReusableTCPServer(socketserver.TCPServer):
    """TCP Server that allows port reuse"""
    allow_reuse_address = True


def run_server():
    """Start the HTTP server"""
    with ReusableTCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("\n" + "=" * 70)
        print("🎵 MUSIC AI WEB SERVER")
        print("=" * 70)
        print(f"\n✅ Server running at: http://localhost:{PORT}")
        print(f"📁 Serving files from: {DIRECTORY}")
        print(f"\n📂 Files being served:")
        print(f"  - index.html (Main UI)")
        print(f"  - style.css (Styling)")
        print(f"  - script.js (Functionality)")
        print(f"\n🔗 Open in browser: http://localhost:{PORT}")
        print(f"\n⚡ Features:")
        print(f"  - Audio feature extraction visualization")
        print(f"  - Music recommendations display")
        print(f"  - File upload and analysis")
        print(f"  - CORS enabled for API integration")
        print(f"\n💡 Tip: Connect with backend_api.py for full functionality")
        print(f"   Run: python backend_api.py (in separate terminal)")
        print(f"\n⏹️  Press CTRL+C to stop the server\n")
        print("=" * 70 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped.")


if __name__ == "__main__":
    run_server()
