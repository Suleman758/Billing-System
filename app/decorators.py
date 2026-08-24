from functools import wraps

from django.contrib.auth import logout
from django.shortcuts import redirect


def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.type != "admin":
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper