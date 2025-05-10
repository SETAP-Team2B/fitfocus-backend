from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

macro_keys = [
    "fat_g",
    "saturates_g",
    "trans_fat_g",
    "protein_g",
    "salt_g",
    "fiber_g",
    "carbohydrates_g",
    "sugars_g",
    "cholesterol_g",
]
"""A list of keys that will be used in any "macros" dictionaries, be it logged macros, or consumable macros.
"""

def positive_validator(value, include_equal: bool = False):
    """A validator to ensure a given numeric field has a positive value.

    :param value: The value to be validated.
    :type value: int | float
    :param include_equal: Whether or not the validator returns true on 0, defaults to False
    :type include_equal: bool, optional
    :return: Whether or not the value is above (or equal to, if include_equal is **True**) 0.
    :rtype: bool
    """
    return value > 0.0 if not include_equal else value >= 0.0

def validate_macros(value):
    """A validator to ensure that all the macro-nutrient values are non-negative.

    This calls the `positive_validator` function, with include_equal = **True**.
    Sometimes the `value` parameter may not actually be of type (dict), but checking the type will return dict.

    :param value: The dictionary of macro-nutrients to be validated.
    :type value: object
    :return: False if the type of `value` is not dict, or if any macro-nutrient value is negative. Otherwise, returns True.
    :rtype: bool
    """
    if type(value) != dict: return False

    for key in value.keys():
        amount = value[key]
        if key in macro_keys:
            if not positive_validator(amount, include_equal=True):
                return False

    return True


class OTP(models.Model):
    """A one-time password.

    ===========  ========  ============================  =====================================================================
    Field        Type      Constraints                   Description
    ===========  ========  ============================  =====================================================================
    user         int       NOT NULL, FOREIGN KEY (User)  The user who the OTP is for.
    otp          str       NOT NULL                      The OTP value.
    created_at   datetime  NOT NULL                      When the OTP was created. Defaults to the current date and time.
    expiry_time  datetime  NOT NULL                      When the OTP cannot be updated. Default is 5 minutes after created_at
    verified     bool      NOT NULL                      Whether the OTP has been verified or not. Default is False.
    ===========  ========  ============================  =====================================================================

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    otp = models.CharField(max_length=6, default="", null=False, db_comment="The OTP sent to the user.")
    created_at = models.DateTimeField(auto_now=True, db_comment="When the OTP was created. Useful for restricting the frequency of new OTP generation.")
    expiry_time = models.DateTimeField(db_comment="When the OTP can no longer be accepted. Default is 5 minutes after when it was created.")
    verified = models.BooleanField(default=False, db_comment="Whether the OTP for the user has been verified. Good for preventing repeat entries and also ensuring user is secure.")

class Exercise(models.Model):  
    """An exercise object
    ======================  =========  ================================  ============================================================================
    Field                   Type       Constraints                       Description
    ======================  =========  ================================  ============================================================================
    ex_name                 str        NOT NULL, MAX_LENGTH=80, UNIQUE   The name of the exercise
    ex_type                 str        NOT NULL, MAX_LENGTH=100          Type of exercise, Cardio, Muscle etc
    ex_body_area            str        NOT NULL, MAX_LENGTH=15           What body part the exercise is working on: Legs, back, chest etc
    equipment_needed        str        NOT NULL, MAX_LENGTH=80           Equipment needed for exercise
    ex_target_muscle        str        MAX_LENGTH=20                     Target Muscle - can be null for cardio
    ex_secondary_muscle_1   str        MAX_LENGTH=30                     Secondary muscle targeted
    ex_secondary_muscle_2   str        MAX_LENGTH=30                     Other Secondary Muscle Targeted
    ======================  =========  ================================  ============================================================================
    """
    ex_name = models.CharField(max_length=80, default="", null=False, db_comment="The name of the exercise")
    ex_type = models.CharField(max_length=100, default="", null=False, db_comment="Type of exercise, Cardio, Muscle etc")
    ex_body_area = models.CharField(max_length=15, default="", null=False, db_comment="What body part the exercise is working on: Legs, back, chest etc")
    equipment_needed = models.CharField(max_length=80, default="none", null=False, db_comment="Equipment needed for exercise")
    ex_target_muscle = models.CharField(max_length=20, default="", null=True, db_comment="Target Muscle - can be null for cardio")
    ex_secondary_muscle_1 = models.CharField(max_length=30, default="", null=True, db_comment= "Secondary muscle targeted")
    ex_secondary_muscle_2 = models.CharField(max_length=30, default="", null=True, db_comment="Other Secondary Muscle Targeted")

# TODO: sort the __todict__ function to return None if applicable
# subject to change with extra fields
class LoggedExercise(models.Model):
    """A logged exercise

    ======================  =========  ========================================  ============================================================================
    Field                   Type       Constraints                               Description
    ======================  =========  ========================================  ============================================================================
    user                    object     NOT NULL, UNIQUE, FOREIGN KEY (user)      The user that is logging an exercise
    exercise                object     NOT NULL, UNIQUE, FOREIGN KEY (exercise)  The type of exercise that is being logged
    date_logged             DATE                                                 The date of when the user is logging the exercise
    time_logged             TIME                                                 The time of when the user is logging the exercise   
    sets                    int                                                  The number of sets the user has done
    reps                    int                                                  The number of reps the user has done
    distance                float                                                The distance covered during the exercise
    distance_units          str        MAX_LENGTH=5                              The units for which distance is measured
    duration                duration                                             How long the exercise lasted
    equpment_weight         list                                                 The weight of the equipment used
    equipment_weight_units  str        MAX_LENGTH=2                              The units for which weight is measured               
    ======================  =========  ========================================  ============================================================================


    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=False)
    date_logged = models.DateField(default=timezone.now)
    time_logged = models.TimeField(default=timezone.now, null=True)
    sets = models.PositiveSmallIntegerField(default=0, null=True)
    reps = models.PositiveSmallIntegerField(default=0, null=True)
    distance = models.FloatField(default=0.0, null=True)
    distance_units = models.CharField(max_length=5, choices=[("km", "km"), ("mi", "mi")], null=True)
    duration = models.DurationField(default=timedelta(hours=0, minutes=0, seconds=0), null=True)
    equipment_weight = models.JSONField(default=list, null=True) # a list of integers for varying weights if multiple were used, MUST ALWAYS BE A LIST OTHERWISE IT BREAKS
    equipment_weight_units = models.CharField(max_length=2, choices=[("kg", "kg"), ("lb", "lb")], null=True)

    # only for making the ML model easier to import
    # only returns the minimum data necessary
    def __todict__(self):
        return {
            "sets": self.sets if self.sets else 0,
            "reps": self.reps if self.reps else 0,
            "distance": self.distance if self.distance else 0.0,
            "duration_mins": self.duration.seconds / 60.0 if self.duration else 0.0,
            "good": 1, # since it's been logged its obviously a good exercise (?)
        }

class VerifiedUser(models.Model):
    """Whether a user's account is verified or not.

    ========  ====  ============================  =========================================================
    Field     Type  Constraints                   Description
    ========  ====  ============================  =========================================================
    user      int   NOT NULL, FOREIGN KEY (User)  The user.
    verified  bool  NOT NULL                      Whether the account is verified or not. Defaults to False
    ========  ====  ============================  =========================================================

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

# TODO: sort the __todict__ function to return None if applicable
class RecommendedExercise(models.Model):
    """A recommended exercise for a given user.

    ======================  =========  ================================  ============================================================================
    Field                   Type       Constraints                       Description
    ======================  =========  ================================  ============================================================================
    user                    int        NOT NULL, FOREIGN KEY (User)      The user the recommended exercise is for.
    exercise                int        NOT NULL, FOREIGN KEY (Exercise)  The exercise that is recommended.
    datetime_recommended    datetime   NOT NULL                          The date and time the recommendation was made. Defaults to current datetime.
    good_recommendation     bool       NOT NULL                          Whether the recommendation is "good" or not. Defaults to True.
    sets                    int                                          The amount of recommended sets in the exercise. Defaults to 0.
    reps                    int                                          The amount of recommended reps per set in the exercise. Defaults to 0.
    distance                float                                        The amount of recommended distance to travel in the exercise. Defaults to 0.
    distance_units          str        MAX_LENGTH=5                      The units for **distance**. Choices are "km" or "mi".
    duration                timedelta                                    The recommended duration of the exercise. Defaults to 0 seconds.
    equipment_weight        list                                         The recommended equipment weight for the exercise.
    equipment_weight_units  str        MAX_LENGTH=2                      The units of the given equipment weight.
    ======================  =========  ================================  ============================================================================

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    datetime_recommended = models.DateTimeField(default=timezone.now)
    good_recommendation = models.BooleanField(default=True)
    sets = models.PositiveSmallIntegerField(default=0, null=True)
    reps = models.PositiveSmallIntegerField(default=0, null=True)
    distance = models.FloatField(default=0.0, null=True)
    distance_units = models.CharField(max_length=5, choices=[("km", "km"), ("mi", "mi")], null=True)
    duration = models.DurationField(default=timedelta(hours=0, minutes=0, seconds=0), null=True)
    equipment_weight = models.JSONField(default=list, null=True) # a list of integers for varying weights if multiple were used
    equipment_weight_units = models.CharField(max_length=2, choices=[("kg", "kg"), ("lb", "lb")], null=True)

    # only for making the ML model easier to import
    # only returns the minimum data necessary
    def __todict__(self):
        """A function which converts any necessary features into a dictionary format.
        Used when recommending an exercise as 

        :return: A dictionary of the following attributes:
            * sets (int)
            * reps (int)
            * distance (float)
            * duration_mins (float)
            * good (int)

        :rtype: dict
        """
        return {
            "sets": self.sets if self.sets else 0,
            "reps": self.reps if self.reps else 0,
            "distance": self.distance if self.distance else 0.0,
            "duration_mins": self.duration.seconds / 60.0,
            "good": 1 if self.good_recommendation else 0,
        }
class UserData(models.Model):
    """Stores user data for the user 

    Attributes:
        user (User) : The user who this data belongs to, foreign key to the User model
        user_age (int) : The age of the user, must be a positive integer
        user_sex (str) : The sex of the user, M / F / X (Other/Prefer not to say) 
        user_height (float) : The height of the user
        user_height_units (str) : The units of the users height, choices (in / cm)
        user_weight (float) : The weight of the user
        user_weight_units (str) : The units of the users weight, choices (lb / kg)
        user_target_weight (float) : The target weight of which the user aims to achieve
        user_body_goals (JSON) : The body goals of the user, JSON field (stored as a multiple choice field)
    """
    
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Prefer not to say/Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User is a foreign key, not null
    user_age = models.PositiveSmallIntegerField()  # Positive int (must be >= 0)
    user_sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    user_height = models.FloatField()
    user_height_units = models.CharField(max_length=2, choices=[('in', 'Inches'), ('cm', 'Centimeters')])
    user_weight = models.FloatField(null=True)
    user_weight_units = models.CharField(max_length=2, choices=[('lb', 'Pounds'), ('kg', 'Kilograms')], null=True)
    user_target_weight = models.FloatField(null=True)
    user_body_goals = models.JSONField(null=True)
    
    """
    Function for the UserData model which returns a string representation of the user data.

    Returns:
        str: A string representation of the user data in the format of "User Data for {username}"
    """
    def __str__(self):
        return f"User Data for {self.user.username}"

# this took a LOT of thinking to make but for simplicity of implementation, we are keeping it as so for now
# i tried thinking about how to make it from other consumables but it broke my brain
class Consumable(models.Model):
    """A consumable item.

    ===============  =====  ================================  =====================================================================
    Field            Type   Constraints                       Description
    ===============  =====  ================================  =====================================================================
    name             str    NOT NULL, MAX_LENGTH=150, UNIQUE  The name of the consumable.
    sample_size      float  NOT NULL, positive_validator      The amount of units in a sample.
    sample_units     str    NOT NULL, MAX_LENGTH=20           The units to measure the item.
    sample_calories  int    NOT NULL                          The calories per size of a sample.
    sample_macros    dict   validate_macros                   The macro-nutrients per size of a sample.
    ===============  =====  ================================  =====================================================================

    """
    global macro_keys, positive_validator, validate_macros

    name = models.CharField(max_length=150, primary_key=True, unique=True) # primary key because it's unique. also stops consumable logging
    sample_size = models.FloatField(validators=[positive_validator])
    sample_units = models.CharField(max_length=20, default="serving")
    sample_calories = models.PositiveIntegerField()
    sample_macros = models.JSONField(validators=[validate_macros], null=True)
    logged_user = models.ManyToManyField(to=User, through="LoggedConsumable")

class LoggedConsumable(models.Model):
    """A logged consumable item.

    ===============  =====  ===================================  ===========================================
    Field            Type   Constraints                          Description
    ===============  =====  ===================================  ===========================================
    user             int    NOT NULL, FOREIGN KEY (User)         The user who logged the consumable.
    consumable       str    NOT NULL, FORIEIGN KEY (Consumable)  The name of the consumable that was logged.
    amount_logged    float  NOT NULL, positive_validator         The amount of samples that were logged.
    date_logged      date   NOT NULL                             The date the consumable was logged.
    calories_logged  int    NOT NULL                             The total amount of calories logged.
    macros_logged    dict   validate_macros                      The total amount of macro-nutrients logged.
    ===============  =====  ===================================  ===========================================

    """
    global macro_keys, positive_validator, validate_macros

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, on_delete=models.DO_NOTHING) # do nothing does create integrity issues, however PK is a string and so is still useable for now-deleted consumables (should never happen but edge case is accounted for)
    amount_logged = models.FloatField(validators=[positive_validator]) # this is a multiplier based on the sample_size of the Consumable
    date_logged = models.DateField() # this is NOT when the instance was created, but when the consumable was consumed.
    calories_logged = models.PositiveIntegerField()
    macros_logged = models.JSONField(validators=[validate_macros], null=True)

class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Each routine belongs to a user
    name = models.CharField(max_length=255)  # Routine name
    description = models.TextField(blank=True, null=True)  # Optional description
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set timestamp

    def __str__(self):
        return f"{self.name} ({self.user.username})"

# RoutineExercise model
class RoutineExercise(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="routine_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.exercise.ex_name} in {self.routine.name} (Order: {self.order})"

class LoggedRoutine(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='logged_routines')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    progress = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username} completed {self.routine.name} on {self.completed_at}"

class UserMood(models.Model):
    """
    Model to store the mood level of the user.
    The mood level is an integer value that represents the user's mood on a scale of 1 to 10.

    Attributes:
        user (User): The user who this mood level belongs to, foreign key to the User model.
        mood_level (int): The mood level of the user between 1 and 10.
        datetime_recorded (datetime): The date and time of when the mood level was recorded.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_level = models.SmallIntegerField(default=0)
    datetime_recorded = models.DateTimeField(default=timezone.now)
