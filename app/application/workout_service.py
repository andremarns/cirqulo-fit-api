from datetime import datetime, timedelta
from typing import List, Optional
from app.domain.entities import Workout, WorkoutSession, WorkoutExercise, UserProgress
from app.application.schemas.workout import (
    WorkoutCreate, WorkoutSessionCreate, WorkoutExerciseCreate,
    UserProgressCreate, WeeklyProgressResponse, WorkoutStatsResponse
)
from app.infrastructure.database import Database

class WorkoutService:
    def __init__(self, db: Database):
        self.db = db

    def create_workout(self, user_id: int, workout_data: WorkoutCreate) -> Workout:
        """Criar um novo treino"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO workouts (user_id, name, description, category, level, duration, exercises_count, xp_reward)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                user_id, workout_data.name, workout_data.description, workout_data.category,
                workout_data.level, workout_data.duration, workout_data.exercises_count, workout_data.xp_reward
            ))
            result = cursor.fetchone()
            
            return Workout(
                id=result['id'],
                user_id=user_id,
                name=workout_data.name,
                description=workout_data.description,
                category=workout_data.category,
                level=workout_data.level,
                duration=workout_data.duration,
                exercises_count=workout_data.exercises_count,
                xp_reward=workout_data.xp_reward,
                is_active=True,
                created_at=result['created_at']
            )

    def get_user_workouts(self, user_id: int, level: Optional[int] = None) -> List[Workout]:
        """Buscar treinos do usuário"""
        with self.db.get_cursor() as cursor:
            if level:
                cursor.execute("""
                    SELECT * FROM workouts 
                    WHERE user_id = %s AND is_active = TRUE AND level <= %s
                    ORDER BY created_at DESC
                """, (user_id, level))
            else:
                cursor.execute("""
                    SELECT * FROM workouts 
                    WHERE user_id = %s AND is_active = TRUE
                    ORDER BY created_at DESC
                """, (user_id,))
            
            results = cursor.fetchall()
            return [
                Workout(
                    id=row['id'],
                    user_id=row['user_id'],
                    name=row['name'],
                    description=row['description'],
                    category=row['category'],
                    level=row['level'],
                    duration=row['duration'],
                    exercises_count=row['exercises_count'],
                    xp_reward=row['xp_reward'],
                    is_active=row['is_active'],
                    created_at=row['created_at']
                )
                for row in results
            ]

    def start_workout_session(self, user_id: int, session_data: WorkoutSessionCreate) -> WorkoutSession:
        """Iniciar uma sessão de treino"""
        with self.db.get_cursor() as cursor:
            started_at = session_data.started_at or datetime.utcnow()
            cursor.execute("""
                INSERT INTO workout_sessions (user_id, workout_id, started_at, duration, xp_earned, is_completed)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_id, session_data.workout_id, started_at, session_data.duration,
                session_data.xp_earned, session_data.is_completed
            ))
            result = cursor.fetchone()
            
            return WorkoutSession(
                id=result['id'],
                user_id=user_id,
                workout_id=session_data.workout_id,
                started_at=started_at,
                duration=session_data.duration,
                xp_earned=session_data.xp_earned,
                is_completed=session_data.is_completed
            )

    def complete_workout_session(self, session_id: int, user_id: int) -> WorkoutSession:
        """Completar uma sessão de treino"""
        with self.db.get_cursor() as cursor:
            completed_at = datetime.utcnow()
            
            # Buscar sessão atual
            cursor.execute("""
                SELECT * FROM workout_sessions 
                WHERE id = %s AND user_id = %s
            """, (session_id, user_id))
            session = cursor.fetchone()
            
            if not session:
                raise ValueError("Sessão não encontrada")
            
            # Calcular duração
            duration = int((completed_at - session['started_at']).total_seconds() / 60)
            
            # Calcular XP (base + duração)
            xp_earned = 10 + (duration * 2) + 50  # 10 base + 2 por minuto + 50 por completar
            
            # Atualizar sessão
            cursor.execute("""
                UPDATE workout_sessions 
                SET completed_at = %s, duration = %s, xp_earned = %s, is_completed = TRUE
                WHERE id = %s
            """, (completed_at, duration, xp_earned, session_id))
            
            # Atualizar progresso do usuário
            self._update_user_progress(user_id, xp_earned)
            
            return WorkoutSession(
                id=session_id,
                user_id=user_id,
                workout_id=session['workout_id'],
                started_at=session['started_at'],
                completed_at=completed_at,
                duration=duration,
                xp_earned=xp_earned,
                is_completed=True
            )

    def add_exercise_to_session(self, session_id: int, exercise_data: WorkoutExerciseCreate) -> WorkoutExercise:
        """Adicionar exercício à sessão"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO workout_exercises (session_id, exercise_name, sets, reps, weight, completed_sets, is_completed)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session_id, exercise_data.exercise_name, exercise_data.sets, exercise_data.reps,
                exercise_data.weight, exercise_data.completed_sets, exercise_data.is_completed
            ))
            result = cursor.fetchone()
            
            return WorkoutExercise(
                id=result['id'],
                session_id=session_id,
                exercise_name=exercise_data.exercise_name,
                sets=exercise_data.sets,
                reps=exercise_data.reps,
                weight=exercise_data.weight,
                completed_sets=exercise_data.completed_sets,
                is_completed=exercise_data.is_completed
            )

    def update_exercise_progress(self, exercise_id: int, completed_sets: int) -> WorkoutExercise:
        """Atualizar progresso do exercício"""
        with self.db.get_cursor() as cursor:
            # Buscar exercício atual
            cursor.execute("""
                SELECT * FROM workout_exercises WHERE id = %s
            """, (exercise_id,))
            exercise = cursor.fetchone()
            
            if not exercise:
                raise ValueError("Exercício não encontrado")
            
            is_completed = completed_sets >= exercise['sets']
            
            # Atualizar exercício
            cursor.execute("""
                UPDATE workout_exercises 
                SET completed_sets = %s, is_completed = %s
                WHERE id = %s
            """, (completed_sets, is_completed, exercise_id))
            
            return WorkoutExercise(
                id=exercise_id,
                session_id=exercise['session_id'],
                exercise_name=exercise['exercise_name'],
                sets=exercise['sets'],
                reps=exercise['reps'],
                weight=exercise['weight'],
                completed_sets=completed_sets,
                is_completed=is_completed
            )

    def get_user_progress(self, user_id: int) -> UserProgress:
        """Buscar progresso do usuário"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM user_progress 
                WHERE user_id = %s 
                ORDER BY date DESC 
                LIMIT 1
            """, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                # Criar progresso inicial
                cursor.execute("""
                    INSERT INTO user_progress (user_id, date, total_workouts, total_exercises, total_xp, current_streak, longest_streak, level)
                    VALUES (%s, %s, 0, 0, 0, 0, 0, 1)
                    RETURNING *
                """, (user_id, datetime.utcnow()))
                result = cursor.fetchone()
            
            return UserProgress(
                id=result['id'],
                user_id=result['user_id'],
                date=result['date'],
                total_workouts=result['total_workouts'],
                total_exercises=result['total_exercises'],
                total_xp=result['total_xp'],
                current_streak=result['current_streak'],
                longest_streak=result['longest_streak'],
                level=result['level']
            )

    def get_weekly_progress(self, user_id: int) -> WeeklyProgressResponse:
        """Buscar progresso semanal"""
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        with self.db.get_cursor() as cursor:
            # Buscar sessões da semana
            cursor.execute("""
                SELECT * FROM workout_sessions 
                WHERE user_id = %s AND started_at >= %s AND started_at <= %s
            """, (user_id, week_start, week_end))
            sessions = cursor.fetchall()
            
            # Buscar progresso atual
            progress = self.get_user_progress(user_id)
            
            # Preparar dados diários
            daily_progress = []
            for i in range(7):
                day = week_start + timedelta(days=i)
                day_sessions = [s for s in sessions if s['started_at'].date() == day.date()]
                daily_progress.append({
                    'date': day.date(),
                    'sessions': len(day_sessions),
                    'completed': len([s for s in day_sessions if s['is_completed']]),
                    'xp_earned': sum(s['xp_earned'] for s in day_sessions if s['is_completed'])
                })
            
            return WeeklyProgressResponse(
                week_start=week_start,
                week_end=week_end,
                total_sessions=len(sessions),
                completed_sessions=len([s for s in sessions if s['is_completed']]),
                total_xp=sum(s['xp_earned'] for s in sessions if s['is_completed']),
                current_streak=progress.current_streak,
                level=progress.level,
                daily_progress=daily_progress
            )

    def get_workout_stats(self, user_id: int) -> WorkoutStatsResponse:
        """Buscar estatísticas de treino"""
        progress = self.get_user_progress(user_id)
        
        # Calcular progresso do nível (cada nível = 5 treinos)
        level_progress = (progress.total_workouts % 5) / 5 * 100
        
        return WorkoutStatsResponse(
            total_workouts=progress.total_workouts,
            total_exercises=progress.total_exercises,
            total_xp=progress.total_xp,
            current_streak=progress.current_streak,
            longest_streak=progress.longest_streak,
            level=progress.level,
            level_progress=level_progress,
            achievements_unlocked=0
        )
    
    def _update_user_progress(self, user_id: int, xp_earned: int):
        """Atualizar progresso do usuário"""
        with self.db.get_cursor() as cursor:
            # Buscar progresso atual
            cursor.execute("""
                SELECT * FROM user_progress 
                WHERE user_id = %s 
                ORDER BY date DESC 
                LIMIT 1
            """, (user_id,))
            progress = cursor.fetchone()
            
            if not progress:
                # Criar progresso inicial
                cursor.execute("""
                    INSERT INTO user_progress (user_id, date, total_workouts, total_exercises, total_xp, current_streak, longest_streak, level)
                    VALUES (%s, %s, 1, 0, %s, 1, 1, 1)
                """, (user_id, datetime.utcnow(), xp_earned))
            else:
                # Atualizar progresso
                new_total_workouts = progress['total_workouts'] + 1
                new_total_xp = progress['total_xp'] + xp_earned
                new_current_streak = progress['current_streak'] + 1
                new_longest_streak = max(progress['longest_streak'], new_current_streak)
                new_level = (new_total_workouts // 5) + 1
                
                cursor.execute("""
                    UPDATE user_progress 
                    SET total_workouts = %s, total_xp = %s, current_streak = %s, 
                        longest_streak = %s, level = %s, date = %s
                    WHERE id = %s
                """, (new_total_workouts, new_total_xp, new_current_streak, 
                      new_longest_streak, new_level, datetime.utcnow(), progress['id']))

