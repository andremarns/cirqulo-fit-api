from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import List

from app.infrastructure.database import db
from app.domain.entities import User
from app.application.schemas.dashboard import DashboardData, WeeklyData, CalendarData, LoadEvolutionData
from routers.auth import get_current_user

router = APIRouter(tags=["dashboard"])

@router.get("/", response_model=DashboardData)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user)
):
    """Obter dados do dashboard"""
    with db.get_cursor() as cursor:
        # Obter dados da última semana
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()
        
        # Buscar sessões da última semana
        cursor.execute("""
            SELECT DATE(started_at) as date, COUNT(*) as sessions, 
                   SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) as completed
            FROM workout_sessions 
            WHERE user_id = %s AND started_at >= %s
            GROUP BY DATE(started_at)
            ORDER BY date
        """, (current_user.id, week_start))
        
        sessions_data = cursor.fetchall()
        
        # Criar dados semanais
        week_days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        weekly_data = []
        
        for i in range(7):
            date = week_start + timedelta(days=i)
            day_sessions = next((row for row in sessions_data if row[0].date() == date.date()), (date.date(), 0, 0))
            
            weekly_data.append(WeeklyData(
                day=week_days[date.weekday()],
                sessions=day_sessions[1],
                completed=day_sessions[2] > 0,
                streak=0  # Implementar cálculo de streak se necessário
            ))
        
        # Criar dados do calendário (últimos 30 dias)
        calendar_data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            day_sessions = next((row for row in sessions_data if row[0].date() == date.date()), (date.date(), 0, 0))
            
            calendar_data.append(CalendarData(
                day=week_days[date.weekday()],
                date=date.day,
                completed=day_sessions[2] > 0,
                sessions=day_sessions[1],
                is_today=i == 29
            ))
        
        # Calcular estatísticas
        total_sessions = sum(day.sessions for day in weekly_data)
        completed_sessions = sum(1 for day in weekly_data if day.completed)
        completion_rate = (completed_sessions / 7) * 100 if weekly_data else 0
        
        # Buscar dados de evolução de carga (mock por enquanto)
        load_evolution_data = []
        
        # Obter ou criar dados de dashboard do usuário
        cursor.execute("""
            SELECT weekly_goal, total_sessions, completion_rate, streak_days
            FROM dashboard_data 
            WHERE user_id = %s
        """, (current_user.id,))
        
        dashboard_row = cursor.fetchone()
        if not dashboard_row:
            # Criar dados iniciais
            cursor.execute("""
                INSERT INTO dashboard_data (user_id, weekly_goal, total_sessions, completion_rate, streak_days, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (current_user.id, 5, total_sessions, completion_rate, 0, datetime.utcnow(), datetime.utcnow()))
            
            weekly_goal = 5
            streak_days = 0
        else:
            weekly_goal = dashboard_row[0]
            streak_days = dashboard_row[3]
        
        return DashboardData(
            weekly_data=weekly_data,
            calendar_data=calendar_data,
            load_evolution_data=load_evolution_data,
            weekly_goal=weekly_goal,
            total_sessions=total_sessions,
            completion_rate=completion_rate,
            streak_days=streak_days
        )

@router.put("/goal")
async def update_weekly_goal(
    weekly_goal: int,
    current_user: User = Depends(get_current_user)
):
    """Atualizar meta semanal"""
    if weekly_goal < 1 or weekly_goal > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meta semanal deve estar entre 1 e 20"
        )
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            UPDATE dashboard_data 
            SET weekly_goal = %s, updated_at = %s
            WHERE user_id = %s
        """, (weekly_goal, datetime.utcnow(), current_user.id))
        
        if cursor.rowcount == 0:
            # Criar se não existir
            cursor.execute("""
                INSERT INTO dashboard_data (user_id, weekly_goal, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """, (current_user.id, weekly_goal, datetime.utcnow(), datetime.utcnow()))
        
        return {"message": "Meta semanal atualizada com sucesso", "weekly_goal": weekly_goal}
