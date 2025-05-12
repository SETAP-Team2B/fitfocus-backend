from django.urls import path
import onboarding.views as views
from rest_framework_simplejwt.views import TokenRefreshView

"""The different urls used to pass HTTP requests.

===========================  =============================
Path                         View
===========================  =============================
create-user/                 CreateAccountView
login-user/                  LoginView
token/refresh/               TokenRefreshView
generate-otp/                GenerateOTPView
validate-otp/                ValidateOTPView
reset-password/              ResetPasswordView
create-exercise/             ExerciseView
create-exercise/<int:pk>/    ExerciseDetailView
log-exercise/                LogExerciseView
userdata/                    UserDataCreateView
recommend-exercise/          RecommendExerciseView
update-recommendation/       UpdateRecommendedExerciseView
create-consumable/           ConsumableView
log-consumable/              LogConsumableView
routines/                    RoutineListCreateView
routines/<int:pk>/           RoutineDetailView
routines/<int:pk>/update/    RoutineUpdateView
routines/<int:pk>/delete/    RoutineDeleteView
routine-exercises/           RoutineExerciseListCreateView
routine-exercises/<int:pk>/  RoutineExerciseDetailView
log-routine/                 LogRoutineView
user-mood/                   UserMoodView
recommend-consumable/        RecommendConsumableView
===========================  =============================

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
