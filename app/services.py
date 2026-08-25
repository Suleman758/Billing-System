from decimal import Decimal

from django.db.models import Sum

from .models import Subscription, Usage,User


def calculate_subscription_overuse(subscription):
    results = []

    # Get all features that belong to this subscription's plan
    features = subscription.Plan.features.all()

    for feature in features:

        # Get total usage of this feature for this subscription
        total_usage = Usage.objects.filter(
            Subscription=subscription,
            Feature=feature,
        ).aggregate(
            total=Sum("units")
        )["total"] or 0

        # If there is no limit, there is no overuse calculation
        if feature.max_unit_limit is None:
            overused_units = 0
            overuse_charge = Decimal("0.00")

        else:
            overused_units = max(
                0,
                total_usage - feature.max_unit_limit
            )

            overuse_charge = (
                Decimal(overused_units)
                * feature.unit_price
            )

        results.append({
            "feature": feature,
            "total_usage": total_usage,
            "max_unit_limit": feature.max_unit_limit,
            "overused_units": overused_units,
            "unit_price": feature.unit_price,
            "overuse_charge": overuse_charge,
        })

    return results


def calculate_subscription_bill(subscription):
    overuse_results = calculate_subscription_overuse(subscription)

    monthly_fee = subscription.Plan.monthly_fee

    total_overuse_charge = sum(
        result["overuse_charge"]
        for result in overuse_results
    )

    total_amount = monthly_fee + total_overuse_charge

    return {
        "monthly_fee": monthly_fee,
        "overuse_results": overuse_results,
        "total_overuse_charge": total_overuse_charge,
        "total_amount": total_amount,
    }

from django.utils import timezone

from .models import Transaction,Usage,Subscription

def create_subscription_transaction(subscription):
    today = timezone.localdate()

    existing_transaction = Transaction.objects.filter(
        Subscription=subscription,
        Billing_date=today,
        Transaction_type="debit",
        Status="success",
    ).first()

    if existing_transaction:
        return existing_transaction

    bill = calculate_subscription_bill(subscription)

    transaction = Transaction.objects.create(
        Buyer=subscription.Buyer,
        Subscription=subscription,
        amount=bill["total_amount"],
        Transaction_type="debit",
        Status="success",
    )

    return transaction


def process_billing_for_today():
    today = timezone.localdate()

    buyers = User.objects.filter(
        buyer_billing_day=today.day
    )

    subscriptions = Subscription.objects.filter(
        Buyer__in=buyers,
        status="active",
    )

    transactions = []

    for subscription in subscriptions:
        transaction = create_subscription_transaction(subscription)
        transactions.append(transaction)

    return transactions