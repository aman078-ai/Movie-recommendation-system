import logging
from typing import Dict, List, Any
from src.config import HF_MODEL_NAME

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionClassifier:
    """Classifies the emotion of a given text using a Hugging Face model or keyword fallback."""
    
    def __init__(self, use_fallback: bool = False):
        self.use_fallback = use_fallback
        self.pipeline = None
        
        if not use_fallback:
            try:
                # Import here to avoid loading heavy libraries if we want to force fallback or debug
                from transformers import pipeline
                logger.info(f"Loading Hugging Face model: {HF_MODEL_NAME}...")
                # top_k=None returns all labels with their corresponding scores
                self.pipeline = pipeline("text-classification", model=HF_MODEL_NAME, top_k=None)
                logger.info("Hugging Face model loaded successfully.")
            except Exception as e:
                logger.warning(
                    f"Failed to load Hugging Face model due to: {e}. "
                    f"Falling back to keyword-based classifier."
                )
                self.use_fallback = True

    def predict(self, text: str) -> Dict[str, float]:
        """
        Predicts the emotion scores for a given text.
        
        Returns:
            A dictionary mapping emotion names (anger, disgust, fear, joy, neutral, sadness, surprise)
            to their confidence scores (floats between 0.0 and 1.0).
        """
        if not text or not text.strip():
            return self._get_default_scores()

        if self.use_fallback:
            return self._predict_fallback(text)
            
        try:
            # The pipeline returns a list of lists of dicts because top_k=None and batch_size=1
            # Format: [[{'label': 'joy', 'score': 0.95}, {'label': 'sadness', 'score': 0.02}, ...]]
            results = self.pipeline(text)
            if not results or not results[0]:
                return self._get_default_scores()
                
            predictions = results[0]
            # Convert list of dicts to a single dict mapping label -> score
            score_dict = {pred["label"].lower(): float(pred["score"]) for pred in predictions}
            return score_dict
        except Exception as e:
            logger.error(f"Inference failed, using fallback. Error: {e}")
            return self._predict_fallback(text)

    def _get_default_scores(self) -> Dict[str, float]:
        """Returns neutral-heavy baseline scores."""
        return {
            "anger": 0.05,
            "disgust": 0.05,
            "fear": 0.05,
            "joy": 0.1,
            "neutral": 0.6,
            "sadness": 0.05,
            "surprise": 0.05
        }

    def _predict_fallback(self, text: str) -> Dict[str, float]:
        """
        A rule-based keyword matcher that serves as a fallback.
        It detects emotions based on typical vocabulary and returns normalized pseudo-probabilities.
        """
        text_lower = text.lower()
        
        # Define keyword maps
        keywords = {
            "joy": ["happy", "glad", "joy", "excited", "laugh", "smile", "cheerful", "good", "great", "wonderful", "love", "fun"],
            "sadness": ["sad", "cry", "depressed", "terrible", "bad", "lonely", "hurt", "grief", "broken", "unhappy", "down", "sorrow"],
            "anger": ["angry", "mad", "furious", "hate", "pissed", "annoyed", "irritated", "frustrated", "rage"],
            "fear": ["scared", "afraid", "fear", "terrified", "panic", "anxious", "worry", "horror", "spooky", "dread"],
            "disgust": ["disgust", "gross", "eww", "sick", "repulsed", "nasty", "hate", "awful"],
            "surprise": ["surprise", "shock", "amazing", "wow", "unexpected", "wonder", "astounded", "sudden"]
        }
        
        scores = {emotion: 0.05 for emotion in self._get_default_scores().keys()}
        scores["neutral"] = 0.4  # Start with neutral baseline
        
        matched_any = False
        for emotion, words in keywords.items():
            for word in words:
                if word in text_lower:
                    scores[emotion] += 0.3
                    matched_any = True
                    
        # Normalize the scores so they sum to 1.0
        total = sum(scores.values())
        if total > 0:
            for emotion in scores:
                scores[emotion] = round(scores[emotion] / total, 4)
                
        return scores
