from django import forms
from .models import Profile
from django.contrib.auth.models import User


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["picture", "bio"]