"""
Test script to trigger the payment webhook
Usage: python test_webhook.py [--type course|supplier|custom] [--amount AMOUNT]
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from django.utils import timezone
from myApp.models import TokenPayment
from myApp.services.webhook_service import send_payment_webhook
import argparse


def create_test_payment(payment_type='course', amount_usdc=4995.00):
    """Create a test payment object for webhook testing"""
    
    # Map payment types to amounts if not specified
    if payment_type == 'course' and amount_usdc == 4995.00:
        amount_usdc = 4995.00
    elif payment_type == 'supplier' and amount_usdc == 4995.00:
        amount_usdc = 100.00
    elif payment_type == 'custom' and amount_usdc == 4995.00:
        amount_usdc = 50.00  # Default custom amount
    
    # Create a mock payment object
    # Note: We'll use get_or_create to avoid duplicate transaction hashes
    test_tx_hash = f"0x{'test' * 16}{int(timezone.now().timestamp())}"
    
    payment, created = TokenPayment.objects.get_or_create(
        transaction_hash=test_tx_hash,
        defaults={
            'from_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',
            'to_address': '0x918e03d7c59d61b6505fed486082419941ffd77f',
            'amount_raw': int(amount_usdc * 1000000),  # USDC has 6 decimals
            'amount_token': amount_usdc,
            'amount_usd': amount_usdc,  # USDC is 1:1 with USD
            'payment_type': payment_type,
            'status': 'confirmed',
            'block_number': 12345678,
            'confirmations': 2,
            'required_confirmations': 2,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'mobile': '+1234567890',
            'company_name': 'Test Company' if payment_type == 'supplier' else '',
            'notes': f'Test webhook for {payment_type} payment',
            'org': 'tanya-client',
            'confirmed_at': timezone.now(),
        }
    )
    
    return payment


def main():
    parser = argparse.ArgumentParser(description='Test payment webhook')
    parser.add_argument(
        '--type',
        choices=['course', 'supplier', 'custom'],
        default='course',
        help='Payment type (default: course)'
    )
    parser.add_argument(
        '--amount',
        type=float,
        help='Custom amount in USDC (only used for custom type)'
    )
    parser.add_argument(
        '--email',
        type=str,
        default='test@example.com',
        help='Customer email (default: test@example.com)'
    )
    parser.add_argument(
        '--name',
        type=str,
        default='Test User',
        help='Customer name (default: Test User)'
    )
    
    args = parser.parse_args()
    
    # Determine amount
    if args.amount:
        amount = args.amount
    elif args.type == 'course':
        amount = 4995.00
    elif args.type == 'supplier':
        amount = 100.00
    else:  # custom
        amount = 50.00
    
    print(f"Creating test payment...")
    print(f"  Type: {args.type}")
    print(f"  Amount: {amount} USDC")
    print(f"  Email: {args.email}")
    print(f"  Name: {args.name}")
    print()
    
    # Create test payment
    payment = create_test_payment(
        payment_type=args.type,
        amount_usdc=amount
    )
    
    # Update customer info if provided
    if args.email != 'test@example.com':
        payment.email = args.email
    if args.name != 'Test User':
        name_parts = args.name.split(' ', 1)
        payment.first_name = name_parts[0]
        payment.last_name = name_parts[1] if len(name_parts) > 1 else ''
    payment.save()
    
    print(f"Payment created: {payment.transaction_hash}")
    print(f"Sending webhook...")
    print()
    
    # Send webhook
    success = send_payment_webhook(payment)
    
    if success:
        print("✅ Webhook sent successfully!")
        print(f"   Payment ID: {payment.id}")
        print(f"   Transaction: {payment.transaction_hash}")
        print(f"   Amount: {payment.amount_token} USDC")
    else:
        print("❌ Webhook failed to send")
        print("   Check your logs for details")
        print("   Make sure PAYMENT_WEBHOOK_URL is set in settings")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())



