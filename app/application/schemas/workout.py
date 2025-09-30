from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "mixed"
    level: int = 1
    duration: Optional[int] = None
    exercises_count: int = 0
    xp_reward: int = 0

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WorkoutSessionBase(BaseModel):
    workout_id: int
    started_at: Optional[datetime] = None
    duration: Optional[int] = None
    xp_earned: int = 0
    is_completed: bool = False

class WorkoutSessionCreate(WorkoutSessionBase):
    pass

class WorkoutSessionUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    xp_earned: Optional[int] = None
    is_completed: Optional[bool] = None

class WorkoutSessionResponse(WorkoutSessionBase):
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WorkoutExerciseBase(BaseModel):
    exercise_name: str
    sets: int
    reps: int
    weight: int = 0
    completed_sets: int = 0
    is_completed: bool = False

class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass

class WorkoutExerciseUpdate(BaseModel):
    completed_sets: Optional[int] = None
    is_completed: Optional[bool] = None

class WorkoutExerciseResponse(WorkoutExerciseBase):
    id: int
    session_id: int
    
    class Config:
        from_attributes = True

class UserProgressBase(BaseModel):
    date: datetime
    total_workouts: int = 0
    total_exercises: int = 0
    total_xp: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    level: int = 1

class UserProgressCreate(UserProgressBase):
    pass

class UserProgressResponse(UserProgressBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class WeeklyProgressResponse(BaseModel):
    week_start: datetime
    week_end: datetime
    total_sessions: int
    completed_sessions: int
    total_xp: int
    current_streak: int
    level: int
    daily_progress: List[dict]

class WorkoutStatsResponse(BaseModel):
    total_workouts: int
    total_exercises: int
    total_xp: int
    current_streak: int
    longest_streak: int
    level: int
    level_progress: float
    achievements_unlocked: int
