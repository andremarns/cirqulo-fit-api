from datetime import datetime, timedelta
from typing import List
from app.application.schemas.dashboard import DashboardData, WeeklyData, CalendarData, LoadEvolutionData
from app.application.workout_service import WorkoutService
from app.infrastructure.database import Database

class DashboardService:
    def __init__(self, db: Database):
        self.db = db
        self.workout_service = WorkoutService(db)

    def get_dashboard_data(self, user_id: int) -> DashboardData:
        """Buscar todos os dados do dashboard"""
        today = datetime.utcnow()
        
        with self.db.get_cursor() as cursor:
            # Dados semanais
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            cursor.execute("""
                SELECT * FROM workout_sessions 
                WHERE user_id = %s AND started_at >= %s AND started_at <= %s
            """, (user_id, week_start, week_end))
            sessions = cursor.fetchall()
            
            # Organizar por dia da semana
            days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
            weekly_data = []
            
            for i, day_name in enumerate(days):
                day_date = week_start + timedelta(days=i)
                day_sessions = [s for s in sessions if s['started_at'].date() == day_date.date()]
                completed_sessions = [s for s in day_sessions if s['is_completed']]
                
                weekly_data.append(WeeklyData(
                    day=day_name,
                    sessions=len(day_sessions),
                    completed=len(completed_sessions) > 0,
                    streak=len(completed_sessions)
                ))
            
            # Dados do calendário (últimos 7 dias)
            start_date = today - timedelta(days=6)
            end_date = today
            
            cursor.execute("""
                SELECT * FROM workout_sessions 
                WHERE user_id = %s AND started_at >= %s AND started_at <= %s
            """, (user_id, start_date, end_date))
            calendar_sessions = cursor.fetchall()
            
            calendar_data = []
            for i in range(7):
                day_date = start_date + timedelta(days=i)
                day_sessions = [s for s in calendar_sessions if s['started_at'].date() == day_date.date()]
                completed_sessions = [s for s in day_sessions if s['is_completed']]
                
                calendar_data.append(CalendarData(
                    day=days[day_date.weekday()],
                    date=day_date.day,
                    completed=len(completed_sessions) > 0,
                    sessions=len(day_sessions),
                    is_today=day_date.date() == today.date()
                ))
            
            # Dados de evolução de carga (últimos 30 dias)
            load_start_date = today - timedelta(days=30)
            cursor.execute("""
                SELECT we.*, ws.started_at 
                FROM workout_exercises we
                JOIN workout_sessions ws ON we.session_id = ws.id
                WHERE ws.user_id = %s AND ws.started_at >= %s AND we.is_completed = TRUE
                ORDER BY ws.started_at
            """, (user_id, load_start_date))
            exercises = cursor.fetchall()
            
            load_evolution_data = []
            for exercise in exercises:
                load_evolution_data.append(LoadEvolutionData(
                    date=exercise['started_at'].strftime('%d/%m'),
                    weight=exercise['weight'],
                    reps=exercise['reps'],
                    exercise=exercise['exercise_name']
                ))
            
            # Calcular métricas
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s['is_completed']])
            weekly_goal = 3
            completion_rate = (completed_sessions / weekly_goal * 100) if weekly_goal > 0 else 0
            streak_days = len([day for day in weekly_data if day.completed])
            
            return DashboardData(
                weekly_data=weekly_data,
                calendar_data=calendar_data,
                load_evolution_data=load_evolution_data,
                weekly_goal=weekly_goal,
                total_sessions=total_sessions,
                completion_rate=completion_rate,
                streak_days=streak_days
            )

