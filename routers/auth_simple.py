from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=dict)
async def register(user_data: dict):
    """Endpoint simplificado de registro para teste"""
    return {
        "message": "Registro simplificado funcionando",
        "user_data": user_data
    }

@router.post("/login-json", response_model=dict)
async def login_json(login_data: dict):
    """Endpoint simplificado de login para teste"""
    return {
        "message": "Login simplificado funcionando",
        "access_token": "fake_token_for_testing",
        "token_type": "bearer"
    }

@router.get("/me", response_model=dict)
async def get_current_user():
    """Endpoint simplificado de usuário atual para teste"""
    return {
        "id": 1,
        "name": "Usuário Teste",
        "email": "teste@example.com",
        "is_active": True
    }
