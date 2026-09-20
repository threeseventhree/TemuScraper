from .product import Product

def filterProducts(
    products: list[Product],
    minRating: float | None = None,
    minReviews: int | None = None,
    minSales: int | None = None,
    maxPrice: float | None = None,
) -> list[Product]:
    filteredProducts = []

    for product in products:
        if minRating is not None:
            if product.rating is None or product.rating < minRating:
                continue

        if minReviews is not None:
            if product.reviews is None or product.reviews < minReviews:
                continue

        if minSales is not None:
            if product.sales < minSales:
                continue

        if maxPrice is not None:
            if product.price > maxPrice:
                continue

        filteredProducts.append(product)
    return filteredProducts
