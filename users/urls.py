from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name="Signup"),
    path('signin/', views.signin, name="Signin"),
    path('signout/', views.signout, name="Signout"),
    path('profile/<int:user_id>', views.profile, name="Profile"),
    path('edit_profile/', views.edit_profile, name="Edit_Profile")    
]