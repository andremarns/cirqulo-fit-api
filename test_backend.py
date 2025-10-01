#!/usr/bin/env python3
"""
Script para testar o backend localmente
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("🔍 Testando imports...")
    
    try:
        import fastapi
        print("✅ FastAPI importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Uvicorn: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar SQLAlchemy: {e}")
        return False
    
    try:
        from jose import jwt
        print("✅ python-jose importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar python-jose: {e}")
        return False
    
    try:
        from passlib.context import CryptContext
        print("✅ passlib importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar passlib: {e}")
        return False
    
    return True

def test_app_creation():
    """Testa se a aplicação pode ser criada"""
    print("\n🔍 Testando criação da aplicação...")
    
    try:
        from main_debug import app
        print("✅ Aplicação criada com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar aplicação: {e}")
        return False

def test_endpoints():
    """Testa se os endpoints estão funcionando"""
    print("\n🔍 Testando endpoints...")
    
    try:
        from main_debug import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Testar endpoint raiz
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Endpoint raiz funcionando")
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
            return False
        
        # Testar endpoint de health
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Endpoint de health funcionando")
        else:
            print(f"❌ Endpoint de health falhou: {response.status_code}")
            return False
        
        # Testar endpoint de teste
        response = client.get("/test")
        if response.status_code == 200:
            print("✅ Endpoint de teste funcionando")
        else:
            print(f"❌ Endpoint de teste falhou: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar endpoints: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do backend CirquloFit...\n")
    
    # Testar imports
    if not test_imports():
        print("\n❌ Teste de imports falhou!")
        return False
    
    # Testar criação da aplicação
    if not test_app_creation():
        print("\n❌ Teste de criação da aplicação falhou!")
        return False
    
    # Testar endpoints
    if not test_endpoints():
        print("\n❌ Teste de endpoints falhou!")
        return False
    
    print("\n🎉 Todos os testes passaram! O backend está funcionando!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
