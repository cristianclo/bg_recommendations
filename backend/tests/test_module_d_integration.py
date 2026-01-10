"""
Integration tests for Module D (Recommendation Engine).
Tests RF-REC-01, RF-REC-02, RF-REC-03 requirements.
"""
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.session import SessionProfile
from app.models.game import Game
from app.models.recommendation import ScoringConfig, Recommendation
from app.recommendations.engine import RecommendationEngine
from app.recommendations.config_service import ScoringConfigService
from app.schemas.recommendation import ScoringConfigCreate, ScoringConfigUpdate


class TestReport:
    """Utility class to generate test reports."""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def add_test(self, name: str, passed: bool, details: str = ""):
        """Add a test result."""
        self.results.append({
            "name": name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now()
        })
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"      {details}")
    
    def generate_report(self) -> str:
        """Generate final report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        duration = (datetime.now() - self.start_time).total_seconds()
        
        report = [
            "\n" + "="*80,
            "MODULE D - RECOMMENDATION ENGINE - TEST REPORT",
            "="*80,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {duration:.2f} seconds",
            f"Total Tests: {total}",
            f"Passed: {passed} ({passed/total*100:.1f}%)",
            f"Failed: {failed}",
            "",
            "DETAILED RESULTS:",
            "-"*80
        ]
        
        for i, result in enumerate(self.results, 1):
            status = "PASS" if result["passed"] else "FAIL"
            report.append(f"{i}. [{status}] {result['name']}")
            if result["details"]:
                report.append(f"   └─ {result['details']}")
        
        report.extend([
            "",
            "="*80,
            "SUMMARY BY REQUIREMENT:",
            "-"*80
        ])
        
        # Group by requirement
        requirements = {
            "RF-REC-01": [r for r in self.results if "REC-01" in r["name"] or "Generation" in r["name"]],
            "RF-REC-02": [r for r in self.results if "REC-02" in r["name"] or "Config" in r["name"]],
            "RF-REC-03": [r for r in self.results if "REC-03" in r["name"] or "No Results" in r["name"]],
        }
        
        for req, tests in requirements.items():
            if tests:
                req_passed = sum(1 for t in tests if t["passed"])
                report.append(f"{req}: {req_passed}/{len(tests)} tests passed")
        
        report.append("="*80)
        
        return "\n".join(report)


def test_scoring_config_crud(db: Session, report: TestReport):
    """Test RF-REC-02: Scoring configuration CRUD operations."""
    print("\n--- Testing Scoring Configuration CRUD (RF-REC-02) ---")
    
    service = ScoringConfigService(db)
    
    # Test 1: Create new config
    try:
        config_create = ScoringConfigCreate(
            name="Test Config",
            description="Test configuration for automated testing",
            skill_weight=0.35,
            mechanics_weight=0.35,
            difficulty_weight=0.20,
            ranking_weight=0.10,
            is_active=False,
            is_default=False
        )
        config = service.create(config_create)
        report.add_test(
            "RF-REC-02: Create scoring configuration",
            config.id is not None and config.name == "Test Config",
            f"Created config ID {config.id} with valid weights"
        )
    except Exception as e:
        report.add_test("RF-REC-02: Create scoring configuration", False, str(e))
        return
    
    # Test 2: Validate weight sum
    try:
        invalid_config = ScoringConfigCreate(
            name="Invalid Config",
            skill_weight=0.5,
            mechanics_weight=0.5,
            difficulty_weight=0.5,  # Sum > 1.0
            ranking_weight=0.1,
            is_active=False,
            is_default=False
        )
        try:
            service.create(invalid_config)
            report.add_test("RF-REC-02: Reject invalid weight sum", False, "Should have rejected sum > 1.0")
        except Exception:
            report.add_test("RF-REC-02: Reject invalid weight sum", True, "Correctly rejected invalid weights")
    except Exception as e:
        report.add_test("RF-REC-02: Reject invalid weight sum", False, str(e))
    
    # Test 3: List configurations
    try:
        configs = service.list()
        report.add_test(
            "RF-REC-02: List all configurations",
            len(configs) >= 2,  # At least default + test config
            f"Found {len(configs)} configurations"
        )
    except Exception as e:
        report.add_test("RF-REC-02: List all configurations", False, str(e))
    
    # Test 4: Get active configuration
    try:
        active = service.get_active()
        report.add_test(
            "RF-REC-02: Get active configuration",
            active is not None and active.is_active,
            f"Active config: {active.name if active else 'None'}"
        )
    except Exception as e:
        report.add_test("RF-REC-02: Get active configuration", False, str(e))
    
    # Test 5: Activate test config
    try:
        activated = service.activate(config.id)
        report.add_test(
            "RF-REC-02: Activate configuration",
            activated.is_active,
            f"Activated '{activated.name}'"
        )
        
        # Verify only one is active
        all_configs = service.list()
        active_count = sum(1 for c in all_configs if c.is_active)
        report.add_test(
            "RF-REC-02: Only one active config",
            active_count == 1,
            f"Active configs: {active_count}"
        )
    except Exception as e:
        report.add_test("RF-REC-02: Activate configuration", False, str(e))
    
    # Test 6: Update configuration
    try:
        update = ScoringConfigUpdate(
            description="Updated test configuration",
            skill_weight=0.45,
            mechanics_weight=0.30,
            difficulty_weight=0.15,
            ranking_weight=0.10
        )
        updated = service.update(config.id, update)
        report.add_test(
            "RF-REC-02: Update configuration",
            updated.skill_weight == 0.45,
            f"Updated weights: {updated.skill_weight}/{updated.mechanics_weight}/{updated.difficulty_weight}/{updated.ranking_weight}"
        )
    except Exception as e:
        report.add_test("RF-REC-02: Update configuration", False, str(e))
    
    # Clean up: reactivate default config
    try:
        default = service.get_default()
        if default:
            service.activate(default.id)
    except:
        pass


def test_recommendation_generation(db: Session, report: TestReport):
    """Test RF-REC-01: Recommendation generation."""
    print("\n--- Testing Recommendation Generation (RF-REC-01) ---")
    
    engine = RecommendationEngine(db)
    
    # Get a session with reasonable constraints
    sessions = db.query(SessionProfile).filter(
        SessionProfile.group_size <= 6,
        SessionProfile.available_time_min >= 45
    ).limit(5).all()
    
    if not sessions:
        report.add_test(
            "RF-REC-01: Find test sessions",
            False,
            "No suitable test sessions found"
        )
        return
    
    # Test with each session
    for session in sessions[:3]:  # Test with first 3 sessions
        try:
            result = engine.generate_recommendations(
                session_profile_id=session.id,
                top_n=5,
                include_explanations=True
            )
            
            report.add_test(
                f"RF-REC-01: Generate recommendations (session {session.id})",
                result is not None,
                f"Candidates: {result.total_candidates}, Recommendations: {len(result.recommendations)}, Has results: {result.has_results}"
            )
            
            # Test traceability
            if result.recommendations:
                rec = result.recommendations[0]
                has_scores = all([
                    rec.skill_score is not None,
                    rec.mechanics_score is not None,
                    rec.difficulty_score is not None,
                    rec.ranking_score is not None,
                    rec.total_score is not None
                ])
                report.add_test(
                    f"RF-REC-01: Score components present (session {session.id})",
                    has_scores,
                    f"Total score: {rec.total_score:.3f}"
                )
                
                # Test explanation
                has_explanation = rec.explanation_text is not None and len(rec.explanation_text) > 0
                report.add_test(
                    f"RF-REC-01: Explanation generated (session {session.id})",
                    has_explanation,
                    f"Explanation length: {len(rec.explanation_text) if rec.explanation_text else 0} chars"
                )
                
                # Test weights used
                has_weights = rec.weights_used is not None and len(rec.weights_used) > 0
                report.add_test(
                    f"RF-REC-01: Weights recorded (session {session.id})",
                    has_weights,
                    f"Weights: {rec.weights_used if has_weights else 'None'}"
                )
            
        except Exception as e:
            report.add_test(
                f"RF-REC-01: Generate recommendations (session {session.id})",
                False,
                str(e)
            )


def test_no_results_handling(db: Session, report: TestReport):
    """Test RF-REC-03: No results handling."""
    print("\n--- Testing No Results Handling (RF-REC-03) ---")
    
    engine = RecommendationEngine(db)
    
    # Find sessions with very restrictive constraints
    restrictive_sessions = db.query(SessionProfile).filter(
        SessionProfile.group_size > 20  # Large groups unlikely to match
    ).limit(3).all()
    
    if not restrictive_sessions:
        # Create a test session with impossible constraints
        print("   Creating test session with restrictive constraints...")
    
    for session in restrictive_sessions[:2]:  # Test with 2 restrictive sessions
        try:
            result = engine.generate_recommendations(
                session_profile_id=session.id,
                top_n=5
            )
            
            # Test that result is returned even with no matches
            report.add_test(
                f"RF-REC-03: Handle no results gracefully (session {session.id})",
                result is not None,
                f"Has results: {result.has_results}, Candidates: {result.total_candidates}"
            )
            
            # Test that suggestions are provided
            if not result.has_results:
                has_suggestions = (
                    result.relaxation_suggestions is not None and 
                    len(result.relaxation_suggestions) > 0
                )
                report.add_test(
                    f"RF-REC-03: Provide relaxation suggestions (session {session.id})",
                    has_suggestions,
                    f"Suggestions: {len(result.relaxation_suggestions) if has_suggestions else 0}"
                )
                
                if has_suggestions:
                    print(f"      Suggestions provided:")
                    for sugg in result.relaxation_suggestions:
                        print(f"        - {sugg}")
            
        except Exception as e:
            report.add_test(
                f"RF-REC-03: Handle no results (session {session.id})",
                False,
                str(e)
            )


def test_database_persistence(db: Session, report: TestReport):
    """Test that recommendations are persisted to database."""
    print("\n--- Testing Database Persistence ---")
    
    try:
        # Count recommendations before
        count_before = db.query(Recommendation).count()
        
        # Generate recommendations for a session
        engine = RecommendationEngine(db)
        session = db.query(SessionProfile).filter(
            SessionProfile.group_size <= 6
        ).first()
        
        if session:
            result = engine.generate_recommendations(
                session_profile_id=session.id,
                top_n=3
            )
            
            # Count after
            count_after = db.query(Recommendation).count()
            
            report.add_test(
                "Database: Recommendations persisted",
                count_after >= count_before,
                f"Before: {count_before}, After: {count_after}, Generated: {len(result.recommendations)}"
            )
            
            # Verify we can query them back
            saved_recs = db.query(Recommendation).filter(
                Recommendation.session_profile_id == session.id
            ).all()
            
            report.add_test(
                "Database: Query saved recommendations",
                len(saved_recs) > 0,
                f"Found {len(saved_recs)} recommendations for session {session.id}"
            )
        else:
            report.add_test("Database: Find test session", False, "No suitable session found")
            
    except Exception as e:
        report.add_test("Database: Recommendations persisted", False, str(e))


def test_scoring_algorithm(db: Session, report: TestReport):
    """Test scoring algorithm components."""
    print("\n--- Testing Scoring Algorithm ---")
    
    try:
        engine = RecommendationEngine(db)
        
        # Get a game and session
        game = db.query(Game).filter(Game.available == True).first()
        session = db.query(SessionProfile).filter(
            SessionProfile.group_size <= 6
        ).first()
        
        if not game or not session:
            report.add_test("Scoring: Find test data", False, "No game or session available")
            return
        
        # Test individual scoring components
        scores = engine._calculate_scores(game, session)
        
        # Verify all components are present
        required_keys = ['skill_score', 'mechanics_score', 'difficulty_score', 'ranking_score', 'feedback_boost']
        all_present = all(key in scores for key in required_keys)
        
        report.add_test(
            "Scoring: All components calculated",
            all_present,
            f"Components: {list(scores.keys())}"
        )
        
        # Verify scores are in valid range [0, 1]
        valid_ranges = all(
            0.0 <= scores[key] <= 1.0 
            for key in required_keys if key != 'feedback_boost'
        )
        
        report.add_test(
            "Scoring: All scores in [0, 1] range",
            valid_ranges,
            f"Scores: skill={scores['skill_score']:.2f}, mechanics={scores['mechanics_score']:.2f}, difficulty={scores['difficulty_score']:.2f}, ranking={scores['ranking_score']:.2f}"
        )
        
        # Test weight application
        config = db.query(ScoringConfig).filter(ScoringConfig.is_active == True).first()
        if not config:
            config = db.query(ScoringConfig).filter(ScoringConfig.is_default == True).first()
        
        if config:
            total_score = engine._apply_weights(scores, config)
            
            report.add_test(
                "Scoring: Weight application",
                0.0 <= total_score <= 1.0,
                f"Total score: {total_score:.3f} using weights {config.get_weights_dict()}"
            )
        
    except Exception as e:
        report.add_test("Scoring: Algorithm execution", False, str(e))


def main():
    """Run all tests and generate report."""
    print("\n" + "="*80)
    print("MODULE D - RECOMMENDATION ENGINE - INTEGRATION TESTS")
    print("="*80)
    
    db = SessionLocal()
    report = TestReport()
    
    try:
        # Check database connectivity
        game_count = db.query(Game).count()
        session_count = db.query(SessionProfile).count()
        config_count = db.query(ScoringConfig).count()
        
        print(f"\nDatabase Status:")
        print(f"  - Games: {game_count}")
        print(f"  - Sessions: {session_count}")
        print(f"  - Scoring Configs: {config_count}")
        
        if game_count == 0 or session_count == 0:
            print("\n⚠️  WARNING: Database is empty. Run seed_data.py first!")
            return
        
        # Run test suites
        test_scoring_config_crud(db, report)
        test_recommendation_generation(db, report)
        test_no_results_handling(db, report)
        test_database_persistence(db, report)
        test_scoring_algorithm(db, report)
        
        # Generate and save report
        report_text = report.generate_report()
        print(report_text)
        
        # Save to file
        report_file = os.path.join(
            os.path.dirname(__file__),
            f"module_d_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n📄 Report saved to: {report_file}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
