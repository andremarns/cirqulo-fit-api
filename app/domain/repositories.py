from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import User, Workout, Exercise, WorkoutSession, ExerciseSet

class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass

class WorkoutRepository(ABC):
    @abstractmethod
    async def create(self, workout: Workout) -> Workout:
        pass
    
    @abstractmethod
    async def get_by_id(self, workout_id: int) -> Optional[Workout]:
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: int) -> List[Workout]:
        pass
    
    @abstractmethod
    async def update(self, workout: Workout) -> Workout:
        pass
    
    @abstractmethod
    async def delete(self, workout_id: int) -> bool:
        pass

class ExerciseRepository(ABC):
    @abstractmethod
    async def create(self, exercise: Exercise) -> Exercise:
        pass
    
    @abstractmethod
    async def get_by_id(self, exercise_id: int) -> Optional[Exercise]:
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: int) -> List[Exercise]:
        pass
    
    @abstractmethod
    async def get_by_workout(self, workout_id: int) -> List[Exercise]:
        pass

class WorkoutSessionRepository(ABC):
    @abstractmethod
    async def create(self, session: WorkoutSession) -> WorkoutSession:
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: int) -> Optional[WorkoutSession]:
        pass
    
    @abstractmethod
    async def get_by_workout(self, workout_id: int) -> List[WorkoutSession]:
        pass

class ExerciseSetRepository(ABC):
    @abstractmethod
    async def create(self, exercise_set: ExerciseSet) -> ExerciseSet:
        pass
    
    @abstractmethod
    async def get_by_session(self, session_id: int) -> List[ExerciseSet]:
        pass
