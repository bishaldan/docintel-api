import csv
import json
from io import StringIO

from app.models.extraction import Extraction


def extractions_to_json(extractions: list[Extraction]) -> str:
    payload = [
        {
            "type": extraction.type.value,
            "label": extraction.label,
            "value": extraction.value,
            "page_number": extraction.page_number,
            "confidence": extraction.confidence,
        }
        for extraction in extractions
    ]
    return json.dumps(payload, indent=2)


def extractions_to_csv(extractions: list[Extraction]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["type", "label", "value", "page_number", "confidence"])
    for extraction in extractions:
        writer.writerow(
            [
                extraction.type.value,
                extraction.label or "",
                extraction.value,
                extraction.page_number,
                extraction.confidence,
            ]
        )
    return buffer.getvalue()

