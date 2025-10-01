#!/usr/bin/env python3
"""
Script de inicialização do banco de dados
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Inicializar banco de dados"""
    print("🚀 Inicializando banco de dados CirquloFit...\n")
    
    try:
        from create_tables import create_tables, verify_tables
        
        # Criar tabelas
        if create_tables():
            print("\n✅ Tabelas criadas com sucesso!")
        else:
            print("\n❌ Falha ao criar tabelas!")
            return False
        
        # Verificar tabelas
        if verify_tables():
            print("\n✅ Verificação das tabelas concluída!")
        else:
            print("\n❌ Falha na verificação das tabelas!")
            return False
        
        print("\n🎉 Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar banco de dados: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
