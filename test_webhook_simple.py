"""
Simple webhook test script (no Django required)
Usage: python test_webhook_simple.py [--type course|supplier|custom] [--amount AMOUNT]
"""
import requests
import json
import argparse
from datetime import datetime


def send_test_webhook(payment_type='course', amount_usdc=4995.00, email='test@example.com', name='Test User'):
    """Send a test webhook payload directly"""
    
    webhook_url = "https://services.leadconnectorhq.com/hooks/QHdTN3veuJ2AYB8f9dQt/webhook-trigger/ca7e5231-a2af-4f8b-8d0c-59ea1a9d364f"
    
    # Parse name
    name_parts = name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    # Create test payload
    payload = {
        # Payment Details
        'transaction_hash': f"0x{'test' * 16}{int(datetime.now().timestamp())}",
        'payment_id': 999,
        'payment_type': payment_type,
        'status': 'confirmed',
        'amount_usdc': str(amount_usdc),
        'amount_usd': str(amount_usdc),
        'currency': 'USDC',
        
        # Customer Information
        'customer_name': name,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'mobile': '+1234567890',
        'company_name': 'Test Company' if payment_type == 'supplier' else '',
        'notes': f'Test webhook for {payment_type} payment',
        
        # Blockchain Details
        'from_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',
        'to_address': '0x918e03d7c59d61b6505fed486082419941ffd77f',
        'block_number': 12345678,
        'confirmations': 2,
        'required_confirmations': 2,
        'basescan_url': f"https://basescan.org/tx/0x{'test' * 16}",
        
        # Timestamps
        'created_at': datetime.now().isoformat(),
        'confirmed_at': datetime.now().isoformat(),
        'webhook_sent_at': datetime.now().isoformat(),
        
        # Additional Metadata
        'org': 'tanya-client',
        'token_contract': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    }
    
    print("Sending webhook...")
    print(f"URL: {webhook_url}")
    print(f"Payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
            },
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text[:500]}")
        print()
        
        if response.status_code == 200:
            print("✅ Webhook sent successfully!")
            return True
        else:
            print(f"❌ Webhook returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Webhook timeout (10 seconds)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Test payment webhook (simple version)')
    parser.add_argument(
        '--type',
        choices=['course', 'supplier', 'custom'],
        default='course',
        help='Payment type (default: course)'
    )
    parser.add_argument(
        '--amount',
        type=float,
        help='Amount in USDC'
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
    
    print("=" * 60)
    print("Webhook Test Script")
    print("=" * 60)
    print(f"Type: {args.type}")
    print(f"Amount: {amount} USDC")
    print(f"Email: {args.email}")
    print(f"Name: {args.name}")
    print("=" * 60)
    print()
    
    success = send_test_webhook(
        payment_type=args.type,
        amount_usdc=amount,
        email=args.email,
        name=args.name
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

