from typing import List, Dict
from app.core.config import settings

class GifService:
    def __init__(self):
        self.api_key = settings.GIPHY_API_KEY
        self.base_url = settings.GIPHY_BASE_URL

    async def search_exercise_gifs(self, exercise_name: str, limit: int = 5) -> List[Dict]:
        """Busca GIFs relacionados a um exercício específico"""
        # Por enquanto, sempre retorna GIFs mockados
        return self._get_mock_gifs(exercise_name, limit)

    async def get_trending_workout_gifs(self, limit: int = 10) -> List[Dict]:
        """Busca GIFs em tendência relacionados a treinos"""
        # Por enquanto, sempre retorna GIFs mockados
        return self._get_mock_trending_gifs(limit)

    def _get_mock_gifs(self, exercise_name: str, limit: int) -> List[Dict]:
        """Retorna GIFs mockados para desenvolvimento"""
        mock_gifs = [
            {
                "id": f"mock_{i}",
                "title": f"{exercise_name} - Exercício {i+1}",
                "url": f"https://via.placeholder.com/200x200/8b5cf6/ffffff?text={exercise_name.replace(' ', '+')}+{i+1}",
                "preview": f"https://via.placeholder.com/100x100/8b5cf6/ffffff?text={exercise_name.replace(' ', '+')}+{i+1}",
                "width": 200,
                "height": 200
            }
            for i in range(min(limit, 3))
        ]
        return mock_gifs

    def _get_mock_trending_gifs(self, limit: int) -> List[Dict]:
        """Retorna GIFs mockados em tendência"""
        trending_exercises = [
            "Flexão", "Agachamento", "Prancha", "Burpee", "Mountain Climber",
            "Jumping Jacks", "Polichinelo", "Abdominal", "Corrida", "Yoga"
        ]
        
        return [
            {
                "id": f"trending_{i}",
                "title": f"{trending_exercises[i % len(trending_exercises)]} - Treino",
                "url": f"https://via.placeholder.com/200x200/8b5cf6/ffffff?text={trending_exercises[i % len(trending_exercises)].replace(' ', '+')}",
                "preview": f"https://via.placeholder.com/100x100/8b5cf6/ffffff?text={trending_exercises[i % len(trending_exercises)].replace(' ', '+')}",
                "width": 200,
                "height": 200
            }
            for i in range(min(limit, 10))
        ]
