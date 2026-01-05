from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Many-to-many relationship tables
game_categories = Table(
    'game_categories',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

game_mechanics = Table(
    'game_mechanics',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id'), primary_key=True),
    Column('mechanic_id', Integer, ForeignKey('mechanics.id'), primary_key=True)
)

class User(Base):
    """User model for pedagogical advisors"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ratings = relationship("Rating", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")

class Game(Base):
    """Board game model"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    min_players = Column(Integer)
    max_players = Column(Integer)
    min_age = Column(Integer)
    duration_minutes = Column(Integer)
    complexity = Column(Float)  # 1-5 scale
    year_published = Column(Integer)
    image_url = Column(String)
    bgg_id = Column(Integer, unique=True)  # BoardGameGeek ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("Category", secondary=game_categories, back_populates="games")
    mechanics = relationship("Mechanic", secondary=game_mechanics, back_populates="games")
    ratings = relationship("Rating", back_populates="game")

class Category(Base):
    """Game category (e.g., Strategy, Family, Party)"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)

    # Relationships
    games = relationship("Game", secondary=game_categories, back_populates="categories")

class Mechanic(Base):
    """Game mechanic (e.g., Deck Building, Worker Placement)"""
    __tablename__ = "mechanics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)

    # Relationships
    games = relationship("Game", secondary=game_mechanics, back_populates="mechanics")

class Rating(Base):
    """User ratings for games"""
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1-10 scale
    review = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="ratings")
    game = relationship("Game", back_populates="ratings")

class Recommendation(Base):
    """Recommendation history and explanations"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    score = Column(Float, nullable=False)  # Recommendation score
    explanation = Column(Text)  # Why this game was recommended
    algorithm_used = Column(String)  # collaborative, content-based, hybrid, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    game = relationship("Game")

class Feedback(Base):
    """User feedback on recommendations (feedback loop)"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    was_useful = Column(Boolean, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    recommendation = relationship("Recommendation")
