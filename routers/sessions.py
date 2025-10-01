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
        """, (
            current_user.id,
            session_data.workout_id,
            started_at,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        # Buscar a sessão criada
        cursor.execute("""
            SELECT id, user_id, workout_id, started_at, completed_at, duration, xp_earned, is_completed, created_at, updated_at
            FROM workout_sessions 
            WHERE user_id = %s AND workout_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (current_user.id, session_data.workout_id))
        
        session_result = cursor.fetchone()
        if not session_result:
            raise HTTPException(
                status_code=500,
                detail="Erro ao criar sessão"
            )
        
        return WorkoutSessionResponse(
            id=session_result['id'],
            user_id=session_result['user_id'],
            workout_id=session_result['workout_id'],
            started_at=session_result['started_at'],
            completed_at=session_result['completed_at'],
            duration=session_result['duration'],
            xp_earned=session_result['xp_earned'],
            is_completed=session_result['is_completed'],
            created_at=session_result['created_at'],
            updated_at=session_result['updated_at']
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
        started_at = session['started_at']
        completed_at = datetime.utcnow()
        duration = int((completed_at - started_at).total_seconds() / 60)  # em minutos
        
        # Calcular XP baseado na duração e exercícios
        cursor.execute("""
            SELECT COUNT(*) FROM workout_exercises WHERE session_id = %s
        """, (session_id,))
        exercise_count = cursor.fetchone()['count']
        xp_earned = duration * 2 + exercise_count * 10
        
        # Atualizar sessão
        cursor.execute("""
            UPDATE workout_sessions 
            SET completed_at = %s, duration = %s, xp_earned = %s, is_completed = true, updated_at = %s
            WHERE id = %s
        """, (
            completed_at,
            duration,
            xp_earned,
            datetime.utcnow(),
            session_id
        ))
        
        # Buscar a sessão atualizada
        cursor.execute("""
            SELECT id, user_id, workout_id, started_at, completed_at, duration, xp_earned, is_completed, created_at, updated_at
            FROM workout_sessions 
            WHERE id = %s
        """, (session_id,))
        
        session_data = cursor.fetchone()
        if not session_data:
            raise HTTPException(
                status_code=500,
                detail="Erro ao atualizar sessão"
            )
        
        return WorkoutSessionResponse(
            id=session_data['id'],
            user_id=session_data['user_id'],
            workout_id=session_data['workout_id'],
            started_at=session_data['started_at'],
            completed_at=session_data['completed_at'],
            duration=session_data['duration'],
            xp_earned=session_data['xp_earned'],
            is_completed=session_data['is_completed'],
            created_at=session_data['created_at'],
            updated_at=session_data['updated_at']
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
        """, (
            session_id,
            exercise_data.exercise_name,
            exercise_data.sets,
            exercise_data.reps,
            exercise_data.weight,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        # Buscar o exercício criado
        cursor.execute("""
            SELECT id, session_id, exercise_name, sets, reps, weight, completed_sets, is_completed, created_at, updated_at
            FROM workout_exercises 
            WHERE session_id = %s AND exercise_name = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (session_id, exercise_data.exercise_name))
        
        exercise_result = cursor.fetchone()
        if not exercise_result:
            raise HTTPException(
                status_code=500,
                detail="Erro ao criar exercício"
            )
        
        return WorkoutExerciseResponse(
            id=exercise_result['id'],
            session_id=exercise_result['session_id'],
            exercise_name=exercise_result['exercise_name'],
            sets=exercise_result['sets'],
            reps=exercise_result['reps'],
            weight=exercise_result['weight'],
            completed_sets=exercise_result['completed_sets'],
            is_completed=exercise_result['is_completed'],
            created_at=exercise_result['created_at'],
            updated_at=exercise_result['updated_at']
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
        is_completed = completed_sets >= exercise['sets']  # exercise['sets'] é o número de sets
        
        cursor.execute("""
            UPDATE workout_exercises 
            SET completed_sets = %s, is_completed = %s, updated_at = %s
            WHERE id = %s
        """, (
            completed_sets,
            is_completed,
            datetime.utcnow(),
            exercise_id
        ))
        
        # Buscar o exercício atualizado
        cursor.execute("""
            SELECT id, session_id, exercise_name, sets, reps, weight, completed_sets, is_completed, created_at, updated_at
            FROM workout_exercises 
            WHERE id = %s
        """, (exercise_id,))
        
        exercise_data = cursor.fetchone()
        if not exercise_data:
            raise HTTPException(
                status_code=500,
                detail="Erro ao atualizar exercício"
            )
        
        return WorkoutExerciseResponse(
            id=exercise_data['id'],
            session_id=exercise_data['session_id'],
            exercise_name=exercise_data['exercise_name'],
            sets=exercise_data['sets'],
            reps=exercise_data['reps'],
            weight=exercise_data['weight'],
            completed_sets=exercise_data['completed_sets'],
            is_completed=exercise_data['is_completed'],
            created_at=exercise_data['created_at'],
            updated_at=exercise_data['updated_at']
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
                id=ex['id'],
                session_id=ex['session_id'],
                exercise_name=ex['exercise_name'],
                sets=ex['sets'],
                reps=ex['reps'],
                weight=ex['weight'],
                completed_sets=ex['completed_sets'],
                is_completed=ex['is_completed'],
                created_at=ex['created_at'],
                updated_at=ex['updated_at']
            )
            for ex in exercises
        ]
