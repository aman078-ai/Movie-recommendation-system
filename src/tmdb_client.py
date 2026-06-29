import logging
import requests
from typing import List, Dict, Any
from src.config import TMDB_API_KEY, TMDB_BASE_URL

logger = logging.getLogger(__name__)

class TMDBClient:
    """Interacts with the TMDB API to discover movies by genre."""
    
    def __init__(self, api_key: str = TMDB_API_KEY):
        self.api_key = api_key.strip()
        self.base_url = TMDB_BASE_URL

    @property
    def is_configured(self) -> bool:
        """Checks if the client has a non-empty API key."""
        return len(self.api_key) > 0

    def discover_movies_by_genres(
        self, 
        genre_ids: List[int], 
        min_rating: float = 6.0, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Discovers movies on TMDB that belong to one or more of the specified genres.
        
        Args:
            genre_ids: List of TMDB genre IDs to filter by.
            min_rating: Minimum vote average rating.
            limit: Maximum number of movies to return (capped at page 1 results, max 20).
            
        Returns:
            A list of movie dictionaries.
        """
        if not self.is_configured:
            logger.info("TMDB API key not configured. Skipping TMDB fetch.")
            return []
            
        if not genre_ids:
            return []

        # Join genre IDs with '|' representing logical OR in TMDB discover
        genres_query = "|".join(str(gid) for gid in genre_ids)
        
        url = f"{self.base_url}/discover/movie"
        params = {
            "api_key": self.api_key,
            "with_genres": genres_query,
            "sort_by": "popularity.desc",
            "vote_average.gte": min_rating,
            "vote_count.gte": 100,  # Ensure it has been rated by a decent number of users
            "language": "en-US",
            "include_adult": "false"
        }
        
        try:
            logger.info(f"Querying TMDB API for genres: {genres_query}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 401:
                logger.error("TMDB API Key is invalid (401 Unauthorized).")
                return []
                
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            movies = []
            
            for item in results[:limit]:
                movies.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "genres": item.get("genre_ids", []),
                    "vote_average": item.get("vote_average", 0.0),
                    "popularity": item.get("popularity", 0.0),
                    "overview": item.get("overview", ""),
                    "release_date": item.get("release_date", ""),
                    "poster_path": item.get("poster_path", "")
                })
            
            logger.info(f"Successfully retrieved {len(movies)} movies from TMDB.")
            return movies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query TMDB API due to request error: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred during TMDB search: {e}")
            return []
