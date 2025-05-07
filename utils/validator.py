import re
from utils.exceptions import WeakPasswordError, InvalidNameException


class Messages:
    """Generic messages for HTTP responses.
    """
    error_400 = "Invalid request. {} is invalid"
    generic_error = "An unknown error has occurred. Please try again!"


class Status:
    """Describes HTTP request status codes.
    """

    INVALID_REQUEST = 400
    """Used for invalid HTTP requests, equivalent to HTTP error 400."""
    
    SUCCESS = 200
    """Used for successful HTTP requests, equivalent to HTTP error 200."""


def validate_email(email: str):
    """A function which determines if a given email is a valid email or not.

    An email address is valid if all of the following are met:
        * The email address contains exactly 1 "@" and at least 1 "."
        * The first character of the email address is an alphabet character.
        * The domain segment of the email address contains either 1 or 2 "."
        * The first character of each segment within the domain segment is an alphabet character.

    :param email: The email address of the user creating an account.
    :type email: str
    :return: **True** if the email is valid, otherwise **False**.
    :rtype: bool
    """
    at, dot = "@", "."
    is_valid = False
    if at not in email or dot not in email:
        return is_valid
    email_segments = email.strip().lower().split(at)
    if len(email_segments) == 2:
        if email_segments[0][0].isalpha():
            # start of email should not be a digit
            domain_seg = email_segments[1].split(dot)
            is_valid = (1 < len(domain_seg) < 4) and domain_seg[0].isalpha() and domain_seg[1].isalpha()
    return is_valid

# a valid username should start with a letter, and only contain letters/numbers
def validate_username(username: str):
    """A function which determines if a given username is valid or not.

    A username is valid if:
        * The entire username is alphanumeric.
        * The first character of the username is an alphabet character.

    :param username: The username to be validated.
    :type username: str
    :return: Whether **username** is valid or not. Returns **True** if **username** is valid, otherwise **False**.
    :rtype: bool
    """
    if len(username) < 1:
        return False
    return username[0].isalpha() and username.isalnum()

def check_name(name: str):
    """A function to assess the validity of a given name.

    For a name to be valid:
        * The name must contain 2-50 (inclusive) alphanumeric characters.

    :param name: The name to be checked.
    :type name: str
    :raises InvalidNameException: if the name does not meet the given requirements.
    :return: **name**
    :rtype: str
    """

    if 1 < len(name) < 50 and name.isalpha():
        return name
    raise InvalidNameException

def check_password(password: str):
    """Password checker function for valid strength.

    All of the following must be met to be considered valid:
        * The password must have at least 6 characters.
        * The password must contain at least 1 digit.
        * The password must contain at least 1 lowercase letter.
        * The password must contain at least 1 uppercase letter.
        * The password must contain at least 1 non-alphanumeric character (excluding underscores).
        * The password must not contain any whitespace at all (e.g. space, tab, form/line feed).

    :param password: The password to be checked.
    :type password: str
    :raises WeakPasswordError: if the valid strength for a password has not been met.
    :return: **password**
    :rtype: str
    """
    if len(password) >= 6 and re.search(r'\d+', password) and re.search(r'[a-z]+', password) \
            and re.search(r'[A-Z]+', password) \
            and re.search(r'\W+', password) \
            and not re.search(r'\s+', password):
        return password
    else:
        raise WeakPasswordError

