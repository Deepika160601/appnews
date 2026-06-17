from datetime import (
    datetime,
    timedelta
)

from jose import (
    jwt,
    JWTError
)

from passlib.context import (
    CryptContext
)

from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from app.core.config import settings
# ========================
# PASSWORD HASHING
# ========================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
# ========================
# BEARER AUTH
# ========================
security = HTTPBearer(
    auto_error=True
)
# ========================
# HASH PASSWORD
# ========================
def hash_password(
    password: str
) -> str:

    return pwd_context.hash(
        password
    )
# ========================
# VERIFY PASSWORD
# ========================
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ========================
# CREATE ACCESS TOKEN
# ========================
def create_access_token(
    data: dict
) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# ========================
# DECODE ACCESS TOKEN
# ========================
def decode_access_token(
    token: str
):

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ]
        )

        return payload

    except JWTError:

        return None


# ========================
# GET CURRENT USER
# ========================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    token = credentials.credentials

    payload = decode_access_token(
        token
    )

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    role = payload.get(
        "role"
    )

    if role != "user":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )

    return payload


# ========================
# GET CURRENT ADMIN
# ========================
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    token = credentials.credentials

    payload = decode_access_token(
        token
    )

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    role = payload.get(
        "role"
    )

    if role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return payload


# ========================
# GET CURRENT USER ID
# ========================
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    payload = await get_current_user(
        credentials
    )

    user_id = payload.get(
        "user_id"
    )

    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )

    return user_id


# ========================
# GET CURRENT ADMIN ID
# ========================
async def get_current_admin_id(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    payload = await get_current_admin(
        credentials
    )

    admin_id = payload.get(
        "admin_id"
    )

    if admin_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin ID not found in token"
        )

    return admin_id