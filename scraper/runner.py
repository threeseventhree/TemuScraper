from .browser import BrowserManager
from .search import TemuSearcher
from .product import getProducts
from .filters import filterProducts
from .scoring import scoreProducts
from .exporter import createSearchResult, exportSearchResults
from .product import getAverageProductPrices

from config import ScraperConfig

def runScraper(queries: list[str], config: ScraperConfig):
    browser = BrowserManager(headless=config.headless)
    searchResults = []
    try:
        browser.start()
        browser.navigate("https://www.temu.com")

        searcher = TemuSearcher(browser)

        for query in queries:
            print(f"Searching: {query}")
            searcher.search(query)
            searcher.load_more_products(maxProducts=config.maxProducts, maxScrolls=config.maxScrolls)

            products = getProducts(browser)
            averagePrice = getAverageProductPrices(products)
            filteredProducts = filterProducts(
                products,
                minRating=config.minRating,
                minReviews=config.minReviews,
                minSales=config.minSales,
                averagePrice=averagePrice
            )

            scoredProducts = scoreProducts(filteredProducts)
            searchResults.append(
                createSearchResult(
                    query=query,
                    products=scoredProducts,
                    totalProducts=len(products),
                    minRating=config.minRating,
                    minReviews=config.minReviews,
                    minSales=config.minSales,
                    averagePrice=averagePrice
                )
            )

    finally:
        browser.close()

    return searchResults
