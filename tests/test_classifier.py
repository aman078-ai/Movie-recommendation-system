import pytest
from src.emotion_classifier import EmotionClassifier

def test_classifier_fallback_initialization():
    """Verify that classifier can be initialized in fallback mode."""
    classifier = EmotionClassifier(use_fallback=True)
    assert classifier.use_fallback is True
    assert classifier.pipeline is None

def test_classifier_default_scores_on_empty_text():
    """Verify default scores are returned on empty input."""
    classifier = EmotionClassifier(use_fallback=True)
    scores = classifier.predict("")
    assert "neutral" in scores
    assert scores["neutral"] > scores["joy"]
    
    scores_none = classifier.predict(None)
    assert scores_none == scores

def test_classifier_prediction_keys():
    """Verify that predictions contain all 7 required emotions."""
    classifier = EmotionClassifier(use_fallback=True)
    scores = classifier.predict("I had a bad day.")
    required_emotions = {"anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"}
    assert set(scores.keys()) == required_emotions

def test_classifier_sentiment_association():
    """Verify keyword mapping triggers correct dominant emotions in fallback."""
    classifier = EmotionClassifier(use_fallback=True)
    
    # Happy input
    joy_scores = classifier.predict("I am so happy and excited today!")
    dominant_joy = max(joy_scores, key=joy_scores.get)
    assert dominant_joy == "joy"
    
    # Sad input
    sad_scores = classifier.predict("I feel so sad and depressed, crying right now")
    dominant_sad = max(sad_scores, key=sad_scores.get)
    assert dominant_sad == "sadness"
    
    # Angry input
    angry_scores = classifier.predict("I am furious, angry, pissed off!")
    dominant_angry = max(angry_scores, key=angry_scores.get)
    assert dominant_angry == "anger"
