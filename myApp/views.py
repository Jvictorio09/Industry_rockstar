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
