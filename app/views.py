from django import http
from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.

from django.shortcuts import render, redirect

from .forms import SignupForm


@login_required
def home(request):
    return render(request, "home.html",{'user' : request.user})

def logout_view(request):
    logout(request)
    return redirect("login")

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
