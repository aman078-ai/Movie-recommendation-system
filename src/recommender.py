import json
import logging
import pandas as pd
from typing import List, Dict, Any, Tuple
from src.config import DATA_PATH, EMOTION_GENRE_MAPPING, GENRES, TMDB_IMAGE_BASE_URL
from src.tmdb_client import TMDBClient

logger = logging.getLogger(__name__)

class MovieRecommender:
    """Core recommendation engine combining TMDB live fetching and local CSV fallback."""
    
    def __init__(self, data_path: str = str(DATA_PATH)):
        self.data_path = data_path
        self.tmdb_client = TMDBClient()
        self.local_df = self._load_local_dataset()

    def _load_local_dataset(self) -> pd.DataFrame:
        """Loads and parses the local fallback movies dataset."""
        try:
            logger.info(f"Loading local movie database from {self.data_path}...")
            df = pd.read_csv(self.data_path)
            
            # Safely parse the genres column which is stored as string representation of lists (e.g. "[28, 80]")
            def parse_genres(genre_str: Any) -> List[int]:
                if pd.isna(genre_str):
                    return []
                if isinstance(genre_str, list):
                    return genre_str
                try:
                    # Try to parse stringified list of IDs
                    return [int(x) for x in json.loads(str(genre_str))]
                except Exception:
                    # Fallback parser for poorly formatted lists
                    try:
                        clean_str = str(genre_str).strip("[]").replace(" ", "")
                        if not clean_str:
                            return []
                        return [int(x) for x in clean_str.split(",") if x.isdigit()]
                    except Exception as e:
                        logger.warning(f"Failed to parse genre string '{genre_str}': {e}")
                        return []
                        
            df["parsed_genres"] = df["genres"].apply(parse_genres)
            logger.info(f"Successfully loaded {len(df)} local movies.")
            return df
        except Exception as e:
            logger.error(f"Failed to load local movies dataset: {e}")
            # Return empty DataFrame with required columns to prevent crashes
            return pd.DataFrame(columns=[
                "id", "title", "genres", "vote_average", "popularity", 
                "overview", "release_date", "poster_path", "parsed_genres"
            ])

    def recommend(
        self, 
        emotion_scores: Dict[str, float], 
        strategy: str = "shift_mood", 
        limit: int = 5
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Recommends movies based on the classified emotion.
        
        Args:
            emotion_scores: Dict mapping emotion to probability confidence.
            strategy: Either "lean_in" (matching genre) or "shift_mood" (uplifting genre).
            limit: Number of recommendations to return.
            
        Returns:
            A tuple of (dominant_emotion, list of recommended movie dicts).
        """
        if not emotion_scores:
            return "neutral", []
            
        # Determine the dominant emotion (highest score)
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        logger.info(f"Dominant emotion detected: '{dominant_emotion}' with strategy: '{strategy}'")
        
        # Get target genre IDs mapping to this emotion & strategy
        mapping = EMOTION_GENRE_MAPPING.get(dominant_emotion, EMOTION_GENRE_MAPPING["neutral"])
        target_genre_ids = mapping.get(strategy, mapping["shift_mood"])
        
        movies = []
        
        # 1. Attempt to fetch from live TMDB API if configured
        if self.tmdb_client.is_configured:
            try:
                movies = self.tmdb_client.discover_movies_by_genres(
                    genre_ids=target_genre_ids,
                    min_rating=6.0,
                    limit=20
                )
            except Exception as e:
                logger.error(f"Live TMDB discover failed: {e}. Falling back to local search.")
                movies = []
                
        # 2. Fall back to local dataset if TMDB is offline or not configured
        if not movies:
            logger.info("Using local dataset to generate recommendations.")
            movies = self._search_local_movies(target_genre_ids, limit=20)
            
        # 3. Format and enrich recommended movies
        formatted_recommendations = []
        for movie in movies[:limit]:
            # Convert genre IDs to human-readable names
            genre_ids = movie.get("genres", [])
            genre_names = [GENRES.get(gid, "Unknown") for gid in genre_ids if gid in GENRES]
            
            # Resolve poster URL
            poster_path = movie.get("poster_path", "")
            if poster_path:
                if poster_path.startswith("http"):
                    poster_url = poster_path
                else:
                    poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}"
            else:
                # Default placeholder image URL
                poster_url = "https://images.unsplash.com/photo-1542204172-e7052809a936?q=80&w=300&auto=format&fit=crop"
                
            formatted_recommendations.append({
                "id": movie.get("id"),
                "title": movie.get("title", "Untitled"),
                "genres": genre_names,
                "vote_average": movie.get("vote_average", 0.0),
                "popularity": movie.get("popularity", 0.0),
                "overview": movie.get("overview", "No synopsis available."),
                "release_date": movie.get("release_date", "N/A"),
                "poster_url": poster_url
            })
            
        return dominant_emotion, formatted_recommendations

    def _search_local_movies(self, genre_ids: List[int], limit: int = 20) -> List[Dict[str, Any]]:
        """Filters and ranks the local dataset by target genres."""
        if self.local_df.empty:
            return []
            
        # Filter movies where at least one genre ID matches target_genre_ids
        def has_matching_genre(movie_genres: List[int]) -> bool:
            return any(gid in genre_ids for gid in movie_genres)
            
        matched_mask = self.local_df["parsed_genres"].apply(has_matching_genre)
        filtered_df = self.local_df[matched_mask].copy()
        
        if filtered_df.empty:
            # If no matches, return top movies generally
            logger.warning(f"No local movies found for genres {genre_ids}. Returning top local movies.")
            filtered_df = self.local_df.copy()
            
        # Rank by vote_average descending, popularity descending
        ranked_df = filtered_df.sort_values(
            by=["vote_average", "popularity"], 
            ascending=[False, False]
        )
        
        results = []
        for _, row in ranked_df.head(limit).iterrows():
            results.append({
                "id": int(row["id"]),
                "title": str(row["title"]),
                "genres": row["parsed_genres"],
                "vote_average": float(row["vote_average"]),
                "popularity": float(row["popularity"]),
                "overview": str(row["overview"]),
                "release_date": str(row["release_date"]),
                "poster_path": str(row["poster_path"]) if not pd.isna(row["poster_path"]) else ""
            })
            
        return results
