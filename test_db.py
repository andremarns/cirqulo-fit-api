#!/usr/bin/env python3
"""
Script para testar conexão com o banco de dados
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Testar conexão com o banco de dados"""
    print("🔍 Testando conexão com o banco de dados...")
    
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine, text
        
        print(f"📡 DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        
        # Criar engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            print("✅ Conectado ao banco de dados")
            
            # Testar query simples
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ Query de teste executada com sucesso")
            else:
                print("❌ Query de teste falhou")
                return False
            
            # Verificar se as tabelas existem
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            print(f"📋 Tabelas encontradas: {tables}")
            
            if 'users' in tables:
                print("✅ Tabela 'users' encontrada")
            else:
                print("❌ Tabela 'users' não encontrada")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        return False

def test_user_creation():
    """Testar criação de usuário"""
    print("\n🔍 Testando criação de usuário...")
    
    try:
        from app.infrastructure.database import db
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Dados de teste
        test_email = "teste@example.com"
        test_password = "123456"
        hashed_password = pwd_context.hash(test_password)
        
        with db.get_cursor() as cursor:
            # Verificar se usuário já existe
            cursor.execute("SELECT id FROM users WHERE email = %s", (test_email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                print("ℹ️ Usuário de teste já existe, removendo...")
                cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
            
            # Criar usuário de teste
            cursor.execute("""
                INSERT INTO users (name, email, hashed_password, gender, is_active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, ("Usuário Teste", test_email, hashed_password, "male", True))
            
            user_id = cursor.fetchone()[0]
            print(f"✅ Usuário de teste criado com ID: {user_id}")
            
            # Verificar se foi criado corretamente
            cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if user:
                print(f"✅ Usuário verificado: {user}")
                return True
            else:
                print("❌ Falha ao verificar usuário criado")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar criação de usuário: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes do banco de dados...\n")
    
    # Testar conexão
    if not test_database_connection():
        print("\n❌ Teste de conexão falhou!")
        return False
    
    # Testar criação de usuário
    if not test_user_creation():
        print("\n❌ Teste de criação de usuário falhou!")
        return False
    
    print("\n🎉 Todos os testes do banco de dados passaram!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
