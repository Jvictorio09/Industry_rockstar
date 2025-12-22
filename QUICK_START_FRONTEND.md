# Quick Start - Web3 Payment Widget

## For Frontend Developers

### Step 1: Copy This Code

```html
<iframe 
  id="web3-payment-iframe"
  src="https://industryrockstar-production.up.railway.app/payment/"
  title="Web3 Payment Widget"
  scrolling="no"
  style="width: 100%; min-height: 600px; border: none;">
</iframe>

<script>
  window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'web3-payment-height') {
      document.getElementById('web3-payment-iframe').style.height = event.data.height + 'px';
    }
  });
</script>
```

### Step 2: Replace Domain

**Domain is already set:**
- `https://industryrockstar-production.up.railway.app/payment/`

### Step 3: Done!

The widget will:
- ✅ Auto-resize to fit content
- ✅ Work on mobile and desktop
- ✅ Handle all payment processing
- ✅ Show real-time transaction status

---

## What You Need

- ✅ Domain URL (provided by backend team)
- ✅ HTML page to embed in
- ✅ That's it! No dependencies needed

---

## Payment Options Available

1. **Course Payment** - $4,995 USDC
2. **Supplier Listing** - 100 USDC/year  
3. **Custom Amount** - Any amount (min 0.01 USDC)

---

## Requirements

- HTTPS (required for security)
- Modern browser
- MetaMask extension (for users making payments)

---

## Need the Domain URL?

Contact: [Your contact info]

---

## Full Documentation

See `FRONTEND_INTEGRATION_GUIDE.md` for:
- React/Vue examples
- Custom styling options
- Troubleshooting
- Advanced configuration

