"""
Explainer Module for CineMatch-AI

Generates human-readable explanations and AI recommendation cards
with confidence scoring based on mood, weather, time, and history matches.
"""

from emotion import get_genre_from_emotion
from weather import get_genre_from_weather


# ============================================================
#  Confidence Label Thresholds
# ============================================================

def get_confidence_label(score):
    """
    Convert a numeric confidence score (0-100) into a human-readable label.

    Args:
        score (int or float): Confidence score out of 100.

    Returns:
        str: One of "Perfect Match", "Great Match", "Good Match", or "Suggested Pick".
    """
    try:
        if score >= 80:
            return "Perfect Match"
        elif score >= 60:
            return "Great Match"
        elif score >= 40:
            return "Good Match"
        else:
            return "Suggested Pick"
    except Exception:
        return "Suggested Pick"


# ============================================================
#  Match-Check Helpers
# ============================================================

def _check_mood_match(movie_genres, mood):
    """
    Check if the movie's genres match the mood-to-genre mapping.

    Args:
        movie_genres (list): List of genre strings for the movie.
        mood (str): User's current mood.

    Returns:
        tuple: (bool, list) — whether there's a mood match and which mood genres are recommended.
    """
    try:
        if not movie_genres or not mood:
            return False, []
        mood_genres = get_genre_from_emotion(mood)
        match = any(g.lower() in [mg.lower() for mg in mood_genres] for g in movie_genres)
        return match, mood_genres
    except Exception:
        return False, []


def _check_weather_match(movie_genres, weather_condition):
    """
    Check if the movie's genres match the weather-to-genre mapping.

    Args:
        movie_genres (list): List of genre strings for the movie.
        weather_condition (str): Current weather description.

    Returns:
        tuple: (bool, list) — whether there's a weather match and which weather genres are recommended.
    """
    try:
        if not movie_genres or not weather_condition:
            return False, []

        weather_genres = get_genre_from_weather(weather_condition)
        if not weather_genres:
            return False, []

        movie_genres_lower = [g.lower() for g in movie_genres]
        match = any(g.lower() in movie_genres_lower for g in weather_genres)
        return match, weather_genres
    except Exception:
        return False, []


def _check_time_match(movie_runtime_minutes, watch_time_minutes):
    """
    Check if the movie runtime fits within the available watch time.

    Args:
        movie_runtime_minutes (int or float): Movie runtime in minutes.
        watch_time_minutes (int or float): Available watch time in minutes.

    Returns:
        bool: True if movie fits within the time budget.
    """
    try:
        if not movie_runtime_minutes or not watch_time_minutes:
            return False
        return float(movie_runtime_minutes) <= float(watch_time_minutes)
    except Exception:
        return False


# ============================================================
#  Explanation Generation
# ============================================================

def generate_explanation(movie_title, mood, weather_condition, watch_time, similar_to=None):
    """
    Generate a human-readable explanation string for why a movie is recommended.

    Args:
        movie_title (str): Title of the recommended movie.
        mood (str): User's detected or selected mood.
        weather_condition (str): Current weather description.
        watch_time (int or float): Available watch time in minutes.
        similar_to (str, optional): A movie title the user has watched before.

    Returns:
        str: A human-readable explanation.
    """
    try:
        parts = []

        if weather_condition:
            parts.append(f"{weather_condition.capitalize()} weather")

        if mood:
            parts.append(f"{mood} mood")

        if watch_time:
            hours = int(watch_time) // 60
            minutes = int(watch_time) % 60
            if hours > 0 and minutes > 0:
                time_str = f"{hours}h {minutes}m watch time"
            elif hours > 0:
                time_str = f"{hours}hr watch time"
            else:
                time_str = f"{minutes}min watch time"
            parts.append(f"Fits in your {time_str}")

        if similar_to:
            parts.append(f"You liked {similar_to}")

        if parts:
            explanation = "Recommended because: " + " + ".join(parts)
        else:
            explanation = f"Recommended: {movie_title}"

        return explanation

    except Exception as e:
        return f"Recommended: {movie_title} (based on your preferences)"


# ============================================================
#  AI Recommendation Card
# ============================================================

def generate_ai_card(movie, mood, weather, watch_time):
    """
    Generate a complete AI recommendation card for a movie.

    The 'movie' parameter is expected to be a dictionary with at least:
        - title (str)
        - genres (list of str)
        - runtime (int or float, in minutes)
        - (optional) vote_average (float)
        - (optional) overview (str)

    Args:
        movie (dict): Movie data dictionary.
        mood (str): User's mood.
        weather (str or dict): Weather condition string or dict with 'weather_condition' key.
        watch_time (int or float): Available watch time in minutes.

    Returns:
        dict: A dictionary with keys:
            - title, explanation, mood_match, weather_match,
              time_match, confidence_score, confidence_label
    """
    try:
        # Extract movie info
        title = movie.get("title", "Unknown")
        genres = movie.get("genres", [])
        runtime = movie.get("runtime", 0)

        # Extract weather condition string
        if isinstance(weather, dict):
            weather_condition = weather.get("weather_condition", "")
        else:
            weather_condition = str(weather) if weather else ""

        # Check each match dimension
        mood_match, mood_genres = _check_mood_match(genres, mood)
        weather_match, weather_genres = _check_weather_match(genres, weather_condition)
        time_match = _check_time_match(runtime, watch_time)

        # Calculate confidence score
        # Base score
        score = 0
        if mood_match:
            score += 40
        if weather_match:
            score += 30
        if time_match:
            score += 20

        # History bonus (optional: can be extended)
        similar_to = movie.get("similar_to")
        if similar_to:
            score += 10

        # Cap at 100
        confidence_score = min(score, 100)
        confidence_label = get_confidence_label(confidence_score)

        # Generate explanation
        explanation = generate_explanation(
            title, mood, weather_condition, watch_time, similar_to
        )

        # Build the card
        card = {
            "title": title,
            "explanation": explanation,
            "mood_match": mood_match,
            "weather_match": weather_match,
            "time_match": time_match,
            "confidence_score": confidence_score,
            "confidence_label": confidence_label,
        }

        return card

    except Exception as e:
        # Return a fallback card on any error
        return {
            "title": movie.get("title", "Unknown") if isinstance(movie, dict) else "Unknown",
            "explanation": "Recommended based on your preferences",
            "mood_match": False,
            "weather_match": False,
            "time_match": False,
            "confidence_score": 0,
            "confidence_label": "Suggested Pick",
        }


# ============================================================
#  Module Initialization
# ============================================================

if __name__ == "__main__":
    print("Explainer module loaded successfully")
