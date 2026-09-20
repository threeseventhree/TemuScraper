from scraper.browser import BrowserManager
from scraper.search import TemuSearcher
from scraper.product import getProducts

TEMU_URL = "https://www.temu.com"
SEARCH_INPUT = "#searchInput"

def main():
    browser = BrowserManager(headless=True)
    try:
        browser.start()
        browser.navigate(TEMU_URL)

        searcher = TemuSearcher(browser)
        searcher.search("ESP32")
        print("Search Submitted")

        products = getProducts(browser)
        print(f"\nFound {len(products)} products\n")
        for product in products:
            print(product)
        
    finally:
        browser.close()

if __name__ == "__main__":
    main()
