from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from jose import JWTError

from app.db.database import engine
from app.schemas.admin import AdminLoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token, decode_token

router = APIRouter(prefix="/admin", tags=["admin"])
bearer = HTTPBearer()

def require_admin(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    token = creds.credentials
    try:
        username = decode_token(token)
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest):
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT username, password_hash FROM admin_users WHERE username=:u"),
            {"u": payload.username},
        ).fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    username, password_hash = row[0], row[1]
    if not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=username)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def admin_me(username: str = Depends(require_admin)):
    return {"admin": username}