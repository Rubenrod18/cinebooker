"""Collection of functions and classes which make common patterns
shorter and easier."""

import secrets
import string


def generate_unique_code(length: int | None = None) -> str:
    length = length or 13
    return ''.join(secrets.choice(string.digits) for _ in range(length))
