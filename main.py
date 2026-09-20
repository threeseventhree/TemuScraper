from scraper.browser import BrowserManager
from scraper.search import TemuSearcher
# Sample code for testing, to be modified later

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

        links = searcher.getProductLinks()
        print(f"Found {len(links)} links")

        count = searcher.getProductCount()
        print(f"Found {count} product cards")

        html = searcher.getFirstProductHTML()
        print(html)
        
    finally:
        browser.close()

if __name__ == "__main__":
    main()
