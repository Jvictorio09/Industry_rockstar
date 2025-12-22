from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Existing pages
    path("", views.home, name="home"),


    # Donation widget + Stripe
    path("donate/widget/", views.widget, name="donation_widget"),
    path("donate/create-checkout-session/", views.CreateCheckoutSessionView.as_view(), name="create_checkout_session"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("donate/success/", TemplateView.as_view(template_name="donate_success.html"), name="donate_success"),
    path("donate/cancel/", TemplateView.as_view(template_name="donate_cancel.html"), name="donate_cancel"),
    
    # MetaMask donation widget
    path("donate/widget/metamask/", views.widget_metamask, name="donation_widget_metamask"),
    
    # Web3 payment portal (Tanya's client)
    path("payment/", views.web3_payment, name="web3_payment"),
    
    # Crypto/Token payment API endpoints
    path("api/crypto/verify-transaction/", views.verify_token_transaction, name="verify_token_transaction"),
    path("api/crypto/payment-status/<str:tx_hash>/", views.payment_status, name="payment_status"),
    path("api/crypto/payment-details/<str:tx_hash>/", views.payment_details, name="payment_details"),
    
    # Payment success page
    path("payment/success/", views.payment_success, name="payment_success"),
]
