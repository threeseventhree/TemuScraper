from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

class BrowserManager:
    # Variables & Type hints
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright : Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
    # Starting the browser environment
    def start(self):
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="en-US"
            )
            self.context.set_default_timeout(10000)
            
            self.page = self.context.new_page()
            return self.page
        except Exception:
            self.close()
            raise

    # Closing the browser environment
    def close(self):
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
