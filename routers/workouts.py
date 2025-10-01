from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import db
from app.domain.entities import User
from app.application.schemas.workout import (
    WorkoutCreate, WorkoutResponse, WeeklyProgressResponse,
    WorkoutStatsResponse
)
from routers.auth import get_current_user

router = APIRouter(tags=["workouts"])

@router.get("/", response_model=List[WorkoutResponse])
async def get_workouts(
    level: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Buscar treinos do usuário"""
    with db.get_cursor() as cursor:
        query = "SELECT * FROM workouts WHERE user_id = %s"
        params = [current_user.id]
        
        if level:
            query += " AND level = %s"
            params.append(level)
            
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        workouts = cursor.fetchall()
        
        return [
            WorkoutResponse(
                id=workout[0],
                name=workout[1],
                description=workout[2],
                category=workout[3],
                level=workout[4],
                duration=workout[5],
                exercises_count=workout[6],
                xp_reward=workout[7],
                user_id=workout[8],
                is_active=workout[9],
                created_at=workout[10],
                updated_at=workout[11]
            )
            for workout in workouts
        ]

@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout: WorkoutCreate,
    current_user: User = Depends(get_current_user)
):
    """Criar novo treino"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO workouts (name, description, category, level, duration, exercises_count, xp_reward, user_id, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, description, category, level, duration, exercises_count, xp_reward, user_id, is_active, created_at, updated_at
        """, (
            workout.name,
            workout.description,
            workout.category,
            workout.level,
            workout.duration,
            workout.exercises_count,
            workout.xp_reward,
            current_user.id,
            True,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        workout_data = cursor.fetchone()
        return WorkoutResponse(
            id=workout_data[0],
            name=workout_data[1],
            description=workout_data[2],
            category=workout_data[3],
            level=workout_data[4],
            duration=workout_data[5],
            exercises_count=workout_data[6],
            xp_reward=workout_data[7],
            user_id=workout_data[8],
            is_active=workout_data[9],
            created_at=workout_data[10],
            updated_at=workout_data[11]
        )

@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user)
):
    """Buscar treino específico"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM workouts WHERE id = %s AND user_id = %s
        """, (workout_id, current_user.id))
        
        workout = cursor.fetchone()
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treino não encontrado"
            )
        
        return WorkoutResponse(
            id=workout[0],
            name=workout[1],
            description=workout[2],
            category=workout[3],
            level=workout[4],
            duration=workout[5],
            exercises_count=workout[6],
            xp_reward=workout[7],
            user_id=workout[8],
            is_active=workout[9],
            created_at=workout[10],
            updated_at=workout[11]
        )

@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout: WorkoutCreate,
    current_user: User = Depends(get_current_user)
):
    """Atualizar treino"""
    with db.get_cursor() as cursor:
        # Verificar se o treino existe e pertence ao usuário
        cursor.execute("""
            SELECT id FROM workouts WHERE id = %s AND user_id = %s
        """, (workout_id, current_user.id))
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treino não encontrado"
            )
        
        # Atualizar treino
        cursor.execute("""
            UPDATE workouts 
            SET name = %s, description = %s, category = %s, level = %s, 
                duration = %s, exercises_count = %s, xp_reward = %s, updated_at = %s
            WHERE id = %s AND user_id = %s
            RETURNING id, name, description, category, level, duration, exercises_count, xp_reward, user_id, is_active, created_at, updated_at
        """, (
            workout.name,
            workout.description,
            workout.category,
            workout.level,
            workout.duration,
            workout.exercises_count,
            workout.xp_reward,
            datetime.utcnow(),
            workout_id,
            current_user.id
        ))
        
        workout_data = cursor.fetchone()
        return WorkoutResponse(
            id=workout_data[0],
            name=workout_data[1],
            description=workout_data[2],
            category=workout_data[3],
            level=workout_data[4],
            duration=workout_data[5],
            exercises_count=workout_data[6],
            xp_reward=workout_data[7],
            user_id=workout_data[8],
            is_active=workout_data[9],
            created_at=workout_data[10],
            updated_at=workout_data[11]
        )

@router.delete("/{workout_id}")
async def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user)
):
    """Deletar treino"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            DELETE FROM workouts WHERE id = %s AND user_id = %s
        """, (workout_id, current_user.id))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treino não encontrado"
            )
        
        return {"message": "Treino deletado com sucesso"}

@router.get("/stats/summary", response_model=WorkoutStatsResponse)
async def get_workout_stats(
    current_user: User = Depends(get_current_user)
):
    """Obter estatísticas de treinos"""
    with db.get_cursor() as cursor:
        # Total de treinos
        cursor.execute("""
            SELECT COUNT(*) FROM workouts WHERE user_id = %s
        """, (current_user.id,))
        total_workouts = cursor.fetchone()[0]
        
        # Treinos ativos
        cursor.execute("""
            SELECT COUNT(*) FROM workouts WHERE user_id = %s AND is_active = true
        """, (current_user.id,))
        active_workouts = cursor.fetchone()[0]
        
        # XP total
        cursor.execute("""
            SELECT COALESCE(SUM(xp_reward), 0) FROM workouts WHERE user_id = %s
        """, (current_user.id,))
        total_xp = cursor.fetchone()[0]
        
        return WorkoutStatsResponse(
            total_workouts=total_workouts,
            total_exercises=0,  # Implementar se necessário
            total_xp=total_xp,
            current_streak=0,  # Implementar se necessário
            longest_streak=0,  # Implementar se necessário
            level=1,  # Implementar se necessário
            level_progress=0.0,  # Implementar se necessário
            achievements_unlocked=0  # Implementar se necessário
        )

@router.get("/progress/weekly", response_model=WeeklyProgressResponse)
async def get_weekly_progress(
    current_user: User = Depends(get_current_user)
):
    """Obter progresso semanal"""
    with db.get_cursor() as cursor:
        # Buscar treinos da última semana
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count, SUM(xp_reward) as xp
            FROM workouts 
            WHERE user_id = %s AND created_at >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (current_user.id,))
        
        progress_data = cursor.fetchall()
        
        from datetime import datetime, timedelta
        
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()
        
        total_sessions = sum(row[1] for row in progress_data)
        total_xp = sum(row[2] or 0 for row in progress_data)
        
        return WeeklyProgressResponse(
            week_start=week_start,
            week_end=week_end,
            total_sessions=total_sessions,
            completed_sessions=total_sessions,  # Assumindo que todos foram completados
            total_xp=total_xp,
            current_streak=0,  # Implementar se necessário
            level=1,  # Implementar se necessário
            daily_progress=[
                {
                    "date": str(row[0]),
                    "workouts": row[1],
                    "xp_earned": row[2] or 0
                }
                for row in progress_data
            ]
        )