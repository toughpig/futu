import hashlib
import re
import logging

logger = logging.getLogger("FutuTrader")

def is_md5_hash(s):
    """
    Check if a string matches MD5 hash format (32 hex characters)
    
    Args:
        s: String to check
        
    Returns:
        bool: True if the string is a valid MD5 hash
    """
    if not s:
        return False
    return bool(re.match(r'^[a-f0-9]{32}$', s.lower()))

def hash_password(password, use_md5=True, is_already_hashed=False):
    """
    Hash a password using MD5 if needed
    
    Args:
        password: Password string to hash
        use_md5: Whether to use MD5 hashing
        is_already_hashed: Whether the password is already hashed
        
    Returns:
        str: Original or hashed password
    """
    if not password:
        return password
        
    # If it's already hashed or we don't need to hash, return as is
    if is_already_hashed or not use_md5:
        return password
        
    # Check if it already looks like an MD5 hash
    if is_md5_hash(password):
        logger.warning("Password appears to be an MD5 hash already but IS_PASSWORD_HASHED is False")
        return password
        
    # Hash the password with MD5
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    logger.debug("Password hashed with MD5")
    return hashed_password

def generate_password_hash(password):
    """
    Generate an MD5 hash for a given password (utility function)
    
    Args:
        password: Password to hash
        
    Returns:
        str: MD5 hash of the password
    """
    return hashlib.md5(password.encode()).hexdigest() 