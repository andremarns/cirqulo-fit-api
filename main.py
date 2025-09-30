from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.database import db
from routers import auth, workouts, users, gifs

app = FastAPI(
    title="CirquloFit API",
    description="API para gamificação de treinos de academia",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar tabelas
db.init_tables()

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
