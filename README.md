

# Selenium Automation Testing — Complete Guide (Detailed Operations) 🚀

This README explains the **entire process** of using **Selenium with Python** for web UI automation — from setup to advanced interactions, test architecture, CI, and troubleshooting. Every common Selenium operation is explained with code examples and best practices.

---

## Table of contents

* [Quickstart](#quickstart)
* [Environment & Drivers](#environment--drivers)
* [Locator Strategies](#locator-strategies)
* [Waits (Implicit vs Explicit)](#waits-implicit-vs-explicit)
* [Basic element operations](#basic-element-operations)
* [Advanced interactions](#advanced-interactions)
* [Frames, windows, alerts, file uploads](#frames-windows-alerts-file-uploads)
* [JavaScript, scrolling, screenshots & cookies](#javascript-scrolling-screenshots--cookies)
* [Page Object Model (POM) & Project structure](#page-object-model-pom--project-structure)
* [Fixtures, conftest.py & test hooks](#fixtures-conftestpy--test-hooks)
* [Reporting, retries & parallel runs](#reporting-retries--parallel-runs)
* [CI / GitHub Actions example](#ci--github-actions-example)
* [Docker example](#docker-example)
* [Debugging & common errors](#debugging--common-errors)
* [Best practices & tips for flaky tests](#best-practices--tips-for-flaky-tests)
* [Further reading & tools](#further-reading--tools)

---

# Quickstart

1. Create and activate a venv:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

2. `requirements.txt` (recommended):

```
selenium>=4.10.0
pytest
pytest-html
webdriver-manager
pytest-rerunfailures
pytest-xdist
python-dotenv
```

3. Install:

```bash
pip install -r requirements.txt
```

4. Run a test:

```bash
pytest -v
```

---

# Environment & Drivers

Selenium controls browsers via a driver binary (ChromeDriver for Chrome, geckodriver for Firefox). You can manage drivers manually — or use `webdriver-manager` to auto-download matching drivers.

Example with `webdriver-manager` (Chrome):

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```

Notes:

* Ensure driver version matches browser version (webdriver-manager handles this).
* For headless runs: `options.add_argument("--headless")` or `options.add_argument("--headless=new")` for newer Chrome.
* For CI/Linux you may need additional packages (libnss, fonts, etc).

---

# Locator strategies (and when to use them)

Selenium supports multiple locators via `By`:

* `By.ID` — fastest and most stable (use when available).
* `By.NAME` — good for forms.
* `By.CLASS_NAME` — when classes are unique.
* `By.TAG_NAME` — for tags (rarely main selector).
* `By.LINK_TEXT` / `By.PARTIAL_LINK_TEXT` — links.
* `By.CSS_SELECTOR` — powerful & faster than XPath for many cases.
* `By.XPATH` — most flexible (text matching, relationships), but can be verbose.

Example:

```python
from selenium.webdriver.common.by import By
el = driver.find_element(By.CSS_SELECTOR, "div.card > a.btn")
```

Best practice: prefer `ID` → `CSS` → `XPATH`. Keep selectors short and resilient to DOM changes.

---

# Waits — implicit vs explicit

**Implicit wait** (applies to all `find_element` calls):

```python
driver.implicitly_wait(5)  # seconds
```

**Explicit wait** — recommended (wait until a specific condition):

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
el = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
```

Common `expected_conditions`:

* `presence_of_element_located`
* `visibility_of_element_located`
* `element_to_be_clickable`
* `invisibility_of_element_located`
* `text_to_be_present_in_element`

Avoid `time.sleep()` — use explicit waits for stability.

---

# Basic element operations

**Open page and assert title**

```python
driver.get("https://example.com")
assert "Example" in driver.title
```

**Type into input and submit**

```python
search = driver.find_element(By.NAME, "q")
search.send_keys("Selenium automation")
search.submit()
```

**Click**

```python
driver.find_element(By.ID, "login").click()
```

**Clear field**

```python
field = driver.find_element(By.ID, "message")
field.clear()
field.send_keys("New text")
```

**Read text**

```python
text = driver.find_element(By.CSS_SELECTOR, "h1").text
```

---

# Advanced interactions

### Mouse actions (hover, double-click, right-click, drag and drop)

```python
from selenium.webdriver.common.action_chains import ActionChains

actions = ActionChains(driver)
elem = driver.find_element(By.ID, "menu")
actions.move_to_element(elem).perform()   # hover

actions.double_click(driver.find_element(By.ID, "dbl")).perform()
actions.context_click(driver.find_element(By.ID, "right")).perform()
# drag and drop
actions.drag_and_drop(source, target).perform()
```

### Selecting from `<select>` dropdowns

```python
from selenium.webdriver.support.ui import Select
sel = Select(driver.find_element(By.ID, "country"))
sel.select_by_visible_text("India")
sel.select_by_value("IN")
sel.select_by_index(3)
```

### Keyboard keys

```python
from selenium.webdriver.common.keys import Keys
el.send_keys("text" + Keys.ENTER)
```

---

# Frames, windows, alerts, file uploads

### Switching frames / iframes

```python
# by name/id
driver.switch_to.frame("frameName")
# by element
frame_el = driver.find_element(By.CSS_SELECTOR, "iframe.some")
driver.switch_to.frame(frame_el)
# back to main
driver.switch_to.default_content()
```

### Windows and tabs

```python
original = driver.current_window_handle
driver.execute_script("window.open('https://example.com')")
handles = driver.window_handles
driver.switch_to.window(handles[-1])  # switch to new tab
# switch back
driver.switch_to.window(original)
```

### Alerts

```python
alert = driver.switch_to.alert
print(alert.text)
alert.accept()    # OK
alert.dismiss()   # Cancel
```

### File upload

If file input element is present:

```python
file_input = driver.find_element(By.ID, "file-upload")
file_input.send_keys(r"C:\path\to\file.txt")
```

If web UI uses custom non-input uploaders, you may need OS-level tools (AutoIt on Windows) or JS injection.

---

# JavaScript, scrolling, screenshots & storage

### Execute JS

```python
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
driver.execute_script("arguments[0].click();", element)  # JS click
# read localStorage
driver.execute_script("return window.localStorage.getItem('myKey');")
```

### Scroll element into view

```python
driver.execute_script("arguments[0].scrollIntoView(true);", element)
```

### Screenshots

```python
driver.save_screenshot("reports/full_page.png")
element.screenshot("reports/element.png")
```

### Cookies

```python
driver.add_cookie({'name': 'token', 'value': 'abc123'})
cookies = driver.get_cookies()
driver.delete_cookie('token')
```

---

# Page Object Model (POM) & Project structure

POM helps keep tests readable and maintainable.

Suggested structure:

```
project/
├── pages/
│   ├── base_page.py
│   ├── login_page.py
├── tests/
│   ├── test_login.py
├── conftest.py
├── requirements.txt
├── reports/
└── README.md
```

**Example: `pages/base_page.py`**

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def visit(self, url):
        self.driver.get(url)

    def find(self, by_locator):
        return self.wait.until(EC.presence_of_element_located(by_locator))

    def click(self, by_locator):
        el = self.wait.until(EC.element_to_be_clickable(by_locator))
        el.click()

    def type(self, by_locator, text):
        el = self.find(by_locator)
        el.clear()
        el.send_keys(text)
```

**Example: `pages/login_page.py`**

```python
from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    LOGIN = (By.ID, "loginBtn")

    def login(self, user, pwd):
        self.type(self.USERNAME, user)
        self.type(self.PASSWORD, pwd)
        self.click(self.LOGIN)
```

**Test using POM**

```python
def test_login_success(driver):
    from pages.login_page import LoginPage
    login = LoginPage(driver)
    login.visit("https://example.com/login")
    login.login("user", "pass")
    assert "dashboard" in driver.current_url
```

---

# Fixtures, `conftest.py` & test hooks (example)

`conftest.py` with configurable browser and headless flag:

```python
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store_true")

@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    if browser == "chrome":
        options = Options()
        options.add_argument("--start-maximized")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        raise Exception("Only chrome supported in this fixture sample")
    yield driver
    driver.quit()
```

**Screenshot on failure** (simple hook)

```python
import pytest

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            path = f"reports/{item.name}.png"
            driver.save_screenshot(path)
```

---

# Reporting, retries & parallelization

* **HTML report**: `pytest --html=reports/report.html --self-contained-html`
* **Allure** (optional more advanced): requires installing `allure-pytest` and Allure CLI.
* **Rerun flaky tests**: `pytest --reruns 2` (requires `pytest-rerunfailures`)
* **Parallel**: `pytest -n 4` (requires `pytest-xdist`) — ensure tests are independent and do not share browser state unless intended.

---

# CI — GitHub Actions example

`.github/workflows/selenium.yml` (basic):

```yaml
name: Selenium Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with: python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: pytest --maxfail=1 -q --html=reports/report.html --self-contained-html
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: reports/report.html
```

Notes:

* On Ubuntu runners, Chrome is often preinstalled; if not, add steps to install Chrome.
* Use `webdriver-manager` for driver installation during the job.

---

# Docker example (simple)

`Dockerfile` (run tests in container; uses `webdriver-manager` to fetch chromedriver and Chrome from package manager):

```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget gnupg unzip \
  && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update && apt-get install -y google-chrome-stable \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["pytest", "--html=reports/report.html", "--self-contained-html"]
```

Tip: For full-headful test execution in containers, consider using `selenium/standalone-chrome` or `selenium/hub` Docker images (Selenium Grid) or use XVFB.

---

# Debugging & common errors (with fixes)

**1. `SessionNotCreatedException` (driver/browser mismatch)**
Fix: Update Chrome or use the appropriate ChromeDriver. Use `webdriver-manager` to auto-match.

**2. `ElementNotInteractableException` / `ElementClickInterceptedException`**
Fix: Ensure element is visible/clickable (use explicit waits). Scroll into view or click via JS if needed.

**3. `NoSuchElementException`**
Fix: Verify locator, use waits, ensure you’re in correct frame/window.

**4. `StaleElementReferenceException`**
Cause: element was re-rendered. Fix: re-locate the element right before interacting.

**5. `WinError 193 / not a valid Win32 application`**
Cause: wrong binary architecture (32/64) mismatch or trying to run `.exe` incorrectly. Ensure correct driver binary.

**6. `TimeoutException`**
Fix: Increase wait timeout or improve locator.

---

# Best practices & tips for flaky tests

* Use explicit waits and avoid `sleep`.
* Prefer stable locators (IDs, data-qa attributes).
* Use POM to encapsulate page behavior.
* Keep tests independent and idempotent.
* Separate test data from tests.
* Capture screenshots & browser logs on failure.
* Use retries sparingly, only for known flaky behavior.
* Run tests in CI with reproducible containers.
* Use test tags (pytest markers) to group slow/unit/smoke tests.
* For real concurrency or scale, use Selenium Grid or cloud providers (BrowserStack, Sauce Labs).

---

# Example: Quick operations cheat-sheet (copyable)

**Wait until clickable**

```python
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary")))
```

**Hover and click**

```python
ActionChains(driver).move_to_element(menu).click(submenu).perform()
```

**Switch & accept alert**

```python
alert = driver.switch_to.alert
alert_text = alert.text
alert.accept()
```

**Open new tab and switch**

```python
driver.execute_script("window.open('https://example.com', '_blank');")
driver.switch_to.window(driver.window_handles[-1])
```

**Take screenshot on failure** (minimal)

```python
driver.save_screenshot("reports/fail.png")
```

---

# Accessibility & performance testing (notes)

* Selenium can help check basic ARIA attributes and keyboard navigation.
* For deeper accessibility checks, integrate tools like Axe (axe-core). You can inject `axe.min.js` and run accessibility scans via JS.
* For performance/network metrics, use browser devtools protocol (CDP) or use dedicated performance tools (Lighthouse).

---

# Frequently asked questions (short)

* **Q**: Should I use XPath or CSS?
  **A**: Prefer ID → CSS → XPath if needed.

* **Q**: How to handle file downloads?
  **A**: Preconfigure browser profile to auto-download to folder; use `options.add_experimental_option("prefs", {...})`.

* **Q**: Can Selenium intercept network calls?
  **A**: Not directly. Use browsermob-proxy, devtools protocol, or Playwright for easier network stubbing.

