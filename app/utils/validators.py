"""Validation helpers placeholder"""

def is_valid_email(email: str) -> bool:
    import re
    return bool(re.match(r"[\w.+-]+@[\w-]+\.[\w.-]+", email or ""))
