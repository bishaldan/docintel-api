from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

FIELD_ALIASES = {
    "amount due": "total",
    "customer": "name",
    "customer name": "name",
    "grand total": "total",
    "invoice date": "date",
    "merchant name": "merchant",
    "total amount": "total",
}


def normalize_label(label: str) -> str:
    cleaned = re.sub(r"[^a-z0-9 ]+", "", label.lower()).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return FIELD_ALIASES.get(cleaned, cleaned.replace(" ", "_"))


def normalize_value(label: str, value: str) -> str:
    if label in {"date", "invoice_date"}:
        return normalize_date(value)
    if label == "total":
        return normalize_decimal(value)
    return value.strip()


def normalize_date(value: str) -> str:
    cleaned = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return cleaned


def normalize_decimal(value: str) -> str:
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    try:
        return str(Decimal(cleaned).quantize(Decimal("0.01")))
    except (InvalidOperation, ValueError):
        return value.strip()

