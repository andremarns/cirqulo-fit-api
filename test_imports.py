#!/usr/bin/env python3
"""
Script para testar imports do backend
"""

try:
    import fastapi
    print("✅ FastAPI importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar FastAPI: {e}")

try:
    import uvicorn
    print("✅ Uvicorn importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Uvicorn: {e}")

try:
    import sqlalchemy
    print("✅ SQLAlchemy importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar SQLAlchemy: {e}")

try:
    import psycopg2
    print("✅ psycopg2 importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar psycopg2: {e}")

try:
    from jose import jwt
    print("✅ python-jose importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar python-jose: {e}")

try:
    from passlib.context import CryptContext
    print("✅ passlib importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar passlib: {e}")

print("\nTeste de imports concluído!")
