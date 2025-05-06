import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext

load_dotenv()


TOKEN_EXPIRE_MINUTES = int(os.getenv('TOKEN_EXPIRE_MINUTES', 30))
API_KEY_HEADER_NAME = 'X-Auth-Token'
api_key_header_scheme = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=True)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# In-Memory token Store
# token looks like this {"username": str, "expires": datetime}
# state is lost on server restart.
# Not inherently thread-safe for multi-worker setups without locks ?
ACTIVE_TOKENS: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_hash(username: str) -> Optional[str]:
    """Fetches the hashed password from environment variables."""
    env_var_name = f"USER_{username.upper()}_HASH"
    return os.getenv(env_var_name)


def create_access_token(username: str) -> str:
    """Creates a new token, stores it, and returns the token string."""
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    # TODO locking needed for multi-threaded access, smth like with token_lock ?
    ACTIVE_TOKENS[token] = {'username': username, 'expires': expires}
    logger.info(f"Created new token for user '{username}' expiring at {expires}")
    return token


def renew_token_expiry(token: str) -> bool:
    """Updates the expiry time for an existing token. Returns True if successful."""
    token_data = ACTIVE_TOKENS.get(token)
    if token_data:
        token_data['expires'] = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        logger.debug(f"Renewed token expiry for user '{token_data['username']}'")
        return True
    return False


def cleanup_expired_tokens():
    """Removes expired tokens from the store"""
    now = datetime.now(timezone.utc)
    expired_tokens = [token for token, data in ACTIVE_TOKENS.items() if data['expires'] < now]
    for token in expired_tokens:
        username = ACTIVE_TOKENS.get(token, {}).get('username', 'unknown')
        del ACTIVE_TOKENS[token]
        logger.info(f"Removed expired token for user '{username}'.")


# Authentication Dependency -> this gets passed to the routes
async def get_current_user(token: str = Depends(api_key_header_scheme)) -> str:
    """
    validate token and return the username
    renews the token's expiration on successful validation
     cleanup of expired tokens.
    """

    cleanup_expired_tokens()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid authentication credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    token_data = ACTIVE_TOKENS.get(token)
    if not token_data:
        logger.warning(f"Token not found: {token[:5]}...")
        raise credentials_exception

    username: str = token_data['username']
    expires: datetime = token_data['expires']

    if expires < datetime.now(timezone.utc):
        logger.warning(f"Token expired for user '{username}'")
        # Remove the  expired token
        if token in ACTIVE_TOKENS:
            del ACTIVE_TOKENS[token]
        raise credentials_exception

    renew_token_expiry(token)

    logger.debug(f"Token validated successfully for user: {username}")
    return username
