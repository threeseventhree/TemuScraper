from config import (
    SEARCH_TERMS,
    MIN_RATING,
    MIN_REVIEWS,
    MIN_SALES,
    MAX_PRODUCTS,
    MAX_SCROLLS,
    HEADLESS,
)

from scraper.browser import BrowserManager
from scraper.search import TemuSearcher
from scraper.product import getProducts, getAverageProductPrices
from scraper.filters import filterProducts
from scraper.scoring import scoreProducts
from scraper.exporter import createSearchResult, exportSearchResults, exportTxt

TEMU_URL = "https://www.temu.com"
SEARCH_INPUT = "#searchInput"

def main():
    browser = BrowserManager(headless=HEADLESS)

    searchResults = []
    try:
        browser.start()
        browser.navigate(TEMU_URL)

        searcher = TemuSearcher(browser)
        for searchTerm in SEARCH_TERMS:
            print(f"\n{'=' * 50}")
            print(f"Searching for: {searchTerm}")
            print(f"{'=' * 50}")

            searcher.search(searchTerm)
            print("Search Submitted")
            searcher.load_more_products(
                maxProducts=MAX_PRODUCTS,
                maxScrolls=MAX_SCROLLS
            )

            products = getProducts(browser)
            AVERAGE_PRICE = getAverageProductPrices(products)
            print(f"\nFound {len(products)} products")
            filteredProducts = filterProducts(
                products,
                minRating=MIN_RATING,
                minReviews=MIN_REVIEWS,
                minSales=MIN_SALES,
                averagePrice=AVERAGE_PRICE
            )
            print(f"After filtering, we're left with " f"{len(filteredProducts)} products.")

            scoredProducts = scoreProducts(filteredProducts)
            searchResult = createSearchResult(
                query=searchTerm,
                products=scoredProducts,
                totalProducts=len(products),
                minRating=MIN_RATING,
                minReviews=MIN_REVIEWS,
                minSales=MIN_SALES,
                averagePrice=AVERAGE_PRICE,
            )

            searchResults.append(searchResult)
    finally:
        browser.close()
    exportSearchResults(searchResults)
    exportTxt(searchResults)

if __name__ == "__main__":
    main()
