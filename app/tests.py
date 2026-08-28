from django.test import TestCase

# Create your tests here.

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from .models import (
    User,
    Feature,
    Plan,
    Subscription,
    Usage,
    Transaction,
)
from .services import (
    calculate_subscription_overuse,
    calculate_subscription_bill,
    create_subscription_transaction,
    process_billing_for_today,
)


class BillingServiceTests(TestCase):

    def setUp(self):
        self.buyer = User.objects.create(
            username="testbuyer",
            password="testpassword",
            email="buyer@test.com",
            type="user",
            buyer_billing_day=timezone.localdate().day,
        )

        self.feature = Feature.objects.create(
            name="API calls",
            code="API_TEST",
            unit_price=Decimal("2.50"),
            max_unit_limit=50,
        )

        self.plan = Plan.objects.create(
            name="Basic Plan",
            monthly_fee=Decimal("29.99"),
        )

        self.plan.features.add(self.feature)

        self.subscription = Subscription.objects.create(
            Buyer=self.buyer,
            Plan=self.plan,
            status="active",
        )

    def test_no_overuse(self):
        Usage.objects.create(
            Subscription=self.subscription,
            Feature=self.feature,
            units=30,
        )

        results = calculate_subscription_overuse(
            self.subscription
        )

        self.assertEqual(
            results[0]["total_usage"],
            30
        )

        self.assertEqual(
            results[0]["overused_units"],
            0
        )

        self.assertEqual(
            results[0]["overuse_charge"],
            Decimal("0.00")
        )

    def test_overuse(self):
        Usage.objects.create(
            Subscription=self.subscription,
            Feature=self.feature,
            units=60,
        )

        results = calculate_subscription_overuse(
            self.subscription
        )

        self.assertEqual(
            results[0]["total_usage"],
            60
        )

        self.assertEqual(
            results[0]["overused_units"],
            10
        )

        self.assertEqual(
            results[0]["overuse_charge"],
            Decimal("25.00")
        )

    def test_total_bill(self):
        Usage.objects.create(
            Subscription=self.subscription,
            Feature=self.feature,
            units=60,
        )

        bill = calculate_subscription_bill(
            self.subscription
        )

        self.assertEqual(
            bill["monthly_fee"],
            Decimal("29.99")
        )

        self.assertEqual(
            bill["total_overuse_charge"],
            Decimal("25.00")
        )

        self.assertEqual(
            bill["total_amount"],
            Decimal("54.99")
        )

    def test_transaction_creation(self):
        transaction = create_subscription_transaction(
            self.subscription
        )

        self.assertEqual(
            transaction.Buyer,
            self.buyer
        )

        self.assertEqual(
            transaction.Subscription,
            self.subscription
        )

        self.assertEqual(
            transaction.amount,
            Decimal("29.99")
        )

        self.assertEqual(
            transaction.Transaction_type,
            "debit"
        )

        self.assertEqual(
            transaction.Status,
            "success"
        )

    def test_duplicate_transaction_is_not_created(self):
        first_transaction = create_subscription_transaction(
            self.subscription
        )

        second_transaction = create_subscription_transaction(
            self.subscription
        )

        self.assertEqual(
            first_transaction.id,
            second_transaction.id
        )

        self.assertEqual(
            Transaction.objects.filter(
                Subscription=self.subscription,
                Transaction_type="debit",
                Status="success",
            ).count(),
            1,
        )

    def test_billing_day(self):
        process_billing_for_today()

        self.assertEqual(
            Transaction.objects.filter(
                Subscription=self.subscription,
                Transaction_type="debit",
                Status="success",
            ).count(),
            1,
        )

    def test_inactive_subscription_is_not_billed(self):
        self.subscription.status = "inactive"
        self.subscription.save()

        process_billing_for_today()

        self.assertEqual(
            Transaction.objects.filter(
                Subscription=self.subscription,
                Transaction_type="debit",
                Status="success",
            ).count(),
            0,
        )
