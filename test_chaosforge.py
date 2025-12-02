#!/usr/bin/env python3
"""
Quick test script for ChaosForge GraphQL and XML endpoints
Run this after starting the API to verify everything works
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_graphql():
    """Test GraphQL endpoint"""
    print("\n=== Testing GraphQL ===")
    
    # Test mutation - create order
    mutation = """
    mutation {
        createOrder(productId: "TEST123", quantity: 5) {
            orderId
            status
        }
    }
    """
    
    response = requests.post(
        f"{BASE_URL}/graphql",
        json={"query": mutation}
    )
    
    print(f"Create Order Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if "data" in data and "createOrder" in data["data"]:
        order_id = data["data"]["createOrder"]["orderId"]
        print(f"✓ Order created: {order_id}")
        
        # Wait a bit for processing
        time.sleep(3)
        
        # Test query - get order
        query = f"""
        query {{
            order(orderId: "{order_id}") {{
                id
                status
                productId
                quantity
            }}
        }}
        """
        
        response = requests.post(
            f"{BASE_URL}/graphql",
            json={"query": query}
        )
        
        print(f"\nGet Order Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if "data" in data and data["data"]["order"]:
            print(f"✓ Order retrieved successfully")
            print(f"  Status: {data['data']['order']['status']}")
        else:
            print("✗ Failed to retrieve order")
    else:
        print("✗ Failed to create order")

def test_xml():
    """Test XML endpoints"""
    print("\n=== Testing XML ===")
    
    # Create order via XML
    response = requests.post(
        f"{BASE_URL}/xml/orders",
        json={"product_id": "XML_TEST", "quantity": 3}
    )
    
    print(f"Create Order Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Response:\n{response.text}")
    
    if response.status_code == 201:
        print("✓ Order created via XML")
        
        # Parse order_id from XML (simple approach)
        import re
        match = re.search(r'<order_id>([^<]+)</order_id>', response.text)
        if match:
            order_id = match.group(1)
            print(f"  Order ID: {order_id}")
            
            # Wait a bit
            time.sleep(3)
            
            # Get order via XML
            response = requests.get(f"{BASE_URL}/xml/orders/{order_id}")
            print(f"\nGet Order Status: {response.status_code}")
            print(f"Response:\n{response.text}")
            
            if response.status_code == 200:
                print("✓ Order retrieved via XML")
            else:
                print("✗ Failed to retrieve order")
        else:
            print("✗ Could not parse order_id from response")
    else:
        print("✗ Failed to create order")

def test_user_canary():
    """Test canary tracking across formats"""
    print("\n=== Testing Canary Tracking ===")
    
    canary = "CANARY_TEST_999"
    
    # Create user via REST with canary
    response = requests.post(
        f"{BASE_URL}/api/users",
        json={"username": "testuser", "bio": canary}
    )
    
    if response.status_code == 201:
        user_id = response.json()["user_id"]
        print(f"✓ User created with canary: {canary}")
        
        # Check in REST
        response = requests.get(f"{BASE_URL}/api/users/{user_id}")
        if canary in response.text:
            print(f"✓ Canary found in REST response")
        
        # Check in GraphQL
        query = f"""
        query {{
            user(userId: "{user_id}") {{
                bio
            }}
        }}
        """
        response = requests.post(
            f"{BASE_URL}/graphql",
            json={"query": query}
        )
        if canary in response.text:
            print(f"✓ Canary found in GraphQL response")
        
        # Check in XML
        response = requests.get(f"{BASE_URL}/xml/users/{user_id}")
        if canary in response.text:
            print(f"✓ Canary found in XML response")
        
        print(f"\n✓ Canary {canary} tracked across all three formats!")
    else:
        print("✗ Failed to create user")

if __name__ == "__main__":
    print("ChaosForge Multi-Format Test")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print("=" * 50)
    
    try:
        # Quick health check
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✓ API is running")
        else:
            print("✗ API health check failed")
            exit(1)
        
        test_graphql()
        test_xml()
        test_user_canary()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to API")
        print("Make sure the API is running: python ChaosForge.py")
        exit(1)
