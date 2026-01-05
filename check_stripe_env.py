"""
Quick script to verify Stripe API key is loaded from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Check if Stripe keys are loaded
stripe_secret = os.environ.get("STRIPE_SECRET_KEY")
stripe_publishable = os.environ.get("STRIPE_PUBLISHABLE_KEY")

print("=" * 60)
print("Stripe Environment Variables Check")
print("=" * 60)

if stripe_secret:
    # Mask the key for security (show first 7 and last 4 chars)
    masked_key = stripe_secret[:7] + "..." + stripe_secret[-4:] if len(stripe_secret) > 11 else "***"
    print(f"✓ STRIPE_SECRET_KEY: {masked_key}")
    print(f"  Full length: {len(stripe_secret)} characters")
    print(f"  Key type: {'Live' if stripe_secret.startswith('sk_live_') else 'Test' if stripe_secret.startswith('sk_test_') else 'Unknown format'}")
else:
    print("✗ STRIPE_SECRET_KEY: NOT SET")
    print("  Please add STRIPE_SECRET_KEY=sk_test_... or sk_live_... to your .env file")

if stripe_publishable:
    masked_key = stripe_publishable[:7] + "..." + stripe_publishable[-4:] if len(stripe_publishable) > 11 else "***"
    print(f"✓ STRIPE_PUBLISHABLE_KEY: {masked_key}")
else:
    print("✗ STRIPE_PUBLISHABLE_KEY: NOT SET")
    print("  Please add STRIPE_PUBLISHABLE_KEY=pk_test_... or pk_live_... to your .env file")

print("=" * 60)

# Check .env file location
env_file = BASE_DIR / ".env"
if env_file.exists():
    print(f"✓ .env file found at: {env_file}")
else:
    print(f"✗ .env file NOT found at: {env_file}")
    print("  Please create a .env file in the project root directory")

print("=" * 60)

