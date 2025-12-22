from django.shortcuts import render

# Create your views here.

# myApp/views.py
import os, json, requests
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe

def home(request):
    return render(request, "home.html")

stripe.api_key = settings.STRIPE_SECRET_KEY

def _usd_cents(amount_str: str) -> int:
    try:
        amt = Decimal(str(amount_str or "0")).quantize(Decimal("0.01"))
        return int(amt * 100) if amt > 0 else 0
    except Exception:
        return 0

def _url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.clickjacking import xframe_options_exempt

# myApp/views.py
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

@xframe_options_exempt
@ensure_csrf_cookie
def widget(request):
    ctx = {
        "org": request.GET.get("org", "solutions-for-change"),
        "RECAPTCHA_SITE_KEY": getattr(settings, "RECAPTCHA_SITE_KEY", ""),
    }
    return render(request, "solutions_for_change.html", ctx)

@xframe_options_exempt
@ensure_csrf_cookie
def widget_metamask(request):
    """MetaMask donation widget"""
    ctx = {
        "org": request.GET.get("org", "solutions-for-change"),
    }
    return render(request, "solutions_for_change_metamask.html", ctx)

@xframe_options_exempt
@ensure_csrf_cookie
def web3_payment(request):
    """Web3 payment portal for Tanya's client"""
    return render(request, "web3_payment.html")


def _verify_recaptcha(token: str) -> bool:
    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not secret:
        return True  # skip if not configured
    try:
        r = requests.post("https://www.google.com/recaptcha/api/siteverify",
                          data={"secret": secret, "response": token}, timeout=10)
        return r.json().get("success", False)
    except Exception:
        return False

@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    """
    Handles one-time and recurring (monthly/quarterly/yearly) via Checkout.
    Uses dynamic price_data (no pre-created Products).
    """
    def post(self, request, *args, **kwargs):
        # reCAPTCHA
        if not _verify_recaptcha(request.POST.get("g-recaptcha-response", "")):
            return JsonResponse({"error": "Invalid reCAPTCHA. Please try again."}, status=400)

        data = request.POST
        amount_cents = _usd_cents(data.get("amount"))
        frequency    = (data.get("frequency") or "one_time").lower().strip()

        if amount_cents <= 0:
            return HttpResponseBadRequest("Invalid amount")

        donor = {
            "first_name": data.get("first_name", ""),
            "last_name":  data.get("last_name", ""),
            "email":      data.get("email", ""),
            "mobile":     data.get("mobile", ""),
            "address":    data.get("address", ""),
            "city":       data.get("city", ""),
            "state":      data.get("state", ""),
            "country":    data.get("country", ""),
            "postal_code":data.get("postal_code", ""),
            "message":    data.get("message", ""),
            "org":        data.get("org", "solutions-for-change"),
            "frequency":  frequency,
        }

        success = _url(settings.DOMAIN, "donate/success/")
        cancel  = _url(settings.DOMAIN, "donate/cancel/")

        try:
            if frequency == "one_time":
                session = stripe.checkout.Session.create(
                    mode="payment",
                    payment_method_types=["card"],
                    customer_creation="if_required",
                    line_items=[{
                        "quantity": 1,
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": amount_cents,
                            "product_data": {"name": "Donation"},
                        }
                    }],
                    customer_email=donor.get("email") or None,
                    success_url=success,
                    cancel_url=cancel,
                    metadata=donor,
                    payment_intent_data={"metadata": donor},
                )
            else:
                # map frequency -> Stripe recurring config
                interval = "month"
                interval_count = 1
                if frequency == "quarterly":
                    interval = "month"; interval_count = 3
                elif frequency == "yearly":
                    interval = "year"; interval_count = 1
                elif frequency == "monthly":
                    interval = "month"; interval_count = 1
                else:
                    # default to monthly if unknown
                    interval = "month"; interval_count = 1

                session = stripe.checkout.Session.create(
                    mode="subscription",
                    payment_method_types=["card"],
                    line_items=[{
                        "quantity": 1,
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": amount_cents,
                            "recurring": {"interval": interval, "interval_count": interval_count},
                            "product_data": {"name": f"Recurring Donation ({frequency.title()})"},
                        },
                    }],
                    customer_email=donor.get("email") or None,
                    success_url=success,
                    cancel_url=cancel,
                    metadata=donor,
                    subscription_data={"metadata": donor},
                )

            return redirect(session.url, code=303)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    secret = settings.STRIPE_WEBHOOK_SECRET or ""
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret) if secret else json.loads(payload)
    except Exception:
        return HttpResponseBadRequest("Invalid webhook")

    # Handle core events (expand as needed)
    etype = event.get("type")
    if etype == "checkout.session.completed":
        # session = event["data"]["object"]
        pass
    elif etype == "invoice.paid":
        pass
    elif etype == "invoice.payment_failed":
        pass

    return HttpResponse(status=200)

# ========== Crypto/Web3 Payment Endpoints ==========
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone
from .models import TokenPayment
from .services.web3_service import Web3Service

@csrf_exempt
@require_http_methods(["POST"])
def verify_token_transaction(request):
    """Verify a MetaMask USDC transaction after user submits"""
    # Rate limiting (simple in-memory cache)
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    rate_limit_key = f'verify_tx_{client_ip}'
    if cache.get(rate_limit_key):
        return JsonResponse({'error': 'Rate limit exceeded. Please wait a moment.'}, status=429)
    cache.set(rate_limit_key, True, 5)  # 5 second rate limit
    
    try:
        data = json.loads(request.body)
        tx_hash = data.get('transaction_hash')
        amount_usdc = Decimal(str(data.get('amount_usdc', 0)))
        from_address = data.get('from_address', '').strip()
        
        if not tx_hash:
            return JsonResponse({'error': 'Transaction hash required'}, status=400)
        
        if amount_usdc <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Check if transaction already processed (prevent replay)
        if TokenPayment.objects.filter(transaction_hash=tx_hash).exists():
            existing = TokenPayment.objects.get(transaction_hash=tx_hash)
            return JsonResponse({
                'error': 'Transaction already processed',
                'payment_id': existing.id,
                'status': existing.status
            }, status=400)
        
        # Get customer information
        customer = {
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'email': data.get('email', ''),
            'mobile': data.get('mobile', ''),
            'company_name': data.get('company_name', ''),
            'message': data.get('message', ''),
            'notes': data.get('message', ''),  # Alias for notes
            'payment_type': data.get('payment_type', 'course'),
            'org': data.get('org', 'tanya-client'),
        }
        
        # Initialize Web3 service
        try:
            web3_service = Web3Service()
        except ValueError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Web3 service configuration error: {e}")
            return JsonResponse({
                'error': f'Blockchain service configuration error: {str(e)}'
            }, status=503)
        except ConnectionError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Web3 service connection error: {e}")
            return JsonResponse({
                'error': f'Blockchain connection error: {str(e)}'
            }, status=503)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Web3 service initialization failed: {e}")
            return JsonResponse({
                'error': f'Blockchain service error: {str(e)}'
            }, status=503)
        
        # Convert USDC amount to raw units
        expected_amount_raw = web3_service.usdc_to_raw(amount_usdc)
        
        # Verify transaction
        receiver_wallet = getattr(settings, 'RECEIVER_WALLET', '0x918e03d7c59d61b6505fed486082419941ffd77f')
        is_valid, message, transfer_event = web3_service.verify_usdc_transfer(
            tx_hash=tx_hash,
            expected_to_address=receiver_wallet,
            expected_amount_raw=expected_amount_raw,
            expected_from_address=from_address if from_address else None
        )
        
        if not is_valid:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Transaction verification failed: {tx_hash} - {message}")
            return JsonResponse({'error': f'Transaction verification failed: {message}'}, status=400)
        
        # Get transaction details
        tx_data = web3_service.get_transaction(tx_hash)
        receipt = tx_data['receipt']
        
        # Create payment record
        payment = TokenPayment.objects.create(
            transaction_hash=tx_hash,
            from_address=transfer_event['from'],
            to_address=transfer_event['to'],
            amount_raw=transfer_event['value'],
            amount_token=web3_service.raw_to_usdc(transfer_event['value']),
            amount_usd=amount_usdc,  # USDC is 1:1 with USD
            status='pending',
            block_number=receipt.blockNumber,
            confirmations=web3_service.get_confirmations(receipt.blockNumber),
            required_confirmations=getattr(settings, 'REQUIRED_CONFIRMATIONS', 2),
            gas_price=tx_data['transaction'].get('gasPrice', 0),
            gas_used=receipt.gasUsed,
            transfer_event_index=transfer_event['log_index'],
            **customer
        )
        
        # Check if already confirmed
        if payment.confirmations >= getattr(settings, 'REQUIRED_CONFIRMATIONS', 2):
            payment.status = 'confirmed'
            payment.confirmed_at = timezone.now()
            payment.save()
        
        return JsonResponse({
            'success': True,
            'payment_id': payment.id,
            'status': payment.status,
            'transaction_hash': tx_hash,
            'confirmations': payment.confirmations,
            'required_confirmations': getattr(settings, 'REQUIRED_CONFIRMATIONS', 2),
            'amount_usdc': str(payment.amount_token),
            'basescan_url': payment.basescan_url,
        })
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error verifying transaction: {e}", exc_info=True)
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@require_http_methods(["GET"])
def payment_status(request, tx_hash):
    """Check payment status"""
    try:
        payment = TokenPayment.objects.get(transaction_hash=tx_hash)
        
        # Update confirmations
        try:
            web3_service = Web3Service()
            if payment.block_number:
                payment.confirmations = web3_service.get_confirmations(payment.block_number)
                
                # Update status if confirmed
                if payment.confirmations >= getattr(settings, 'REQUIRED_CONFIRMATIONS', 2):
                    if payment.status == 'pending':
                        payment.status = 'confirmed'
                        payment.confirmed_at = timezone.now()
                        payment.save()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating confirmations: {e}")
            # Continue with cached confirmations
        
        return JsonResponse({
            'status': payment.status,
            'confirmations': payment.confirmations,
            'required_confirmations': getattr(settings, 'REQUIRED_CONFIRMATIONS', 2),
            'amount_usdc': str(payment.amount_token),
            'amount_usd': str(payment.amount_usd),
            'basescan_url': payment.basescan_url,
            'from_address': payment.from_address,
            'to_address': payment.to_address,
        })
    
    except TokenPayment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking payment status: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def payment_details(request, tx_hash):
    """Get full payment details for receipt"""
    try:
        payment = TokenPayment.objects.get(transaction_hash=tx_hash)
        
        customer_name = f"{payment.first_name} {payment.last_name}".strip()
        if not customer_name:
            customer_name = "N/A"
        
        return JsonResponse({
            'transaction_hash': payment.transaction_hash,
            'payment_type': payment.payment_type,
            'amount_usdc': str(payment.amount_token),
            'amount_usd': str(payment.amount_usd),
            'status': payment.status,
            'customer_name': customer_name,
            'email': payment.email or 'N/A',
            'company_name': payment.company_name or '',
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
            'confirmed_at': payment.confirmed_at.isoformat() if payment.confirmed_at else None,
            'basescan_url': payment.basescan_url,
            'from_address': payment.from_address,
            'to_address': payment.to_address,
            'block_number': payment.block_number,
            'confirmations': payment.confirmations,
        })
    
    except TokenPayment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching payment details: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def payment_success(request):
    """Payment success page"""
    return render(request, "payment_success.html")
