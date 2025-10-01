from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.database import db
from app.core.config import settings

# Importar routers apenas se as dependências estiverem disponíveis
try:
    from routers import auth, workouts, users, gifs
    ROUTERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Routers não disponíveis: {e}")
    ROUTERS_AVAILABLE = False

app = FastAPI(
    title="CirquloFit API",
    description="API para gamificação de treinos de academia",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar tabelas
try:
    print("🔍 Inicializando banco de dados...")
    db.init_tables()
    print("✅ Banco de dados inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar banco de dados: {e}")
    print("🔧 Tentando criar tabelas com SQLAlchemy...")
    try:
        from create_tables import create_tables
        if create_tables():
            print("✅ Tabelas criadas com sucesso")
        else:
            print("❌ Falha ao criar tabelas")
    except Exception as e2:
        print(f"❌ Erro ao criar tabelas: {e2}")

# Incluir routers apenas se estiverem disponíveis
if ROUTERS_AVAILABLE:
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
    app.include_router(gifs.router, prefix="/api/gifs", tags=["gifs"])

@app.get("/")
async def root():
    return {"message": "CirquloFit API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/db-status")
async def database_status():
    """Endpoint para verificar status do banco de dados"""
    try:
        from app.infrastructure.database import db
        from sqlalchemy import create_engine, text
        from app.core.config import settings
        
        # Testar conexão
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Verificar se as tabelas existem
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            return {
                "status": "connected",
                "tables": tables,
                "table_count": len(tables),
                "has_users_table": "users" in tables
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "tables": [],
            "table_count": 0,
            "has_users_table": False
        }
