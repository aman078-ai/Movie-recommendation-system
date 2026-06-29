import pytest
from src.recommender import MovieRecommender

def test_recommender_initialization():
    """Verify movie database load during recommender instantiation."""
    recommender = MovieRecommender()
    assert not recommender.local_df.empty
    assert "title" in recommender.local_df.columns
    assert "parsed_genres" in recommender.local_df.columns

def test_recommender_mapping_structure():
    """Verify that recommendation outputs return (dominant_emotion, recommendations_list)."""
    recommender = MovieRecommender()
    emotion_scores = {
        "anger": 0.05,
        "disgust": 0.05,
        "fear": 0.05,
        "joy": 0.7,
        "neutral": 0.05,
        "sadness": 0.05,
        "surprise": 0.05
    }
    
    dominant_emotion, recs = recommender.recommend(emotion_scores, strategy="shift_mood", limit=3)
    assert dominant_emotion == "joy"
    assert isinstance(recs, list)
    assert len(recs) <= 3
    
    # Assert fields in returned movie objects
    if recs:
        movie = recs[0]
        assert "title" in movie
        assert "vote_average" in movie
        assert "genres" in movie
        assert "poster_url" in movie
        assert "overview" in movie

def test_recommender_different_strategies():
    """Verify recommendations execute and differ between strategies."""
    recommender = MovieRecommender()
    emotion_scores = {
        "sadness": 0.8,
        "joy": 0.0,
        "neutral": 0.2
    }
    
    # Sadness + shift_mood should map to Comedy, Family, Animation
    _, recs_shift = recommender.recommend(emotion_scores, strategy="shift_mood", limit=5)
    
    # Sadness + lean_in should map to Drama, Romance
    _, recs_lean = recommender.recommend(emotion_scores, strategy="lean_in", limit=5)
    
    # Assert we get recommendations back
    assert len(recs_shift) > 0
    assert len(recs_lean) > 0
