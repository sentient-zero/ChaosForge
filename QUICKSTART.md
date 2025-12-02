# ChaosForge Quick Start

## Installation

```bash
pip install -r requirements.txt
```

## Run the API

```bash
python ChaosForge.py
```

API runs at: **http://localhost:8000**

## Test All Formats

```bash
python test_chaosforge.py
```

## Access Points

| Format | Endpoint | Interactive Docs |
|--------|----------|-----------------|
| REST/JSON | `/api/*` | http://localhost:8000/docs |
| GraphQL | `/graphql` | http://localhost:8000/graphql |
| XML | `/xml/*` | N/A (use cURL/Burp) |

## Quick Examples

### REST/JSON
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD123", "quantity": 2}'
```

### GraphQL
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createOrder(productId: \"PROD123\", quantity: 2) { orderId status } }"
  }'
```

### XML
```bash
curl -X POST http://localhost:8000/xml/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD123", "quantity": 2}'
```

## ChainJockey Testing

**Scenario**: Create order → Wait for completion → Ship

```bash
# 1. Create (any format)
ORDER_ID=$(curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD123", "quantity": 2}' | jq -r '.order_id')

# 2. Poll status (retry until completed - ~5s)
watch -n 1 "curl -s http://localhost:8000/api/orders/$ORDER_ID | jq '.status'"

# 3. Ship when status="completed"
curl -X PUT http://localhost:8000/api/orders/$ORDER_ID/ship
```

## SnitchLab Testing

**Scenario**: Track canary across formats

```bash
# Inject canary
USER_ID=$(curl -s -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "bio": "CANARY_XSS_12345"}' | jq -r '.user_id')

# Track in REST
curl http://localhost:8000/api/feed | grep CANARY_XSS_12345

# Track in GraphQL
curl -X POST http://localhost:8000/graphql \
  -d '{"query": "query { allUsers { bio } }"}' | grep CANARY_XSS_12345

# Track in XML
curl http://localhost:8000/xml/feed | grep CANARY_XSS_12345
```

## Documentation

- **Main README**: Complete testing scenarios
- **GRAPHQL_XML_GUIDE.md**: Format-specific examples
- **IMPLEMENTATION_SUMMARY.md**: Architecture details

## Reset Between Tests

```bash
curl -X POST http://localhost:8000/api/reset
```

---

**That's it!** ChaosForge is ready to forge chaos for your extensions.
