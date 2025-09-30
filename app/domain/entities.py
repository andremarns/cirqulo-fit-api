from datetime import datetime
from typing import Optional, List
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class User:
    def __init__(self, id: int, name: str, email: str, gender: GenderEnum, 
                 is_active: bool = True, created_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.email = email
        self.gender = gender
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        
        # Relacionamentos
        self.workouts: List['Workout'] = []
        self.workout_sessions: List['WorkoutSession'] = []
        self.progress: List['UserProgress'] = []

class Workout:
    def __init__(self, id: int, name: str, user_id: int, description: Optional[str] = None,
                 category: str = "mixed", level: int = 1, duration: Optional[int] = None,
                 exercises_count: int = 0, xp_reward: int = 0, is_active: bool = True, 
                 created_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.description = description
        self.category = category
        self.level = level
        self.duration = duration
        self.exercises_count = exercises_count
        self.xp_reward = xp_reward
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        
        # Relacionamentos
        self.sessions: List['WorkoutSession'] = []

class Exercise:
    def __init__(self, id: int, name: str, user_id: int, muscle_group: Optional[str] = None,
                 description: Optional[str] = None, workout_id: Optional[int] = None,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.muscle_group = muscle_group
        self.description = description
        self.workout_id = workout_id
        self.created_at = created_at or datetime.utcnow()

class WorkoutSession:
    def __init__(self, id: int, user_id: int, workout_id: int, started_at: Optional[datetime] = None,
                 completed_at: Optional[datetime] = None, duration: Optional[int] = None,
                 xp_earned: int = 0, is_completed: bool = False):
        self.id = id
        self.user_id = user_id
        self.workout_id = workout_id
        self.started_at = started_at or datetime.utcnow()
        self.completed_at = completed_at
        self.duration = duration
        self.xp_earned = xp_earned
        self.is_completed = is_completed
        
        # Relacionamentos
        self.exercises: List['WorkoutExercise'] = []

class ExerciseSet:
    def __init__(self, id: int, exercise_id: int, session_id: int, reps: int, weight: float,
                 rest_time: Optional[int] = None, order: int = 1, 
                 completed_at: Optional[datetime] = None):
        self.id = id
        self.exercise_id = exercise_id
        self.session_id = session_id
        self.reps = reps
        self.weight = weight
        self.rest_time = rest_time
        self.order = order
        self.completed_at = completed_at or datetime.utcnow()

class WorkoutExercise:
    def __init__(self, id: int, session_id: int, exercise_name: str, sets: int, reps: int,
                 weight: int = 0, completed_sets: int = 0, is_completed: bool = False):
        self.id = id
        self.session_id = session_id
        self.exercise_name = exercise_name
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.completed_sets = completed_sets
        self.is_completed = is_completed

class UserProgress:
    def __init__(self, id: int, user_id: int, date: datetime, total_workouts: int = 0,
                 total_exercises: int = 0, total_xp: int = 0, current_streak: int = 0,
                 longest_streak: int = 0, level: int = 1):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.total_workouts = total_workouts
        self.total_exercises = total_exercises
        self.total_xp = total_xp
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.level = level

