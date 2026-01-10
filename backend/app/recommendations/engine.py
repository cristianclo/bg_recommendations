"""
Recommendation engine service.
Implements RF-REC-01, RF-REC-02, RF-REC-03 requirements.
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone
import math

from ..models.game import Game, LanguageDependency
from ..models.session import SessionProfile
from ..models.recommendation import Recommendation, ScoringConfig
from ..schemas.recommendation import (
    RecommendationCreate,
    RecommendationResponse,
    Recommendation as RecommendationSchema,
    ScoringConfig as ScoringConfigSchema
)
from ..core.exceptions import NotFoundException


class RecommendationEngine:
    """
    Main recommendation engine implementing scoring algorithm.
    
    RF-REC-01: Generate top-N recommendations with traceability
    RF-REC-02: Use configurable weights
    RF-REC-03: Handle no results with relaxation suggestions
    """
    
    # Hard filter thresholds
    MIN_DURATION_BUFFER = 0.8  # Game can be 20% shorter than available time
    MAX_DURATION_BUFFER = 1.2  # Game can be 20% longer if session allows
    
    # Language dependency hierarchy for filtering
    LANGUAGE_HIERARCHY = {
        LanguageDependency.NINGUNA: 0,
        LanguageDependency.BAJA: 1,
        LanguageDependency.MEDIA: 2,
        LanguageDependency.ALTA: 3,
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Main Generation Method (RF-REC-01)
    # ========================================================================
    
    def generate_recommendations(
        self,
        session_profile_id: int,
        top_n: int = 10,
        config_id: Optional[int] = None,
        include_explanations: bool = True
    ) -> RecommendationResponse:
        """
        Generate top-N game recommendations for a session profile.
        
        Args:
            session_profile_id: Session to generate recommendations for
            top_n: Number of recommendations to return (1-50)
            config_id: Specific scoring config to use (None = active config)
            include_explanations: Generate human-readable explanations
        
        Returns:
            RecommendationResponse with ranked recommendations
        
        Raises:
            NotFoundException: If session or config not found
        """
        # Load session profile
        session = self.db.query(SessionProfile).filter(
            SessionProfile.id == session_profile_id
        ).first()
        
        if not session:
            raise NotFoundException("SessionProfile", str(session_profile_id))
        
        # Load scoring configuration (RF-REC-02)
        config = self._get_scoring_config(config_id)
        
        # Step 1: Apply hard filters to get candidates
        candidates = self._apply_hard_filters(session)
        
        # RF-REC-03: Handle no results
        if not candidates:
            return self._handle_no_results(session, config)
        
        # Step 2: Score each candidate
        scored_games = []
        for game in candidates:
            scores = self._calculate_scores(game, session)
            total_score = self._apply_weights(scores, config)
            
            scored_games.append({
                'game': game,
                'total_score': total_score,
                **scores
            })
        
        # Step 3: Sort by total score and take top-N
        scored_games.sort(key=lambda x: x['total_score'], reverse=True)
        top_games = scored_games[:top_n]
        
        # Step 4: Create recommendation records
        recommendations = []
        for rank, item in enumerate(top_games, start=1):
            explanation = None
            match_reasons = None
            
            if include_explanations:
                explanation = self._generate_explanation(item, session)
                match_reasons = self._generate_match_reasons(item, session)
            
            rec_create = RecommendationCreate(
                session_profile_id=session_profile_id,
                game_id=item['game'].id,
                rank=rank,
                total_score=item['total_score'],
                skill_score=item['skill_score'],
                mechanics_score=item['mechanics_score'],
                difficulty_score=item['difficulty_score'],
                ranking_score=item['ranking_score'],
                feedback_boost=item.get('feedback_boost', 0.0),
                weights_used=config.get_weights_dict(),
                explanation_text=explanation,
                match_reasons=match_reasons,
                was_selected=False
            )
            
            # Save to database for traceability (RF-REC-01, RF-EXP-02)
            rec = Recommendation(**rec_create.model_dump())
            self.db.add(rec)
            recommendations.append(rec)
        
        self.db.commit()
        
        # Update session flag
        session.has_recommendations = True
        self.db.commit()
        
        # Convert SQLAlchemy objects to Pydantic schemas
        # We need to expunge objects to avoid lazy loading the game relationship
        recommendation_schemas = []
        for rec in recommendations:
            # Create dict manually to avoid lazy loading relationships
            rec_dict = {
                'id': rec.id,
                'session_profile_id': rec.session_profile_id,
                'game_id': rec.game_id,
                'rank': rec.rank,
                'total_score': rec.total_score,
                'skill_score': rec.skill_score,
                'mechanics_score': rec.mechanics_score,
                'difficulty_score': rec.difficulty_score,
                'ranking_score': rec.ranking_score,
                'feedback_boost': rec.feedback_boost,
                'weights_used': rec.weights_used,
                'explanation_text': rec.explanation_text,
                'match_reasons': rec.match_reasons,
                'was_selected': rec.was_selected,
                'user_feedback_score': rec.user_feedback_score,
                'created_at': rec.created_at,
                'game': None  # Explicitly set to None to avoid serialization issues
            }
            recommendation_schemas.append(RecommendationSchema(**rec_dict))
        
        # Build response
        return RecommendationResponse(
            session_profile_id=session_profile_id,
            recommendations=recommendation_schemas,
            total_candidates=len(candidates),
            scoring_config_used=ScoringConfigSchema.model_validate(config),
            generation_timestamp=datetime.now(timezone.utc),
            has_results=True,
            relaxation_suggestions=None
        )
    
    # ========================================================================
    # Hard Filters (RF-REC-01)
    # ========================================================================
    
    def _apply_hard_filters(self, session: SessionProfile) -> List[Game]:
        """
        Apply hard constraints to filter candidate games.
        
        Filters:
        - Available in CJEI catalog
        - Supports player count
        - Fits time constraints (with buffer)
        - Language dependency <= session requirements
        """
        filters = [Game.available == True]
        
        # Player count filter
        filters.append(and_(
            Game.min_players <= session.group_size,
            Game.max_players >= session.group_size
        ))
        
        # Duration filter (with buffer)
        min_duration = session.available_time_min * self.MIN_DURATION_BUFFER
        max_duration = session.available_time_min * self.MAX_DURATION_BUFFER
        filters.append(and_(
            Game.duration_min >= min_duration,
            Game.duration_min <= max_duration
        ))
        
        # Language dependency filter (hierarchy)
        session_lang_level = self.LANGUAGE_HIERARCHY.get(
            session.max_language_dependency,
            3  # Default to ALTA if unknown
        )
        
        allowed_languages = [
            lang for lang, level in self.LANGUAGE_HIERARCHY.items()
            if level <= session_lang_level
        ]
        
        filters.append(Game.language_dependency.in_(allowed_languages))
        
        # Execute query
        candidates = self.db.query(Game).filter(and_(*filters)).all()
        
        return candidates
    
    # ========================================================================
    # Scoring Components (RF-REC-01)
    # ========================================================================
    
    def _calculate_scores(
        self,
        game: Game,
        session: SessionProfile
    ) -> Dict[str, float]:
        """
        Calculate individual score components for a game.
        
        Returns dict with:
        - skill_score: Match between game skills and session objectives
        - mechanics_score: Mechanics alignment
        - difficulty_score: Appropriateness of complexity
        - ranking_score: Normalized BGG ranking
        - feedback_boost: Historical feedback bonus (future: RF-RETRO-02)
        """
        return {
            'skill_score': self._score_skills(game, session),
            'mechanics_score': self._score_mechanics(game, session),
            'difficulty_score': self._score_difficulty(game, session),
            'ranking_score': self._score_ranking(game),
            'feedback_boost': 0.0  # TODO: Implement in Module G
        }
    
    def _score_skills(self, game: Game, session: SessionProfile) -> float:
        """
        Score skill match between game and session objectives.
        
        Currently placeholder - will integrate with Module C (Skills taxonomy)
        when game-skill associations are implemented.
        
        For now, returns moderate score based on complexity match.
        """
        # TODO: Query game_skills associations and match with session.targeted_skills
        # This requires implementing the many-to-many relationship in Module C
        
        # Placeholder: use complexity as proxy for skill level
        if session.group_size <= 4:  # Small group, can handle complex games
            ideal_complexity = 3.5
        elif session.group_size <= 10:  # Medium group
            ideal_complexity = 2.5
        else:  # Large group needs simpler games
            ideal_complexity = 2.0
        
        complexity_diff = abs(game.complexity - ideal_complexity)
        # Convert to score: 0 diff = 1.0, 2+ diff = 0.0
        score = max(0.0, 1.0 - (complexity_diff / 2.0))
        
        return score
    
    def _score_mechanics(self, game: Game, session: SessionProfile) -> float:
        """
        Score mechanics alignment with session constraints.
        
        Considers:
        - Modality (presencial vs virtual): affects certain mechanics
        - Group size: affects cooperative/competitive balance
        """
        if not game.mechanics:
            return 0.5  # Neutral score if no mechanics data
        
        score = 0.5  # Base score
        mechanics_set = set(game.mechanics)
        
        # Modality bonuses
        if session.preferred_modality.value == "presencial":
            # Favor physical interaction mechanics
            physical_mechanics = {'dexterity', 'real-time', 'action/movement'}
            if mechanics_set & physical_mechanics:
                score += 0.2
        elif session.preferred_modality.value == "virtual":  # virtual
            # Favor turn-based, less physical mechanics
            digital_friendly = {'turn-based', 'simultaneous', 'card drafting'}
            if mechanics_set & digital_friendly:
                score += 0.2
        
        # Group size bonuses
        if session.group_size > 20:
            # Large groups need team/party mechanics
            large_group_mechanics = {'party game', 'team-based', 'cooperative'}
            if mechanics_set & large_group_mechanics:
                score += 0.3
        
        # Cap at 1.0
        return min(1.0, score)
    
    def _score_difficulty(self, game: Game, session: SessionProfile) -> float:
        """
        Score complexity appropriateness.
        
        Considers:
        - Available time: complex games need more time
        - Group size: large groups need simpler games
        - Session warnings: penalize if already time-constrained
        """
        # Determine ideal complexity based on context
        ideal_complexity = 3.0  # Default moderate
        
        # Adjust for time
        if session.available_time_min < 60:
            ideal_complexity = 2.0  # Short time = simple games
        elif session.available_time_min > 120:
            ideal_complexity = 3.5  # Long time = complex games allowed
        
        # Adjust for group size
        if session.group_size > 20:
            ideal_complexity = min(ideal_complexity, 2.5)
        elif session.group_size > 10:
            ideal_complexity = min(ideal_complexity, 3.0)
        
        # Calculate score based on distance from ideal
        complexity_diff = abs(game.complexity - ideal_complexity)
        score = max(0.0, 1.0 - (complexity_diff / 3.0))
        
        # Penalty if session has time warnings
        if session.has_warnings:
            warnings = session.validation_warnings or []
            if any('LIMITED_TIME' in str(w) for w in warnings):
                if game.complexity > 3.0:
                    score *= 0.7  # 30% penalty for complex games with time constraints
        
        return score
    
    def _score_ranking(self, game: Game) -> float:
        """
        Score based on BGG ranking (quality indicator).
        
        Normalizes ranking to [0, 1] scale:
        - Rank 1-100: score 1.0-0.8
        - Rank 101-1000: score 0.8-0.5
        - Rank 1001+: score 0.5-0.0
        - No rank: score 0.3 (neutral)
        """
        if not game.bgg_rank:
            return 0.3  # Neutral for unranked games
        
        rank = game.bgg_rank
        
        if rank <= 100:
            # Top 100: very high scores
            return 1.0 - (rank / 100) * 0.2  # 1.0 to 0.8
        elif rank <= 1000:
            # Top 1000: good scores
            return 0.8 - ((rank - 100) / 900) * 0.3  # 0.8 to 0.5
        else:
            # Beyond 1000: lower scores
            return max(0.0, 0.5 - ((rank - 1000) / 10000) * 0.5)  # 0.5 to 0.0
    
    # ========================================================================
    # Weight Application (RF-REC-02)
    # ========================================================================
    
    def _apply_weights(
        self,
        scores: Dict[str, float],
        config: ScoringConfig
    ) -> float:
        """
        Apply configurable weights to score components.
        
        RF-REC-02: Uses scoring configuration weights.
        """
        total = (
            scores['skill_score'] * config.skill_weight +
            scores['mechanics_score'] * config.mechanics_weight +
            scores['difficulty_score'] * config.difficulty_weight +
            scores['ranking_score'] * config.ranking_weight +
            scores.get('feedback_boost', 0.0)  # Direct boost, not weighted
        )
        
        # Ensure within [0, 1] bounds
        return max(0.0, min(1.0, total))
    
    # ========================================================================
    # Explainability (RF-EXP-01)
    # ========================================================================
    
    def _generate_explanation(
        self,
        scored_item: Dict,
        session: SessionProfile
    ) -> str:
        """
        Generate human-readable explanation for recommendation.
        
        RF-EXP-01: Natural language explanation with at least 3 specific reasons.
        Includes: skill match, operational constraints, mechanics, and boost factors.
        Max 200 words as per requirements.
        """
        game = scored_item['game']
        scores = scored_item
        
        # Start with game introduction
        parts = [f"**{game.name}** (Puntuación: {scored_item['total_score']:.2f}/1.0)\n"]
        reasons = []
        
        # REASON 1: Primary skill alignment (RF-EXP-01 requirement)
        skill_score = scores.get('skill_score', 0)
        if skill_score > 0.5:
            complexity_desc = "baja" if game.complexity < 2.0 else "moderada" if game.complexity < 3.5 else "alta"
            reasons.append(
                f"✓ **Habilidades objetivo:** La complejidad {complexity_desc} ({game.complexity:.1f}/5.0) "
                f"es apropiada para desarrollar las habilidades planteadas (alineación: {skill_score:.0%})"
            )
        elif skill_score > 0:
            reasons.append(
                f"✓ **Habilidades objetivo:** Complejidad {game.complexity:.1f}/5.0 "
                f"(alineación moderada: {skill_score:.0%})"
            )
        
        # REASON 2: Operational constraints met (RF-EXP-01 requirement)
        time_buffer = session.available_time_min * 0.2
        time_fits = game.duration_min <= (session.available_time_min + time_buffer)
        players_fit = game.min_players <= session.group_size <= game.max_players
        
        if time_fits and players_fit:
            reasons.append(
                f"✓ **Restricciones cumplidas:** Duración {game.duration_min} min "
                f"(disponible: {session.available_time_min} min), "
                f"soporta {game.min_players}-{game.max_players} jugadores "
                f"(grupo: {session.group_size})"
            )
        elif time_fits:
            reasons.append(
                f"✓ **Tiempo apropiado:** {game.duration_min} minutos se ajusta a los "
                f"{session.available_time_min} min disponibles"
            )
        
        # REASON 3: Relevant mechanics (RF-EXP-01 requirement)
        mechanics_score = scores.get('mechanics_score', 0)
        if game.mechanics and len(game.mechanics) > 0:
            mechanics_display = ", ".join(game.mechanics[:3])
            if len(game.mechanics) > 3:
                mechanics_display += f" (+{len(game.mechanics)-3} más)"
            
            modality_match = ""
            if session.preferred_modality.value in ['cooperative', 'any']:
                if any(m.lower() in ['cooperative play', 'cooperation'] for m in game.mechanics):
                    modality_match = " (incluye mecánicas cooperativas ✓)"
            
            reasons.append(
                f"✓ **Mecánicas relevantes:** {mechanics_display}{modality_match} "
                f"(similitud: {mechanics_score:.0%})"
            )
        
        # REASON 4: Quality/Popularity indicator
        ranking_score = scores.get('ranking_score', 0)
        if game.bgg_rank:
            if game.bgg_rank <= 100:
                reasons.append(
                    f"✓ **Altamente valorado:** Posición #{game.bgg_rank} en BoardGameGeek "
                    f"(top 100 mundial)"
                )
            elif game.bgg_rank <= 500:
                reasons.append(
                    f"✓ **Bien valorado:** Posición #{game.bgg_rank} en BoardGameGeek"
                )
        
        # BOOST FACTOR: Historical feedback (RF-EXP-01 requirement)
        feedback_boost = scores.get('feedback_boost', 0)
        if feedback_boost > 0.1:
            # This will be populated when Module G (Feedback) is fully implemented
            reasons.append(
                f"⭐ **Recomendado altamente** por asesores en contextos similares "
                f"(boost: +{feedback_boost:.1%})"
            )
        
        # WARNING: Complexity edge case (RF-EXP-01 requirement)
        difficulty_score = scores.get('difficulty_score', 0)
        if game.complexity >= 3.5 and difficulty_score < 0.6:
            reasons.append(
                f"⚠️ **Advertencia:** Complejidad alta ({game.complexity:.1f}/5.0), "
                f"considere grupo experimentado o tiempo adicional para explicación"
            )
        elif game.complexity <= 1.5 and session.available_time_min > 90:
            reasons.append(
                f"ℹ️ **Nota:** Juego simple ({game.complexity:.1f}/5.0), "
                f"podría combinar con otra actividad si sobra tiempo"
            )
        
        # Combine all reasons
        parts.append("\n".join(reasons))
        
        return "\n".join(parts)
    
    def _generate_match_reasons(
        self,
        scored_item: Dict,
        session: SessionProfile
    ) -> List[str]:
        """Generate structured list of match reasons."""
        reasons = []
        game = scored_item['game']
        
        # Time match
        if game.duration_min <= session.available_time_min * 1.1:
            reasons.append(f"duration_fits:{game.duration_min}min")
        
        # Player count match
        reasons.append(f"players_supported:{game.min_players}-{game.max_players}")
        
        # Complexity appropriateness
        if scored_item['difficulty_score'] > 0.7:
            reasons.append(f"complexity_appropriate:{game.complexity}")
        
        # High ranking
        if game.bgg_rank and game.bgg_rank <= 500:
            reasons.append(f"high_ranking:#{game.bgg_rank}")
        
        # Language compatibility
        reasons.append(f"language_ok:{game.language_dependency.value}")
        
        return reasons
    
    # ========================================================================
    # No Results Handling (RF-REC-03)
    # ========================================================================
    
    def _handle_no_results(
        self,
        session: SessionProfile,
        config: ScoringConfig
    ) -> RecommendationResponse:
        """
        Handle case when no games match hard filters.
        
        RF-REC-03: Provide actionable relaxation suggestions.
        """
        suggestions = []
        
        # Analyze why no results
        total_games = self.db.query(Game).filter(Game.available == True).count()
        
        if total_games == 0:
            suggestions.append("El catálogo está vacío. Agregue juegos primero.")
            return self._build_empty_response(session, config, suggestions)
        
        # Check each filter individually
        
        # Player count
        games_with_players = self.db.query(Game).filter(
            and_(
                Game.available == True,
                Game.min_players <= session.group_size,
                Game.max_players >= session.group_size
            )
        ).count()
        
        if games_with_players == 0:
            suggestions.append(
                f"Ningún juego soporta {session.group_size} jugadores. "
                f"Considere dividir en grupos más pequeños."
            )
        
        # Duration
        games_with_duration = self.db.query(Game).filter(
            and_(
                Game.available == True,
                Game.duration_min <= session.available_time_min * 1.5
            )
        ).count()
        
        if games_with_duration == 0:
            suggestions.append(
                f"Ningún juego se ajusta a {session.available_time_min} minutos. "
                f"Considere extender el tiempo disponible."
            )
        
        # Language dependency
        session_lang_level = self.LANGUAGE_HIERARCHY.get(session.max_language_dependency, 3)
        games_with_language = self.db.query(Game).filter(
            and_(
                Game.available == True,
                Game.language_dependency.in_([
                    lang for lang, level in self.LANGUAGE_HIERARCHY.items()
                    if level <= session_lang_level
                ])
            )
        ).count()
        
        if games_with_language == 0:
            suggestions.append(
                f"Ningún juego cumple con requisito de idioma '{session.max_language_dependency.value}'. "
                f"Considere aceptar juegos con mayor dependencia de idioma."
            )
        
        # If all individual filters pass but combination fails
        if not suggestions:
            suggestions.append(
                "La combinación de filtros es muy restrictiva. "
                "Considere relajar algunos requisitos (ej: ampliar rango de tiempo, dividir grupo)."
            )
        
        return self._build_empty_response(session, config, suggestions)
    
    def _build_empty_response(
        self,
        session: SessionProfile,
        config: ScoringConfig,
        suggestions: List[str]
    ) -> RecommendationResponse:
        """Build response object for no results case."""
        return RecommendationResponse(
            session_profile_id=session.id,
            recommendations=[],
            total_candidates=0,
            scoring_config_used=ScoringConfigSchema.model_validate(config),
            generation_timestamp=datetime.now(timezone.utc),
            has_results=False,
            relaxation_suggestions=suggestions
        )
    
    # ========================================================================
    # Configuration Management (RF-REC-02)
    # ========================================================================
    
    def _get_scoring_config(self, config_id: Optional[int] = None) -> ScoringConfig:
        """
        Get scoring configuration by ID or return active config.
        
        Args:
            config_id: Specific config ID, or None for active config
        
        Returns:
            ScoringConfig instance
        
        Raises:
            NotFoundException: If config not found
        """
        if config_id:
            config = self.db.query(ScoringConfig).filter(
                ScoringConfig.id == config_id
            ).first()
            
            if not config:
                raise NotFoundException("ScoringConfig", str(config_id))
        else:
            # Get active configuration
            config = self.db.query(ScoringConfig).filter(
                ScoringConfig.is_active == True
            ).first()
            
            if not config:
                # Fallback: get default config
                config = self.db.query(ScoringConfig).filter(
                    ScoringConfig.is_default == True
                ).first()
            
            if not config:
                raise NotFoundException(
                    "ScoringConfig",
                    "No active or default configuration found. Create one first."
                )
        
        return config
