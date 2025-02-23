class WeakPasswordError(BaseException):

    def __str__(self):
        return "Password is too weak." \
               " Use a strong password with at least 6 upper and lower case alpha-numeric" \
               " characters including special symbols"


class InvalidNameException(BaseException):

    def __str__(self):
        return "Name cannot exceed 50 or contain less than 2 characters."
