from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import GenderEnum

class UserBase(BaseModel):
    name: str
    email: EmailStr
    gender: GenderEnum

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_group: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    workout_id: Optional[int] = None

class ExerciseResponse(ExerciseBase):
    id: int
    user_id: int
    workout_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class ExerciseSetBase(BaseModel):
    reps: int
    weight: float
    rest_time: Optional[int] = None
    order: int

class ExerciseSetCreate(ExerciseSetBase):
    exercise_id: int

class ExerciseSetResponse(ExerciseSetBase):
    id: int
    exercise_id: int
    session_id: int
    completed_at: datetime

    class Config:
        from_attributes = True

class WorkoutSessionBase(BaseModel):
    workout_id: int
    notes: Optional[str] = None

class WorkoutSessionCreate(WorkoutSessionBase):
    pass

class WorkoutSessionResponse(WorkoutSessionBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime]
    total_duration: Optional[int]

    class Config:
        from_attributes = True
