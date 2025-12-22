"""
Simple script to trigger BOTH course and supplier payment webhooks (no Django required)
Usage: python test_webhook_both_simple.py
"""
import requests
import json
from datetime import datetime
import time


def send_test_webhook(payment_type, amount_usdc, email, name, company_name=''):
    """Send a test webhook payload directly"""
    
    webhook_url = "https://services.leadconnectorhq.com/hooks/QHdTN3veuJ2AYB8f9dQt/webhook-trigger/ca7e5231-a2af-4f8b-8d0c-59ea1a9d364f"
    
    # Parse name
    name_parts = name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    # Create unique transaction hash
    timestamp = int(datetime.now().timestamp())
    tx_hash = f"0x{'test' * 16}{timestamp}{payment_type[:3]}"
    
    # Create test payload
    payload = {
        # Payment Details
        'transaction_hash': tx_hash,
        'payment_id': 999 if payment_type == 'course' else 998,
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
        'company_name': company_name,
        'notes': f'Test webhook for {payment_type} payment',
        
        # Blockchain Details
        'from_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',
        'to_address': '0x918e03d7c59d61b6505fed486082419941ffd77f',
        'block_number': 12345678,
        'confirmations': 2,
        'required_confirmations': 2,
        'basescan_url': f"https://basescan.org/tx/{tx_hash}",
        
        # Timestamps
        'created_at': datetime.now().isoformat(),
        'confirmed_at': datetime.now().isoformat(),
        'webhook_sent_at': datetime.now().isoformat(),
        
        # Additional Metadata
        'org': 'tanya-client',
        'token_contract': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    }
    
    print(f"  Sending {payment_type} webhook...")
    print(f"  Transaction: {tx_hash}")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✅ SUCCESS (Status: {response.status_code})")
            return True
        else:
            print(f"  ❌ FAILED (Status: {response.status_code})")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  ❌ TIMEOUT (10 seconds)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ UNEXPECTED ERROR: {str(e)}")
        return False


def main():
    print("=" * 70)
    print("Testing BOTH Payment Webhooks (Course + Supplier)")
    print("=" * 70)
    print()
    
    results = []
    
    # 1. Course Payment
    print("📚 COURSE PAYMENT")
    print("-" * 70)
    print("  Amount: $4,995 USDC")
    print("  Customer: Course Student")
    print("  Email: course.student@example.com")
    print()
    
    course_success = send_test_webhook(
        payment_type='course',
        amount_usdc=4995.00,
        email='course.student@example.com',
        name='Course Student',
        company_name=''
    )
    results.append(('Course Payment', course_success))
    print()
    
    # Small delay between webhooks
    time.sleep(1)
    
    # 2. Supplier Listing Payment
    print("🏢 SUPPLIER LISTING PAYMENT")
    print("-" * 70)
    print("  Amount: 100 USDC")
    print("  Customer: Supplier Manager")
    print("  Email: supplier@company.com")
    print("  Company: ABC Supply Co.")
    print()
    
    supplier_success = send_test_webhook(
        payment_type='supplier',
        amount_usdc=100.00,
        email='supplier@company.com',
        name='Supplier Manager',
        company_name='ABC Supply Co.'
    )
    results.append(('Supplier Listing', supplier_success))
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for payment_type, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{payment_type:20} {status}")
    print()
    
    total_success = sum(1 for _, success in results if success)
    print(f"Total: {total_success}/{len(results)} webhooks sent successfully")
    print()
    
    if total_success == len(results):
        print("🎉 All webhooks sent successfully!")
        return 0
    else:
        print("⚠️  Some webhooks failed. Check the output above for details.")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

