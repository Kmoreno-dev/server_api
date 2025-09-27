from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import hashlib
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from database_config import SessionLocal, UserModel

SECRET_KEY = "clave-super-secreta"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Helpers

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: int) -> str:
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(UserModel).filter_by(id=user_id).first()
    if not user:
        return {"message":"usuario no encontrado"}
    return user