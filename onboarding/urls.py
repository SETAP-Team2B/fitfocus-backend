from django.urls import path
from . import views

urlpatterns = [
    path("create-user/", views.CreateAccountView().as_view()),
    path("generate-otp/", views.CreateGetOTPView().as_view()),
    path("validate-otp/", views.ValidateOTPView().as_view())
]