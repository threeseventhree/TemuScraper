import re
from statistics import median
from .browser import BrowserManager
from .parser import parseSales, parseReviews, parseRating, parsePrice, cleanProductName
from dataclasses import dataclass
from urllib.parse import urljoin

TEMU_BASE_URL = "https://www.temu.com"
PRODUCT_LIST = ".autoFitGoodsList"

@dataclass
class Product:
    id: str
    name: str
    url: str
    price: float
    sales: int
    rating: float | None
    reviews: int | None

def extractProductId(url: str) -> str:
    match = re.search(r"-g-(\d+)\.html", url)

    if not match:
        raise ValueError(
            f"Could not extract product ID from URL: {url}"
        )

    return match.group(1)

def parseProductCard(card) -> Product:
    name = cleanProductName(card.locator("a[href] h2").inner_text())

    url = card.locator("a[href]").first.get_attribute("href")
    if not url:
        raise ValueError("Could not find product URL")
    url = urljoin(TEMU_BASE_URL, url)

    priceText = card.locator('[data-type="price"]').inner_text()

    salesLocator = card.locator('[data-type="saleTips"]')
    if salesLocator.count() > 0:
        salesText = salesLocator.first.inner_text()
        sales = parseSales(salesText)
    else:
        sales = 0

    ratingLocator = card.locator('[role="img"][aria-label*="din 5 stele"]')
    if ratingLocator.count() > 0:
        ratingText = ratingLocator.first.get_attribute("aria-label")
        rating = ( parseRating(ratingText) if ratingText else None)
    else:
        rating = None
    
    reviewsLocator = card.get_by_text(re.compile(r"recenzii", re.IGNORECASE))
    if reviewsLocator.count() > 0:
        reviewsText = reviewsLocator.first.inner_text()
        reviews = parseReviews(reviewsText)
    else:
        reviews = None

    return Product(
        id=extractProductId(url),
        name=name,
        url=url,
        price=parsePrice(priceText),
        sales=sales,
        rating=rating,
        reviews=reviews,
    )

def getProducts(browser: BrowserManager) -> list[Product]:
    if not browser.page:
        raise RuntimeError("Browser has not been started. Call start() first.")
    cards = browser.page.locator(f"{PRODUCT_LIST} > div")
    products = []
    for i in range(cards.count()):
        card = cards.nth(i)
        try:
            product = parseProductCard(card)
            products.append(product)
        except Exception as error:
            print(f"Could not parse product #{i + 1}: {error}")

    return products

def getAverageProductPrices(products: list[Product]):
    totalPrice = 0;
    for product in products:
        totalPrice += product.price

    return totalPrice / len(products)

def getMedianProductPrice(products: list[Product]) -> float:
    prices = [product.price for product in products]

    return median(prices)
