from django import http
from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.

from django.shortcuts import render, redirect
from .forms import PlanForm, SignupForm,FeatureForm, SubscriptionForm, UsageForm
from .models import Transaction, User, Feature,Plan,Subscription,Usage
from .decorators import admin_required
from django.shortcuts import get_object_or_404
from .services import calculate_subscription_overuse,create_subscription_transaction,process_billing_for_today


@login_required
def home(request):
    return render(request, "home.html",{'user' : request.user})

def logout_view(request):
    logout(request)
    return redirect("login")

@admin_required
def some_admin_view(request):
    #return render(request, "some_admin_view.html")
    pass

@admin_required
def launch_billing(request):
    if request.method == "POST":
        transactions = process_billing_for_today()

        return render(
            request,
            "billing_launched.html",
            {"transactions": transactions},
        )

    return render(request, "launch_billing.html")

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(
        Buyer=request.user
    ).select_related(
        "Subscription",
        "Subscription__Plan",
    )

    return render(
        request,
        "transaction_list.html",
        {"transactions": transactions},
    )

@admin_required
def bill_subscription(request, subscription_id):
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        status="active"
    )

    if request.method == "POST":
        transaction = create_subscription_transaction(subscription)

        return redirect(
            "transaction_list"
        )

    return render(
        request,
        "bill_subscription.html",
        {
            "subscription": subscription,
        },
    )


@login_required
def billing_summary(request, subscription_id):
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        Buyer=request.user
    )

    overuse_data = calculate_subscription_overuse(subscription)

    return render(
        request,
        "billing_summary.html",
        {
            "subscription": subscription,
            "overuse_data": overuse_data,
        },
    )


@login_required
def usage_list(request):
    usages = Usage.objects.filter(
        Subscription__Buyer=request.user
    ).select_related(
        "Subscription",
        "Feature",
    )

    return render(
        request,
        "usage_list.html",
        {"usages": usages},
    )

@login_required
def create_usage(request):
    if request.method == "POST":
        form = UsageForm(
            request.user,
            request.POST
        )

        if form.is_valid():
            usage = form.save(commit=False)

            # Make sure the selected subscription belongs to
            # the currently logged-in buyer
            if usage.Subscription.Buyer != request.user:
                form.add_error(
                    "Subscription",
                    "Invalid subscription."
                )
            else:
                usage.save()
                return redirect("usage_list")

    else:
        form = UsageForm(request.user)

    return render(
        request,
        "create_usage.html",
        {"form": form},
    )

@login_required
def deactivate_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, Buyer=request.user)

    if request.method == "POST":
        subscription.status = "Inactive"
        subscription.save()
        return redirect("subscription_list")

    return render(request, "deactivate_subscription.html", {"subscription": subscription})


@login_required
def create_subscription(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)

        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.Buyer = request.user
            subscription.save()
            return redirect("subscription_list")
    else:
        form = SubscriptionForm()

    return render(request, "create_subscription.html", {"form": form})

@login_required
def subscription_list(request):
    subscriptions = Subscription.objects.filter(
        Buyer = request.user
    )

    return render(request, "subscription_list.html", {"subscriptions": subscriptions})

@admin_required
def delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == "POST":
        plan.delete()
        return redirect("plan_list")

    return render(request, "delete_plan.html", {"plan": plan})

@admin_required
def edit_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == "POST":
        form = PlanForm(request.POST, instance=plan)

        if form.is_valid():
            form.save()
            return redirect("plan_list")
    else:
        form = PlanForm(instance=plan)

    return render(request, "edit_plan.html", {"form": form, "plan": plan})

@admin_required
def plan_list(request):
    plans = Plan.objects.all()
    return render(request, "plan_list.html", {"plans": plans})

@admin_required
def create_plan(request):
    if request.method == "POST":
        form = PlanForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("plan_list")
    else:
        form = PlanForm()

    return render(request, "create_plan.html", {"form": form})

@admin_required
def delete_feature(request, feature_id):
    feature = get_object_or_404(Feature, id=feature_id)

    if request.method == "POST":
        feature.delete()
        return redirect("feature_list")

    return render(request, "delete_feature.html", {"feature": feature})


@admin_required
def edit_feature(request, feature_id):
    feature = get_object_or_404(Feature, id=feature_id)

    if request.method == "POST":
        form = FeatureForm(request.POST, instance=feature)

        if form.is_valid():
            form.save()
            return redirect("feature_list")
    else:
        form = FeatureForm(instance=feature)

    return render(request, "edit_feature.html", {"form": form, "feature": feature})


@admin_required
def create_feature(request):
    if request.method == "POST":
        form = FeatureForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("feature_list")
    else:
        form = FeatureForm()

    return render(request, "create_feature.html", {"form": form})

@admin_required
def feature_list(request):
    features = Feature.objects.all()
    return render(request, "feature_list.html", {"features": features})


def signup(request):
    if request.method == "POST":
        form = SignupForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            user = form.save()
            user.type = user.UserType.BUYER
            user.save()

            return redirect("login")

    else:
        form = SignupForm()

    #return http.HttpResponse("Signup page is under construction.")
    #return render(request, 'signup.html')

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(
            request,
            "login.html",
            {"error": "Invalid email or password"},
        )

    return render(request, "login.html")
