from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt

from core.security import (
    verify_password, create_access_token, create_refresh_token,
    get_password_hash, SECRET_KEY, ALGORITHM
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Фейкова база користувачів (пароль: "secret")
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("secret")
    }
}


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Перевіряємо, чи існує користувач і чи співпадає пароль
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Генеруємо пару токенів
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    try:
        # Декодуємо refresh токен
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        # Перевіряємо, чи це дійсно refresh токен
        if username is None or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Якщо все ок, генеруємо новий access токен
        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")