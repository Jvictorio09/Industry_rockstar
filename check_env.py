#!/usr/bin/env python
"""Quick script to check if environment variables are loaded correctly"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)

base_rpc = os.environ.get("BASE_RPC_URL", "")
receiver = os.environ.get("RECEIVER_WALLET", "")
usdc_contract = os.environ.get("USDC_CONTRACT_ADDRESS", "")

print(f"\nBASE_RPC_URL:")
print(f"  Set: {bool(base_rpc)}")
print(f"  Length: {len(base_rpc)}")
if base_rpc:
    print(f"  Value: {base_rpc[:50]}..." if len(base_rpc) > 50 else f"  Value: {base_rpc}")
    if not base_rpc.startswith("https://"):
        print(f"  ⚠️  WARNING: URL doesn't start with https://")
    if "alchemy" not in base_rpc.lower() and "base" not in base_rpc.lower():
        print(f"  ⚠️  WARNING: URL might be incomplete")
else:
    print(f"  ❌ NOT SET - Add BASE_RPC_URL to your .env file")

print(f"\nRECEIVER_WALLET:")
print(f"  Set: {bool(receiver)}")
print(f"  Value: {receiver}")

print(f"\nUSDC_CONTRACT_ADDRESS:")
print(f"  Set: {bool(usdc_contract)}")
print(f"  Value: {usdc_contract}")

print("\n" + "=" * 60)
if not base_rpc:
    print("❌ BASE_RPC_URL is missing! Add it to your .env file")
elif len(base_rpc) < 50:
    print("⚠️  BASE_RPC_URL looks incomplete. Should be full Alchemy URL")
else:
    print("✅ Environment variables look good!")
print("=" * 60)



