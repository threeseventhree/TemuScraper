from .browser import BrowserManager

SEARCH_INPUT = "#searchInput"
PRODUCT_LIST = ".autoFitGoodsList"
PRODUCT_CARD = f"{PRODUCT_LIST} > div"

class TemuSearcher:
    def __init__(self, browser: BrowserManager):
        self.browser = browser
    # Searching for a product based on a query
    def search(self, query: str):
        self.browser.ensureLoggedIn()
        self.browser.waitForSelector(SEARCH_INPUT)
        self.browser.fill(SEARCH_INPUT, query)
        self.browser.press(SEARCH_INPUT, "Enter")
    # Getting the links to each product so we can later navigate to their respsective pages and extract data
    def getProductLinks(self) -> list[str]:
        self.browser.waitForSelector(PRODUCT_LIST)
        links = self.browser.getLinks(f"{PRODUCT_LIST} a[href]")
        return links
    # Counting how many products our scraper sees in the list of divs
    def getProductCount(self) -> int:
        return self.browser.countElements(PRODUCT_CARD)
    # Displaying the HTML data of a product, mainly for debugging to know what we're working with
    def getFirstProductHTML(self) -> str:
        return self.browser.getInnerHTML(PRODUCT_CARD)
    # Loading more products because the original version can load up to 14 products max, a.k.a what is visible on the initial load.
    def load_more_products(
        self,
        maxProducts: int = 100,
        maxScrolls: int = 20,
    ):
        if not self.browser.page:
            raise RuntimeError("Browser has not been started. Call start() first.")
        page = self.browser.page
        previousCount = 0
        stableScrolls = 0
        for _ in range(maxScrolls):
            currentCount = page.locator(
                PRODUCT_CARD
            ).count()
            print(f"Products currently loaded: {currentCount}")
            if currentCount >= maxProducts:
                break

            if currentCount == previousCount:
                stableScrolls += 1
            else:
                stableScrolls = 0

            if stableScrolls >= 3:
                break

            previousCount = currentCount
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(1000)
