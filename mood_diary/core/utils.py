import hashlib


def hash_email(email: str) -> str:
    """
    Hashes the email address to 64 characters.
    """
    return hashlib.sha256(email.encode()).hexdigest()
