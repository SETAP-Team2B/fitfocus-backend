import re

from utils.exceptions import WeakPasswordError, InvalidNameException


class Messages:
    error_400 = "Invalid request. {} is invalid"
    generic_error = "An unknown error has occurred. Please try again!"


class Status:
    INVALID_REQUEST = 400
    SUCCESS = 200


def validate_email(email: str):
    """
    Validate if an email is correct or not
    """
    at, dot = "@", "."
    is_valid = False
    if at not in email or dot not in email:
        return is_valid
    email_segments = email.strip().split(at)
    if len(email_segments) == 2:
        # email_segments[0][0].isalpha() and email_segments[0].isalnum()
        if validate_username(email_segments[0]):
            # start of email should not be a digit
            domain_seg = email_segments[1].split(dot)
            is_valid = len(domain_seg) == 2 and domain_seg[0].isalpha() and domain_seg[1].isalpha()
    return is_valid


def validate_username(username: str):
    return username[0].isalpha() and username.isalnum()


def check_name(name: str):
    if 1 < len(name) < 50 and name.isalpha():
        return name
    raise InvalidNameException


def check_password(password: str):
    if len(password) >= 6 and re.search(r'\d+', password) and re.search(r'[a-z]+', password) \
            and re.search(r'[A-Z]+', password) \
            and re.search(r'\W+', password) \
            and not re.search(r'\s+', password):
        return password
    else:
        raise WeakPasswordError

