"""
Password hashing and verification utilities.
Uses bcrypt for secure, salted password storage.
"""
import bcrypt

def hash_password(password: str) -> str:
    """
    Creates a secure salted hash from a plain-text password.
    """
    # bcrypt operations must be performed on bytes
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() # Automatically handles salt generation
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8') # Return as string for database storage

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain-text password matches its stored hash.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
