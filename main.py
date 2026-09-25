from config import ScraperConfig

from scraper.browser import BrowserManager
from scraper.search import TemuSearcher
from scraper.product import getProducts, getAverageProductPrices
from scraper.filters import filterProducts
from scraper.scoring import scoreProducts
from scraper.exporter import createSearchResult, exportSearchResults, exportTxt

TEMU_URL = "https://www.temu.com"
SEARCH_INPUT = "#searchInput"
config = ScraperConfig()

def main():
    browser = BrowserManager(headless=config.headless)

    searchResults = []
    try:
        browser.start()
        browser.navigate(TEMU_URL)

        searcher = TemuSearcher(browser)
        for searchTerm in ["esp32", "oled screen esp32"]:
            print(f"\n{'=' * 50}")
            print(f"Searching for: {searchTerm}")
            print(f"{'=' * 50}")

            searcher.search(searchTerm)
            print("Search Submitted")
            searcher.load_more_products(
                maxProducts=config.maxProducts,
                maxScrolls=config.maxScrolls
            )

            products = getProducts(browser)
            averagePrice = getAverageProductPrices(products)
            print(f"\nFound {len(products)} products")
            filteredProducts = filterProducts(
                products,
                minRating=config.minRating,
                minReviews=config.minReviews,
                minSales=config.minSales,
                averagePrice=averagePrice
            )
            print(f"After filtering, we're left with " f"{len(filteredProducts)} products.")

            scoredProducts = scoreProducts(filteredProducts)
            searchResult = createSearchResult(
                query=searchTerm,
                products=scoredProducts,
                totalProducts=len(products),
                minRating=config.minRating,
                minReviews=config.minReviews,
                minSales=config.minSales,
                averagePrice=averagePrice,
            )

            searchResults.append(searchResult)
    finally:
        browser.close()
    exportSearchResults(searchResults)
    exportTxt(searchResults)

if __name__ == "__main__":
    main()
