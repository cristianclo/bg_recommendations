"""
Explainability Service for Module E - RF-EXP-01, RF-EXP-02.
Handles detailed explanations and traceability of recommendations.
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime

from ..models.recommendation import Recommendation
from ..models.session import SessionProfile
from ..models.game import Game
from ..core.exceptions import NotFoundException


class ExplainabilityService:
    """
    Service for managing recommendation explanations and traceability.
    
    Implements:
    - RF-EXP-01: Detailed, natural language explanations
    - RF-EXP-02: Complete traceability of recommendation decisions
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # RF-EXP-01: Detailed Explanations
    # ========================================================================
    
    def get_recommendation_explanation(
        self,
        recommendation_id: int,
        include_technical: bool = False
    ) -> Dict:
        """
        Get detailed explanation for a specific recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            include_technical: Include technical scoring details
        
        Returns:
            Dict with structured explanation data
        
        Raises:
            NotFoundException: If recommendation not found
        """
        recommendation = self.db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise NotFoundException("Recommendation", str(recommendation_id))
        
        # Base explanation from stored text
        explanation_data = {
            "recommendation_id": recommendation.id,
            "game_id": recommendation.game_id,
            "game_name": recommendation.game.name,
            "rank": recommendation.rank,
            "total_score": recommendation.total_score,
            "explanation_text": recommendation.explanation_text,
            "match_reasons": recommendation.match_reasons or [],
            "created_at": recommendation.created_at,
        }
        
        # Add score components breakdown
        explanation_data["score_components"] = {
            "skill_score": {
                "value": recommendation.skill_score,
                "weight": recommendation.weights_used.get('skill', 0),
                "contribution": recommendation.skill_score * recommendation.weights_used.get('skill', 0),
                "description": "Alineación con habilidades objetivo"
            },
            "mechanics_score": {
                "value": recommendation.mechanics_score,
                "weight": recommendation.weights_used.get('mechanics', 0),
                "contribution": recommendation.mechanics_score * recommendation.weights_used.get('mechanics', 0),
                "description": "Similitud de mecánicas con perfil"
            },
            "difficulty_score": {
                "value": recommendation.difficulty_score,
                "weight": recommendation.weights_used.get('difficulty', 0),
                "contribution": recommendation.difficulty_score * recommendation.weights_used.get('difficulty', 0),
                "description": "Apropiación de complejidad para el contexto"
            },
            "ranking_score": {
                "value": recommendation.ranking_score,
                "weight": recommendation.weights_used.get('ranking', 0),
                "contribution": recommendation.ranking_score * recommendation.weights_used.get('ranking', 0),
                "description": "Calidad y popularidad (BGG)"
            }
        }
        
        # Add feedback boost if applicable
        if recommendation.feedback_boost and recommendation.feedback_boost > 0:
            explanation_data["score_components"]["feedback_boost"] = {
                "value": recommendation.feedback_boost,
                "weight": 1.0,  # Direct boost
                "contribution": recommendation.feedback_boost,
                "description": "Boost por retroalimentación positiva histórica"
            }
        
        # Add game context
        game = recommendation.game
        explanation_data["game_details"] = {
            "duration_min": game.duration_min,
            "complexity": game.complexity,
            "min_players": game.min_players,
            "max_players": game.max_players,
            "mechanics": game.mechanics,
            "language_dependency": game.language_dependency.value,
            "bgg_rank": game.bgg_rank,
            "year_published": game.year_published
        }
        
        # Add session context for full traceability
        session = recommendation.session_profile
        explanation_data["session_context"] = {
            "session_name": session.session_name,
            "group_size": session.group_size,
            "available_time_min": session.available_time_min,
            "objectives": session.objectives,
            "preferred_modality": session.preferred_modality.value,
            "max_language_dependency": session.max_language_dependency.value
        }
        
        # Technical details (if requested)
        if include_technical:
            explanation_data["technical_details"] = {
                "weights_configuration": recommendation.weights_used,
                "generation_timestamp": recommendation.created_at,
                "session_profile_id": recommendation.session_profile_id,
                "was_selected": recommendation.was_selected,
                "user_feedback_score": recommendation.user_feedback_score
            }
        
        return explanation_data
    
    def compare_recommendations(
        self,
        recommendation_ids: List[int]
    ) -> Dict:
        """
        Compare multiple recommendations side-by-side.
        
        Useful for understanding why one game was recommended over another.
        
        Args:
            recommendation_ids: List of 2-5 recommendation IDs to compare
        
        Returns:
            Dict with comparative analysis
        
        Raises:
            ValueError: If less than 2 or more than 5 IDs provided
            NotFoundException: If any recommendation not found
        """
        if len(recommendation_ids) < 2 or len(recommendation_ids) > 5:
            raise ValueError("Must provide between 2 and 5 recommendations to compare")
        
        recommendations = self.db.query(Recommendation).filter(
            Recommendation.id.in_(recommendation_ids)
        ).order_by(Recommendation.total_score.desc()).all()
        
        if len(recommendations) != len(recommendation_ids):
            raise NotFoundException("Recommendation", "One or more IDs not found")
        
        # Build comparison matrix
        comparison = {
            "recommendations": [],
            "score_comparison": {},
            "key_differences": []
        }
        
        for rec in recommendations:
            comparison["recommendations"].append({
                "id": rec.id,
                "game_name": rec.game.name,
                "rank": rec.rank,
                "total_score": rec.total_score,
                "skill_score": rec.skill_score,
                "mechanics_score": rec.mechanics_score,
                "difficulty_score": rec.difficulty_score,
                "ranking_score": rec.ranking_score,
                "feedback_boost": rec.feedback_boost or 0
            })
        
        # Identify key differences
        # Compare top vs others
        top_rec = recommendations[0]
        for rec in recommendations[1:]:
            score_diff = top_rec.total_score - rec.total_score
            
            # Find biggest component difference
            diffs = {
                "skill": abs(top_rec.skill_score - rec.skill_score),
                "mechanics": abs(top_rec.mechanics_score - rec.mechanics_score),
                "difficulty": abs(top_rec.difficulty_score - rec.difficulty_score),
                "ranking": abs(top_rec.ranking_score - rec.ranking_score)
            }
            
            max_diff_component = max(diffs.items(), key=lambda x: x[1])
            
            comparison["key_differences"].append({
                "comparison": f"{top_rec.game.name} vs {rec.game.name}",
                "score_difference": round(score_diff, 3),
                "main_factor": max_diff_component[0],
                "factor_difference": round(max_diff_component[1], 3),
                "explanation": self._explain_difference(
                    top_rec, rec, max_diff_component[0]
                )
            })
        
        return comparison
    
    # ========================================================================
    # RF-EXP-02: Traceability
    # ========================================================================
    
    def get_session_recommendation_history(
        self,
        session_profile_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get historical recommendations for a specific session profile.
        
        Supports RF-EXP-02: Complete traceability over time.
        
        Args:
            session_profile_id: Session profile ID
            limit: Maximum number of historical entries
        
        Returns:
            List of recommendation batches with timestamps
        """
        # Group recommendations by timestamp (same generation batch)
        recommendations = self.db.query(Recommendation).filter(
            Recommendation.session_profile_id == session_profile_id
        ).order_by(desc(Recommendation.created_at)).limit(limit * 10).all()
        
        # Group by timestamp (within 1 second = same batch)
        batches = {}
        for rec in recommendations:
            ts_key = rec.created_at.replace(microsecond=0)
            if ts_key not in batches:
                batches[ts_key] = []
            batches[ts_key].append(rec)
        
        # Format output
        history = []
        for timestamp, recs in sorted(batches.items(), reverse=True)[:limit]:
            history.append({
                "timestamp": timestamp,
                "count": len(recs),
                "recommendations": [
                    {
                        "id": rec.id,
                        "game_name": rec.game.name,
                        "rank": rec.rank,
                        "total_score": rec.total_score,
                        "was_selected": rec.was_selected
                    }
                    for rec in sorted(recs, key=lambda x: x.rank)
                ]
            })
        
        return history
    
    def get_traceability_report(
        self,
        recommendation_id: int
    ) -> Dict:
        """
        Generate complete traceability report for audit purposes.
        
        RF-EXP-02: Non-editable, complete decision trail.
        
        Args:
            recommendation_id: Recommendation ID
        
        Returns:
            Complete traceability report
        """
        rec = self.db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not rec:
            raise NotFoundException("Recommendation", str(recommendation_id))
        
        session = rec.session_profile
        game = rec.game
        
        return {
            "recommendation_id": rec.id,
            "audit_trail": {
                "generated_at": rec.created_at,
                "session_profile": {
                    "id": session.id,
                    "name": session.session_name,
                    "created_by": session.created_by_name,
                    "created_at": session.created_at,
                    "objectives": session.objectives,
                    "constraints": {
                        "group_size": session.group_size,
                        "available_time_min": session.available_time_min,
                        "max_language_dependency": session.max_language_dependency.value,
                        "preferred_modality": session.preferred_modality.value
                    }
                },
                "game_selected": {
                    "id": game.id,
                    "name": game.name,
                    "bgg_id": game.bgg_id,
                    "duration_min": game.duration_min,
                    "complexity": game.complexity,
                    "player_range": f"{game.min_players}-{game.max_players}",
                    "mechanics": game.mechanics,
                    "language_dependency": game.language_dependency.value
                },
                "scoring_configuration": {
                    "weights": rec.weights_used,
                    "score_components": {
                        "skill_score": rec.skill_score,
                        "mechanics_score": rec.mechanics_score,
                        "difficulty_score": rec.difficulty_score,
                        "ranking_score": rec.ranking_score,
                        "feedback_boost": rec.feedback_boost or 0
                    },
                    "total_score": rec.total_score
                },
                "decision_rationale": {
                    "explanation": rec.explanation_text,
                    "match_reasons": rec.match_reasons,
                    "rank_in_results": rec.rank
                },
                "outcome": {
                    "was_selected_by_user": rec.was_selected,
                    "user_feedback_score": rec.user_feedback_score,
                    "feedback_provided_at": None  # Will be updated by Module G
                }
            },
            "audit_metadata": {
                "record_created": rec.created_at,
                "record_immutable": True,
                "can_edit": False,
                "purpose": "RF-EXP-02: Complete traceability for evaluation and adjustment"
            }
        }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _explain_difference(
        self,
        rec1: Recommendation,
        rec2: Recommendation,
        component: str
    ) -> str:
        """Generate natural language explanation of score difference."""
        game1 = rec1.game.name
        game2 = rec2.game.name
        
        explanations = {
            "skill": f"{game1} tiene mejor alineación con las habilidades objetivo",
            "mechanics": f"{game1} tiene mecánicas más similares al perfil solicitado",
            "difficulty": f"{game1} tiene complejidad más apropiada para el contexto",
            "ranking": f"{game1} tiene mejor valoración en BoardGameGeek"
        }
        
        return explanations.get(component, f"{game1} supera a {game2} en este aspecto")
