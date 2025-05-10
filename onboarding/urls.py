from django.urls import path
import onboarding.views as views
from rest_framework_simplejwt.views import TokenRefreshView

# URL patterns that connect the views to a URL/sub-URL for the domain
"""The differenct urls used to pass HTTP requests
============================  ===========================
Path                          Name
============================  ===========================
create-user/                  create-user
login-user/                   login-user
token/refresh/                token-refresh
generate-otp/                 generate-otp
validate-otp/                 validate-otp
reset-password/               reset-password
create-exercise/              create-exercise
create-exercise/<int:pk>/     get-exercise-by-ID
log-exercise/                 log-exercise
userdata/                     userdata-create
recommend-exercise/           recommend-exercise
update-recommendation/        update-recommendation
create-consumable/            create-consumable
log-consumable/               log-consumable
routines/                     routines
routines/<int:pk>/            routine-detail
routines/<int:pk>/update/     routine-update
routines/<int:pk>/delete/     routine-delete
routine-exercises/            routine-exercise-list
routine-exercises/<int:pk>/   routine-exercise-detail
log-routine/                  log-routine
user-mood/                    user-mood
recommend-consumable/         recommend-consumable
============================  ===========================
    """
urlpatterns = [
    path("create-user/", views.CreateAccountView.as_view(), name="create-user"),
    path("login-user/", views.LoginView.as_view(), name="login-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("generate-otp/", views.GenerateOTPView().as_view(), name="generate-otp"),
    path("validate-otp/", views.ValidateOTPView().as_view(), name="validate-otp"),
    path("reset-password/", views.ResetPasswordView().as_view(), name="reset-password"),
    path("create-exercise/", views.ExerciseView().as_view(), name="create-exercise"),
    path('create-exercise/<int:pk>/', views.ExerciseDetailView.as_view(), name ="get-exercise-by-ID"),
    path("log-exercise/", views.LogExerciseView().as_view(), name="log-exercise"),
    path("userdata/", views.UserDataCreateView().as_view(), name="userdata-create"),
    path("recommend-exercise/", views.RecommendExerciseView.as_view(), name="recommend-exercise"),
    path("update-recommendation/", views.UpdateRecommendedExerciseView.as_view(), name="update-recommendation"),
    path("userdata/", views.UserDataCreateView().as_view(), name="userdata-create"),
    path("create-consumable/", views.ConsumableView().as_view(), name="create-consumable"),
    path("log-consumable/", views.LogConsumableView().as_view(), name="log-consumable"),
    path("routines/", views.RoutineListCreateView.as_view(), name="routines"),
    path("routines/<int:pk>/", views.RoutineDetailView.as_view(), name="routine-detail"),
    path("routines/<int:pk>/update/", views.RoutineUpdateView.as_view(), name="routine-update"),
    path("routines/<int:pk>/delete/", views.RoutineDeleteView.as_view(), name="routine-delete"),
    path("routine-exercises/", views.RoutineExerciseListCreateView.as_view(), name="routine-exercise-list"),
    path("routine-exercises/<int:pk>/", views.RoutineExerciseDetailView.as_view(), name="routine-exercise-detail"),
    path('log-routine/', views.LogRoutineView.as_view(), name='log-routine'),
    path("user-mood/", views.UserMoodView().as_view(), name="user-mood"),
    path("recommend-consumable/", views.RecommendConsumableView().as_view(), name="recommend-consumable"),
]
