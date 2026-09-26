from pathlib import Path
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, TimeoutError as PlaywrightTimeoutError, sync_playwright

class BrowserManager:
    # Variables & Type hints
    def __init__(self, headless: bool = True, state_file: str = "temu_state.json"):
        self.headless = headless
        self.state_file = Path(state_file)

        self.playwright : Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
    # Starting the browser environment
    def start(self):
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            context_options = {
                "viewport": {
                    "width": 1920,
                    "height": 1080,
                },
                "locale": "en-US",
            }
            if self.state_file.exists():
                context_options["storage_state"] = str(self.state_file)

            self.context = self.browser.new_context(**context_options)

            self.context.set_default_timeout(10000)

            self.page = self.context.new_page()
            return self.page
        except Exception:
            self.close()
            raise

    def waitForSelector(self, selector: str):
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        try:
            return self.page.wait_for_selector(selector)

        except PlaywrightTimeoutError as error:
            if self.isLoginPage():
                raise RuntimeError("Temu session expired. Please log in again.") from error
            raise

    def fill(self, selector: str, text: str):
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        self.page.locator(selector).fill(text)

    def press(self, selector: str, key: str):
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        self.page.locator(selector).press(key)

    def navigate(self, url:str):
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        
        print(f"Navigating to: {url}")
        response = self.page.goto(url, wait_until="domcontentloaded")
        if response:
            print(f"Status: {response.status}")
        # Debug
        self.page.screenshot(
            path="debug.png",
            full_page=True,
        )
        return response
    
    def getTitle(self) -> str:
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        return self.page.title()

    # Closing the browser environment
    def close(self):
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    def save_state(self):
            if not self.context:
                raise RuntimeError("Browser has not been started. Call start() first.")
            # Saving browser cookies and local storage
            self.context.storage_state(path=str(self.state_file))
            print(f"Session saved to: {self.state_file}")

    def getLinks(self, selector: str) -> list[str]:
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        return self.page.locator(selector).evaluate_all("""elements => elements.map(element => element.href)""")

    def countElements(self, selector: str) -> int:
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        return self.page.locator(selector).count()

    def getInnerHTML(self, selector: str) -> str:
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        return self.page.locator(selector).first.inner_html()

    def getText(self, selector: str) -> str:
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        return self.page.locator(selector).first.inner_text()

    def isLoginPage(self) -> bool:
        if not self.page:
            return False
        return "/login.html" in self.page.url

    def ensureLoggedIn(self):
        if self.isLoginPage():
            raise RuntimeError("Temu session expired. Please log in again.")
