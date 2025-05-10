class WeakPasswordError(BaseException):
    """A generic exception that gets raised whenever a password is too weak.
    Will raise with the following message:
    "Password is too weak. Use a strong password with at least 6 upper and lower case alpha-numeric characters including special symbols"
    """

    def __str__(self):
        return "Password is too weak." \
               " Use a strong password with at least 6 upper and lower case alpha-numeric" \
               " characters including special symbols"


class InvalidNameException(BaseException):
    """A generic exception that gets raised whenever a given name (not username) is invalid.
    Will raise with the following message:
    "Name cannot exceed 50 or contain less than 2 characters."
    """

    def __str__(self):
        return "Name cannot exceed 50 or contain less than 2 characters."
