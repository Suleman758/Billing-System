# Create your models here. 

from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):

    class UserType(models.TextChoices):
        ADMIN = "admin", "Admin"
        BUYER = "buyer", "Buyer"

    name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.BUYER,
    )

    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )

    billing_day = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(28),
        ],
        blank=True,
        null=True,
    )

    REQUIRED_FIELDS = ["email", "name"]

class Plan(models.Model):
    name = models.CharField(max_length=100)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.ManyToManyField('Feature')

class Feature(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100,unique=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(0)])
    max_unit_limit = models.IntegerField(null=True, blank=True,validators=[MinValueValidator(0)])

class Subscription(models.Model):
    Buyer = models.ForeignKey(User, on_delete=models.CASCADE,related_name='subscriptions', limit_choices_to={'type': 'user'})
    Plan = models.ForeignKey(Plan, on_delete=models.CASCADE,related_name='subscriptions')
    start_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')


class Usage(models.Model):
    Subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,related_name='usages')
    Feature = models.ForeignKey(Feature, on_delete=models.CASCADE,related_name='usages')
    units = models.IntegerField(validators=[MinValueValidator(0)])
    usage_date = models.DateField(auto_now_add=True)

class Transaction(models.Model):
    Buyer = models.ForeignKey(User, on_delete=models.CASCADE,related_name='transactions', limit_choices_to={'type': 'user'})
    Subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    Transaction_type = models.CharField(max_length=50, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    Status = models.CharField(max_length=50, choices=[('success', 'Success'), ('failed', 'Failed')])
    Billing_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
