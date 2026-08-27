from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Subscription, User, Feature,Plan,Usage

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'profile_photo',
            'buyer_billing_day',
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

class AdminUsageForm(forms.ModelForm):

    class Meta:
        model = Usage
        fields = [
            "Subscription",
            "Feature",
            "units",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["Subscription"].queryset = Subscription.objects.filter(
            status="active"
        )

        self.fields["Feature"].queryset = Feature.objects.none()

        if self.is_bound:
            subscription_id = self.data.get("Subscription")

            if subscription_id:
                try:
                    subscription = Subscription.objects.get(
                        id=subscription_id,
                        status="active",
                    )

                    self.fields["Feature"].queryset = (
                        subscription.Plan.features.all()
                    )

                except Subscription.DoesNotExist:
                    pass

    def clean(self):
        cleaned_data = super().clean()

        subscription = cleaned_data.get("Subscription")
        feature = cleaned_data.get("Feature")

        if subscription and feature:
            if not subscription.Plan.features.filter(
                id=feature.id
            ).exists():
                raise forms.ValidationError(
                    "This feature does not belong to the selected subscription's plan."
                )

        return cleaned_data


class UsageForm(forms.ModelForm):

    class Meta:
        model = Usage
        fields = [
            "Subscription",
            "Feature",
            "units",
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is None:
            raise ValueError("UsageForm requires a user.")

        self.user = user

        subscriptions = Subscription.objects.filter(
            Buyer=user,
            status="active",
        )

        self.fields["Subscription"].queryset = subscriptions

        self.fields["Feature"].queryset = Feature.objects.filter(
            subscriptions__in=subscriptions
        ).distinct()

    def clean(self):
        cleaned_data = super().clean()

        subscription = cleaned_data.get("Subscription")
        feature = cleaned_data.get("Feature")

        if subscription:
            if subscription.Buyer != self.user:
                self.add_error(
                    "Subscription",
                    "You cannot use this subscription."
                )

        if subscription and feature:
            if not subscription.Plan.features.filter(
                id=feature.id
            ).exists():
                self.add_error(
                    "Feature",
                    "This feature does not belong to the selected subscription's plan."
                )

        return cleaned_data