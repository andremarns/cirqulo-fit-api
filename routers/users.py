from fastapi import APIRouter, Depends, HTTPException
from app.domain.entities import User
from app.application.schemas.user import UserResponse
from routers.auth import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    name: str = None,
    gender: str = None,
    current_user: User = Depends(get_current_user)
):
    from app.infrastructure.database import db
    from datetime import datetime
    
    if name or gender:
        with db.get_cursor() as cursor:
            update_fields = []
            values = []
            
            if name:
                update_fields.append("name = %s")
                values.append(name)
            if gender:
                update_fields.append("gender = %s")
                values.append(gender)
            
            update_fields.append("updated_at = %s")
            values.append(datetime.utcnow())
            values.append(current_user.id)
            
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, name, email, gender, is_active, created_at, updated_at
            """, values)
            
            user_data = cursor.fetchone()
            return UserResponse(
                id=user_data[0],
                name=user_data[1],
                email=user_data[2],
                gender=user_data[3],
                is_active=user_data[4],
                created_at=user_data[5],
                updated_at=user_data[6]
            )
    
    return current_user
