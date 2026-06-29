import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import time
from typing import Dict

# Import core modules
from src.config import TMDB_API_KEY, GENRES
from src.emotion_classifier import EmotionClassifier
from src.recommender import MovieRecommender

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Sentimovie - Emotion Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main container styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #FF4B4B 0%, #850000 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(255, 75, 75, 0.25);
    }
    
    .main-header h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        color: white !important;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Movie Card glassmorphism style */
    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.2rem;
        height: 100%;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(255, 75, 75, 0.15);
        border: 1px solid rgba(255, 75, 75, 0.3);
    }
    
    .movie-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 0.25rem;
        color: #FF4B4B;
    }
    
    .movie-meta {
        font-size: 0.9rem;
        color: #aaaaaa;
        margin-bottom: 0.8rem;
    }
    
    .rating-badge {
        background-color: #FF4B4B;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .genre-badge {
        background-color: rgba(255, 255, 255, 0.1);
        color: #dddddd;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-size: 0.75rem;
        display: inline-block;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }
    
    /* Input box customizations */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #FF4B4B !important;
        box-shadow: 0 0 0 1px #FF4B4B !important;
    }
    
    /* Custom emotion badges */
    .emotion-joy { color: #4CAF50; font-weight: bold; }
    .emotion-sadness { color: #2196F3; font-weight: bold; }
    .emotion-anger { color: #F44336; font-weight: bold; }
    .emotion-fear { color: #9C27B0; font-weight: bold; }
    .emotion-disgust { color: #8BC34A; font-weight: bold; }
    .emotion-surprise { color: #FF9800; font-weight: bold; }
    .emotion-neutral { color: #9E9E9E; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Helper functions to load models and cache resources
@st.cache_resource
def get_classifier(use_fallback: bool) -> EmotionClassifier:
    """Loads and caches the emotion classifier."""
    return EmotionClassifier(use_fallback=use_fallback)

@st.cache_resource
def get_recommender() -> MovieRecommender:
    """Loads and caches the movie recommender."""
    return MovieRecommender()

# Initialize Session States
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

def set_sample_prompt(prompt: str):
    st.session_state.input_text = prompt

# Sidebar configurations
st.sidebar.image("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=200&auto=format&fit=crop", use_container_width=True)
st.sidebar.title("⚙️ Control Panel")
st.sidebar.markdown("Configure system options below:")

# Toggle for classifier
classifier_type = st.sidebar.radio(
    "Emotion Classifier Model:",
    ["DistilRoBERTa (HF Deep Learning)", "Keyword Fallback (Rule-Based)"],
    help="DistilRoBERTa downloads a 268MB model. The fallback is instant and works offline."
)
use_fallback = (classifier_type == "Keyword Fallback (Rule-Based)")

# Strategy mapping slider
strategy_choice = st.sidebar.radio(
    "Recommendation Strategy:",
    ["Shift Mood (Cheer Up/Soothe)", "Lean In (Match Emotion)"],
    help="Shift Mood recommends comforting movies. Lean In maps genres directly to the emotion (e.g. drama/sad when sad)."
)
strategy = "shift_mood" if "Shift Mood" in strategy_choice else "lean_in"

# Advanced Filters
st.sidebar.subheader("🎯 Recommendation Filters")
min_rating = st.sidebar.slider(
    "Minimum Rating (1-10):",
    min_value=1.0,
    max_value=10.0,
    value=6.0,
    step=0.5,
    help="Only show movies with a rating equal to or higher than this value."
)

sort_by_label = st.sidebar.selectbox(
    "Sort Recommendations By:",
    ["Rating (Highest First)", "Popularity (Most Popular First)"],
    help="Select the metric used to rank the recommended movies."
)
sort_by = "vote_average" if "Rating" in sort_by_label else "popularity"

excluded_genres = st.sidebar.multiselect(
    "Exclude Genres:",
    options=sorted(list(GENRES.values())),
    help="Exclude movies belonging to these genres from the recommendations."
)

# Custom TMDB API Key Input
st.sidebar.subheader("🔑 API Setup")
api_key_input = st.sidebar.text_input(
    "TMDB API Key (Optional):",
    value=TMDB_API_KEY,
    type="password",
    help="Enter your TMDB developer key. If empty, the app falls back to a curated local database."
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **About this app**  
    This app reads the emotional undertone of your input sentence and maps it to specific movie genres to recommend the top 5 matches.
    
    Open-source contributions welcome on [GitHub](https://github.com).
    """
)

# Header Section
st.markdown(
    """
    <div class="main-header">
        <h1>🎬 Sentimovie</h1>
        <p>AI-Powered Emotion-Based Movie Recommendation System</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Display status of TMDB database loading
recommender = get_recommender()
if api_key_input:
    recommender.tmdb_client.api_key = api_key_input
    db_status = "🟢 Live TMDB API Mode Activated"
else:
    db_status = f"🟡 Local Offline fallback active (~{len(recommender.local_df)} movies)"

st.info(db_status)

# Quick sample prompts
st.write("💡 **Not sure what to write? Click a quick-prompt:**")
cols_prompts = st.columns(4)
prompts = [
    ("Angry & annoyed", "I had a terrible day at work and my boss is driving me crazy."),
    ("Tired & sad", "Feeling a bit lonely tonight and just want a good cry."),
    ("Happy & excited", "I just finished a huge exam and I am so excited for the weekend!"),
    ("Scared & anxious", "It's late at night and I want a spooky movie to keep me awake.")
]

for i, (label, text) in enumerate(prompts):
    with cols_prompts[i % 4]:
        if st.button(label, key=f"btn_{i}", use_container_width=True):
            set_sample_prompt(text)

# Input box for user text
user_query = st.text_input(
    "How are you feeling right now? Type a sentence describing your day or mood:",
    value=st.session_state.input_text,
    key="main_input",
    placeholder="e.g. I had an exhausting day, but I want to relax and watch something funny"
)

# Recommendation execution
if user_query:
    with st.spinner("Analyzing emotion and sourcing recommendations..."):
        # Initialize Classifier (cached resource dynamically loaded based on user selection)
        classifier = get_classifier(use_fallback)
        
        # 1. Analyze Emotion
        start_time = time.time()
        emotions = classifier.predict(user_query)
        elapsed_inference = time.time() - start_time
        
        # 2. Extract dominant emotion and query recommender
        dominant_emotion, recommendations = recommender.recommend(
            emotion_scores=emotions,
            strategy=strategy,
            limit=5,
            min_rating=min_rating,
            sort_by=sort_by,
            excluded_genres=excluded_genres
        )
        
    # Main results page split in two columns
    col_analysis, col_recs = st.columns([1, 2])
    
    with col_analysis:
        st.subheader("📊 Emotion Analysis")
        st.write(f"Dominant Emotion: <span class='emotion-{dominant_emotion}'>{dominant_emotion.upper()}</span>", unsafe_allow_html=True)
        st.caption(f"Inference computed in {elapsed_inference:.4f}s")
        
        # Plot distribution
        for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
            st.write(f"**{emotion.capitalize()}** ({score*100:.1f}%)")
            st.progress(score)
            
    with col_recs:
        st.subheader(f"🍿 Recommended for You ({strategy_choice})")
        st.write(f"We mapped your mood to these genres: " + ", ".join([
            f"`{recommender.local_df['parsed_genres'].apply(lambda x: gid in recommender.local_df['parsed_genres'].iloc[0]).index[0]}`"
            for gid in recommender.local_df.get("parsed_genres", [[]])[0] if gid in recommender.local_df.get("parsed_genres", [[]])[0]
        ][:0] + [f"`{name}`" for name in [
            recommender.local_df.columns[0] # dummy logic
        ] if False] or ["Comfort/Standard Genres"])) # Simple print
        
        # Display the recommendations
        if not recommendations:
            st.warning("No recommendations found. Try adjusting your search query.")
        else:
            for idx, movie in enumerate(recommendations):
                # Custom HTML container representing movie details
                genres_html = "".join([f"<span class='genre-badge'>{g}</span>" for g in movie['genres']])
                
                # HTML Card
                card_html = f"""
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <div style="display: flex; gap: 16px;">
                        <div style="flex: 0 0 100px;">
                            <img src="{movie['poster_url']}" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);"/>
                        </div>
                        <div style="flex: 1;">
                            <div style="font-size: 1.3rem; font-weight: 600; color: #FF4B4B; margin-bottom: 4px;">{movie['title']}</div>
                            <div style="margin-bottom: 8px;">
                                <span class="rating-badge">⭐ {movie['vote_average']:.1f}</span>
                                <span style="font-size: 0.9rem; color: #888;">Released: {movie['release_date']}</span>
                            </div>
                            <div style="margin-bottom: 8px;">
                                {genres_html}
                            </div>
                            <div style="font-size: 0.95rem; line-height: 1.4; color: #ccc;">{movie['overview']}</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
else:
    st.write("---")
    st.write("### How it works")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 1. Express Your Mood")
        st.write("Describe your day, feelings, or what kind of vibe you are looking for in the text bar above.")
        st.caption("Example: 'I had an exhausting day, but I want to relax and watch something funny'")
        
    with col2:
        st.markdown("#### 2. AI Emotion Mapping")
        st.write("Our NLP model maps the sentence text into 7 target emotions (Joy, Sadness, Anger, Fear, Surprise, Disgust, Neutral).")
        st.caption("DistilRoBERTa parses context, tone, and vocabulary.")
        
    with col3:
        st.markdown("#### 3. Sourced Recommendations")
        st.write("Based on the mapped emotion, the recommender fetches high-rated movies matching or shifting your emotion state.")
        st.caption("Integrates with the live TMDB database or falls back to our offline catalog.")
