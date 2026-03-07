import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

# Config from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7days


# 1. Hash Password
def hash_password(password: str) -> str:
    # bcrypt in newer versions expects str, not bytes
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# 2. Verify Password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_byte_enc = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)


# Create JWT Access Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Adding expiration timestamp to payload
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        return None  # Will be caught by FASTAPI dependency
