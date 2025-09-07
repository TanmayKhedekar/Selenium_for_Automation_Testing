"""
Automation Testing Tool (prototype)

Features:
- Accepts a target URL and crawls same-domain pages up to a depth limit
- For each page it runs a set of automated checks:
  * HTTP status check
  * Page load success (Selenium)
  * Console JS errors detection
  * Find and test forms (fill with dummy data and attempt submit)
  * Find internal links and check for broken links
  * Click safe buttons (non-destructive heuristics)
  * Capture screenshots
- Generates a simple HTML report listing pass/fail counts and per-page details

Limitations / safety:
- Avoids clicking elements that look destructive ("delete", "remove", "logout", etc.)
- May not handle CAPTCHAs, logins, or multi-step JS flows—best run against a staging/test environment
- Uses chromium via webdriver-manager (it auto-downloads a compatible driver)

Usage:
1. Install dependencies: pip install -r requirements.txt
2. python automation_tester.py https://example.com

Author: Prototype for Tanmay
"""

import sys
import os
import time
import json
import re
import socket
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# --------------------- Config ---------------------
CRAWL_DEPTH = 1                # depth for link discovery (0 = only start page)
MAX_PAGES = 30                 # hard cap on number of pages crawled
PAGE_LOAD_TIMEOUT = 20         # seconds
FORM_INPUT_PRESET = {
    'text': 'test',
    'email': 'test@example.com',
    'password': 'P@ssw0rd123',
    'tel': '9999999999',
    'url': 'https://example.com',
}
SAFE_CLICK_BLACKLIST = [r'delete', r'remove', r'logout', r'signout', r'pay', r'purchase', r'buy']
OUTPUT_DIR = 'reports'
# --------------------------------------------------


def is_safe_text(text: str) -> bool:
    if not text:
        return True
    text = text.lower()
    for pattern in SAFE_CLICK_BLACKLIST:
        if re.search(pattern, text):
            return False
    return True


def retry_on_stale(func):
    def wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except StaleElementReferenceException:
                time.sleep(1)
        raise
    return wrapper


class PageResult:
    def __init__(self, url):
        self.url = url
        self.tests = []  # list of (name, passed(bool), message)
        self.screenshot = None

    def add(self, name, passed, message=''):
        self.tests.append({'name': name, 'passed': bool(passed), 'message': message})

    @property
    def passed_count(self):
        return sum(1 for t in self.tests if t['passed'])

    @property
    def failed_count(self):
        return sum(1 for t in self.tests if not t['passed'])


class SiteTester:
    def __init__(self, base_url):
        self.base_url = self.normalise(base_url)
        self.parsed_base = urlparse(self.base_url)
        self.domain = self.parsed_base.netloc
        self.scheme = self.parsed_base.scheme
        self.visited = set()
        self.to_visit = [self.base_url]
        self.results = {}
        self.start_time = datetime.utcnow()

        # selenium setup
        chrome_options = Options()
        chrome_options.headless = True
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1200,900')
        chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        # suppress noisy logs
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    def normalise(self, url):
        if not url.startswith('http'):
            url = 'http://' + url
        return url

    def same_domain(self, url):
        try:
            p = urlparse(url)
            return (p.netloc == '' or p.netloc == self.domain)
        except Exception:
            return False

    def discover_links(self, page_source, base_url):
        soup = BeautifulSoup(page_source, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if href.startswith('mailto:') or href.startswith('tel:'):
                continue
            absolute = urljoin(base_url, href)
            if absolute.startswith('javascript:'):
                continue
            absolute = absolute.split('#')[0]
            if self.same_domain(absolute):
                links.add(absolute)
        return links

    def http_status_check(self, url):
        try:
            r = requests.head(url, allow_redirects=True, timeout=10)
            return r.status_code, ''
        except Exception as e:
            return None, str(e)

    def grab_console_errors(self):
        try:
            logs = self.driver.get_log('browser')
            errors = [l for l in logs if l['level'].upper() in ('SEVERE', 'ERROR')]
            return errors
        except Exception:
            return []

    @retry_on_stale
    def fill_and_submit_forms(self, page_result: PageResult):
        try:
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
        except Exception:
            forms = []
        if not forms:
            page_result.add('forms_detected', True, 'No forms on page')
            return
        page_result.add('forms_detected', True, f'{len(forms)} form(s)')
        # (form filling logic unchanged, omitted here for brevity)

    @retry_on_stale
    def check_internal_links(self, page_source, base_url, page_result: PageResult):
        links = self.discover_links(page_source, base_url)
        broken = []
        checked = 0
        for link in links:
            if checked >= 20:
                break
            try:
                r = requests.head(link, allow_redirects=True, timeout=8)
                if r.status_code >= 400:
                    broken.append((link, r.status_code))
            except Exception as e:
                broken.append((link, str(e)))
            checked += 1
        if broken:
            page_result.add('broken_links', False, f'{len(broken)} broken or problematic links (sample: {broken[:3]})')
        else:
            page_result.add('broken_links', True, 'No broken links found (checked up to 20)')

    @retry_on_stale
    def safe_click_buttons(self, page_result: PageResult):
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
        except Exception:
            buttons = []
        clicked = 0
        for b in buttons:
            if clicked >= 3:
                break
            text = (b.text or b.get_attribute('aria-label') or '')
            if not is_safe_text(text):
                continue
            try:
                b.click()
                time.sleep(1)
                page_result.add(f'button_click_{clicked}', True, f'Clicked button: "{text}"')
                self.driver.back()
                time.sleep(1)
                clicked += 1
            except Exception as e:
                page_result.add(f'button_click_{clicked}', False, f'Could not click "{text}" - {e}')
                continue
        if clicked == 0:
            page_result.add('button_clicks', True, 'No safe clickable buttons found or none clicked')

    # (rest of SiteTester code unchanged, omitted here for brevity)


# main() remains unchanged
