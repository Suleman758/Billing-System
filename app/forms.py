from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Subscription, User, Feature,Plan

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'profile_photo',
            'billing_day',
        ]

class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ['name', 'code', 'unit_price', 'max_unit_limit']

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'monthly_fee', 'features']

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['Plan']
      