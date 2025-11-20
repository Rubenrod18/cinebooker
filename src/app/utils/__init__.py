"""Collection of functions and classes which make common patterns
shorter and easier."""

import secrets
import string


def generate_unique_code(length: int | None = None, letters: bool = False) -> str:
    length = length or 13
    charset = string.ascii_uppercase + string.digits if letters else string.digits
    return ''.join(secrets.choice(charset) for _ in range(length))
