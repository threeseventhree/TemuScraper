import re

def parsePrice(text: str) -> float:
    match = re.search(r"[\d,.]+", text)
    if not match:
        raise ValueError(f"Could not parse price: {text}")

    value = match.group()
    value = value.replace(",", ".")

    return float(value)

def parseRating(text: str) -> float:
    match = re.search(r"[\d,.]+", text)
    if not match:
        raise ValueError(f"Could not parse rating: {text}")
    
    value = match.group().replace(",", ".")

    return float(value)

def parseReviews(text: str) -> int:
    match = re.search(r"[\d,.]+", text)
    if not match:
        raise ValueError(f"Could not parse reviews: {text}")

    value = match.group()
    value = value.replace(".", "")
    value = value.replace(",", "")

    return int(value)

def parseSales(text: str) -> int:
    text = text.lower().replace(" ", "")
    match = re.search(r"[\d,.]+", text)
    if not match:
        raise ValueError(f"Could not parse sales: {text}")
    
    number = match.group().replace(",", ".")
    value = float(number)
    if "mii" in text:
        value *= 1000
    elif "mil" in text:
        value *= 1000000
    elif "m" in text:
        value *= 1000000
    elif "k" in text:
        value *= 1000

    return int(value)

def cleanProductName(name: str) -> str:
    name = name.replace("Deschide într-o fereastră nouă.","")
    return name.strip()
