from .browser import BrowserManager
SEARCH_INPUT = "#searchInput"
PRODUCT_LIST = ".autoFitGoodsList"

class TemuSearcher:
    def __init__(self, browser: BrowserManager):
        self.browser = browser
    # Searching for a product based on a query
    def search(self, query: str):
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
        return self.browser.countElements(f"{PRODUCT_LIST} > div")
    # Displaying the HTML data of a product, mainly for debugging to know what we're working with
    def getFirstProductHTML(self) -> str:
        return self.browser.getInnerHTML(f"{PRODUCT_LIST} > div")
