from django.urls import path
from .import views


from .views import (
    edit_feature,
    signup,
    login_view,
    logout_view,
    home,
    create_feature,
    feature_list,
    delete_feature,
    create_plan,
    plan_list,
    edit_plan,
    delete_plan,
    create_subscription,
    subscription_list,
)

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.home, name="home"),

    path("features/", views.feature_list, name="feature_list"),

    path("features/create/",
          views.create_feature,
            name="create_feature"
    ),

    path(
    "features/<int:feature_id>/edit/",
    views.edit_feature,
    name="edit_feature",
    ),

    path(
    "features/<int:feature_id>/delete/",
    views.delete_feature,
    name="delete_feature",
    ),

    path(
    "plans/create/",
    views.create_plan,
    name="create_plan"
    ),

    path(
    "plans/",
    views.plan_list,
    name="plan_list"
    ),

    path(
    "plans/<int:plan_id>/edit/",
    views.edit_plan,
    name="edit_plan"
    ),

    path(
    "plans/<int:plan_id>/delete/",
    views.delete_plan,
    name="delete_plan"
    ),

    path(
    "subscriptions/create/",
    views.create_subscription,
    name="create_subscription"
    ),

    path(
    "subscriptions/",
    views.subscription_list,
    name="subscription_list"
    ),
]