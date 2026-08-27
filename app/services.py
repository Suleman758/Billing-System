from decimal import Decimal

from django.db.models import Sum

from .models import Subscription, Usage,User


from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from .models import Subscription, Usage, Transaction
from django.db import transaction


def calculate_subscription_overuse(subscription):
    today = timezone.localdate()

    # Find the most recent successful debit for this subscription.
    last_transaction = (
        Transaction.objects
        .filter(
            Subscription=subscription,
            Transaction_type="debit",
            Status="success",
        )
        .order_by("-Billing_date")
        .first()
    )

    results = []

    features = subscription.Plan.features.all()

    for feature in features:

        usage_queryset = Usage.objects.filter(
            Subscription=subscription,
            Feature=feature,
            usage_date__lte=today,
        )

        if last_transaction:
            # Previous billing date has already been processed.
            usage_queryset = usage_queryset.filter(
                usage_date__gt=last_transaction.Billing_date
            )
        else:
            # First billing: include usage from the subscription start date.
            usage_queryset = usage_queryset.filter(
                usage_date__gte=subscription.start_date
            )

        total_usage = usage_queryset.aggregate(
            total=Sum("units")
        )["total"] or 0

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

    with transaction.atomic():
        for subscription in subscriptions:
            created_transaction = create_subscription_transaction(
                subscription
            )
            transactions.append(created_transaction)

    return transactions