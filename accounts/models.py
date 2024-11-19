from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    currency = models.CharField(
        max_length=4,
        default='USD',
        choices=[
            # Fiat Currencies
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
            ('GBP', 'British Pound'),
            ('JPY', 'Japanese Yen'),
            ('AUD', 'Australian Dollar'),
            ('CAD', 'Canadian Dollar'),
            ('ZAR', 'South African Rand'),
            ('CHF', 'Swiss Franc'),
            ('CNY', 'Chinese Yuan'),
            ('INR', 'Indian Rupee'),
            ('SGD', 'Singapore Dollar'),
            ('NZD', 'New Zealand Dollar'),
            ('HKD', 'Hong Kong Dollar'),
            ('AED', 'UAE Dirham'),
            ('BRL', 'Brazilian Real'),
            ('MXN', 'Mexican Peso'),
            # Cryptocurrencies
            ('BTC', 'Bitcoin'),
            ('ETH', 'Ethereum'),
            ('USDT', 'Tether USD'),
            ('LAC', 'Lacoin'),
        ]
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'