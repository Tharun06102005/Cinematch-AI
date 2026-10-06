"""
CineMatch-AI Recommender System
--------------------------------
Uses TF-IDF vectorization and cosine similarity on movie genres
to recommend movies based on mood and available watch time.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------- Configuration --------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MOVIES_FILE = os.path.join(DATA_DIR, "movies.csv")
RATINGS_FILE = os.path.join(DATA_DIR, "ratings.csv")

DEFAULT_RUNTIME_MIN = 100  # average movie runtime estimate in minutes
RUNTIME_RANGE = (90, 120)  # estimated runtime range when no runtime column exists

# -------------------- Mood-to-Genre Mapping --------------------
MOOD_GENRE_MAP = {
    "happy": ["Comedy", "Animation", "Family"],
    "sad": ["Drama", "Romance"],
    "angry": ["Action", "Thriller"],
    "stressed": ["Comedy", "Music", "Animation"],
    "surprised": ["Mystery", "Sci-Fi", "Fantasy"],
    "neutral": ["Adventure", "Documentary"],
}

# Global variables (loaded once at import time)
_movies_df = None
_ratings_df = None
_tfidf_matrix = None
_tfidf_vectorizer = None
_cosine_sim = None
_movie_indices = None


# -------------------- Data Loading --------------------
def load_data():
    """
    Load movies and ratings DataFrames from CSV files.
    Handles common MovieLens column naming variations.
    Returns (movies_df, ratings_df).
    """
    global _movies_df, _ratings_df

    try:
        _movies_df = pd.read_csv(MOVIES_FILE)
        print(f"[INFO] Loaded {len(_movies_df)} movies from {MOVIES_FILE}")
    except FileNotFoundError:
        print(f"[ERROR] Movies file not found at {MOVIES_FILE}")
        _movies_df = pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] Failed to load movies: {e}")
        _movies_df = pd.DataFrame()

    try:
        _ratings_df = pd.read_csv(RATINGS_FILE)
        print(f"[INFO] Loaded {len(_ratings_df)} ratings from {RATINGS_FILE}")
    except FileNotFoundError:
        print(f"[ERROR] Ratings file not found at {RATINGS_FILE}")
        _ratings_df = pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] Failed to load ratings: {e}")
        _ratings_df = pd.DataFrame()

    return _movies_df, _ratings_df


# -------------------- TF-IDF & Cosine Similarity --------------------
def build_similarity_matrix():
    """
    Build TF-IDF matrix from movie genres and compute cosine similarity.
    Stores results in global variables for reuse.
    """
    global _tfidf_matrix, _tfidf_vectorizer, _cosine_sim, _movie_indices

    if _movies_df is None or _movies_df.empty:
        print("[WARN] No movies data available to build similarity matrix.")
        return

    try:
        # Ensure a 'genres' column exists (handle common variations)
        genre_column = None
        for col in ["genres", "genre", "Genres", "Genre"]:
            if col in _movies_df.columns:
                genre_column = col
                break

        if genre_column is None:
            # Create a default genre column
            _movies_df["genres"] = ""
            print("[WARN] No genre column found. Using empty genres.")
        else:
            if genre_column != "genres":
                _movies_df["genres"] = _movies_df[genre_column].fillna("")

        # Fill missing genres with empty string
        _movies_df["genres"] = _movies_df["genres"].fillna("")

        # Build TF-IDF matrix
        _tfidf_vectorizer = TfidfVectorizer(
            stop_words="english",
            token_pattern=r"(?u)\b[A-Za-z][A-Za-z\-]+\b",
        )
        _tfidf_matrix = _tfidf_vectorizer.fit_transform(_movies_df["genres"])

        # Compute cosine similarity matrix
        _cosine_sim = cosine_similarity(_tfidf_matrix, _tfidf_matrix)

        # Build index mapping: title -> row index
        title_column = None
        for col in ["title", "Title", "movie_title", "Movie_Title"]:
            if col in _movies_df.columns:
                title_column = col
                break

        if title_column is None:
            _movie_indices = pd.Series(range(len(_movies_df)), index=range(len(_movies_df)))
            print("[WARN] No title column found. Creating default index.")
        else:
            # Create a clean title series for lookup (lowercased, stripped)
            _movies_df["_clean_title"] = _movies_df[title_column].astype(str).str.strip().str.lower()
            _movie_indices = pd.Series(
                _movies_df.index,
                index=_movies_df["_clean_title"],
            )

        print(f"[INFO] Built similarity matrix for {_tfidf_matrix.shape[0]} movies.")

    except Exception as e:
        print(f"[ERROR] Failed to build similarity matrix: {e}")
        _tfidf_matrix = None
        _cosine_sim = None
        _movie_indices = None


# -------------------- Recommendation Functions --------------------
def get_recommendations(mood, watch_time_minutes=120):
    """
    Recommend movies based on mood and available watch time.

    Parameters
    ----------
    mood : str
        One of: 'happy', 'sad', 'angry', 'stressed', 'surprised', 'neutral'
    watch_time_minutes : int
        Approximate minutes the user has to watch.

    Returns
    -------
    list[dict]
        Top 10 movies as dicts with keys: title, genres, score, estimated_runtime
    """
    try:
        mood = mood.strip().lower()

        if _movies_df is None or _movies_df.empty:
            load_data()
            build_similarity_matrix()

        if _movies_df is None or _movies_df.empty:
            return []

        # 1. Determine genres for this mood
        matching_genres = MOOD_GENRE_MAP.get(mood, [])
        if not matching_genres:
            print(f"[WARN] Unknown mood '{mood}'. Returning top-rated movies instead.")
            return _get_fallback_recommendations(watch_time_minutes)

        # 2. Filter movies by mood-mapped genres
        def matches_mood(genres_str):
            """Check if at least one mood genre appears in the movie's genre string."""
            genres_str_lower = str(genres_str).lower()
            return any(g.lower() in genres_str_lower for g in matching_genres)

        mask = _movies_df["genres"].apply(matches_mood)
        mood_movies = _movies_df[mask].copy()

        if mood_movies.empty:
            print(f"[WARN] No movies found for mood '{mood}'. Returning top-rated fallback.")
            return _get_fallback_recommendations(watch_time_minutes)

        # 3. Filter by watch time (use runtime column if available, otherwise estimate)
        mood_movies["estimated_runtime"] = _estimate_runtime(mood_movies)

        time_mask = mood_movies["estimated_runtime"] <= watch_time_minutes
        filtered = mood_movies[time_mask]

        # If no movies fit the time constraint, relax it
        if filtered.empty:
            filtered = mood_movies
            print(f"[INFO] No movies under {watch_time_minutes} mins for '{mood}'; relaxing time constraint.")

        # 4. Score movies using average rating (if available)
        filtered = _compute_scores(filtered)

        # 5. Sort by score descending and return top 10
        filtered = filtered.sort_values("score", ascending=False).head(10)

        # 6. Format results
        title_column = _resolve_title_column()
        results = []
        for _, row in filtered.iterrows():
            results.append({
                "title": str(row.get(title_column, "Unknown")),
                "genres": str(row.get("genres", "")),
                "score": round(float(row["score"]), 4),
                "estimated_runtime": int(row["estimated_runtime"]),
            })

        print(f"[INFO] Recommended {len(results)} movies for mood '{mood}' (≤{watch_time_minutes} mins).")
        return results

    except Exception as e:
        print(f"[ERROR] get_recommendations failed: {e}")
        return []


def get_similar_movies(movie_title):
    """
    Find movies similar to the given title using cosine similarity.

    Parameters
    ----------
    movie_title : str
        Title of the movie to find similar movies for.

    Returns
    -------
    list[dict]
        Top 5 similar movies as dicts with keys: title, genres, score, estimated_runtime
    """
    try:
        if _cosine_sim is None:
            load_data()
            build_similarity_matrix()

        if _cosine_sim is None:
            return []

        title_column = _resolve_title_column()
        clean_title = movie_title.strip().lower()

        # Find the movie index
        if clean_title in _movie_indices.index:
            idx = _movie_indices[clean_title]
        else:
            # Try partial matching
            matches = _movie_indices[
                _movie_indices.index.str.contains(clean_title, na=False)
            ]
            if matches.empty:
                print(f"[WARN] Movie '{movie_title}' not found in dataset.")
                return []
            idx = matches.iloc[0]
            found_title = _movies_df.loc[idx, title_column]
            print(f"[INFO] Partial match: '{movie_title}' -> '{found_title}'")

        # Get similarity scores for this movie
        sim_scores = list(enumerate(_cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Skip the first result (itself), take the next 5
        sim_scores = sim_scores[1:6]

        # Format results with actual cosine similarity scores
        title_column = _resolve_title_column()
        results = []
        for movie_idx, sim_score in sim_scores:
            movie_row = _movies_df.iloc[movie_idx]
            est_runtime = _estimate_runtime(pd.DataFrame([movie_row])).iloc[0]
            results.append({
                "title": str(movie_row.get(title_column, "Unknown")),
                "genres": str(movie_row.get("genres", "")),
                "score": round(sim_score, 4),
                "estimated_runtime": int(est_runtime),
            })

        print(f"[INFO] Found {len(results)} similar movies for '{movie_title}'.")
        return results

    except Exception as e:
        print(f"[ERROR] get_similar_movies failed: {e}")
        return []


# -------------------- Helper Functions --------------------
def _resolve_title_column():
    """Return the actual title column name in the movies DataFrame."""
    for col in ["title", "Title", "movie_title", "Movie_Title"]:
        if col in _movies_df.columns:
            return col
    return "title"


def _estimate_runtime(df):
    """
    Estimate runtime for each movie.
    If a runtime column exists, use it; otherwise return a random value
    within the average range to add variety.
    """
    runtime_col = None
    for col in ["runtime", "Runtime", "running_time", "length"]:
        if col in df.columns:
            runtime_col = col
            break

    if runtime_col:
        return df[runtime_col].fillna(DEFAULT_RUNTIME_MIN)
    else:
        # Return a deterministic spread of runtimes based on index for consistency
        # Spread values between 90 and 120 minutes (as specified)
        return df.index.to_series().apply(
            lambda i: RUNTIME_RANGE[0] + (hash(str(i)) % (RUNTIME_RANGE[1] - RUNTIME_RANGE[0] + 1))
        )


def _compute_scores(df):
    """
    Compute a recommendation score for each movie.
    Uses average rating from ratings.csv if available, otherwise uses
    a baseline score derived from genre TF-IDF magnitude.
    """
    if _ratings_df is not None and not _ratings_df.empty:
        # Find movie ID column names
        movie_id_col = None
        for col in ["movieId", "movie_id", "MovieID", "item_id"]:
            if col in _ratings_df.columns:
                movie_id_col = col
                break

        rating_col = None
        for col in ["rating", "Rating"]:
            if col in _ratings_df.columns:
                rating_col = col
                break

        if movie_id_col and rating_col:
            # Find movie ID column in movies
            movie_id_col_movies = None
            for col in ["movieId", "movie_id", "MovieID", "item_id"]:
                if col in df.columns:
                    movie_id_col_movies = col
                    break

            if movie_id_col_movies:
                avg_ratings = (
                    _ratings_df.groupby(movie_id_col)[rating_col]
                    .mean()
                    .reset_index()
                )
                df = df.merge(
                    avg_ratings, left_on=movie_id_col_movies, right_on=movie_id_col, how="left"
                )
                df["score"] = df[rating_col].fillna(5.0)  # default to average
                return df

    # Fallback: use a baseline score
    df["score"] = 5.0
    return df


def _get_fallback_recommendations(watch_time_minutes=120):
    """
    Return top-rated movies as a fallback when mood-based filtering fails.
    """
    try:
        if _ratings_df is not None and not _ratings_df.empty:
            # Find the right columns
            movie_id_col = None
            for col in ["movieId", "movie_id", "MovieID"]:
                if col in _ratings_df.columns:
                    movie_id_col = col
                    break

            rating_col = None
            for col in ["rating", "Rating"]:
                if col in _ratings_df.columns:
                    rating_col = col
                    break

            if movie_id_col and rating_col:
                avg_ratings = (
                    _ratings_df.groupby(movie_id_col)[rating_col]
                    .mean()
                    .reset_index()
                )

                # Merge with movies
                movie_id_col_movies = None
                for col in ["movieId", "movie_id", "MovieID"]:
                    if col in _movies_df.columns:
                        movie_id_col_movies = col
                        break

                if movie_id_col_movies:
                    merged = _movies_df.merge(
                        avg_ratings,
                        left_on=movie_id_col_movies,
                        right_on=movie_id_col,
                        how="inner",
                    )
                    merged["estimated_runtime"] = _estimate_runtime(merged)
                    merged = merged[merged["estimated_runtime"] <= watch_time_minutes]
                    merged = merged.sort_values(rating_col, ascending=False).head(10)

                    title_column = _resolve_title_column()
                    results = []
                    for _, row in merged.iterrows():
                        results.append({
                            "title": str(row.get(title_column, "Unknown")),
                            "genres": str(row.get("genres", "")),
                            "score": round(float(row[rating_col]), 4),
                            "estimated_runtime": int(row["estimated_runtime"]),
                        })
                    return results

        # Ultimate fallback: return some movies with default scores
        title_column = _resolve_title_column()
        fallback = _movies_df.head(10).copy()
        fallback["estimated_runtime"] = _estimate_runtime(fallback)
        results = []
        for _, row in fallback.iterrows():
            results.append({
                "title": str(row.get(title_column, "Unknown")),
                "genres": str(row.get("genres", "")),
                "score": 5.0,
                "estimated_runtime": int(row["estimated_runtime"]),
            })
        return results

    except Exception as e:
        print(f"[ERROR] Fallback recommendations failed: {e}")
        return []


# -------------------- Initialization --------------------
# Load data and build the similarity matrix when the module is imported
load_data()
build_similarity_matrix()
print("Recommender loaded successfully")
