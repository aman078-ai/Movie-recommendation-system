import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_PATH = DATA_DIR / "movies.csv"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# API Configurations
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# ML Model Configuration
HF_MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"

# TMDB Genre ID Mapping
# Source: https://developer.themoviedb.org/reference/genre-movie-list
GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}

# Invert genre mapping for text queries
GENRE_NAME_TO_ID = {name.lower(): gid for gid, name in GENRES.items()}

# Emotion to Genre mapping strategies
# Lean In: Match the emotion directly (e.g. watch a sad movie to cry, or horror when scared)
# Shift Mood: Transform the emotion (e.g. watch comedy when sad to cheer up)
EMOTION_GENRE_MAPPING = {
    "anger": {
        "lean_in": [18, 53, 28],      # Drama, Thriller, Action (intense themes to channel energy)
        "shift_mood": [35, 10751, 10402] # Comedy, Family, Music (relaxing and lighthearted)
    },
    "disgust": {
        "lean_in": [27, 80, 99],       # Horror, Crime, Documentary (exploring gritty/raw concepts)
        "shift_mood": [35, 12, 14]       # Comedy, Adventure, Fantasy (escapist, refreshing)
    },
    "fear": {
        "lean_in": [27, 53, 9648],      # Horror, Thriller, Mystery (lean into the thrill)
        "shift_mood": [35, 10751, 16]    # Comedy, Family, Animation (comforting, lighthearted)
    },
    "joy": {
        "lean_in": [35, 12, 10749, 10751], # Comedy, Adventure, Romance, Family (keep the good vibes)
        "shift_mood": [9648, 878, 18]   # Mystery, Sci-Fi, Drama (reflective, deeper topics)
    },
    "neutral": {
        "lean_in": [18, 9648, 878],    # Drama, Mystery, Sci-Fi (cerebral, thought-provoking)
        "shift_mood": [28, 12, 53]      # Action, Adventure, Thriller (exciting, high pacing)
    },
    "sadness": {
        "lean_in": [18, 10749],         # Drama, Romance (cathartic cry, emotional connection)
        "shift_mood": [35, 10751, 16]    # Comedy, Family, Animation (cheering up, laughter)
    },
    "surprise": {
        "lean_in": [9648, 878, 53],     # Mystery, Sci-Fi, Thriller (plot twists, mind-benders)
        "shift_mood": [10751, 10749, 99] # Family, Romance, Documentary (grounded, comforting)
    }
}
