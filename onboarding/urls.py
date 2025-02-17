from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("create-user/", views.CreateAccountView.as_view(), name="create-user"),
    path("login-user/", views.LoginView.as_view(), name="login-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("generate-otp/", views.CreateGetOTPView().as_view(), name="generate-otp"),
    path("validate-otp/", views.ValidateOTPView().as_view(), name="validate-otp")
]