import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from urllib.parse import urlparse
from app.core.config import settings

class Database:
    def __init__(self):
        # Parse da DATABASE_URL para extrair parâmetros de conexão
        parsed_url = urlparse(settings.DATABASE_URL)
        self.connection_params = {
            'host': parsed_url.hostname,
            'port': parsed_url.port or 5432,
            'database': parsed_url.path[1:],  # Remove a barra inicial
            'user': parsed_url.username,
            'password': parsed_url.password
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão com o banco"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self):
        """Context manager para cursor do banco"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def init_tables(self):
        """Criar tabelas se não existirem"""
        with self.get_cursor() as cursor:
            # Tabela de usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    gender VARCHAR(20) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Adicionar coluna updated_at se não existir
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            
            # Tabela de treinos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    category VARCHAR(50) NOT NULL,
                    level INTEGER NOT NULL DEFAULT 1,
                    duration INTEGER,
                    exercises_count INTEGER DEFAULT 0,
                    xp_reward INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de sessões de treino
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workout_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    workout_id INTEGER REFERENCES workouts(id),
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    duration INTEGER,
                    xp_earned INTEGER DEFAULT 0,
                    is_completed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Tabela de exercícios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workout_exercises (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES workout_sessions(id),
                    exercise_name VARCHAR(255) NOT NULL,
                    sets INTEGER NOT NULL,
                    reps INTEGER NOT NULL,
                    weight INTEGER DEFAULT 0,
                    completed_sets INTEGER DEFAULT 0,
                    is_completed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Tabela de progresso do usuário
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    date TIMESTAMP NOT NULL,
                    total_workouts INTEGER DEFAULT 0,
                    total_exercises INTEGER DEFAULT 0,
                    total_xp INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1
                )
            """)
            
            # Tabela de sessões de treino
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workout_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    workout_id INTEGER REFERENCES workouts(id),
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration INTEGER,
                    xp_earned INTEGER DEFAULT 0,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de exercícios da sessão
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workout_exercises (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES workout_sessions(id),
                    exercise_name VARCHAR(255) NOT NULL,
                    sets INTEGER NOT NULL,
                    reps INTEGER NOT NULL,
                    weight DECIMAL(5,2) DEFAULT 0,
                    completed_sets INTEGER DEFAULT 0,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de dashboard data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_data (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    weekly_goal INTEGER DEFAULT 5,
                    total_sessions INTEGER DEFAULT 0,
                    completion_rate DECIMAL(5,2) DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

# Instância global do database
db = Database()
