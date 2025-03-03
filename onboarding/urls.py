from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

# defines URL patterns for views
urlpatterns = [
    path("create-user/", views.CreateAccountView.as_view(), name="create-user"),
    path("login-user/", views.LoginView.as_view(), name="login-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("generate-otp/", views.GenerateOTPView().as_view(), name="generate-otp"),
    path("validate-otp/", views.ValidateOTPView().as_view(), name="validate-otp"),
    path("reset-password/", views.ResetPasswordView().as_view(), name="reset-password"),
    path("create-exercise/", views.ExerciseView().as_view(), name="create-exercise"),
    path("log-exercise/", views.LogExerciseView().as_view(), name="log-exercise")
]
