"""
Async Demo API for Testing BurpSuite Extensions
Simulates realistic async workflows with state transitions, delays, and storage patterns.
Built for testing ChainJockey and SnitchLab extensions.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid
import random
from collections import defaultdict

app = FastAPI(
    title="Async Demo API",
    description="Demo API for testing BurpSuite async extensions (ChainJockey & SnitchLab)",
    version="1.0.0"
)

# CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# In-Memory Storage (simulating database with eventual consistency)
# ============================================================================

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SHIPPED = "shipped"

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ResourceStatus(str, Enum):
    PROVISIONING = "provisioning"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"

# Storage
orders: Dict[str, Dict[str, Any]] = {}
jobs: Dict[str, Dict[str, Any]] = {}
resources: Dict[str, Dict[str, Any]] = {}
user_profiles: Dict[str, Dict[str, Any]] = {}
comments: List[Dict[str, Any]] = []
webhooks: List[Dict[str, Any]] = []
activity_feed: List[Dict[str, Any]] = []

# Eventual consistency simulation - data appears in different views at different times
eventual_data: Dict[str, Dict[str, Any]] = defaultdict(dict)

# ============================================================================
# Request/Response Models
# ============================================================================

class OrderCreate(BaseModel):
    product_id: str
    quantity: int
    metadata: Optional[Dict[str, Any]] = None

class OrderUpdate(BaseModel):
    action: str  # "ship", "cancel"

class JobCreate(BaseModel):
    job_type: str
    parameters: Optional[Dict[str, Any]] = None
    delay: Optional[int] = 5  # seconds to complete

class ResourceCreate(BaseModel):
    resource_type: str
    config: Optional[Dict[str, Any]] = None

class ProfileCreate(BaseModel):
    username: str
    bio: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CommentCreate(BaseModel):
    post_id: str
    content: str
    author: str

# ============================================================================
# Background State Transition Tasks
# ============================================================================

async def process_order_background(order_id: str):
    """Simulates async order processing with state transitions"""
    await asyncio.sleep(2)  # Simulate processing delay
    
    if order_id in orders:
        orders[order_id]["status"] = OrderStatus.PROCESSING
        orders[order_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to activity feed
        activity_feed.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "order_processing",
            "order_id": order_id,
            "status": "processing"
        })
        
        await asyncio.sleep(3)  # Additional processing time
        
        # Random success/failure
        if random.random() > 0.1:  # 90% success rate
            orders[order_id]["status"] = OrderStatus.COMPLETED
            orders[order_id]["completed_at"] = datetime.utcnow().isoformat()
        else:
            orders[order_id]["status"] = OrderStatus.FAILED
            orders[order_id]["error"] = "Processing failed - payment declined"
        
        orders[order_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to activity feed
        activity_feed.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "order_completed",
            "order_id": order_id,
            "status": orders[order_id]["status"]
        })

async def process_job_background(job_id: str, delay: int):
    """Simulates async job execution"""
    if job_id in jobs:
        jobs[job_id]["status"] = JobStatus.RUNNING
        jobs[job_id]["started_at"] = datetime.utcnow().isoformat()
        
        await asyncio.sleep(delay)
        
        # Random success/failure
        if random.random() > 0.15:  # 85% success rate
            jobs[job_id]["status"] = JobStatus.COMPLETED
            jobs[job_id]["result"] = {"output": f"Job {job_id} completed successfully"}
        else:
            jobs[job_id]["status"] = JobStatus.FAILED
            jobs[job_id]["error"] = "Job execution failed"
        
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()

async def provision_resource_background(resource_id: str):
    """Simulates async resource provisioning with multiple state transitions"""
    await asyncio.sleep(2)
    
    if resource_id in resources:
        resources[resource_id]["status"] = ResourceStatus.INITIALIZING
        resources[resource_id]["updated_at"] = datetime.utcnow().isoformat()
        
        await asyncio.sleep(4)
        
        # Random success/failure
        if random.random() > 0.2:  # 80% success rate
            resources[resource_id]["status"] = ResourceStatus.READY
            resources[resource_id]["endpoint"] = f"https://resource-{resource_id}.example.com"
        else:
            resources[resource_id]["status"] = ResourceStatus.ERROR
            resources[resource_id]["error"] = "Provisioning failed - insufficient capacity"
        
        resources[resource_id]["updated_at"] = datetime.utcnow().isoformat()

async def eventual_consistency_propagation(data_type: str, data_id: str, data: Dict[str, Any]):
    """Simulates eventual consistency - data appears in different views over time"""
    # Immediate view (no delay)
    eventual_data[f"{data_type}_immediate"][data_id] = data
    
    # Delayed view 1 (2 seconds)
    await asyncio.sleep(2)
    eventual_data[f"{data_type}_cached"][data_id] = data
    
    # Delayed view 2 (5 seconds)
    await asyncio.sleep(3)
    eventual_data[f"{data_type}_search"][data_id] = data
    
    # Delayed view 3 (10 seconds)
    await asyncio.sleep(5)
    eventual_data[f"{data_type}_analytics"][data_id] = data

# ============================================================================
# Order Endpoints (ChainJockey Testing)
# ============================================================================

@app.post("/api/orders", status_code=201)
async def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    """Create a new order - starts async processing"""
    order_id = str(uuid.uuid4())
    
    order_data = {
        "id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "metadata": order.metadata,
        "status": OrderStatus.PENDING,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    orders[order_id] = order_data
    
    # Start background processing
    background_tasks.add_task(process_order_background, order_id)
    
    return {"order_id": order_id, "status": OrderStatus.PENDING}

@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Get order status - may return 404 until processing starts"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return orders[order_id]

@app.put("/api/orders/{order_id}/ship")
async def ship_order(order_id: str):
    """Ship order - only works when status is 'completed'"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders[order_id]
    
    if order["status"] != OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot ship order with status '{order['status']}'. Order must be completed first."
        )
    
    order["status"] = OrderStatus.SHIPPED
    order["shipped_at"] = datetime.utcnow().isoformat()
    order["updated_at"] = datetime.utcnow().isoformat()
    
    return order

@app.delete("/api/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel order - only works if not yet shipped"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders[order_id]
    
    if order["status"] == OrderStatus.SHIPPED:
        raise HTTPException(status_code=409, detail="Cannot cancel shipped order")
    
    del orders[order_id]
    return {"message": "Order cancelled"}

# ============================================================================
# Job/Task Queue Endpoints (ChainJockey Testing)
# ============================================================================

@app.post("/api/jobs", status_code=202)
async def create_job(job: JobCreate, background_tasks: BackgroundTasks):
    """Submit a job to queue - processes asynchronously"""
    job_id = str(uuid.uuid4())
    
    job_data = {
        "id": job_id,
        "job_type": job.job_type,
        "parameters": job.parameters,
        "status": JobStatus.QUEUED,
        "created_at": datetime.utcnow().isoformat()
    }
    
    jobs[job_id] = job_data
    
    # Start background job
    background_tasks.add_task(process_job_background, job_id, job.delay)
    
    return {"job_id": job_id, "status": JobStatus.QUEUED}

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/api/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    """Get job result - only available when status is 'completed'"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Job result not available. Current status: {job['status']}"
        )
    
    return job.get("result", {})

# ============================================================================
# Resource Provisioning Endpoints (ChainJockey Testing)
# ============================================================================

@app.post("/api/resources", status_code=202)
async def create_resource(resource: ResourceCreate, background_tasks: BackgroundTasks):
    """Provision a new resource - takes time to become ready"""
    resource_id = str(uuid.uuid4())
    
    resource_data = {
        "id": resource_id,
        "resource_type": resource.resource_type,
        "config": resource.config,
        "status": ResourceStatus.PROVISIONING,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    resources[resource_id] = resource_data
    
    # Start provisioning
    background_tasks.add_task(provision_resource_background, resource_id)
    
    return {"resource_id": resource_id, "status": ResourceStatus.PROVISIONING}

@app.get("/api/resources/{resource_id}")
async def get_resource(resource_id: str):
    """Get resource status"""
    if resource_id not in resources:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    return resources[resource_id]

@app.post("/api/resources/{resource_id}/connect")
async def connect_to_resource(resource_id: str):
    """Connect to resource - only works when status is 'ready'"""
    if resource_id not in resources:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource = resources[resource_id]
    
    if resource["status"] != ResourceStatus.READY:
        raise HTTPException(
            status_code=503,
            detail=f"Resource not ready. Current status: {resource['status']}"
        )
    
    return {
        "connection_string": resource.get("endpoint"),
        "credentials": {"user": "demo", "token": str(uuid.uuid4())}
    }

# ============================================================================
# User Profile Endpoints (SnitchLab Testing - Storage & Retrieval)
# ============================================================================

@app.post("/api/users", status_code=201)
async def create_user_profile(profile: ProfileCreate, background_tasks: BackgroundTasks):
    """Create user profile - data appears in various endpoints over time"""
    user_id = str(uuid.uuid4())
    
    profile_data = {
        "id": user_id,
        "username": profile.username,
        "bio": profile.bio,
        "email": profile.email,
        "metadata": profile.metadata,
        "created_at": datetime.utcnow().isoformat()
    }
    
    user_profiles[user_id] = profile_data
    
    # Simulate eventual consistency propagation
    background_tasks.add_task(eventual_consistency_propagation, "profile", user_id, profile_data)
    
    return {"user_id": user_id, "username": profile.username}

@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile - immediate view"""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_profiles[user_id]

@app.get("/api/users/{user_id}/public")
async def get_user_public_profile(user_id: str):
    """Get public user profile - cached view (2 second delay)"""
    profile_key = f"profile_cached"
    
    if user_id not in eventual_data.get(profile_key, {}):
        raise HTTPException(status_code=404, detail="User profile not yet available in public view")
    
    profile = eventual_data[profile_key][user_id]
    # Return only public fields
    return {
        "username": profile["username"],
        "bio": profile["bio"],
        "created_at": profile["created_at"]
    }

@app.get("/api/feed")
async def get_user_feed():
    """Get activity feed - may contain user bios from profile creation"""
    feed_items = []
    
    # Include recent user profiles in feed
    for user_id, profile in user_profiles.items():
        feed_items.append({
            "type": "user_joined",
            "user_id": user_id,
            "username": profile["username"],
            "bio": profile.get("bio", ""),
            "timestamp": profile["created_at"]
        })
    
    # Include order activity
    feed_items.extend(activity_feed[-10:])  # Last 10 activities
    
    # Sort by timestamp
    feed_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {"feed": feed_items[:20]}

@app.get("/api/search")
async def search_profiles(q: str):
    """Search profiles - search index view (5 second delay)"""
    profile_key = "profile_search"
    
    if profile_key not in eventual_data:
        return {"results": []}
    
    results = []
    for user_id, profile in eventual_data[profile_key].items():
        # Simple search in username and bio
        search_text = f"{profile['username']} {profile.get('bio', '')}".lower()
        if q.lower() in search_text:
            results.append(profile)
    
    return {"results": results}

# ============================================================================
# Comments Endpoints (SnitchLab Testing - Stored XSS Patterns)
# ============================================================================

@app.post("/api/comments", status_code=201)
async def create_comment(comment: CommentCreate):
    """Create a comment - stored and retrieved later"""
    comment_id = str(uuid.uuid4())
    
    comment_data = {
        "id": comment_id,
        "post_id": comment.post_id,
        "content": comment.content,  # NOT sanitized - for testing
        "author": comment.author,
        "created_at": datetime.utcnow().isoformat()
    }
    
    comments.append(comment_data)
    
    return {"comment_id": comment_id}

@app.get("/api/posts/{post_id}/comments")
async def get_post_comments(post_id: str):
    """Get comments for a post - returns stored content including canaries"""
    post_comments = [c for c in comments if c["post_id"] == post_id]
    return {"comments": post_comments}

@app.get("/api/comments/recent")
async def get_recent_comments():
    """Get recent comments across all posts"""
    return {"comments": comments[-10:]}

# ============================================================================
# Analytics/Reporting Endpoints (SnitchLab Testing - Delayed Appearance)
# ============================================================================

@app.get("/api/analytics/users")
async def get_user_analytics():
    """User analytics - data appears here last (10 second delay)"""
    profile_key = "profile_analytics"
    
    if profile_key not in eventual_data:
        return {"total_users": 0, "users": []}
    
    users = list(eventual_data[profile_key].values())
    
    return {
        "total_users": len(users),
        "users": users,
        "aggregated_data": {
            "with_bio": sum(1 for u in users if u.get("bio")),
            "with_email": sum(1 for u in users if u.get("email"))
        }
    }

# ============================================================================
# Webhook Simulation (SnitchLab Testing - Callback Tracking)
# ============================================================================

@app.post("/api/webhooks/register")
async def register_webhook(url: str, event_type: str):
    """Register a webhook - simulates callback mechanism"""
    webhook_id = str(uuid.uuid4())
    
    webhook_data = {
        "id": webhook_id,
        "url": url,
        "event_type": event_type,
        "created_at": datetime.utcnow().isoformat()
    }
    
    webhooks.append(webhook_data)
    
    return {"webhook_id": webhook_id}

@app.get("/api/webhooks/events")
async def get_webhook_events():
    """Get recent webhook events - shows registered URLs including canaries"""
    return {"webhooks": webhooks}

# ============================================================================
# Error Simulation Endpoints (Testing Retry Logic)
# ============================================================================

@app.get("/api/flaky")
async def flaky_endpoint():
    """Randomly fails - good for testing retry logic"""
    if random.random() < 0.5:  # 50% failure rate
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    
    return {"status": "success", "message": "Request succeeded"}

@app.get("/api/rate-limited")
async def rate_limited_endpoint():
    """Simulates rate limiting"""
    if random.random() < 0.3:  # 30% chance of rate limit
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return {"status": "success"}

# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Async Demo API",
        "version": "1.0.0",
        "description": "Demo API for testing BurpSuite async extensions",
        "docs": "/docs",
        "endpoints": {
            "orders": "/api/orders - Order processing workflow",
            "jobs": "/api/jobs - Async job queue",
            "resources": "/api/resources - Resource provisioning",
            "users": "/api/users - User profiles with eventual consistency",
            "comments": "/api/comments - Stored content tracking",
            "webhooks": "/api/webhooks - Callback simulation",
            "analytics": "/api/analytics - Delayed data views"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "stats": {
            "orders": len(orders),
            "jobs": len(jobs),
            "resources": len(resources),
            "users": len(user_profiles),
            "comments": len(comments)
        }
    }

@app.post("/api/reset")
async def reset_state():
    """Reset all state - useful between tests"""
    orders.clear()
    jobs.clear()
    resources.clear()
    user_profiles.clear()
    comments.clear()
    webhooks.clear()
    activity_feed.clear()
    eventual_data.clear()
    
    return {"message": "State reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

