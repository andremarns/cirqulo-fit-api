from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import get_db
from app.application.workout_service import WorkoutService
from app.application.schemas.workout import (
    WorkoutCreate, WorkoutResponse, WorkoutSessionCreate, WorkoutSessionResponse,
    WorkoutExerciseCreate, WorkoutExerciseResponse, WeeklyProgressResponse,
    WorkoutStatsResponse
)
from app.application.schemas.dashboard import DashboardData
from app.application.dashboard_service import DashboardService
from app.application.auth_service import get_current_user

router = APIRouter(prefix="/api/workouts", tags=["workouts"])

@router.get("/", response_model=List[WorkoutResponse])
async def get_workouts(
    level: Optional[int] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Buscar treinos do usuário"""
    service = WorkoutService(db)
    workouts = service.get_user_workouts(current_user.id, level)
    return workouts

@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout_data: WorkoutCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Criar novo treino"""
    service = WorkoutService(db)
    workout = service.create_workout(current_user.id, workout_data)
    return workout

@router.post("/sessions/", response_model=WorkoutSessionResponse)
async def start_workout_session(
    session_data: WorkoutSessionCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Iniciar sessão de treino"""
    service = WorkoutService(db)
    session = service.start_workout_session(current_user.id, session_data)
    return session

@router.patch("/sessions/{session_id}/complete", response_model=WorkoutSessionResponse)
async def complete_workout_session(
    session_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Completar sessão de treino"""
    service = WorkoutService(db)
    try:
        session = service.complete_workout_session(session_id, current_user.id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/sessions/{session_id}/exercises", response_model=WorkoutExerciseResponse)
async def add_exercise_to_session(
    session_id: int,
    exercise_data: WorkoutExerciseCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Adicionar exercício à sessão"""
    service = WorkoutService(db)
    exercise = service.add_exercise_to_session(session_id, exercise_data)
    return exercise

@router.patch("/exercises/{exercise_id}/progress", response_model=WorkoutExerciseResponse)
async def update_exercise_progress(
    exercise_id: int,
    completed_sets: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Atualizar progresso do exercício"""
    service = WorkoutService(db)
    try:
        exercise = service.update_exercise_progress(exercise_id, completed_sets)
        return exercise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/progress/weekly", response_model=WeeklyProgressResponse)
async def get_weekly_progress(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Buscar progresso semanal"""
    service = WorkoutService(db)
    progress = service.get_weekly_progress(current_user.id)
    return progress

@router.get("/stats", response_model=WorkoutStatsResponse)
async def get_workout_stats(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Buscar estatísticas de treino"""
    service = WorkoutService(db)
    stats = service.get_workout_stats(current_user.id)
    return stats

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Buscar dados do dashboard"""
    service = DashboardService(db)
    data = service.get_dashboard_data(current_user.id)
    return data