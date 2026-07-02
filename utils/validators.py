import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_REGEX.match(email))


def is_strong_password(password: str) -> bool:
    """
    Minimum requirements: 8+ chars, at least one letter and one number.
    Adjust as needed for your firm's security policy.
    """
    if not password or len(password) < 8:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit


def allowed_resume_file(filename: str, allowed_extensions: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
