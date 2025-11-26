"""Collection of functions and classes which make common patterns
shorter and easier."""

import base64
import secrets
import string
from io import BytesIO

import qrcode


def generate_unique_code(length: int | None = None, letters: bool = False) -> str:
    length = length or 13
    charset = string.ascii_uppercase + string.digits if letters else string.digits
    return ''.join(secrets.choice(charset) for _ in range(length))


def generate_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer)
    qr_bytes = buffer.getvalue()
    return base64.b64encode(qr_bytes).decode('utf-8')
