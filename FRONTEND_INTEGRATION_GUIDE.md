# Web3 Payment Widget - Frontend Integration Guide

## Quick Start

### Basic Embed Code

Copy and paste this code into your website where you want the payment widget to appear:

```html
<iframe 
  id="web3-payment-iframe"
  src="https://YOUR_DOMAIN/payment/"
  title="Web3 Payment Widget"
  scrolling="no"
  style="min-height: 600px; width: 100%; border: none;">
</iframe>

<script>
  // Auto-resize iframe based on content
  window.addEventListener('message', function(event) {
    if (event.data.type === 'web3-payment-height') {
      const iframe = document.getElementById('web3-payment-iframe');
      if (iframe) {
        iframe.style.height = event.data.height + 'px';
      }
    }
  });
</script>
```

**Replace `YOUR_DOMAIN`** with the actual domain where the payment widget is hosted (e.g., `https://payments.yourcompany.com`).

---

## Complete Example

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Website</title>
</head>
<body>
  <!-- Your website content -->
  
  <!-- Web3 Payment Widget -->
  <div class="payment-widget-container">
    <iframe 
      id="web3-payment-iframe"
      src="https://YOUR_DOMAIN/payment/"
      title="Web3 Payment Widget"
      scrolling="no"
      style="min-height: 600px; width: 100%; border: none;">
    </iframe>
  </div>
  
  <!-- Auto-resize script -->
  <script>
    window.addEventListener('message', function(event) {
      if (event.data.type === 'web3-payment-height') {
        const iframe = document.getElementById('web3-payment-iframe');
        if (iframe) {
          iframe.style.height = event.data.height + 'px';
        }
      }
    });
  </script>
</body>
</html>
```

---

## Styling Options

### Custom Container Styling

```html
<style>
  .payment-widget-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    background: white;
  }
  
  #web3-payment-iframe {
    width: 100%;
    border: none;
    display: block;
  }
</style>
```

### Full Width Embed

```html
<div style="width: 100%; margin: 0;">
  <iframe 
    id="web3-payment-iframe"
    src="https://YOUR_DOMAIN/payment/"
    style="width: 100%; min-height: 600px; border: none;">
  </iframe>
</div>
```

### Centered Container

```html
<div style="max-width: 900px; margin: 40px auto; padding: 20px;">
  <iframe 
    id="web3-payment-iframe"
    src="https://YOUR_DOMAIN/payment/"
    style="width: 100%; min-height: 600px; border: none; border-radius: 12px;">
  </iframe>
</div>
```

---

## React Component Example

```jsx
import React, { useEffect, useRef } from 'react';

function Web3PaymentWidget({ domain = 'https://YOUR_DOMAIN' }) {
  const iframeRef = useRef(null);

  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data.type === 'web3-payment-height') {
        if (iframeRef.current) {
          iframeRef.current.style.height = `${event.data.height}px`;
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
      <iframe
        ref={iframeRef}
        src={`${domain}/payment/`}
        title="Web3 Payment Widget"
        scrolling="no"
        style={{
          width: '100%',
          minHeight: '600px',
          border: 'none',
          borderRadius: '12px',
        }}
      />
    </div>
  );
}

export default Web3PaymentWidget;
```

---

## Vue Component Example

```vue
<template>
  <div class="payment-widget-container">
    <iframe
      ref="paymentIframe"
      :src="widgetUrl"
      title="Web3 Payment Widget"
      scrolling="no"
      :style="iframeStyle"
    />
  </div>
</template>

<script>
export default {
  name: 'Web3PaymentWidget',
  data() {
    return {
      widgetUrl: 'https://YOUR_DOMAIN/payment/',
      iframeStyle: {
        width: '100%',
        minHeight: '600px',
        border: 'none',
        borderRadius: '12px',
      },
    };
  },
  mounted() {
    window.addEventListener('message', this.handleMessage);
  },
  beforeUnmount() {
    window.removeEventListener('message', this.handleMessage);
  },
  methods: {
    handleMessage(event) {
      if (event.data.type === 'web3-payment-height') {
        this.$refs.paymentIframe.style.height = `${event.data.height}px`;
      }
    },
  },
};
</script>

<style scoped>
.payment-widget-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}
</style>
```

---

## Requirements

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- MetaMask extension required for payments
- JavaScript enabled

### Dependencies
- None! The widget is self-contained
- No external libraries needed on your end

### Security
- Widget uses HTTPS (required)
- CSRF protection enabled
- Secure iframe communication

---

## Features

The widget includes:

✅ **Three Payment Options:**
- Course Payment: $4,995 USDC
- Supplier Listing: 100 USDC/year
- Custom Amount: Any amount (minimum 0.01 USDC)

✅ **Auto-Resizing:**
- Iframe automatically adjusts height based on content
- No manual height management needed

✅ **Mobile Responsive:**
- Works on all screen sizes
- Touch-friendly interface

✅ **Real-Time Updates:**
- Transaction status updates
- Confirmation tracking
- Payment receipt

---

## Testing

### Test the Embed

1. Replace `YOUR_DOMAIN` with your actual domain
2. Open the page in a browser
3. The widget should load and display properly
4. Test with MetaMask installed to verify payment flow

### Test Checklist

- [ ] Widget loads correctly
- [ ] Iframe resizes automatically
- [ ] MetaMask connection works
- [ ] Payment form displays
- [ ] All payment types work (Course, Supplier, Custom)
- [ ] Mobile view looks good
- [ ] Transaction status updates work

---

## Troubleshooting

### Iframe Not Resizing

Make sure you included the message listener:

```javascript
window.addEventListener('message', function(event) {
  if (event.data.type === 'web3-payment-height') {
    const iframe = document.getElementById('web3-payment-iframe');
    if (iframe) {
      iframe.style.height = event.data.height + 'px';
    }
  }
});
```

### Widget Not Loading

- Check that the domain URL is correct
- Ensure the page is served over HTTPS
- Check browser console for errors
- Verify the iframe `src` attribute is correct

### MetaMask Not Connecting

- User must have MetaMask extension installed
- User must approve the connection request
- Check browser console for error messages

---

## Support

For technical support or questions:
- Contact: [Your contact information]
- Documentation: [Link to full docs]
- Issues: [Link to issue tracker]

---

## Example URLs

Replace these with your actual domain:

- **Production:** `https://payments.yourcompany.com/payment/`
- **Staging:** `https://staging-payments.yourcompany.com/payment/`
- **Development:** `http://localhost:8000/payment/` (for testing only)

---

## Payment Flow

1. User clicks "Connect MetaMask"
2. MetaMask popup appears for connection
3. User selects payment type (Course/Supplier/Custom)
4. User fills in customer information
5. User clicks "Pay with USDC"
6. MetaMask popup appears for transaction approval
7. Transaction is submitted to blockchain
8. Payment status updates in real-time
9. User sees confirmation page with transaction details

---

## Security Notes

- All payments are processed on the Base blockchain
- No credit card information is stored
- Customer data is sent to webhook on payment confirmation
- Transaction verification happens on the backend
- All communication is encrypted (HTTPS)

---

## Need Help?

If you encounter any issues or need customization, contact the development team.

