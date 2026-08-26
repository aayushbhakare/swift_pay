import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Merchant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant', null=True, blank=True)
    name = models.CharField(max_length=255)
    webhook_url = models.URLField(blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    
    # Extended Profile Fields
    trading_name = models.CharField(max_length=255, null=True, blank=True)
    entity_type = models.CharField(max_length=50, null=True, blank=True)
    pan = models.CharField(max_length=20, null=True, blank=True, validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', 'Invalid PAN format')])
    gst = models.CharField(max_length=20, null=True, blank=True, validators=[RegexValidator(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$', 'Invalid GST format')])
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True, validators=[RegexValidator(r'^\d{9,18}$', 'Account number must be 9-18 digits')])
    ifsc_code = models.CharField(max_length=20, null=True, blank=True, validators=[RegexValidator(r'^[A-Z]{4}0[A-Z0-9]{6}$', 'Invalid IFSC code')])
    business_address = models.TextField(null=True, blank=True)
    
    # Phone verification
    phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    phone_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def is_profile_complete(self):
        return all([self.name, self.pan, self.bank_name, self.account_number, self.ifsc_code])



class MerchantBalance(models.Model):
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name='balance')
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='INR')
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Balance for {self.merchant.name}: Available=₹{self.available_balance}, Pending=₹{self.pending_balance}"

class ApiKey(models.Model):
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name='api_key')
    key_id = models.CharField(max_length=255, unique=True)
    key_secret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ApiKey for {self.merchant.name} ({self.key_id})"
