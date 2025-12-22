"""
Test script to trigger BOTH course and supplier payment webhooks at once
Usage: python test_webhook_both.py
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
import time


def create_test_payment(payment_type, amount_usdc, customer_name='Test User', email='test@example.com', company_name=''):
    """Create a test payment object for webhook testing"""
    
    # Create unique transaction hash
    timestamp = int(timezone.now().timestamp())
    test_tx_hash = f"0x{'test' * 16}{timestamp}{payment_type[:3]}"
    
    # Parse customer name
    name_parts = customer_name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
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
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'mobile': '+1234567890',
            'company_name': company_name,
            'notes': f'Test webhook for {payment_type} payment',
            'org': 'tanya-client',
            'confirmed_at': timezone.now(),
        }
    )
    
    return payment


def main():
    print("=" * 70)
    print("Testing BOTH Payment Webhooks")
    print("=" * 70)
    print()
    
    results = []
    
    # 1. Course Payment
    print("📚 Creating Course Payment...")
    print(f"   Amount: $4,995 USDC")
    print(f"   Customer: Course Student")
    print()
    
    course_payment = create_test_payment(
        payment_type='course',
        amount_usdc=4995.00,
        customer_name='Course Student',
        email='course.student@example.com',
        company_name=''
    )
    
    print(f"   Payment ID: {course_payment.id}")
    print(f"   Transaction: {course_payment.transaction_hash}")
    print(f"   Sending webhook...")
    
    course_success = send_payment_webhook(course_payment)
    results.append(('Course Payment', course_success, course_payment.transaction_hash))
    
    if course_success:
        print("   ✅ Course payment webhook sent successfully!")
    else:
        print("   ❌ Course payment webhook failed")
    print()
    
    # Small delay between webhooks
    time.sleep(1)
    
    # 2. Supplier Listing Payment
    print("🏢 Creating Supplier Listing Payment...")
    print(f"   Amount: 100 USDC")
    print(f"   Customer: Supplier Company")
    print()
    
    supplier_payment = create_test_payment(
        payment_type='supplier',
        amount_usdc=100.00,
        customer_name='Supplier Manager',
        email='supplier@company.com',
        company_name='ABC Supply Co.'
    )
    
    print(f"   Payment ID: {supplier_payment.id}")
    print(f"   Transaction: {supplier_payment.transaction_hash}")
    print(f"   Sending webhook...")
    
    supplier_success = send_payment_webhook(supplier_payment)
    results.append(('Supplier Listing', supplier_success, supplier_payment.transaction_hash))
    
    if supplier_success:
        print("   ✅ Supplier listing webhook sent successfully!")
    else:
        print("   ❌ Supplier listing webhook failed")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for payment_type, success, tx_hash in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{payment_type:20} {status:15} {tx_hash[:20]}...")
    print()
    
    total_success = sum(1 for _, success, _ in results if success)
    print(f"Total: {total_success}/{len(results)} webhooks sent successfully")
    print()
    
    if total_success == len(results):
        print("🎉 All webhooks sent successfully!")
        return 0
    else:
        print("⚠️  Some webhooks failed. Check logs for details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

