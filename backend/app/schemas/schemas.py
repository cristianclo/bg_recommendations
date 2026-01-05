from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Game Schemas
class GameBase(BaseModel):
    name: str
    description: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    min_age: Optional[int] = None
    duration_minutes: Optional[int] = None
    complexity: Optional[float] = Field(None, ge=1.0, le=5.0)
    year_published: Optional[int] = None
    image_url: Optional[str] = None

class GameCreate(GameBase):
    pass

class GameResponse(GameBase):
    id: int
    is_active: bool
    created_at: datetime
    categories: List[str] = []
    mechanics: List[str] = []

    class Config:
        from_attributes = True

# Rating Schemas
class RatingBase(BaseModel):
    game_id: int
    rating: float = Field(..., ge=1.0, le=10.0)
    review: Optional[str] = None

class RatingCreate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    game_id: int
    game_name: str
    score: float
    explanation: str
    algorithm_used: str
    created_at: datetime

    class Config:
        from_attributes = True

# Feedback Schemas
class FeedbackCreate(BaseModel):
    recommendation_id: int
    was_useful: bool
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    recommendation_id: int
    was_useful: bool
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
