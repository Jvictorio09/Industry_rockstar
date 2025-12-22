#!/usr/bin/env python
"""Test script to verify Base RPC URL is working"""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Get RPC URL
rpc_url = os.environ.get("BASE_RPC_URL", "")

print("=" * 60)
print("Testing Base RPC URL")
print("=" * 60)

if not rpc_url:
    print("❌ BASE_RPC_URL is not set in .env file")
    exit(1)

print(f"\nRPC URL: {rpc_url[:50]}..." if len(rpc_url) > 50 else f"\nRPC URL: {rpc_url}")

# Test the RPC endpoint
print("\nTesting connection...")
try:
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_blockNumber"
    }
    
    response = requests.post(
        rpc_url,
        headers={
            'accept': 'application/json',
            'content-type': 'application/json'
        },
        json=payload,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            block_number = int(data['result'], 16)  # Convert hex to decimal
            print(f"✅ Connection successful!")
            print(f"Current Block Number: {block_number:,}")
            print(f"Response: {json.dumps(data, indent=2)}")
        elif 'error' in data:
            print(f"❌ RPC Error: {data['error']}")
        else:
            print(f"⚠️  Unexpected response: {data}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Connection failed: {e}")
    print("\nPossible issues:")
    print("  - RPC URL is incorrect or incomplete")
    print("  - Network connectivity issue")
    print("  - API key is invalid or expired")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)



