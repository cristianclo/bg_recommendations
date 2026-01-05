"""
Session validator for operational coherence checks (RF-CTX-02).
Validates session parameters and generates warnings without blocking.
"""
import logging
from typing import List

from ..models.session import SessionProfile, Modality
from ..schemas.session import ValidationWarning

logger = logging.getLogger(__name__)


class SessionValidator:
    """
    Validates session profiles for operational coherence (RF-CTX-02).
    
    Generates warnings (not errors) for potentially problematic configurations:
    - Large groups (>20 people)
    - Very large groups (>30 people)
    - Limited time (<30 minutes)
    - Cooperative games with very large groups
    
    Warnings never block the query but are stored for advisor awareness.
    """
    
    # Thresholds (RF-CTX-02 specifications)
    LARGE_GROUP_THRESHOLD = 20
    VERY_LARGE_GROUP_THRESHOLD = 30
    LIMITED_TIME_THRESHOLD = 30
    
    @classmethod
    def validate_session(cls, session: SessionProfile) -> List[ValidationWarning]:
        """
        Validate session profile and return list of warnings.
        
        Args:
            session: SessionProfile to validate
            
        Returns:
            List of ValidationWarning objects (may be empty)
        """
        warnings = []
        
        # Check group size warnings
        warnings.extend(cls._check_group_size(session))
        
        # Check time constraints
        warnings.extend(cls._check_time_constraints(session))
        
        # Check cooperative + large group combination
        warnings.extend(cls._check_cooperative_large_group(session))
        
        logger.info(
            f"Session validation completed: {len(warnings)} warnings for "
            f"group_size={session.group_size}, time={session.available_time_min}min"
        )
        
        return warnings
    
    @classmethod
    def _check_group_size(cls, session: SessionProfile) -> List[ValidationWarning]:
        """
        Check for group size warnings (RF-CTX-02).
        
        - Group >20: suggest stations/multiple tables
        - Group >30: strongly recommend stations
        """
        warnings = []
        
        if session.group_size > cls.VERY_LARGE_GROUP_THRESHOLD:
            # Very large group (>30)
            warnings.append(ValidationWarning(
                code="VERY_LARGE_GROUP",
                message=f"Very large group ({session.group_size} people) detected",
                severity="warning",
                suggestions=[
                    "Strongly recommend using station-based rotation system",
                    "Consider dividing into 4-6 stations with different games",
                    "Assign 5-8 people per station for optimal engagement",
                    "Plan 10-15 minute rotations if time permits",
                    "Consider having facilitators at each station"
                ]
            ))
        
        elif session.group_size > cls.LARGE_GROUP_THRESHOLD:
            # Large group (>20 but ≤30)
            warnings.append(ValidationWarning(
                code="LARGE_GROUP",
                message=f"Large group ({session.group_size} people) detected",
                severity="info",
                suggestions=[
                    "Consider using multiple tables/stations for better engagement",
                    "Look for games that scale well or support parallel play",
                    "Consider dividing into 2-3 groups with different games",
                    "Team-based games may work well for this group size",
                    "Ensure adequate physical space for all participants"
                ]
            ))
        
        return warnings
    
    @classmethod
    def _check_time_constraints(cls, session: SessionProfile) -> List[ValidationWarning]:
        """
        Check for time constraint warnings (RF-CTX-02).
        
        - Time <30min: warn about complexity limitations
        """
        warnings = []
        
        if session.available_time_min < cls.LIMITED_TIME_THRESHOLD:
            warnings.append(ValidationWarning(
                code="LIMITED_TIME",
                message=f"Limited time available ({session.available_time_min} minutes)",
                severity="warning",
                suggestions=[
                    "Focus on games with low complexity (≤2.0)",
                    "Avoid games requiring extensive rule explanation",
                    "Consider games with simple, intuitive mechanics",
                    "Allow 5-10 minutes for setup and explanation",
                    "Party games or familiar mechanics work best",
                    "Consider running a quick demo round instead of full game"
                ]
            ))
        
        return warnings
    
    @classmethod
    def _check_cooperative_large_group(cls, session: SessionProfile) -> List[ValidationWarning]:
        """
        Check cooperative game + large group combination (RF-CTX-02).
        
        - Cooperative + group >30: suggest team subdivision
        """
        warnings = []
        
        if (session.preferred_modality == Modality.COOPERATIVE and 
            session.group_size > cls.VERY_LARGE_GROUP_THRESHOLD):
            
            warnings.append(ValidationWarning(
                code="COOPERATIVE_LARGE_GROUP",
                message=f"Cooperative game requested for very large group ({session.group_size} people)",
                severity="warning",
                suggestions=[
                    "Consider subdividing into smaller cooperative teams (4-6 per team)",
                    "Multiple teams can play the same cooperative game in parallel",
                    "Assign team leaders/coordinators to facilitate each group",
                    "Consider competitive team-based games as alternative",
                    "Debrief collectively after parallel sessions for shared learning",
                    "Ensure each team has adequate space and materials"
                ]
            ))
        
        return warnings
    
    @classmethod
    def get_warning_summary(cls, warnings: List[ValidationWarning]) -> dict:
        """
        Generate a summary of warnings by severity.
        
        Args:
            warnings: List of validation warnings
            
        Returns:
            Dictionary with counts by severity
        """
        summary = {
            "total": len(warnings),
            "critical": 0,
            "warning": 0,
            "info": 0,
            "codes": []
        }
        
        for warning in warnings:
            severity = warning.severity.lower()
            if severity in summary:
                summary[severity] += 1
            summary["codes"].append(warning.code)
        
        return summary
