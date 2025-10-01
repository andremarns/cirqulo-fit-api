from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class WorkoutSessionBase(BaseModel):
    workout_id: int
    started_at: Optional[datetime] = None

class WorkoutSessionCreate(WorkoutSessionBase):
    pass

class WorkoutSessionResponse(WorkoutSessionBase):
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    xp_earned: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkoutExerciseBase(BaseModel):
    exercise_name: str
    sets: int
    reps: int
    weight: float = 0.0

class WorkoutExerciseCreate(WorkoutExerciseBase):
    session_id: int

class WorkoutExerciseResponse(WorkoutExerciseBase):
    id: int
    session_id: int
    completed_sets: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExerciseProgressUpdate(BaseModel):
    completed_sets: int
