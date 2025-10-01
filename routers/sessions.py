from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.infrastructure.database import db
from app.domain.entities import User
from app.application.schemas.session import (
    WorkoutSessionCreate, WorkoutSessionResponse,
    WorkoutExerciseCreate, WorkoutExerciseResponse,
    ExerciseProgressUpdate
)
from routers.auth import get_current_user

router = APIRouter(tags=["sessions"])

@router.post("/", response_model=WorkoutSessionResponse)
async def start_workout_session(
    session_data: WorkoutSessionCreate,
    current_user: User = Depends(get_current_user)
):
    """Iniciar uma nova sessão de treino"""
    with db.get_cursor() as cursor:
        # Verificar se o treino existe e pertence ao usuário
        cursor.execute("""
            SELECT id FROM workouts WHERE id = %s AND user_id = %s
        """, (session_data.workout_id, current_user.id))
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treino não encontrado"
            )
        
        # Criar sessão
        started_at = session_data.started_at or datetime.utcnow()
        cursor.execute("""
            INSERT INTO workout_sessions (user_id, workout_id, started_at, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, user_id, workout_id, started_at, completed_at, duration, xp_earned, is_completed, created_at, updated_at
        """, (
            current_user.id,
            session_data.workout_id,
            started_at,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        session_data = cursor.fetchone()
        return WorkoutSessionResponse(
            id=session_data[0],
            user_id=session_data[1],
            workout_id=session_data[2],
            started_at=session_data[3],
            completed_at=session_data[4],
            duration=session_data[5],
            xp_earned=session_data[6],
            is_completed=session_data[7],
            created_at=session_data[8],
            updated_at=session_data[9]
        )

@router.patch("/{session_id}/complete", response_model=WorkoutSessionResponse)
async def complete_workout_session(
    session_id: int,
    current_user: User = Depends(get_current_user)
):
    """Completar uma sessão de treino"""
    with db.get_cursor() as cursor:
        # Verificar se a sessão existe e pertence ao usuário
        cursor.execute("""
            SELECT * FROM workout_sessions WHERE id = %s AND user_id = %s
        """, (session_id, current_user.id))
        
        session = cursor.fetchone()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
            )
        
        # Calcular duração e XP
        started_at = session[3]
        completed_at = datetime.utcnow()
        duration = int((completed_at - started_at).total_seconds() / 60)  # em minutos
        
        # Calcular XP baseado na duração e exercícios
        cursor.execute("""
            SELECT COUNT(*) FROM workout_exercises WHERE session_id = %s
        """, (session_id,))
        exercise_count = cursor.fetchone()[0]
        xp_earned = duration * 2 + exercise_count * 10
        
        # Atualizar sessão
        cursor.execute("""
            UPDATE workout_sessions 
            SET completed_at = %s, duration = %s, xp_earned = %s, is_completed = true, updated_at = %s
            WHERE id = %s
            RETURNING id, user_id, workout_id, started_at, completed_at, duration, xp_earned, is_completed, created_at, updated_at
        """, (
            completed_at,
            duration,
            xp_earned,
            datetime.utcnow(),
            session_id
        ))
        
        session_data = cursor.fetchone()
        return WorkoutSessionResponse(
            id=session_data[0],
            user_id=session_data[1],
            workout_id=session_data[2],
            started_at=session_data[3],
            completed_at=session_data[4],
            duration=session_data[5],
            xp_earned=session_data[6],
            is_completed=session_data[7],
            created_at=session_data[8],
            updated_at=session_data[9]
        )

@router.post("/{session_id}/exercises", response_model=WorkoutExerciseResponse)
async def add_exercise_to_session(
    session_id: int,
    exercise_data: WorkoutExerciseCreate,
    current_user: User = Depends(get_current_user)
):
    """Adicionar exercício a uma sessão"""
    with db.get_cursor() as cursor:
        # Verificar se a sessão existe e pertence ao usuário
        cursor.execute("""
            SELECT id FROM workout_sessions WHERE id = %s AND user_id = %s
        """, (session_id, current_user.id))
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
            )
        
        # Adicionar exercício
        cursor.execute("""
            INSERT INTO workout_exercises (session_id, exercise_name, sets, reps, weight, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, session_id, exercise_name, sets, reps, weight, completed_sets, is_completed, created_at, updated_at
        """, (
            session_id,
            exercise_data.exercise_name,
            exercise_data.sets,
            exercise_data.reps,
            exercise_data.weight,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        exercise_data = cursor.fetchone()
        return WorkoutExerciseResponse(
            id=exercise_data[0],
            session_id=exercise_data[1],
            exercise_name=exercise_data[2],
            sets=exercise_data[3],
            reps=exercise_data[4],
            weight=exercise_data[5],
            completed_sets=exercise_data[6],
            is_completed=exercise_data[7],
            created_at=exercise_data[8],
            updated_at=exercise_data[9]
        )

@router.patch("/exercises/{exercise_id}/progress", response_model=WorkoutExerciseResponse)
async def update_exercise_progress(
    exercise_id: int,
    progress_data: ExerciseProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """Atualizar progresso de um exercício"""
    with db.get_cursor() as cursor:
        # Verificar se o exercício existe e pertence ao usuário
        cursor.execute("""
            SELECT we.* FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            WHERE we.id = %s AND ws.user_id = %s
        """, (exercise_id, current_user.id))
        
        exercise = cursor.fetchone()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercício não encontrado"
            )
        
        # Atualizar progresso
        completed_sets = progress_data.completed_sets
        is_completed = completed_sets >= exercise[3]  # exercise[3] é o número de sets
        
        cursor.execute("""
            UPDATE workout_exercises 
            SET completed_sets = %s, is_completed = %s, updated_at = %s
            WHERE id = %s
            RETURNING id, session_id, exercise_name, sets, reps, weight, completed_sets, is_completed, created_at, updated_at
        """, (
            completed_sets,
            is_completed,
            datetime.utcnow(),
            exercise_id
        ))
        
        exercise_data = cursor.fetchone()
        return WorkoutExerciseResponse(
            id=exercise_data[0],
            session_id=exercise_data[1],
            exercise_name=exercise_data[2],
            sets=exercise_data[3],
            reps=exercise_data[4],
            weight=exercise_data[5],
            completed_sets=exercise_data[6],
            is_completed=exercise_data[7],
            created_at=exercise_data[8],
            updated_at=exercise_data[9]
        )

@router.get("/{session_id}/exercises", response_model=List[WorkoutExerciseResponse])
async def get_session_exercises(
    session_id: int,
    current_user: User = Depends(get_current_user)
):
    """Obter exercícios de uma sessão"""
    with db.get_cursor() as cursor:
        # Verificar se a sessão existe e pertence ao usuário
        cursor.execute("""
            SELECT id FROM workout_sessions WHERE id = %s AND user_id = %s
        """, (session_id, current_user.id))
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
            )
        
        # Buscar exercícios
        cursor.execute("""
            SELECT id, session_id, exercise_name, sets, reps, weight, completed_sets, is_completed, created_at, updated_at
            FROM workout_exercises 
            WHERE session_id = %s
            ORDER BY created_at
        """, (session_id,))
        
        exercises = cursor.fetchall()
        return [
            WorkoutExerciseResponse(
                id=ex[0],
                session_id=ex[1],
                exercise_name=ex[2],
                sets=ex[3],
                reps=ex[4],
                weight=ex[5],
                completed_sets=ex[6],
                is_completed=ex[7],
                created_at=ex[8],
                updated_at=ex[9]
            )
            for ex in exercises
        ]
