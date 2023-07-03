from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import EditProfileForm, EditUserForm
from .models import Profile


# USER SIGN UP PAGE
def signup(request):
    context = {}

    if request.user.is_authenticated:
        return redirect("Poetry")
    
    signup_form = UserCreationForm()
    if request.method == "POST":
        signup_form = UserCreationForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            login(request, user)
            Profile(user=user).save()
            context['user'] = user
            return render(request, 'users/profile.html', context)
        else:
            signup_form = UserCreationForm(request.POST)
            
    context["signup_form"] = signup_form
    return render(request, 'users/signup.html', context)


# USER SIGNIN PAGE
def signin(request):

    if request.user.is_authenticated:
        return redirect('Poetry')

    if request.method == "POST":
        signin_form = AuthenticationForm(request, data=request.POST)
        if signin_form.is_valid():
            user = signin_form.get_user()
            login(request, user)
            return redirect('HomePage')
    else:
        signin_form = AuthenticationForm()
            
    context = {
        "signin_form": signin_form
    }
    return render(request, 'users/signin.html', context)


# USER LOGOUT
@login_required
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("Signin")


# USER PROFILE PAGE
@login_required
def profile(request, user_id):
    context = {}
    user =  User.objects.get(id=user_id)
    context['user'] = user
    return render(request, 'users/profile.html', context)


# USER EDIT PROFILE PAGE
@login_required
def edit_profile(request):
    context = {}

    if request.method=="POST":
        user_form = EditUserForm(request.POST, request.FILES, instance=request.user)
        profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user = user_form.save()
            context['user'] = user
            return render(request, 'users/profile.html', context)
    else:
        profile_form = EditProfileForm(instance=request.user.profile)
        user_form = EditUserForm(instance=request.user)

    context['profile_form'] = profile_form
    context['user_form'] = user_form
    return render(request, 'users/edit_profile.html', context)