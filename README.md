# ChaosForge
Demo API that forges async chaos: state-dependent chains, eventual consistency, random failures. Built to stress-test BurpSuite extensions against the async hellscape that breaks traditional tooling.

# Async Demo API for BurpSuite Extensions

Demo API designed to test **BurpExtension1** and **BurpExtension2** BurpSuite extensions with realistic async workflows, state transitions, and storage patterns.

ChaosForge - Where async workflows go to die (so your extensions don't have to)

Demo API that throws everything broken about modern async at your tooling. State-dependent chains that fail halfway through. Resources that take their sweet time provisioning. Data that surfaces three endpoints later when you've stopped looking. The kind of eventually-consistent nightmare that makes traditional testing tools curl up and cry.

Built to stress-test BurpExtension1's state handling and BurpExtension2's canary tracking against real-world async chaos.

Features:
- Multi-state workflows with random failures
- Eventual consistency across delayed views
- Retry-worthy flaky endpoints
- Storage patterns that span request chains
- Background processing that doesn't give a damn about your timeline

Not a mock. Not a stub. A forge for tempering security tools against the async hellscape that is modern API architecture.

Deploy it. Break against it. Ship tools that actually handle the chaos.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python async_demo_api.py
```

API will be available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

## What This API Does

This API simulates **real-world async complexity** that breaks traditional testing tools:

- **State-dependent workflows** - Resources transition through multiple states
- **Async processing** - Operations complete in the background with delays
- **Eventual consistency** - Data appears in different views at different times
- **Retry scenarios** - Endpoints that fail randomly for testing retry logic
- **Storage & retrieval patterns** - Injected data surfaces in later requests

## Testing BurpExtension1

BurpExtension1 handles complex request chains with state dependencies. Here are the key test scenarios:

### Scenario 1: Order Processing Workflow

**The Challenge:** Orders go through async state transitions. You can't ship an order until it's processed.

```
1. POST /api/orders
   → Returns order_id, status="pending"
   
2. Wait ~2s for processing to start
   
3. GET /api/orders/{order_id}  
   → May return 404 initially, retry with backoff
   → Eventually shows status="processing"
   
4. Wait ~3s for completion
   
5. GET /api/orders/{order_id}
   → Status should be "completed" (90% success rate)
   
6. PUT /api/orders/{order_id}/ship
   → Only succeeds if status=="completed"
   → Returns 409 if wrong state
```

**BurpExtension1 Config:**
```json
{
  "flow": [
    {"request": "create_order", "method": "POST", "endpoint": "/api/orders"},
    {"request": "check_order", "method": "GET", "endpoint": "/api/orders/{order_id}", 
     "retry": {"max_attempts": 5, "delay": 1, "on_status": [404]}},
    {"request": "wait_processing", "method": "GET", "endpoint": "/api/orders/{order_id}",
     "retry": {"max_attempts": 10, "delay": 1, "until_state": {"status": "completed"}}},
    {"request": "ship_order", "method": "PUT", "endpoint": "/api/orders/{order_id}/ship",
     "require_state": {"status": "completed"}}
  ]
}
```

### Scenario 2: Job Queue with Result Retrieval

**The Challenge:** Submit a job, wait for it to run, then fetch the result.

```
1. POST /api/jobs
   Body: {"job_type": "data_export", "delay": 5}
   → Returns job_id, status="queued"
   
2. GET /api/jobs/{job_id}
   → Poll until status=="running" or "completed"
   
3. GET /api/jobs/{job_id}/result
   → Returns 409 until job is completed
   → Retry until successful
```

### Scenario 3: Resource Provisioning

**The Challenge:** Create a resource, wait for it to provision, then connect.

```
1. POST /api/resources
   Body: {"resource_type": "database", "config": {...}}
   → Returns resource_id, status="provisioning"
   
2. GET /api/resources/{resource_id}
   → Polls through: provisioning → initializing → ready (takes ~6s)
   
3. POST /api/resources/{resource_id}/connect
   → Only works when status=="ready"
   → Returns connection credentials
```

### Scenario 4: Flaky Endpoint with Retry

**The Challenge:** Endpoint fails randomly, needs retry logic.

```
GET /api/flaky
→ 50% chance of 503 error
→ Test retry logic with exponential backoff
```

## Testing BurpExtension2

BurpExtension2 tracks canaries across async storage and retrieval. Here are the key patterns:

### Pattern 1: User Profile Storage

**The Challenge:** Data posted to `/api/users` surfaces in multiple endpoints at different times.

```
1. POST /api/users
   Body: {"username": "testuser", "bio": "CANARY_XSS_12345", "email": "test@example.com"}
   → Returns user_id
   
2. GET /api/users/{user_id}
   → IMMEDIATE: Canary appears here right away
   
3. GET /api/users/{user_id}/public  
   → DELAYED 2s: Canary appears here after cache propagation
   
4. GET /api/feed
   → DELAYED: Canary appears in activity feed items
   
5. GET /api/search?q=CANARY_XSS_12345
   → DELAYED 5s: Canary appears in search results
   
6. GET /api/analytics/users
   → DELAYED 10s: Canary appears in analytics last
```

**BurpExtension2 should track:** Where `CANARY_XSS_12345` surfaces across all these endpoints.

### Pattern 2: Comment Storage (Stored XSS Pattern)

**The Challenge:** Comments are stored unsanitized and retrieved later.

```
1. POST /api/comments
   Body: {"post_id": "post123", "content": "CANARY_STORED_001", "author": "attacker"}
   → Returns comment_id
   
2. GET /api/posts/post123/comments
   → Canary appears in comments array
   
3. GET /api/comments/recent
   → Canary appears in recent comments
```

**BurpExtension2 should track:** Stored canary appearing in different comment views.

### Pattern 3: Webhook Callback Tracking

**The Challenge:** URLs with canaries get stored and retrieved.

```
1. POST /api/webhooks/register
   Body: {"url": "https://canary-webhook-123.com/callback", "event_type": "user.created"}
   
2. GET /api/webhooks/events
   → Canary URL appears in webhook list
```

### Pattern 4: Multiple Canaries in Complex Flow

**The Challenge:** Track multiple different canaries through a complex workflow.

```
1. Create user with bio="CANARY_BIO_001"
2. Create another user with email="canary_email_002@test.com"  
3. Post comment with content="CANARY_COMMENT_003"
4. Monitor /api/feed, /api/search, /api/analytics/users
5. Track which canaries surface where and when
```

## Endpoint Reference

### Order Endpoints
- `POST /api/orders` - Create order (async processing starts)
- `GET /api/orders/{order_id}` - Get order status
- `PUT /api/orders/{order_id}/ship` - Ship order (requires status="completed")
- `DELETE /api/orders/{order_id}` - Cancel order

### Job Endpoints
- `POST /api/jobs` - Submit job to queue
- `GET /api/jobs/{job_id}` - Get job status
- `GET /api/jobs/{job_id}/result` - Get job result (requires status="completed")

### Resource Endpoints
- `POST /api/resources` - Provision resource (async)
- `GET /api/resources/{resource_id}` - Get resource status
- `POST /api/resources/{resource_id}/connect` - Connect (requires status="ready")

### User Profile Endpoints
- `POST /api/users` - Create user profile (eventual consistency)
- `GET /api/users/{user_id}` - Get profile (immediate view)
- `GET /api/users/{user_id}/public` - Get public profile (cached, 2s delay)
- `GET /api/feed` - Activity feed (includes user data)
- `GET /api/search?q=<query>` - Search profiles (5s delay)
- `GET /api/analytics/users` - User analytics (10s delay)

### Comment Endpoints
- `POST /api/comments` - Create comment (stored unsanitized)
- `GET /api/posts/{post_id}/comments` - Get post comments
- `GET /api/comments/recent` - Get recent comments

### Webhook Endpoints
- `POST /api/webhooks/register` - Register webhook
- `GET /api/webhooks/events` - Get webhook events

### Testing Utilities
- `GET /api/flaky` - Randomly fails (50% rate)
- `GET /api/rate-limited` - Randomly rate-limits (30% rate)
- `GET /api/health` - Health check with stats
- `POST /api/reset` - Reset all state

## State Transition Details

### Order States
`pending` → `processing` (2s) → `completed`/`failed` (3s) → `shipped` (manual)

### Job States
`queued` → `running` (immediate) → `completed`/`failed` (configurable delay)

### Resource States
`provisioning` → `initializing` (2s) → `ready`/`error` (4s)

### Eventual Consistency Timeline
- **Immediate view**: Data available right away
- **Cached view**: 2 seconds delay
- **Search view**: 5 seconds delay  
- **Analytics view**: 10 seconds delay

## Success/Failure Rates

- Orders: 90% success, 10% failure
- Jobs: 85% success, 15% failure
- Resources: 80% success, 20% failure
- Flaky endpoint: 50% success
- Rate-limited endpoint: 70% success

## Tips for Testing

### For BurpExtension1:
1. Start with the order flow - it has the most complex state dependencies
2. Test retry logic on `/api/flaky` endpoint
3. Try chaining resource provisioning → connection
4. Experiment with different delay configurations

### For BurpExtension2:
1. Use distinct canary patterns per test: `CANARY_TEST1_001`, `CANARY_TEST2_002`, etc.
2. Monitor the feed endpoint - it aggregates data from multiple sources
3. Test the eventual consistency pattern with user profiles
4. Try injecting canaries in different fields (bio, email, metadata)
5. Check the analytics endpoint last (10s delay)

### General:
- Use `/api/reset` between test runs to clear state
- Check `/api/health` to see current object counts
- Interactive docs at `/docs` let you manually test endpoints

## Architecture Notes

- **In-memory storage** - Data doesn't persist between restarts
- **Background tasks** - State transitions happen via FastAPI BackgroundTasks
- **Async/await** - Proper async support for realistic delays
- **No authentication** - Intentionally insecure for testing
- **CORS enabled** - Can be called from browser

## Example cURL Commands

### BurpExtension1 Flow Test
```bash
# Create order
ORDER_ID=$(curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD123", "quantity": 2}' | jq -r '.order_id')

# Wait and check (retry on 404)
sleep 3
curl http://localhost:8000/api/orders/$ORDER_ID

# Ship (after status=completed)
sleep 4
curl -X PUT http://localhost:8000/api/orders/$ORDER_ID/ship
```

### BurpExtension2 Canary Test
```bash
# Create user with canary
USER_ID=$(curl -s -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "bio": "CANARY_XSS_12345"}' | jq -r '.user_id')

# Check immediate view
curl http://localhost:8000/api/users/$USER_ID

# Check feed
curl http://localhost:8000/api/feed

# Wait for search index
sleep 6
curl "http://localhost:8000/api/search?q=CANARY_XSS_12345"

# Wait for analytics
sleep 11
curl http://localhost:8000/api/analytics/users
```

## License

MIT - Built for testing BurpSuite extensions in realistic async scenarios.

