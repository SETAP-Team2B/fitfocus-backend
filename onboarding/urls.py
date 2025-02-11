from django.urls import path
from . import views

urlpatterns = [
    path("create-user/", views.CreateAccountView().as_view())
]