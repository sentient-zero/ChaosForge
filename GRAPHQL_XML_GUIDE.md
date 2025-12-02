# GraphQL and XML Support - ChaosForge

ChaosForge now supports three API formats: **REST (JSON)**, **GraphQL**, and **XML**.

## Quick Reference

- **REST/JSON**: `/api/*` (original endpoints)
- **GraphQL**: `/graphql` (queries + mutations)
- **XML**: `/xml/*` (mirrors REST structure)

---

## GraphQL Endpoint

**Location:** `http://localhost:8000/graphql`  
**GraphiQL Interface:** Available at `/graphql` in browser for interactive testing

### Queries

#### Get Order
```graphql
query GetOrder {
  order(orderId: "123e4567-e89b-12d3-a456-426614174000") {
    id
    productId
    quantity
    status
    createdAt
    updatedAt
    completedAt
    shippedAt
    error
  }
}
```

#### Get Job
```graphql
query GetJob {
  job(jobId: "123e4567-e89b-12d3-a456-426614174001") {
    id
    jobType
    status
    createdAt
    startedAt
    completedAt
    result
    error
  }
}
```

#### Get Resource
```graphql
query GetResource {
  resource(resourceId: "123e4567-e89b-12d3-a456-426614174002") {
    id
    resourceType
    status
    createdAt
    updatedAt
    endpoint
    error
  }
}
```

#### Get User Profile
```graphql
query GetUser {
  user(userId: "123e4567-e89b-12d3-a456-426614174003") {
    id
    username
    bio
    email
    createdAt
  }
}
```

#### Get Comments for Post
```graphql
query GetComments {
  commentsForPost(postId: "post123") {
    id
    postId
    content
    author
    createdAt
  }
}
```

#### Get All Users
```graphql
query GetAllUsers {
  allUsers {
    id
    username
    bio
    email
    createdAt
  }
}
```

### Mutations

#### Create Order
```graphql
mutation CreateOrder {
  createOrder(
    productId: "PROD123"
    quantity: 2
    metadata: "{\"priority\": \"high\"}"
  ) {
    orderId
    status
  }
}
```

#### Ship Order
```graphql
mutation ShipOrder {
  shipOrder(orderId: "123e4567-e89b-12d3-a456-426614174000") {
    id
    status
    shippedAt
  }
}
```

#### Create Job
```graphql
mutation CreateJob {
  createJob(
    jobType: "data_export"
    delay: 5
    parameters: "{\"format\": \"csv\"}"
  ) {
    jobId
    status
  }
}
```

#### Create Resource
```graphql
mutation CreateResource {
  createResource(
    resourceType: "database"
    config: "{\"size\": \"large\"}"
  ) {
    resourceId
    status
  }
}
```

#### Create User
```graphql
mutation CreateUser {
  createUser(
    username: "testuser"
    bio: "CANARY_XSS_12345"
    email: "test@example.com"
  ) {
    userId
    username
  }
}
```

#### Create Comment
```graphql
mutation CreateComment {
  createComment(
    postId: "post123"
    content: "CANARY_STORED_001"
    author: "attacker"
  ) {
    commentId
  }
}
```

### GraphQL with cURL

```bash
# Query example
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { order(orderId: \"YOUR_ORDER_ID\") { id status } }"
  }'

# Mutation example
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createOrder(productId: \"PROD123\", quantity: 2) { orderId status } }"
  }'
```

### Testing with ChainJockey

GraphQL is perfect for testing batched operations and complex state chains:

```graphql
# Create order and immediately check status in one request
mutation CreateAndCheck {
  order: createOrder(productId: "PROD123", quantity: 2) {
    orderId
    status
  }
}

# Then use the orderId in a follow-up query
query CheckOrder {
  order(orderId: "...") {
    status
  }
}
```

**ChainJockey Use Case:**
1. Mutation to create order → Extract `orderId`
2. Query to poll status → Retry until `status="completed"`
3. Mutation to ship → Execute when ready

---

## XML Endpoints

XML endpoints mirror the REST structure but return XML instead of JSON.

**Base Path:** `/xml/*`

### Create Order (XML)

**Request:**
```bash
curl -X POST http://localhost:8000/xml/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD123",
    "quantity": 2
  }'
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<order>
  <order_id>123e4567-e89b-12d3-a456-426614174000</order_id>
  <status>pending</status>
</order>
```

### Get Order (XML)

**Request:**
```bash
curl http://localhost:8000/xml/orders/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<order>
  <id>123e4567-e89b-12d3-a456-426614174000</id>
  <product_id>PROD123</product_id>
  <quantity>2</quantity>
  <status>completed</status>
  <created_at>2024-01-15T10:30:00.000000</created_at>
  <updated_at>2024-01-15T10:30:05.000000</updated_at>
  <completed_at>2024-01-15T10:30:05.000000</completed_at>
</order>
```

### Ship Order (XML)

**Request:**
```bash
curl -X PUT http://localhost:8000/xml/orders/123e4567-e89b-12d3-a456-426614174000/ship
```

**Response (Success):**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<order>
  <id>123e4567-e89b-12d3-a456-426614174000</id>
  <status>shipped</status>
  <shipped_at>2024-01-15T10:31:00.000000</shipped_at>
  ...
</order>
```

**Response (Error):**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<error>
  <error>Cannot ship order with status 'pending'. Order must be completed first.</error>
</error>
```

### Available XML Endpoints

All these mirror their REST equivalents:

#### Orders
- `POST /xml/orders` - Create order
- `GET /xml/orders/{order_id}` - Get order
- `PUT /xml/orders/{order_id}/ship` - Ship order

#### Jobs
- `POST /xml/jobs` - Create job
- `GET /xml/jobs/{job_id}` - Get job status

#### Resources
- `POST /xml/resources` - Create resource
- `GET /xml/resources/{resource_id}` - Get resource status

#### Users
- `POST /xml/users` - Create user profile
- `GET /xml/users/{user_id}` - Get user profile

#### Comments
- `POST /xml/comments` - Create comment
- `GET /xml/posts/{post_id}/comments` - Get post comments

#### Feed
- `GET /xml/feed` - Get activity feed

### Testing with SnitchLab

XML endpoints are great for tracking canaries in XML-formatted responses:

```bash
# Create user with canary in XML
curl -X POST http://localhost:8000/xml/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "bio": "CANARY_XML_12345",
    "email": "test@example.com"
  }'

# Track where CANARY_XML_12345 appears
curl http://localhost:8000/xml/users/{user_id}
curl http://localhost:8000/xml/feed
```

SnitchLab should track canaries across XML responses just like JSON.

---

## Why Multiple Formats?

### REST/JSON
- **Standard**: Most common API format
- **Use case**: Default testing, general workflows

### GraphQL
- **Batch operations**: Query multiple resources in one request
- **Flexible queries**: Only request fields you need
- **Use case**: Testing complex state dependencies with nested queries
- **ChainJockey benefit**: Can chain mutations and queries in single requests

### XML
- **Legacy systems**: Many older APIs use XML
- **Different parsing**: XML parsers have different vulnerabilities (XXE, etc.)
- **Use case**: Testing extension handling of non-JSON responses
- **SnitchLab benefit**: Track canaries across different serialization formats

---

## Testing Scenarios

### Scenario 1: GraphQL State Chain (ChainJockey)

```graphql
# 1. Create order
mutation { 
  createOrder(productId: "PROD123", quantity: 2) { 
    orderId 
  } 
}

# 2. Poll status (ChainJockey retries until completed)
query { 
  order(orderId: "...") { 
    status 
  } 
}

# 3. Ship when ready
mutation { 
  shipOrder(orderId: "...") { 
    status 
    shippedAt 
  } 
}
```

### Scenario 2: XML Canary Tracking (SnitchLab)

```bash
# Inject canary via XML endpoint
curl -X POST http://localhost:8000/xml/users \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "bio": "CANARY_XML_001"}'

# Track across different XML endpoints
curl http://localhost:8000/xml/users/{user_id}
curl http://localhost:8000/xml/feed

# Also check JSON endpoints to see if canary appears
curl http://localhost:8000/api/feed
```

### Scenario 3: Cross-Format Testing

```bash
# Create via REST
curl -X POST http://localhost:8000/api/users \
  -d '{"username": "test", "bio": "CANARY_CROSS_001"}'

# Check in GraphQL
curl -X POST http://localhost:8000/graphql \
  -d '{"query": "query { allUsers { bio } }"}'

# Check in XML
curl http://localhost:8000/xml/feed
```

---

## Interactive Testing

### GraphQL Playground

Visit `http://localhost:8000/graphql` in your browser for the interactive GraphiQL interface. You can:
- Explore schema with auto-complete
- Test queries and mutations
- View documentation
- See response timing

### REST Swagger UI

Visit `http://localhost:8000/docs` for the standard FastAPI Swagger interface (JSON endpoints only).

---

## Implementation Notes

- **Shared logic**: All three formats use the same business logic and storage
- **Same async behavior**: State transitions, delays, and eventual consistency work identically across formats
- **No authentication**: Intentionally insecure for testing
- **Error handling**: GraphQL uses exceptions, REST/XML use HTTP status codes

---

## Tips

1. **ChainJockey**: GraphQL mutations are great for testing batched operations
2. **SnitchLab**: Test canary tracking across all three formats
3. **Mixed workflows**: Create in one format, query in another
4. **XML parsing**: Look for XXE vulnerabilities in XML parsing logic
5. **GraphQL injection**: Test for query depth limits and injection points
