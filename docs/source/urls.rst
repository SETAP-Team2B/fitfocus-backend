urls module
===========

The different urls used to pass HTTP requests.

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


.. automodule:: onboarding.urls
   :members:
   :show-inheritance:
   :undoc-members:
