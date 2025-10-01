from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CirquloFit API",
    description="API para gamificação de treinos de academia",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporário para teste
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers simplificados
try:
    from routers.auth_simple import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
    print("✅ Router de autenticação carregado com sucesso")
except Exception as e:
    print(f"❌ Erro ao carregar router de autenticação: {e}")

@app.get("/")
async def root():
    return {"message": "CirquloFit API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test")
async def test_endpoint():
    return {"message": "API funcionando!", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
