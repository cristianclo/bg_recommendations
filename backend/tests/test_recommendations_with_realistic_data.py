"""
Quick test to verify recommendations are generated with realistic session data.
Tests that sessions with 2-8 players actually get game recommendations.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.session import SessionProfile
from app.recommendations.engine import RecommendationEngine
from app.recommendations.config_service import ScoringConfigService


def test_recommendations_with_realistic_sessions():
    """Test recommendation generation with realistic session profiles."""
    db = SessionLocal()
    
    print("=" * 80)
    print("TESTING RECOMMENDATIONS WITH REALISTIC SESSION DATA")
    print("=" * 80)
    
    try:
        # Get all sessions
        sessions = db.query(SessionProfile).all()
        
        print(f"\n🎯 Found {len(sessions)} session profiles")
        print("-" * 80)
        
        # Test recommendation generation for each session
        engine = RecommendationEngine(db)
        total_recommendations = 0
        sessions_with_results = 0
        sessions_without_results = 0
        
        for session in sessions:
            print(f"\n📋 Session: {session.session_name}")
            print(f"   Group Size: {session.group_size} players")
            print(f"   Time: {session.available_time_min} min")
            print(f"   Language: {session.max_language_dependency.value}")
            print(f"   Modality: {session.preferred_modality.value}")
            
            # Generate recommendations
            result = engine.generate_recommendations(
                session_profile_id=session.id,
                top_n=5
            )
            
            if result.has_results:
                sessions_with_results += 1
                num_recs = len(result.recommendations)
                total_recommendations += num_recs
                
                print(f"   ✅ {num_recs} recommendations generated!")
                
                # Show top 3 recommendations
                for i, rec in enumerate(result.recommendations[:3], 1):
                    game = rec.game
                    print(f"      {i}. {game.name} (Score: {rec.total_score:.3f})")
                    print(f"         Players: {game.min_players}-{game.max_players}, "
                          f"Duration: {game.duration_min} min, "
                          f"Complexity: {game.complexity:.1f}")
            else:
                sessions_without_results += 1
                print(f"   ❌ No recommendations (0 games matched)")
                if result.relaxation_suggestions:
                    print(f"   💡 Suggestion: {result.relaxation_suggestions[0]}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Sessions with recommendations: {sessions_with_results}/{len(sessions)} "
              f"({sessions_with_results/len(sessions)*100:.1f}%)")
        print(f"❌ Sessions without matches: {sessions_without_results}/{len(sessions)}")
        print(f"📊 Total recommendations generated: {total_recommendations}")
        print(f"📈 Average per session: {total_recommendations/max(sessions_with_results, 1):.1f}")
        
        if sessions_with_results > 0:
            print("\n✅ SUCCESS: Recommendation engine is working with realistic data!")
            return True
        else:
            print("\n⚠️  WARNING: No sessions generated recommendations. Check game catalog and session constraints.")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_recommendations_with_realistic_sessions()
    sys.exit(0 if success else 1)
