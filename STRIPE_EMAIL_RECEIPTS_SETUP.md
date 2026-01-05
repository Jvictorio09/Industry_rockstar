# Stripe Email Receipts Setup for Solutions for Change

## Overview
This guide explains how to ensure donors receive email receipts when they make donations via Stripe.

## Current Implementation

The code already sets `customer_email` in the Stripe Checkout session, which should trigger automatic receipt emails. However, you need to ensure receipts are enabled in your Stripe Dashboard.

## Method 1: Enable Automatic Receipts in Stripe Dashboard (Recommended)

Stripe automatically sends receipts when `customer_email` is provided in the checkout session. To ensure this is enabled:

1. **Log in to Stripe Dashboard**
   - Go to https://dashboard.stripe.com
   - Navigate to **Settings** → **Emails**

2. **Enable Receipt Emails**
   - Find the "Receipts" section
   - Ensure "Send receipts for successful payments" is **enabled**
   - Optionally customize the receipt email template

3. **For Subscriptions/Recurring Donations**
   - In the same section, ensure "Send invoice emails" is **enabled**
   - This will automatically send receipts for recurring donations

## Method 2: Programmatic Receipt Sending (Backup)

The webhook handler (`stripe_webhook` in `myApp/views.py`) has been updated to programmatically send receipts as a backup:

- **One-time payments**: Configures receipt email on PaymentIntent
- **Recurring donations**: Sends invoice emails when invoices are paid

This ensures receipts are sent even if automatic receipts are disabled in the dashboard.

## How It Works

### One-Time Donations
1. Donor completes checkout with email address
2. `customer_email` is set in the checkout session (already implemented)
3. Stripe automatically sends receipt email (if enabled in dashboard)
4. Webhook handler also ensures receipt is configured (backup)

### Recurring Donations (Monthly/Quarterly/Yearly)
1. Donor subscribes with email address
2. Stripe creates subscription and first invoice
3. When invoice is paid, Stripe automatically sends invoice email (if enabled)
4. Webhook handler also sends invoice email programmatically (backup)

## Testing

To test if receipts are working:

1. **Make a test donation**:
   - Go to the Solutions for Change donation page
   - Enter a test email address (use a real email you can check)
   - Complete a test donation using Stripe test mode

2. **Check your email**:
   - You should receive a receipt email from Stripe
   - The email will contain:
     - Payment amount
     - Payment date
     - Receipt number
     - Link to download PDF receipt

3. **Check Stripe Dashboard**:
   - Go to **Payments** in Stripe Dashboard
   - Find your test payment
   - Check if receipt email was sent (shown in payment details)

## Troubleshooting

### Receipts Not Being Sent

1. **Check Stripe Dashboard Settings**:
   - Go to Settings → Emails
   - Ensure "Send receipts for successful payments" is enabled

2. **Check Email Address**:
   - Ensure `customer_email` is being set correctly
   - Check the checkout session in Stripe Dashboard to verify email

3. **Check Webhook Logs**:
   - Go to Stripe Dashboard → Developers → Webhooks
   - Check webhook event logs for `checkout.session.completed`
   - Look for any errors in the webhook handler

4. **Check Spam Folder**:
   - Receipt emails may go to spam
   - Emails come from `receipts@stripe.com`

### For Recurring Donations

1. **Check Invoice Settings**:
   - Go to Settings → Emails
   - Ensure "Send invoice emails" is enabled

2. **Check Subscription**:
   - Go to Customers → Subscriptions
   - Verify customer email is set correctly
   - Check if invoices are being generated

## Customizing Receipt Emails

You can customize receipt emails in Stripe Dashboard:

1. Go to **Settings** → **Emails**
2. Click on **Receipts** or **Invoices**
3. Customize the email template:
   - Add your organization logo
   - Customize email text
   - Add tax-exempt information (for 501(c)3 organizations)

## Important Notes

- **Tax-Exempt Status**: Solutions for Change is a 501(c)3 organization. You can add this information to the receipt email template in Stripe Dashboard.
- **Receipts are Required**: For tax-deductible donations, donors need receipts. Ensure receipts are always sent.
- **Automatic vs. Programmatic**: The automatic method (dashboard setting) is preferred, but the programmatic method (webhook) serves as a backup.

## Code Reference

The relevant code is in:
- `myApp/views.py` - `CreateCheckoutSessionView` (sets `customer_email`)
- `myApp/views.py` - `stripe_webhook` (sends receipts programmatically)

## Support

If receipts are still not being sent after following this guide:
1. Check Stripe Dashboard for any error messages
2. Review webhook logs in Stripe Dashboard
3. Contact Stripe support if needed

