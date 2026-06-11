# API Examples

```bash
BASE_URL=http://localhost:8001/api/v1
```

## Upload

```bash
curl -sS -X POST "$BASE_URL/documents" \
  -F "file=@sample-invoice.txt"
```

## Process

```bash
curl -sS -X POST "$BASE_URL/documents/1/process"
```

## Read Extractions

```bash
curl -sS "$BASE_URL/documents/1/extractions"
```

## Export JSON

```bash
curl -sS "$BASE_URL/documents/1/exports/json"
```

## Export CSV

```bash
curl -sS "$BASE_URL/documents/1/exports/csv"
```

