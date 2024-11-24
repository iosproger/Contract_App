from typing import List

from fastapi import APIRouter, Depends, HTTPException, Form,status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import crud, schemas
from test_login_with_token.dependencies import get_db
from jwt.exceptions import InvalidTokenError

import utils as auth_utils

from fastapi.security import (
    # HTTPBearer,
    # HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)

router = APIRouter(prefix='/jwt', tags=["sign"])

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="jwt/login/",
)

def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db)
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if not (user := crud.get_user_by_name(db=db, name=username)):
        raise unauthed_exc

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        raise unauthed_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )

    return user





@router.post("/signup", response_model=dict)
async def create_user(
    user: schemas.UserBase ,
    db: Session = Depends(get_db)
):

    if crud.user_check(db= db,name = user.name) :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already registered")


    hashed_password = auth_utils.hash_password(user.password)

    response = crud.create_user(db=db , name=user.name,hashed_password=hashed_password,active=user.active)

    return {"message": f" add user successfully {response.name}"}



@router.post("/login/", response_model=schemas.TokenInfo)
def auth_user_issue_jwt(
    user  = Depends(validate_auth_user),
):

    jwt_payload = {
        # subjec
        "sub": user.name,
        "username": user.name,
        # "email": user,
        # "logged_in_at"
    }

    token = auth_utils.encode_jwt(jwt_payload)

    return schemas.TokenInfo(
        access_token=token,
        token_type="Bearer",
    )

def get_current_token_payload(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    token: str = Depends(oauth2_scheme),
) -> dict:
    # token = credentials.credentials
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
            # detail=f"invalid token error",
        )
    return payload

def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    db: Session = Depends(get_db),
) -> schemas.UserBase:
    username: str | None = payload.get("sub")
    if user := crud.get_user_by_name(db= db, name= username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )

def get_current_active_auth_user(
    user: schemas.UserBase = Depends(get_current_auth_user),
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive",
    )



@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: schemas.UserBase = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "username": user.name,
        "email": user.name,
        "logged_in_at": iat,
    }