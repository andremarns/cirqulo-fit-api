from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.domain.entities import User, GenderEnum
from app.domain.repositories import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def register_user(self, name: str, email: str, password: str, gender: GenderEnum) -> User:
        # Verificar se usuário já existe
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Criar novo usuário
        hashed_password = self.get_password_hash(password)
        user = User(
            id=0,  # Será definido pelo repositório
            name=name,
            email=email,
            gender=gender
        )
        return await self.user_repository.create(user)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def get_current_user(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
        except JWTError:
            return None
        
        return await self.user_repository.get_by_email(email)

# Função standalone para dependency injection
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    """Dependency para obter usuário atual"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    # Aqui precisaríamos de uma instância do repositório
    # Por enquanto, vamos retornar um usuário mock para teste
    return User(
        id=1,
        name="Test User",
        email=email,
        gender=GenderEnum.MALE
    )
