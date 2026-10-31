"""
test_all_links.py — Automated Health & Link Integrity Checker for Abhishek Gangwar Portfolio
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

# Ensure stdout handles UTF-8 gracefully across all platforms
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_html_files_structure():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    assert len(html_files) > 0, "No HTML files found in root directory!"
    print(f"[OK] Found {len(html_files)} HTML pages.")

    required_tags = ['<meta charset=', '<meta name="viewport"', '<title>']
    for file in html_files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for tag in required_tags:
            assert tag in content, f"Missing required tag '{tag}' in {file}"
    print("[OK] All HTML files contain valid meta tags and titles.")

def test_internal_links_and_assets():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    broken = []

    for file in html_files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find static href and src (ignore Alpine/Vue dynamic attributes)
        matches = re.findall(r'(?<![:\w])(?:href|src)=["\']([^"\'#?]+)["\']', content)
        for link in matches:
            if link.startswith(('http://', 'https://', 'mailto:', 'tel:', 'data:', 'javascript:')):
                continue
            clean = link.strip('/')
            if not clean or clean == '.':
                continue

            candidates = [
                clean,
                clean + '.html',
                os.path.join(clean, 'index.html') if os.path.isdir(clean) else None
            ]
            if not any(c and os.path.exists(c) for c in candidates):
                broken.append((file, link))

    assert len(broken) == 0, f"Broken internal links found: {broken}"
    print("[OK] All internal links and asset paths verified successfully.")

def test_sitemap_integrity():
    assert os.path.exists('sitemap.xml'), "sitemap.xml is missing!"
    tree = ET.parse('sitemap.xml')
    root = tree.getroot()
    urls = [elem.text for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert len(urls) >= 5, f"Expected at least 5 indexed URLs in sitemap, found {len(urls)}"
    print(f"[OK] Sitemap verified with {len(urls)} indexed production URLs.")

def test_robots_txt():
    assert os.path.exists('robots.txt'), "robots.txt is missing!"
    with open('robots.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'Sitemap:' in content, "robots.txt must point to sitemap.xml"
    print("[OK] robots.txt verified.")

if __name__ == '__main__':
    print("\nRunning Portfolio Health & Integrity Suite...")
    test_html_files_structure()
    test_internal_links_and_assets()
    test_sitemap_integrity()
    test_robots_txt()
    print("\n[SUCCESS] All tests passed with 100% integrity!\n")
