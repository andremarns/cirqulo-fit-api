from datetime import datetime
from typing import List
from pydantic import BaseModel

class WeeklyData(BaseModel):
    day: str
    sessions: int
    completed: bool
    streak: int

class CalendarData(BaseModel):
    day: str
    date: int
    completed: bool
    sessions: int
    is_today: bool

class LoadEvolutionData(BaseModel):
    date: str
    weight: float
    reps: int
    exercise: str

class DashboardData(BaseModel):
    weekly_data: List[WeeklyData]
    calendar_data: List[CalendarData]
    load_evolution_data: List[LoadEvolutionData]
    weekly_goal: int
    total_sessions: int
    completion_rate: float
    streak_days: int