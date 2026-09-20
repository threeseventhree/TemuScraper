from .product import Product

def normalize(value: float, minimum: float, maximum: float) -> float:
    if maximum == minimum:
        return 1.0

    return (value - minimum) / (maximum - minimum)

def scoreProducts(products: list[Product]) -> list[tuple[Product, float]]:
    if not products:
        return []
    ratings = [
        product.rating
        for product in products
        if product.rating is not None
    ]
    reviews = [product.reviews or 0 for product in products]
    sales = [product.sales for product in products]
    prices = [product.price for product in products]

    minRating = min(ratings)
    maxRating = max(ratings)

    minReviews = min(reviews)
    maxReviews = max(reviews)

    minSales = min(sales)
    maxSales = max(sales)

    minPrice = min(prices)
    maxPrice = max(prices)

    scoredProducts = []

    for product in products:
        ratingScore = (
            normalize(product.rating, minRating, maxRating)
            if product.rating is not None
            else 0
        )
        reviewScore = normalize(
            product.reviews or 0,
            minReviews,
            maxReviews
        )
        salesScore = normalize(
            product.sales,
            minSales,
            maxSales
        )
        priceScore = 1 - normalize(
            product.price,
            minPrice,
            maxPrice
        )
        score = (
            ratingScore * 0.35 +
            reviewScore * 0.20 +
            salesScore * 0.30 +
            priceScore * 0.15
        )
        scoredProducts.append((product, score))
    scoredProducts.sort(
        key=lambda item: item[1],
        reverse=True
    )
    return scoredProducts
