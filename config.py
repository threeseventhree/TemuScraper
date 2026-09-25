from dataclasses import dataclass

@dataclass
class ScraperConfig:
    minRating: float = 4.5
    minReviews: int = 100
    minSales: int = 1000

    maxProducts: int = 100
    maxScrolls: int = 20

    headless: bool = True
