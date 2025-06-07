import hashlib
import hmac

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a stored password against one provided by user."""
    return hmac.compare_digest(hash_password(password), hashed)
