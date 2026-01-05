"""
Webhook service for sending payment notifications
"""
import requests
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_payment_webhook(payment):
    """
    Send payment confirmation data to webhook URL
    
    Args:
        payment: TokenPayment instance
        
    Returns:
        bool: True if webhook was sent successfully, False otherwise
    """
    webhook_url = getattr(settings, 'PAYMENT_WEBHOOK_URL', None)
    
    if not webhook_url:
        logger.warning("PAYMENT_WEBHOOK_URL not configured, skipping webhook")
        return False
    
    try:
        # Prepare webhook payload
        customer_name = f"{payment.first_name} {payment.last_name}".strip()
        if not customer_name:
            customer_name = "N/A"
        
        payload = {
            # Payment Details
            'transaction_hash': payment.transaction_hash,
            'payment_id': payment.id,
            'payment_type': payment.payment_type,
            'status': payment.status,
            'amount_usdc': str(payment.amount_token),
            'amount_usd': str(payment.amount_usd),
            'currency': 'USDC',
            
            # Customer Information
            'customer_name': customer_name,
            'first_name': payment.first_name,
            'last_name': payment.last_name,
            'email': payment.email or '',
            'mobile': payment.mobile or '',
            'company_name': payment.company_name or '',
            'notes': payment.notes or '',
            
            # Blockchain Details
            'from_address': payment.from_address,
            'to_address': payment.to_address,
            'block_number': payment.block_number,
            'confirmations': payment.confirmations,
            'required_confirmations': payment.required_confirmations,
            'basescan_url': payment.basescan_url,
            
            # Timestamps
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
            'confirmed_at': payment.confirmed_at.isoformat() if payment.confirmed_at else None,
            'webhook_sent_at': timezone.now().isoformat(),
            
            # Additional Metadata
            'org': payment.org,
            'token_contract': payment.token_contract,
        }
        
        # Send POST request to webhook
        response = requests.post(
            webhook_url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
            },
            timeout=10  # 10 second timeout
        )
        
        # Check response
        if response.status_code == 200:
            logger.info(f"Webhook sent successfully for payment {payment.transaction_hash}")
            return True
        else:
            logger.warning(
                f"Webhook returned status {response.status_code} for payment {payment.transaction_hash}. "
                f"Response: {response.text[:200]}"
            )
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Webhook timeout for payment {payment.transaction_hash}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook request failed for payment {payment.transaction_hash}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending webhook for payment {payment.transaction_hash}: {str(e)}", exc_info=True)
        return False



