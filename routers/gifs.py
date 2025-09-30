from fastapi import APIRouter, HTTPException
from typing import List
from app.application.gif_service import GifService
from app.core.config import settings

router = APIRouter()
gif_service = GifService()

@router.get("/search")
async def search_exercise_gifs(exercise: str, limit: int = 5):
    """Busca GIFs relacionados a um exercício específico"""
    try:
        gifs = await gif_service.search_exercise_gifs(exercise, limit)
        return gifs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar GIFs: {str(e)}")

@router.get("/trending")
async def get_trending_workout_gifs(limit: int = 10):
    """Busca GIFs em tendência relacionados a treinos"""
    try:
        gifs = await gif_service.get_trending_workout_gifs(limit)
        return gifs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar GIFs em tendência: {str(e)}")
