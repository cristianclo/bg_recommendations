"""
Feedback service for Module G - RF-RETRO-01/02/03.
Handles feedback submission, retrieval, and analytics.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from ..models.recommendation import Recommendation
from ..models.game import Game
from ..schemas.feedback import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse,
    GameFeedbackStatistics,
    FeedbackAnalytics
)
from ..core.exceptions import NotFoundException, ValidationException


class FeedbackService:
    """Service for managing feedback on recommendations (Module G)."""
    
    FEEDBACK_EDIT_DAYS = 7  # Feedback editable for 7 days (RF-RETRO-01)
    
    def submit_feedback(
        self,
        db: Session,
        recommendation_id: int,
        feedback: FeedbackCreate
    ) -> Recommendation:
        """
        Submit feedback for a recommendation (RF-RETRO-01).
        
        Args:
            db: Database session
            recommendation_id: ID of recommendation to give feedback on
            feedback: Feedback data
            
        Returns:
            Updated recommendation with feedback
            
        Raises:
            NotFoundException: If recommendation not found
            ValidationException: If feedback already exists (use update instead)
        """
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise NotFoundException("Recommendation", str(recommendation_id))
        
        # Check if feedback already exists
        if recommendation.feedback_date is not None:
            raise ValidationException(
                "Feedback already exists for this recommendation. Use update endpoint instead."
            )
        
        # Update recommendation with feedback
        now = datetime.now()
        recommendation.was_used = feedback.was_used
        recommendation.user_feedback_score = feedback.user_feedback_score
        recommendation.feedback_date = now
        recommendation.feedback_asesor = feedback.feedback_asesor
        recommendation.skill_actually_worked = feedback.skill_actually_worked
        recommendation.what_worked_well = feedback.what_worked_well
        recommendation.what_didnt_work = feedback.what_didnt_work
        recommendation.additional_notes = feedback.additional_notes
        recommendation.can_edit_until = now + timedelta(days=self.FEEDBACK_EDIT_DAYS)
        recommendation.was_selected = True  # Mark as selected if feedback given
        
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
    
    def update_feedback(
        self,
        db: Session,
        recommendation_id: int,
        feedback: FeedbackUpdate
    ) -> Recommendation:
        """
        Update existing feedback (editable for 7 days - RF-RETRO-01).
        
        Args:
            db: Database session
            recommendation_id: ID of recommendation
            feedback: Updated feedback data
            
        Returns:
            Updated recommendation
            
        Raises:
            NotFoundException: If recommendation not found
            ValidationException: If no feedback exists or edit period expired
        """
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise NotFoundException("Recommendation", str(recommendation_id))
        
        # Check if feedback exists
        if recommendation.feedback_date is None:
            raise ValidationException(
                "No feedback exists for this recommendation. Use submit endpoint instead."
            )
        
        # Check if still editable
        if recommendation.can_edit_until and datetime.now() > recommendation.can_edit_until:
            raise ValidationException(
                f"Feedback edit period expired. Feedback was editable until {recommendation.can_edit_until}."
            )
        
        # Update fields (only non-None values)
        if feedback.was_used is not None:
            recommendation.was_used = feedback.was_used
        if feedback.user_feedback_score is not None:
            recommendation.user_feedback_score = feedback.user_feedback_score
        if feedback.skill_actually_worked is not None:
            recommendation.skill_actually_worked = feedback.skill_actually_worked
        if feedback.what_worked_well is not None:
            recommendation.what_worked_well = feedback.what_worked_well
        if feedback.what_didnt_work is not None:
            recommendation.what_didnt_work = feedback.what_didnt_work
        if feedback.additional_notes is not None:
            recommendation.additional_notes = feedback.additional_notes
        
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
    
    def get_feedback(
        self,
        db: Session,
        recommendation_id: int
    ) -> FeedbackResponse:
        """
        Get feedback for a specific recommendation.
        
        Args:
            db: Database session
            recommendation_id: ID of recommendation
            
        Returns:
            Feedback response with metadata
            
        Raises:
            NotFoundException: If recommendation not found or no feedback exists
        """
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise NotFoundException("Recommendation", str(recommendation_id))
        
        if recommendation.feedback_date is None:
            raise NotFoundException("Feedback", f"for recommendation {recommendation_id}")
        
        return FeedbackResponse(
            recommendation_id=recommendation.id,
            game_id=recommendation.game_id,
            game_name=recommendation.game.name,
            session_profile_id=recommendation.session_profile_id,
            was_used=recommendation.was_used,
            user_feedback_score=recommendation.user_feedback_score,
            skill_actually_worked=recommendation.skill_actually_worked,
            what_worked_well=recommendation.what_worked_well,
            what_didnt_work=recommendation.what_didnt_work,
            additional_notes=recommendation.additional_notes,
            feedback_date=recommendation.feedback_date,
            feedback_asesor=recommendation.feedback_asesor,
            can_edit_until=recommendation.can_edit_until,
            is_editable=datetime.now() <= recommendation.can_edit_until if recommendation.can_edit_until else False
        )
    
    def get_game_feedback_statistics(
        self,
        db: Session,
        game_id: int
    ) -> GameFeedbackStatistics:
        """
        Get aggregated feedback statistics for a game (RF-RETRO-02).
        
        Args:
            db: Database session
            game_id: ID of game
            
        Returns:
            Aggregated statistics and recent feedback
            
        Raises:
            NotFoundException: If game not found
        """
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise NotFoundException("Game", str(game_id))
        
        # Get all feedback for this game
        feedback_records = db.query(Recommendation).filter(
            and_(
                Recommendation.game_id == game_id,
                Recommendation.feedback_date.isnot(None)
            )
        ).all()
        
        total_uses = len(feedback_records)
        
        # Calculate statistics
        if total_uses == 0:
            return GameFeedbackStatistics(
                game_id=game_id,
                game_name=game.name,
                total_uses=0,
                average_utility=None,
                score_distribution={},
                most_common_skill=None,
                recent_feedback=[]
            )
        
        # Average utility
        scores = [r.user_feedback_score for r in feedback_records if r.user_feedback_score]
        average_utility = sum(scores) / len(scores) if scores else None
        
        # Score distribution
        score_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for score in scores:
            score_distribution[score] = score_distribution.get(score, 0) + 1
        
        # Most common skill
        skills = [r.skill_actually_worked for r in feedback_records if r.skill_actually_worked]
        most_common_skill = max(set(skills), key=skills.count) if skills else None
        
        # Recent feedback (up to 3)
        recent = sorted(feedback_records, key=lambda x: x.feedback_date, reverse=True)[:3]
        recent_feedback = [
            FeedbackResponse(
                recommendation_id=r.id,
                game_id=r.game_id,
                game_name=game.name,
                session_profile_id=r.session_profile_id,
                was_used=r.was_used,
                user_feedback_score=r.user_feedback_score,
                skill_actually_worked=r.skill_actually_worked,
                what_worked_well=r.what_worked_well,
                what_didnt_work=r.what_didnt_work,
                additional_notes=r.additional_notes,
                feedback_date=r.feedback_date,
                feedback_asesor=r.feedback_asesor,
                can_edit_until=r.can_edit_until,
                is_editable=datetime.now() <= r.can_edit_until if r.can_edit_until else False
            )
            for r in recent
        ]
        
        return GameFeedbackStatistics(
            game_id=game_id,
            game_name=game.name,
            total_uses=total_uses,
            average_utility=average_utility,
            score_distribution=score_distribution,
            most_common_skill=most_common_skill,
            recent_feedback=recent_feedback
        )
    
    def get_system_analytics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> FeedbackAnalytics:
        """
        Get system-wide feedback analytics (RF-RETRO-03).
        
        Args:
            db: Database session
            start_date: Optional filter start date
            end_date: Optional filter end date
            
        Returns:
            System-wide analytics
        """
        # Base query
        query = db.query(Recommendation).filter(
            Recommendation.feedback_date.isnot(None)
        )
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Recommendation.feedback_date >= start_date)
        if end_date:
            query = query.filter(Recommendation.feedback_date <= end_date)
        
        all_feedback = query.all()
        
        if not all_feedback:
            return FeedbackAnalytics(
                total_feedback_count=0,
                total_games_with_feedback=0,
                average_utility_overall=0.0,
                most_used_games=[],
                highest_rated_games=[],
                underperforming_games=[],
                skills_distribution={}
            )
        
        # Total counts
        total_feedback_count = len(all_feedback)
        unique_games = set(r.game_id for r in all_feedback)
        total_games_with_feedback = len(unique_games)
        
        # Average utility
        scores = [r.user_feedback_score for r in all_feedback if r.user_feedback_score]
        average_utility_overall = sum(scores) / len(scores) if scores else 0.0
        
        # Most used games (Top 10)
        game_usage = {}
        for r in all_feedback:
            game_usage[r.game_id] = game_usage.get(r.game_id, 0) + 1
        
        most_used_games = []
        for game_id in sorted(game_usage, key=game_usage.get, reverse=True)[:10]:
            game = db.query(Game).filter(Game.id == game_id).first()
            if game:
                most_used_games.append({
                    'game_id': game_id,
                    'game_name': game.name,
                    'use_count': game_usage[game_id]
                })
        
        # Highest rated games (utility >= 4.5, >= 3 uses)
        game_ratings = {}
        for r in all_feedback:
            if r.user_feedback_score:
                if r.game_id not in game_ratings:
                    game_ratings[r.game_id] = []
                game_ratings[r.game_id].append(r.user_feedback_score)
        
        highest_rated_games = []
        for game_id, scores in game_ratings.items():
            if len(scores) >= 3:
                avg_rating = sum(scores) / len(scores)
                if avg_rating >= 4.5:
                    game = db.query(Game).filter(Game.id == game_id).first()
                    if game:
                        highest_rated_games.append({
                            'game_id': game_id,
                            'game_name': game.name,
                            'average_rating': round(avg_rating, 2),
                            'use_count': len(scores)
                        })
        
        # Underperforming games (utility < 3.0, >= 3 uses)
        underperforming_games = []
        for game_id, scores in game_ratings.items():
            if len(scores) >= 3:
                avg_rating = sum(scores) / len(scores)
                if avg_rating < 3.0:
                    game = db.query(Game).filter(Game.id == game_id).first()
                    if game:
                        underperforming_games.append({
                            'game_id': game_id,
                            'game_name': game.name,
                            'average_rating': round(avg_rating, 2),
                            'use_count': len(scores)
                        })
        
        # Skills distribution
        skills_distribution = {}
        for r in all_feedback:
            if r.skill_actually_worked:
                skills_distribution[r.skill_actually_worked] = \
                    skills_distribution.get(r.skill_actually_worked, 0) + 1
        
        return FeedbackAnalytics(
            total_feedback_count=total_feedback_count,
            total_games_with_feedback=total_games_with_feedback,
            average_utility_overall=round(average_utility_overall, 2),
            most_used_games=most_used_games,
            highest_rated_games=highest_rated_games,
            underperforming_games=underperforming_games,
            skills_distribution=skills_distribution
        )
    
    def list_feedback(
        self,
        db: Session,
        game_id: Optional[int] = None,
        asesor: Optional[str] = None,
        min_score: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[FeedbackResponse]:
        """
        List feedback with optional filters.
        
        Args:
            db: Database session
            game_id: Filter by game
            asesor: Filter by asesor name
            min_score: Filter by minimum score
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of feedback responses
        """
        query = db.query(Recommendation).filter(
            Recommendation.feedback_date.isnot(None)
        )
        
        if game_id:
            query = query.filter(Recommendation.game_id == game_id)
        if asesor:
            query = query.filter(Recommendation.feedback_asesor == asesor)
        if min_score:
            query = query.filter(Recommendation.user_feedback_score >= min_score)
        
        query = query.order_by(desc(Recommendation.feedback_date))
        feedback_records = query.offset(skip).limit(limit).all()
        
        return [
            FeedbackResponse(
                recommendation_id=r.id,
                game_id=r.game_id,
                game_name=r.game.name,
                session_profile_id=r.session_profile_id,
                was_used=r.was_used,
                user_feedback_score=r.user_feedback_score,
                skill_actually_worked=r.skill_actually_worked,
                what_worked_well=r.what_worked_well,
                what_didnt_work=r.what_didnt_work,
                additional_notes=r.additional_notes,
                feedback_date=r.feedback_date,
                feedback_asesor=r.feedback_asesor,
                can_edit_until=r.can_edit_until,
                is_editable=datetime.now() <= r.can_edit_until if r.can_edit_until else False
            )
            for r in feedback_records
        ]
