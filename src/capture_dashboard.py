"""
Grito Labs Marketing Analytics & Attribution Framework
Module: src/capture_dashboard.py
Description: Uses Playwright with the system Microsoft Edge executable to render
             dashboard/index.html, taking a high-res full-page PNG screenshot and
             compiling a pixel-perfect publication PDF.
"""

import os
import sys
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, "dashboard", "index.html")
SHOT_PATH = os.path.join(BASE_DIR, "dashboard", "dashboard_screenshot.png")
PDF_PATH = os.path.join(BASE_DIR, "dashboard", "Dashboard_Report.pdf")

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
]

def main():
    print("Capturing dashboard visuals...")
    edge_exe = None
    for p in EDGE_PATHS:
        if os.path.exists(p):
            edge_exe = p
            break

    if not edge_exe:
        print("No Edge/Chrome executable found on system.")
        return

    print(f"Using browser at: {edge_exe}")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=edge_exe, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        file_url = f"file:///{os.path.abspath(HTML_PATH).replace(os.sep, '/')}"
        page.goto(file_url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2500) # Allow Chart.js animations to complete
        
        # Capture screenshot
        page.screenshot(path=SHOT_PATH, full_page=True)
        print(f"Saved full-page screenshot: {SHOT_PATH}")
        
        # Capture PDF
        page.pdf(path=PDF_PATH, format="A4", print_background=True)
        print(f"Saved publication PDF: {PDF_PATH}")
        
        browser.close()

if __name__ == "__main__":
    main()
