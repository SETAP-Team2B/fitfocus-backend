from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default="", null=False, db_comment="The OTP sent to the user.")
    created_at = models.DateTimeField(auto_now=True, db_comment="When the OTP was created. Useful for restricting the frequency of new OTP generation.")
    expiry_time = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=5), db_comment="When the OTP can no longer be accepted. Default is 5 minutes after when it was created.")
    verified = models.BooleanField(default=False, db_comment="Whether the OTP for the user has been verified. Good for preventing repeat entries and also ensuring user is secure.")

class Exercise(models.Model): 
    exercise_type = [
        ("muscle","Muscle"),
        ("cardio","Cardio"),
        ("flexibility","Flexibility"),
    ]

    body_area_choices = [
        ("arms", "Arms"),
        ("back", "Back"),
        ("legs", "Legs"),
        ("core", "Core"),
        ("chest", "Chest"),
        ("shoulder", "Shoulder"),
        ("cardio", "Cardio"),
        ("flexibility", "Flexibility"),
        ("neck", "Neck"),
    ]

    muscle_choices = [
        ("biceps", "Biceps"),
        ("triceps", "Triceps"),
        ("forearms", "Forearms"),
        ("lats", "Lats"),
        ("lower_back", "Lower Back"),
        ("traps", "Traps"),
        ("upper_back", "Upper Back"),
        ("calves", "Calves"),
        ("hamstrings", "Hamstrings"),
        ("quadriceps", "Quadriceps"),
        ("adductors", "Adductors"),
        ("glutes", "Glutes"),
        ("abs", "Abdominals"),
        ("abductors", "Abductors"),
        ("levator_scapulae", "Levator Scapulae"),
        ("delts", "Delts"),
        ("pecs", "Pectorals"),
        ("serratus terior", "Serratus Anterior"),
    ]
    
    ex_id = models.IntegerField(default=0, db_comment="ID of each exercise")
    ex_name = models.CharField(max_length=80, default="", null=False, db_comment="The name of the exercise")
    ex_type = models.CharField(max_length=100, choices=exercise_type, null=False, db_comment="Type of exercise, Cardio, Muscle etc")
    ex_body_area = models.CharField(max_length=15, choices=body_area_choices, null=False, db_comment="What body part the exercise is working on: Legs, back, chest etc")
    equipment_needed = models.CharField(max_length=80, default="none", null=False, db_comment="Equipment needed for exercise")
    ex_target_muscle = models.CharField(max_length=20, choices=muscle_choices, null=True, db_comment="Target Muscle - can be null for cardio")
    ex_secondary_muscle = models.CharField(max_length=30, choices=muscle_choices, null=True, db_comment= "Secondary muscle targeted")