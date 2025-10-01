#!/usr/bin/env python3
"""
Script para criar tabelas no banco de dados
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_tables():
    """Criar todas as tabelas necessárias"""
    print("🔍 Conectando ao banco de dados...")
    
    try:
        # Criar engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            print("✅ Conectado ao banco de dados")
            
            # Criar tabela de usuários
            print("📝 Criando tabela de usuários...")
            conn.execute(text("""
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
            """))
            conn.commit()
            print("✅ Tabela de usuários criada")
            
            # Criar tabela de treinos
            print("📝 Criando tabela de treinos...")
            conn.execute(text("""
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
            """))
            conn.commit()
            print("✅ Tabela de treinos criada")
            
            # Criar tabela de sessões de treino
            print("📝 Criando tabela de sessões de treino...")
            conn.execute(text("""
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
            """))
            conn.commit()
            print("✅ Tabela de sessões de treino criada")
            
            # Criar tabela de exercícios
            print("📝 Criando tabela de exercícios...")
            conn.execute(text("""
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
            """))
            conn.commit()
            print("✅ Tabela de exercícios criada")
            
            # Criar tabela de progresso do usuário
            print("📝 Criando tabela de progresso do usuário...")
            conn.execute(text("""
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
            """))
            conn.commit()
            print("✅ Tabela de progresso do usuário criada")
            
            print("\n🎉 Todas as tabelas foram criadas com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def verify_tables():
    """Verificar se as tabelas foram criadas"""
    print("\n🔍 Verificando tabelas criadas...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Listar todas as tabelas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            print("📋 Tabelas encontradas:")
            for table in tables:
                print(f"  ✅ {table}")
            
            expected_tables = ['users', 'workouts', 'workout_sessions', 'workout_exercises', 'user_progress']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"\n❌ Tabelas faltando: {missing_tables}")
                return False
            else:
                print("\n✅ Todas as tabelas esperadas foram criadas!")
                return True
                
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando criação de tabelas do CirquloFit...\n")
    
    # Criar tabelas
    if not create_tables():
        print("\n❌ Falha ao criar tabelas!")
        return False
    
    # Verificar tabelas
    if not verify_tables():
        print("\n❌ Falha na verificação das tabelas!")
        return False
    
    print("\n🎉 Processo concluído com sucesso!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
