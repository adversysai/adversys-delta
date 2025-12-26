from python.helpers import dotenv
import hashlib
import os


def get_credentials_hash():
    # Check environment variable first (before .env file override)
    # This allows docker-compose to explicitly disable auth
    user = os.getenv("AUTH_LOGIN")
    if not user or not user.strip():
        # Fall back to .env file if env var not set
        user = dotenv.get_dotenv_value("AUTH_LOGIN")
    
    password = os.getenv("AUTH_PASSWORD")
    if not password:
        password = dotenv.get_dotenv_value("AUTH_PASSWORD")
    
    # Treat empty strings and None as "not set"
    if not user or not user.strip():
        return None
    return hashlib.sha256(f"{user}:{password}".encode()).hexdigest()


def is_login_required():
    # Check environment variable first (before .env file override)
    # This allows docker-compose to explicitly disable auth
    user = os.getenv("AUTH_LOGIN")
    if user is None:
        # Fall back to .env file if env var not set
        user = dotenv.get_dotenv_value("AUTH_LOGIN")
    
    # Treat empty strings and None as "not set"
    return bool(user and user.strip())
