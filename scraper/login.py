import threading

from scraper.browser import BrowserManager
TEMU_URL = "https://www.temu.com"

class TemuLogin:
    def __init__(self):
        self.browser = BrowserManager(headless=False)
        self.finishEvent = threading.Event()

    def start(self):
        try:
            self.browser.start()
            self.browser.navigate(TEMU_URL)

            while not self.finishEvent.wait(0.5):
                if self.browser.page and self.browser.page.is_closed():
                    raise RuntimeError("Login browser was closed before login was finished.")
                if (self.browser.page and self.browser.page.is_closed()):
                    raise RuntimeError("Login browser page was closed before login was finished.")
            self.browser.save_state()

        finally:
            self.browser.close()

    def requestFinish(self):
        self.finishEvent.set()
