# MetaMask Payment Integration Plan - USDC on Base Mainnet

## Table of Contents
1. [Overview](#overview)
2. [What is MetaMask?](#what-is-metamask)
3. [Technical Requirements](#technical-requirements)
4. [Dependencies & Libraries](#dependencies--libraries)
5. [Architecture Overview](#architecture-overview)
6. [Implementation Steps](#implementation-steps)
7. [Database Models](#database-models)
8. [Backend Implementation](#backend-implementation)
9. [Frontend Implementation](#frontend-implementation)
10. [Security Considerations](#security-considerations)
11. [Testing Requirements](#testing-requirements)
12. [Integration with Existing Payment System](#integration-with-existing-payment-system)
13. [Costs & Considerations](#costs--considerations)
14. [Timeline Estimate](#timeline-estimate)

---

## Overview

This document outlines the requirements and implementation plan for integrating MetaMask cryptocurrency payments into the existing donation system. MetaMask will allow users to make donations using **USDC (USD Coin)** on **Base mainnet** directly from their Web3 wallet.

**Current System**: Stripe-based payment processing for one-time and recurring donations  
**New Addition**: MetaMask/Web3 payment option using USDC on Base mainnet alongside existing Stripe payments

**Key Implementation Note**: Because USDC is an ERC-20 token (not native ETH), we must verify donations using `Transfer` event logs from the USDC token contract, NOT using `tx.value`.

---

## What is MetaMask?

MetaMask is a browser extension and mobile app that serves as a cryptocurrency wallet and gateway to Web3 applications. It allows users to:
- Store cryptocurrencies (ETH, ERC-20 tokens like USDC)
- Interact with blockchain-based applications
- Sign transactions securely
- Connect to decentralized applications (dApps)

**Key Concepts:**
- **Wallet Address**: A unique identifier (0x...) representing a user's account
- **Transaction**: A signed operation that transfers cryptocurrency
- **Gas Fees**: Network fees required to process blockchain transactions (paid in ETH, even for USDC transfers)
- **ERC-20 Tokens**: Standardized tokens on Ethereum-compatible networks (like USDC)
- **Transfer Events**: Logs emitted by ERC-20 contracts when tokens are transferred
- **Base Network**: A Layer 2 scaling solution for Ethereum with lower fees
- **Web3.js/Ethers.js**: JavaScript libraries to interact with blockchain networks

---

## Technical Requirements

### 1. **Blockchain Network**
- **Network**: Base Mainnet (Chain ID: 8453)
- **Token**: USDC (USD Coin) - ERC-20 token
- **USDC Contract Address on Base**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **USDC Decimals**: 6 (1 USDC = 1,000,000 smallest units)
- **Receiving Wallet**: `0x918e03d7c59d61b6505fed486082419941ffd77f` (confirmed by client)

### 2. **RPC Provider**
- **Alchemy Base RPC URL**: Provided by client (store in environment variables as secret)
- Alternative: Public Base RPC (less reliable, may be rate-limited)

### 3. **Transaction Verification Method**
- **CRITICAL**: USDC is an ERC-20 token, so we **cannot** use `tx.value` (which is always 0 for token transfers)
- **Must verify**: `Transfer` event logs emitted by the USDC contract
- Verify event parameters:
  - `from`: Donor's wallet address
  - `to`: Our receiving wallet address (`0x918e03d7c59d61b6505fed486082419941ffd77f`)
  - `value`: Amount in smallest units (with 6 decimals)

### 4. **Backend Requirements**
- Python Web3 library (web3.py) for blockchain interaction
- ERC-20 Transfer event parsing and verification
- Transaction confirmation monitoring
- Payment status tracking
- Integration with existing donation models

### 5. **Frontend Requirements**
- MetaMask detection and connection
- Base network detection and switching
- Ethers.js for ERC-20 token interaction
- USDC contract `transfer()` function call
- Transaction signing UI
- Payment status updates
- Error handling for failed transactions

### 6. **Configuration Requirements**
- `CHAIN=base`
- `BASE_RPC_URL=<Alchemy URL>` (treat as secret)
- `RECEIVER_WALLET=0x918e03d7c59d61b6505fed486082419941ffd77f`
- `USDC_CONTRACT_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- `USDC_DECIMALS=6`
- `REQUIRED_CONFIRMATIONS=2` (default 1-3; recommend 2)

---

## Dependencies & Libraries

### Backend (Python/Django)
```python
# Add to requirements.txt
web3==6.15.1              # Python library for blockchain interaction
eth-account==0.10.0       # Ethereum account management
eth-utils==2.3.1          # Ethereum utility functions
python-dotenv==1.0.1      # Already installed - for env vars
```

### Frontend (JavaScript)
```html
<!-- Add to templates -->
<script src="https://cdn.ethers.io/lib/ethers-5.7.2.umd.min.js"></script>
```

**Recommended**: Use Ethers.js v5 (modern, easier to use, better ERC-20 support)

### Environment Variables Needed
```env
# Blockchain Configuration
CHAIN=base
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY  # From Alchemy (SECRET)
RECEIVER_WALLET=0x918e03d7c59d61b6505fed486082419941ffd77f
USDC_CONTRACT_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
USDC_DECIMALS=6
REQUIRED_CONFIRMATIONS=2
```

**IMPORTANT**: 
- Never commit `BASE_RPC_URL` to version control
- Store in `.env` file or secure secrets management
- Treat RPC URL as sensitive (rate limiting, API keys)

---

## Architecture Overview

```
┌─────────────────┐
│   User Browser  │
│  (MetaMask)     │
└────────┬────────┘
         │
         │ 1. Connect Wallet
         │ 2. Switch to Base Network
         │ 3. Call USDC.transfer()
         │ 4. Sign Transaction
         │
┌────────▼─────────────────────────┐
│      Frontend (JavaScript)       │
│  - Detect MetaMask               │
│  - Ensure Base Network           │
│  - Build USDC transfer() call    │
│  - Send Transaction              │
│  - Get Transaction Hash          │
└────────┬─────────────────────────┘
         │
         │ Transaction Hash
         │
┌────────▼─────────────────────────┐
│    Base Mainnet Blockchain       │
│  - USDC Contract                 │
│  - Transfer Event Emitted        │
└────────┬─────────────────────────┘
         │
         │ Transaction Receipt
         │ Transfer Event Logs
         │
┌────────▼─────────────────────────┐
│    Django Backend                │
│  - Verify Transaction            │
│  - Parse Transfer Events         │
│  - Verify: to, from, value       │
│  - Check Confirmations            │
│  - Update Database               │
│  - Send Confirmation Email       │
└──────────────────────────────────┘
```

---

## Implementation Steps

### Phase 1: Setup & Configuration
1. **Configure Environment Variables**
   - Add Base RPC URL from Alchemy to `.env` (never commit)
   - Set receiving wallet address
   - Set USDC contract address and decimals
   - Set required confirmations (recommend 2)

2. **Install Dependencies**
   ```bash
   pip install web3 eth-account eth-utils
   ```

3. **Update Settings**
   - Add blockchain configuration to `settings.py`
   - Load environment variables securely

### Phase 2: Database Models
1. **Create TokenPayment Model** (or rename CryptoPayment)
   - Store USDC transaction details
   - Link to existing donation records (if applicable)

2. **Fields Needed**:
   - Transaction hash (unique identifier)
   - From address (donor's wallet)
   - To address (receiving wallet)
   - Token type (USDC)
   - Amount (raw + human-readable)
   - Status (pending, confirmed, failed)
   - Block number
   - Confirmation count
   - Timestamp
   - Donor information (name, email, etc.)

### Phase 3: Backend Implementation
1. **ERC-20 Transfer Event Verification Service**
   - Function to fetch transaction receipt
   - Parse Transfer event logs
   - Verify event parameters (to, from, value)
   - Check transaction status
   - Monitor confirmations

2. **API Endpoints**
   - `POST /api/crypto/verify-transaction/` - Verify transaction after user submits
   - `GET /api/crypto/payment-status/<tx_hash>/` - Check payment status
   - `GET /api/crypto/usdc-info/` - Get USDC contract info (optional)

3. **Background Tasks** (Optional)
   - Celery task to periodically check pending transactions
   - Auto-update payment status when confirmed

### Phase 4: Frontend Implementation
1. **MetaMask Detection**
   - Check if MetaMask is installed
   - Prompt user to install if missing

2. **Network Detection & Switching**
   - Check if connected to Base (Chain ID: 8453)
   - Prompt user to switch if on wrong network
   - Add Base network if not present

3. **USDC Contract Interaction**
   - Load USDC contract ABI
   - Call `transfer(recipient, amount)` function
   - Handle transaction signing
   - Get transaction hash

4. **Transaction Sending**
   - Build transaction with USDC contract address
   - Set value to 0 (token transfer, not ETH)
   - Include gas estimation
   - Request user signature
   - Send transaction to network
   - Get transaction hash

5. **Payment Confirmation**
   - POST transaction hash to backend
   - Poll backend for transaction status
   - Show confirmation when verified
   - Redirect to success page

### Phase 5: UI/UX Integration
1. **Payment Method Selection**
   - Add "Pay with MetaMask (USDC)" option to donation form
   - Toggle between Stripe and MetaMask

2. **Transaction Status Display**
   - Show pending transactions
   - Display transaction hash with link to Basescan
   - Show confirmation progress

3. **Error Handling**
   - Handle rejected transactions
   - Handle network errors
   - Handle insufficient USDC balance
   - Handle wrong network
   - Handle insufficient ETH for gas

---

## Database Models

### New Model: `TokenPayment`

```python
# myApp/models.py

from django.db import models
from django.utils import timezone
from django.conf import settings

class TokenPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    TOKEN_CHOICES = [
        ('USDC', 'USD Coin'),
        # Can add more tokens later
    ]
    
    # Transaction Details
    transaction_hash = models.CharField(max_length=66, unique=True, db_index=True)
    from_address = models.CharField(max_length=42)  # Donor's wallet
    to_address = models.CharField(max_length=42)    # Receiving wallet
    amount_raw = models.DecimalField(max_digits=36, decimal_places=0)  # Amount in smallest units
    amount_token = models.DecimalField(max_digits=18, decimal_places=6)  # Amount in USDC (6 decimals)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)  # USD equivalent (1:1 for USDC)
    token_type = models.CharField(max_length=10, choices=TOKEN_CHOICES, default='USDC')
    token_contract = models.CharField(max_length=42, default=settings.USDC_CONTRACT_ADDRESS)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    block_number = models.BigIntegerField(null=True, blank=True)
    confirmations = models.IntegerField(default=0)
    required_confirmations = models.IntegerField(default=2)
    
    # Donor Information (from form)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    org = models.CharField(max_length=100, default='solutions-for-change')
    
    # Frequency (for future recurring donations)
    frequency = models.CharField(max_length=20, default='one_time')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    gas_price = models.DecimalField(max_digits=36, decimal_places=0, null=True, blank=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    
    # Verification details
    transfer_event_index = models.IntegerField(null=True, blank=True)  # Which log index had the Transfer event
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['from_address']),
            models.Index(fields=['to_address']),
        ]
    
    def __str__(self):
        return f"{self.transaction_hash[:10]}... - {self.amount_token} USDC - {self.status}"
    
    @property
    def basescan_url(self):
        """Generate Basescan URL for transaction"""
        return f"https://basescan.org/tx/{self.transaction_hash}"
```

---

## Backend Implementation

### 1. Settings Configuration

```python
# myProject/settings.py - Add these

# Base Network / USDC Configuration
CHAIN = os.environ.get("CHAIN", "base")
BASE_RPC_URL = os.environ.get("BASE_RPC_URL", "")  # From Alchemy (SECRET)
RECEIVER_WALLET = os.environ.get("RECEIVER_WALLET", "0x918e03d7c59d61b6505fed486082419941ffd77f")
USDC_CONTRACT_ADDRESS = os.environ.get("USDC_CONTRACT_ADDRESS", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
USDC_DECIMALS = int(os.environ.get("USDC_DECIMALS", "6"))
REQUIRED_CONFIRMATIONS = int(os.environ.get("REQUIRED_CONFIRMATIONS", "2"))

if not BASE_RPC_URL:
    raise ValueError("BASE_RPC_URL must be set in environment variables")
```

### 2. ERC-20 ABI (Minimal)

```python
# myApp/services/erc20_abi.py

# Minimal ABI for USDC contract - only what we need
USDC_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]
```

### 3. Web3 Service

```python
# myApp/services/web3_service.py (create new file)

from web3 import Web3
from django.conf import settings
from decimal import Decimal
import logging
from .erc20_abi import USDC_ABI

logger = logging.getLogger(__name__)

class Web3Service:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BASE_RPC_URL))
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Base network")
        
        # Initialize USDC contract
        self.usdc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(settings.USDC_CONTRACT_ADDRESS),
            abi=USDC_ABI
        )
    
    def usdc_to_raw(self, usdc_amount):
        """Convert USDC amount to raw units (with 6 decimals)"""
        return int(Decimal(str(usdc_amount)) * Decimal(10 ** settings.USDC_DECIMALS))
    
    def raw_to_usdc(self, raw_amount):
        """Convert raw units to USDC amount"""
        return Decimal(str(raw_amount)) / Decimal(10 ** settings.USDC_DECIMALS)
    
    def get_transaction(self, tx_hash):
        """Get transaction details from blockchain"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'transaction': tx,
                'receipt': receipt,
                'status': receipt.status,  # 1 = success, 0 = failed
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'logs': receipt.logs,
            }
        except Exception as e:
            logger.error(f"Error fetching transaction {tx_hash}: {e}")
            return None
    
    def get_current_block(self):
        """Get current block number"""
        return self.w3.eth.block_number
    
    def get_confirmations(self, block_number):
        """Get number of confirmations for a block"""
        current_block = self.get_current_block()
        if block_number:
            return max(0, current_block - block_number)
        return 0
    
    def parse_transfer_events(self, receipt_logs):
        """Parse Transfer events from transaction logs"""
        transfer_events = []
        
        for log in receipt_logs:
            try:
                # Try to decode as Transfer event
                event = self.usdc_contract.events.Transfer().process_log(log)
                transfer_events.append({
                    'from': event.args['from'],
                    'to': event.args['to'],
                    'value': event.args['value'],
                    'log_index': log.logIndex,
                })
            except Exception:
                # Not a Transfer event, skip
                continue
        
        return transfer_events
    
    def verify_usdc_transfer(self, tx_hash, expected_to_address, expected_amount_raw=None, expected_from_address=None):
        """
        Verify USDC Transfer event matches expected parameters.
        
        Returns: (is_valid, message, transfer_event)
        """
        tx_data = self.get_transaction(tx_hash)
        if not tx_data:
            return False, "Transaction not found", None
        
        receipt = tx_data['receipt']
        
        # Check transaction status
        if receipt.status != 1:
            return False, "Transaction failed", None
        
        # Parse Transfer events
        transfer_events = self.parse_transfer_events(receipt.logs)
        
        if not transfer_events:
            return False, "No Transfer events found in transaction", None
        
        # Find Transfer event to our receiving wallet
        target_transfer = None
        for event in transfer_events:
            if event['to'].lower() == expected_to_address.lower():
                target_transfer = event
                break
        
        if not target_transfer:
            return False, f"No Transfer event found to receiving wallet {expected_to_address}", None
        
        # Verify recipient
        if target_transfer['to'].lower() != expected_to_address.lower():
            return False, f"Recipient mismatch: {target_transfer['to']} != {expected_to_address}", None
        
        # Verify amount if provided
        if expected_amount_raw is not None:
            # Allow small tolerance for rounding (1 unit = 0.000001 USDC)
            tolerance = 1
            if abs(target_transfer['value'] - expected_amount_raw) > tolerance:
                return False, f"Amount mismatch: {target_transfer['value']} != {expected_amount_raw}", None
        
        # Verify from address if provided
        if expected_from_address is not None:
            if target_transfer['from'].lower() != expected_from_address.lower():
                return False, f"Sender mismatch: {target_transfer['from']} != {expected_from_address}", None
        
        return True, "Transfer verified", target_transfer
```

### 4. Views

```python
# myApp/views.py - Add these views

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils import timezone
from .models import TokenPayment
from .services.web3_service import Web3Service
from decimal import Decimal
import json
import logging

logger = logging.getLogger(__name__)

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
        
        # Get donor information
        donor = {
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'email': data.get('email', ''),
            'mobile': data.get('mobile', ''),
            'address': data.get('address', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'country': data.get('country', ''),
            'postal_code': data.get('postal_code', ''),
            'message': data.get('message', ''),
            'org': data.get('org', 'solutions-for-change'),
            'frequency': data.get('frequency', 'one_time'),
        }
        
        # Initialize Web3 service
        try:
            web3_service = Web3Service()
        except Exception as e:
            logger.error(f"Web3 service initialization failed: {e}")
            return JsonResponse({'error': 'Blockchain service unavailable'}, status=503)
        
        # Convert USDC amount to raw units
        expected_amount_raw = web3_service.usdc_to_raw(amount_usdc)
        
        # Verify transaction
        is_valid, message, transfer_event = web3_service.verify_usdc_transfer(
            tx_hash=tx_hash,
            expected_to_address=settings.RECEIVER_WALLET,
            expected_amount_raw=expected_amount_raw,
            expected_from_address=from_address if from_address else None
        )
        
        if not is_valid:
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
            required_confirmations=settings.REQUIRED_CONFIRMATIONS,
            gas_price=tx_data['transaction'].get('gasPrice', 0),
            gas_used=receipt.gasUsed,
            transfer_event_index=transfer_event['log_index'],
            **donor
        )
        
        # Check if already confirmed
        if payment.confirmations >= settings.REQUIRED_CONFIRMATIONS:
            payment.status = 'confirmed'
            payment.confirmed_at = timezone.now()
            payment.save()
        
        return JsonResponse({
            'success': True,
            'payment_id': payment.id,
            'status': payment.status,
            'transaction_hash': tx_hash,
            'confirmations': payment.confirmations,
            'required_confirmations': settings.REQUIRED_CONFIRMATIONS,
            'amount_usdc': str(payment.amount_token),
            'basescan_url': payment.basescan_url,
        })
    
    except Exception as e:
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
                if payment.confirmations >= settings.REQUIRED_CONFIRMATIONS:
                    if payment.status == 'pending':
                        payment.status = 'confirmed'
                        payment.confirmed_at = timezone.now()
                        payment.save()
        except Exception as e:
            logger.error(f"Error updating confirmations: {e}")
            # Continue with cached confirmations
        
        return JsonResponse({
            'status': payment.status,
            'confirmations': payment.confirmations,
            'required_confirmations': settings.REQUIRED_CONFIRMATIONS,
            'amount_usdc': str(payment.amount_token),
            'amount_usd': str(payment.amount_usd),
            'basescan_url': payment.basescan_url,
            'from_address': payment.from_address,
            'to_address': payment.to_address,
        })
    
    except TokenPayment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@cache_page(60)  # Cache for 1 minute
def usdc_info(request):
    """Get USDC contract information"""
    return JsonResponse({
        'contract_address': settings.USDC_CONTRACT_ADDRESS,
        'decimals': settings.USDC_DECIMALS,
        'receiver_wallet': settings.RECEIVER_WALLET,
        'chain': settings.CHAIN,
        'chain_id': 8453,  # Base mainnet
    })
```

### 5. URL Configuration

```python
# myApp/urls.py - Add these routes

urlpatterns = [
    # ... existing patterns ...
    
    # Crypto/Token payment endpoints
    path('api/crypto/verify-transaction/', views.verify_token_transaction, name='verify_token_transaction'),
    path('api/crypto/payment-status/<str:tx_hash>/', views.payment_status, name='payment_status'),
    path('api/crypto/usdc-info/', views.usdc_info, name='usdc_info'),
]
```

---

## Frontend Implementation

### 1. MetaMask Detection & Connection

```javascript
// Add to solutions_for_change.html or create separate JS file

// Base Network Configuration
const BASE_CHAIN_ID = 8453; // Base mainnet
const BASE_CHAIN_NAME = 'Base';
const BASE_RPC_URL = 'https://mainnet.base.org'; // Public RPC (or use your Alchemy URL)
const BASE_EXPLORER_URL = 'https://basescan.org';

// USDC Contract Address on Base
const USDC_CONTRACT_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const USDC_DECIMALS = 6;
const RECEIVER_WALLET = '0x918e03d7c59d61b6505fed486082419941ffd77f';

// Minimal USDC ABI (only transfer function and Transfer event)
const USDC_ABI = [
    {
        "constant": false,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "name": "from", "type": "address"},
            {"indexed": true, "name": "to", "type": "address"},
            {"indexed": false, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
];

// Check if MetaMask is installed
function isMetaMaskInstalled() {
    return typeof window.ethereum !== 'undefined' && window.ethereum.isMetaMask;
}

// Connect to MetaMask
async function connectMetaMask() {
    if (!isMetaMaskInstalled()) {
        alert('MetaMask is not installed. Please install MetaMask to continue.');
        window.open('https://metamask.io/download/', '_blank');
        return null;
    }
    
    try {
        // Request account access
        const accounts = await window.ethereum.request({
            method: 'eth_requestAccounts'
        });
        
        if (accounts.length === 0) {
            throw new Error('No accounts found');
        }
        
        return accounts[0];
    } catch (error) {
        console.error('Error connecting to MetaMask:', error);
        alert('Failed to connect to MetaMask. Please try again.');
        return null;
    }
}

// Get current network
async function getNetwork() {
    try {
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });
        return parseInt(chainId, 16);
    } catch (error) {
        console.error('Error getting network:', error);
        return null;
    }
}

// Switch to Base network
async function switchToBase() {
    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: `0x${BASE_CHAIN_ID.toString(16)}` }],
        });
        return true;
    } catch (switchError) {
        // This error code indicates that the chain has not been added to MetaMask
        if (switchError.code === 4902) {
            // Add Base network to MetaMask
            try {
                await window.ethereum.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: `0x${BASE_CHAIN_ID.toString(16)}`,
                        chainName: BASE_CHAIN_NAME,
                        nativeCurrency: {
                            name: 'Ethereum',
                            symbol: 'ETH',
                            decimals: 18
                        },
                        rpcUrls: [BASE_RPC_URL],
                        blockExplorerUrls: [BASE_EXPLORER_URL]
                    }],
                });
                return true;
            } catch (addError) {
                console.error('Error adding Base network:', addError);
                alert('Failed to add Base network to MetaMask');
                return false;
            }
        } else {
            console.error('Error switching network:', switchError);
            alert('Failed to switch to Base network');
            return false;
        }
    }
}

// Ensure connected to Base network
async function ensureBaseNetwork() {
    const currentNetwork = await getNetwork();
    if (currentNetwork !== BASE_CHAIN_ID) {
        const switched = await switchToBase();
        if (!switched) {
            return false;
        }
        // Wait a moment for network switch
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    return true;
}
```

### 2. USDC Transfer Function

```javascript
// Convert USDC amount to raw units (with 6 decimals)
function usdcToRaw(usdcAmount) {
    return ethers.utils.parseUnits(usdcAmount.toString(), USDC_DECIMALS);
}

// Send USDC transfer
async function sendUSDCTransfer(amountUSDC, donorInfo) {
    try {
        // Connect wallet
        const account = await connectMetaMask();
        if (!account) {
            return { success: false, error: 'Failed to connect wallet' };
        }
        
        // Ensure Base network
        const onBase = await ensureBaseNetwork();
        if (!onBase) {
            return { success: false, error: 'Please switch to Base network' };
        }
        
        // Initialize provider and signer
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        
        // Initialize USDC contract
        const usdcContract = new ethers.Contract(
            USDC_CONTRACT_ADDRESS,
            USDC_ABI,
            signer
        );
        
        // Convert amount to raw units
        const amountRaw = usdcToRaw(amountUSDC);
        
        // Estimate gas
        let gasEstimate;
        try {
            gasEstimate = await usdcContract.estimateGas.transfer(RECEIVER_WALLET, amountRaw);
        } catch (error) {
            console.error('Gas estimation failed:', error);
            // Use default gas limit for ERC-20 transfer
            gasEstimate = ethers.BigNumber.from('100000');
        }
        
        // Send transfer transaction
        const tx = await usdcContract.transfer(RECEIVER_WALLET, amountRaw, {
            gasLimit: gasEstimate.mul(120).div(100), // Add 20% buffer
        });
        
        console.log('Transaction sent:', tx.hash);
        
        // Wait for transaction to be mined (optional - can also poll backend)
        // const receipt = await tx.wait();
        // console.log('Transaction confirmed:', receipt);
        
        // Verify transaction with backend
        const verifyResponse = await fetch('/api/crypto/verify-transaction/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transaction_hash: tx.hash,
                amount_usdc: amountUSDC,
                from_address: account,
                ...donorInfo,
            }),
        });
        
        const verifyData = await verifyResponse.json();
        
        if (!verifyData.success) {
            return { success: false, error: verifyData.error };
        }
        
        return {
            success: true,
            transaction_hash: tx.hash,
            payment_id: verifyData.payment_id,
            confirmations: verifyData.confirmations,
            required_confirmations: verifyData.required_confirmations,
        };
        
    } catch (error) {
        console.error('Error sending USDC transfer:', error);
        
        // Handle specific errors
        if (error.code === 4001) {
            return { success: false, error: 'Transaction rejected by user' };
        } else if (error.code === -32603) {
            return { success: false, error: 'Insufficient USDC balance or gas' };
        } else {
            return { success: false, error: error.message || 'Transaction failed' };
        }
    }
}
```

### 3. Payment Status Polling

```javascript
// Poll for payment status
async function checkPaymentStatus(txHash) {
    try {
        const response = await fetch(`/api/crypto/payment-status/${txHash}/`);
        if (!response.ok) {
            return null;
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error checking payment status:', error);
        return null;
    }
}

// Poll until confirmed
async function waitForConfirmation(txHash, onUpdate) {
    const maxAttempts = 120; // 10 minutes (5 second intervals)
    let attempts = 0;
    
    const poll = async () => {
        attempts++;
        const status = await checkPaymentStatus(txHash);
        
        if (status) {
            onUpdate(status);
            
            if (status.status === 'confirmed') {
                return true;
            }
            
            if (status.status === 'failed') {
                return false;
            }
        }
        
        if (attempts >= maxAttempts) {
            return false; // Timeout
        }
        
        // Poll again in 5 seconds
        setTimeout(poll, 5000);
    };
    
    poll();
}
```

### 4. UI Integration

```html
<!-- Add to solutions_for_change.html -->

<!-- Payment Method Selection -->
<div class="mb-6">
    <h2 class="text-lg font-semibold mb-3 text-center">Payment Method</h2>
    <div class="flex justify-center gap-2">
        <button type="button" id="payment-stripe" class="payment-method-btn px-4 py-2 border rounded-md bg-blue-600 text-white" data-method="stripe">
            Credit Card (Stripe)
        </button>
        <button type="button" id="payment-metamask" class="payment-method-btn px-4 py-2 border rounded-md hover:bg-gray-100" data-method="metamask">
            Crypto (USDC on Base)
        </button>
    </div>
</div>

<!-- MetaMask Payment Section (initially hidden) -->
<div id="metamask-payment-section" class="hidden">
    <div id="metamask-status" class="mb-4 p-4 bg-gray-100 rounded-lg">
        <p class="text-sm text-gray-700">
            <strong>Pay with USDC on Base:</strong> Connect your MetaMask wallet and complete the payment. 
            You'll need USDC tokens and a small amount of ETH for gas fees.
        </p>
    </div>
    
    <!-- Donor form (same fields as Stripe) -->
    <form id="metamask-donor-form" class="space-y-4 mb-4">
        <!-- Copy all form fields from Stripe form -->
        <!-- ... (first_name, last_name, email, etc.) ... -->
    </form>
    
    <button type="button" id="metamask-donate-btn" class="w-full bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white py-3 rounded-lg font-semibold shadow-md">
        <span>Donate with MetaMask (USDC)</span>
    </button>
    
    <div id="metamask-transaction-status" class="mt-4 hidden">
        <div class="p-4 bg-blue-50 rounded-lg">
            <p class="font-semibold">Transaction Pending</p>
            <p class="text-sm text-gray-600">Hash: <span id="tx-hash" class="font-mono"></span></p>
            <p class="text-sm">Confirmations: <span id="tx-confirmations">0</span> / <span id="tx-required">2</span></p>
            <a id="basescan-link" href="#" target="_blank" class="text-blue-600 hover:underline text-sm">View on Basescan</a>
        </div>
    </div>
</div>

<script>
// Payment method selection
let selectedPaymentMethod = 'stripe';
const paymentMethodBtns = document.querySelectorAll('.payment-method-btn');
const stripeForm = document.getElementById('donation-form');
const metamaskSection = document.getElementById('metamask-payment-section');

paymentMethodBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        selectedPaymentMethod = btn.dataset.method;
        paymentMethodBtns.forEach(b => {
            b.classList.remove('bg-blue-600', 'text-white');
            b.classList.add('hover:bg-gray-100');
        });
        btn.classList.add('bg-blue-600', 'text-white');
        btn.classList.remove('hover:bg-gray-100');
        
        if (selectedPaymentMethod === 'metamask') {
            stripeForm.style.display = 'none';
            metamaskSection.classList.remove('hidden');
        } else {
            stripeForm.style.display = 'block';
            metamaskSection.classList.add('hidden');
        }
    });
});

// MetaMask donation button
document.getElementById('metamask-donate-btn').addEventListener('click', async () => {
    const amount = parseFloat(document.getElementById('final-amount').value);
    
    if (!amount || amount <= 0) {
        alert('Please select an amount');
        return;
    }
    
    // Collect donor info from form
    const donorInfo = {
        first_name: document.querySelector('[name="first_name"]').value,
        last_name: document.querySelector('[name="last_name"]').value,
        email: document.querySelector('[name="email"]').value,
        mobile: document.querySelector('[name="mobile"]').value,
        address: document.querySelector('[name="address"]').value,
        city: document.querySelector('[name="city"]').value,
        state: document.querySelector('[name="state"]').value,
        country: document.querySelector('[name="country"]').value,
        postal_code: document.querySelector('[name="postal_code"]').value,
        message: document.querySelector('[name="message"]').value,
        org: document.querySelector('[name="org"]').value,
        frequency: document.getElementById('donation-frequency').value,
    };
    
    // Disable button
    const btn = document.getElementById('metamask-donate-btn');
    btn.disabled = true;
    btn.textContent = 'Processing...';
    
    try {
        const result = await sendUSDCTransfer(amount, donorInfo);
        
        if (result.success) {
            // Show transaction status
            document.getElementById('metamask-transaction-status').classList.remove('hidden');
            document.getElementById('tx-hash').textContent = result.transaction_hash;
            document.getElementById('tx-confirmations').textContent = result.confirmations;
            document.getElementById('tx-required').textContent = result.required_confirmations;
            document.getElementById('basescan-link').href = `https://basescan.org/tx/${result.transaction_hash}`;
            
            // Poll for status
            waitForConfirmation(result.transaction_hash, (status) => {
                document.getElementById('tx-confirmations').textContent = status.confirmations;
                document.getElementById('tx-required').textContent = status.required_confirmations;
                
                if (status.status === 'confirmed') {
                    // Redirect to success page
                    window.location.href = `/donate/success/?method=metamask&tx=${result.transaction_hash}`;
                }
            });
        } else {
            alert('Payment failed: ' + result.error);
            btn.disabled = false;
            btn.textContent = 'Donate with MetaMask (USDC)';
        }
    } catch (error) {
        alert('Error: ' + error.message);
        btn.disabled = false;
        btn.textContent = 'Donate with MetaMask (USDC)';
    }
});
</script>
```

---

## Security Considerations

### 1. **RPC URL Security**
- **NEVER** commit RPC URLs to version control
- Store in environment variables or secure key management services
- Treat Alchemy API keys as secrets
- Use different keys for development and production

### 2. **Transaction Verification**
- **Always verify on backend** - never trust frontend-only verification
- Verify Transfer event logs, not `tx.value` (which is 0 for token transfers)
- Verify recipient address matches receiving wallet
- Verify amount matches expected value (with small tolerance for rounding)
- Check transaction status (success/failure)
- Prevent replay attacks by checking if `tx_hash` already exists

### 3. **Frontend Security**
- Validate all user inputs
- Sanitize transaction parameters
- Handle errors gracefully
- Don't expose sensitive information in client-side code
- Don't hardcode wallet addresses or contract addresses (load from backend)

### 4. **Rate Limiting**
- Implement rate limiting on verification endpoint
- Prevent abuse and spam
- Use Django cache or Redis for rate limiting

### 5. **Logging & Monitoring**
- Log all verification attempts
- Log verification failures with reasons
- Monitor for suspicious activity
- Alert on unusual patterns

---

## Testing Requirements

### 1. **Unit Tests**
- Test Web3 service functions
- Test Transfer event parsing
- Test amount conversions (USDC with 6 decimals)
- Test transaction verification logic
- Test model creation and updates

### 2. **Integration Tests**
- Test full payment flow
- Test error scenarios (wrong network, insufficient balance, etc.)
- Test network switching
- Test confirmation polling
- Test replay prevention

### 3. **Base Mainnet Testing**
- Test with real USDC on Base mainnet (small amounts)
- Test with test MetaMask accounts
- Test various transaction scenarios
- Test edge cases (failed transactions, network issues, etc.)

### 4. **User Acceptance Testing**
- Test with real users
- Gather feedback on UX
- Test on different browsers
- Test on mobile devices
- Test MetaMask mobile app

---

## Integration with Existing Payment System

### Recommended: Parallel System
- Keep Stripe and MetaMask as separate payment options
- Users choose at checkout
- Both can write to similar database structures
- Separate or unified success pages (your choice)

### Database Structure
- `TokenPayment` model for USDC payments
- Can create unified reporting by joining with Stripe payments
- Maintain separate models for clarity and maintainability

---

## Costs & Considerations

### 1. **Gas Fees**
- Users pay gas fees in ETH (not USDC)
- Gas fees on Base are much lower than Ethereum mainnet
- Typical Base transaction: $0.01 - $0.10 in gas
- Users need ETH in their wallet for gas, even when paying in USDC

### 2. **RPC Provider Costs**
- **Alchemy**: Free tier available, then paid plans
- **Public RPC**: Free but rate-limited and less reliable
- Recommend using Alchemy for production reliability

### 3. **USDC Stability**
- USDC is a stablecoin (pegged to USD)
- 1 USDC = 1 USD (approximately)
- Minimal exchange rate risk compared to ETH

### 4. **Regulatory Considerations**
- Cryptocurrency regulations vary by jurisdiction
- May need to report large transactions
- Consider tax implications
- Consult legal counsel

---

## Timeline Estimate

### Phase 1: Setup & Configuration (1 day)
- Configure environment variables
- Install dependencies
- Set up Base RPC connection

### Phase 2: Database & Models (1 day)
- Create TokenPayment model
- Run migrations

### Phase 3: Backend Implementation (3-4 days)
- Web3 service with Transfer event parsing
- API endpoints
- Transaction verification logic

### Phase 4: Frontend Implementation (3-4 days)
- MetaMask integration
- Base network detection/switching
- USDC contract interaction
- UI updates

### Phase 5: Testing & Refinement (3-4 days)
- Unit tests
- Integration tests
- Base mainnet testing
- Bug fixes

### Phase 6: Production Deployment (1-2 days)
- Security review
- Deployment
- Monitoring setup

**Total Estimated Time: 12-16 days** (depending on experience level)

---

## Open Items / Blockers

### Confirmed by Client ✅
- Receiving wallet: `0x918e03d7c59d61b6505fed486082419941ffd77f`
- Base RPC URL: Provided (Alchemy)
- Token: USDC on Base
- USDC Contract: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- USDC Decimals: 6

### To Confirm with Client
- Required confirmations (recommend 2)
- Whether to accept only USDC or more tokens later
- Success page handling (separate or unified with Stripe)

---

## One-Liner Summary

**"Implement MetaMask donations as an ERC-20 USDC transfer on Base mainnet, verified on backend via Transfer event logs, not ETH tx.value."**

---

## Additional Resources

### Documentation
- [MetaMask Documentation](https://docs.metamask.io/)
- [Ethers.js Documentation](https://docs.ethers.io/v5/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Base Network Documentation](https://docs.base.org/)
- [USDC on Base](https://developers.circle.com/stablecoins/usdc-contract-addresses)

### Tools
- [Basescan](https://basescan.org/) - Base blockchain explorer
- [Alchemy Base](https://www.alchemy.com/base) - RPC provider
- [Base Bridge](https://bridge.base.org/) - Bridge assets to Base

### Testing
- Test with small amounts on Base mainnet
- Use MetaMask test accounts
- Monitor transactions on Basescan

---

## Next Steps

1. **Review this document** with your team
2. **Set up environment variables** (Base RPC URL, wallet address)
3. **Install dependencies** and configure environment
4. **Start with Phase 1** and work through sequentially
5. **Test thoroughly** on Base mainnet with small amounts
6. **Deploy to production** when ready

---

**Document Version**: 2.0  
**Last Updated**: [Current Date]  
**Status**: Ready for Implementation  
**Network**: Base Mainnet  
**Token**: USDC (ERC-20)
