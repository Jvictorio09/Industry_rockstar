from django.db import models
from django.utils import timezone
from django.conf import settings

class TokenPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('course', 'Course Payment'),
        ('supplier', 'Supplier Listing'),
        ('custom', 'Custom Amount'),
    ]
    
    # Transaction Details
    transaction_hash = models.CharField(max_length=66, unique=True, db_index=True)
    from_address = models.CharField(max_length=42)  # Customer's wallet
    to_address = models.CharField(max_length=42)    # Receiving wallet
    amount_raw = models.DecimalField(max_digits=36, decimal_places=0)  # Amount in smallest units
    amount_token = models.DecimalField(max_digits=18, decimal_places=6)  # Amount in USDC (6 decimals)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)  # USD equivalent
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='course')
    token_contract = models.CharField(max_length=42, default='0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    block_number = models.BigIntegerField(null=True, blank=True)
    confirmations = models.IntegerField(default=0)
    required_confirmations = models.IntegerField(default=2)
    
    # Customer Information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=200, blank=True)  # For supplier listings
    notes = models.TextField(blank=True)
    org = models.CharField(max_length=100, default='tanya-client')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    gas_price = models.DecimalField(max_digits=36, decimal_places=0, null=True, blank=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    transfer_event_index = models.IntegerField(null=True, blank=True)  # Which log index had the Transfer event
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['from_address']),
            models.Index(fields=['payment_type']),
        ]
    
    def __str__(self):
        return f"{self.transaction_hash[:10]}... - {self.amount_token} USDC - {self.status}"
    
    @property
    def basescan_url(self):
        """Generate Basescan URL for transaction"""
        return f"https://basescan.org/tx/{self.transaction_hash}"
