import json
from dataclasses import asdict
from pathlib import Path

from .product import Product


def exportSearchResults(
    searchResults: list[dict],
    filename: str = "data/products.json",
):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            searchResults,
            file,
            indent=4,
            ensure_ascii=False
        )

    totalProducts = sum(
        len(result["products"])
        for result in searchResults
    )
    print(f"Saved {totalProducts} products to {path}")

def createSearchResult(
    query: str,
    products: list[tuple[Product, float]],
    totalProducts: int,
    minRating: float,
    minReviews: int,
    minSales: int,
    maxPrice: float,
) -> dict:

    productData = []

    for product, score in products:
        data = asdict(product)
        data["score"] = round(score, 3)
        productData.append(data)

    return {
        "query": query,
        "totalProducts": totalProducts,
        "filteredProducts": len(products),
        "filters": {
            "minRating": minRating,
            "minReviews": minReviews,
            "minSales": minSales,
            "maxPrice": maxPrice
        },
        "products": productData
    }
