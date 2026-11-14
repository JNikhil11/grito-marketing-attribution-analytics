"""
Grito Labs Marketing Analytics & Attribution Framework
Module: dashboard/app.py
Description: Python Web Server & Dashboard Runner.
             Launches a local HTTP server and automatically opens the interactive
             multi-touch attribution dashboard in the default browser.
"""

import os
import sys
import webbrowser
import http.server
import socketserver

PORT = 8501
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)
    def log_message(self, format, *args):
        pass # Suppress routine access logs for clean CLI

def main():
    print("=" * 80)
    print("GRITO LABS: INTERACTIVE ATTRIBUTION DASHBOARD")
    print(f"Serving dashboard from: {DASHBOARD_DIR}")
    print(f"URL: http://localhost:{PORT}/index.html")
    print("=" * 80)
    
    url = f"http://localhost:{PORT}/index.html"
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        
    print("\nPress Ctrl+C to terminate dashboard server.\n")
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard server terminated cleanly.")

if __name__ == "__main__":
    main()
