"""
CineMatch-AI — Main Flask Application
---------------------------------------
Integrates emotion detection, weather, recommendations, platforms,
and explainer modules into a single web server.
"""

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# -------------------- Module Imports --------------------
from recommender import get_recommendations, get_similar_movies
from emotion import detect_emotion, get_emotion_manually, get_genre_from_emotion
from weather import get_weather, get_genre_from_weather
from platforms import get_platforms, get_platform_badge
from explainer import generate_ai_card

# -------------------- App Initialization --------------------
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# -------------------- Routes --------------------

@app.route("/")
def index():
    """Render the main page."""
    try:
        return render_template("index.html")
    except Exception as e:
        return jsonify({"error": f"Failed to render index page: {str(e)}"}), 500


@app.route("/api/weather")
def api_weather():
    """Return current weather data and suggested genres as JSON."""
    try:
        city = request.args.get("city", None)
        weather_data = get_weather(city)
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({"error": f"Weather fetch failed: {str(e)}"}), 500


@app.route("/api/detect-emotion", methods=["POST"])
def api_detect_emotion():
    """Trigger webcam emotion detection and return the detected emotion."""
    try:
        emotion = detect_emotion()
        return jsonify({"emotion": emotion})
    except Exception as e:
        return jsonify({"error": f"Emotion detection failed: {str(e)}"}), 500


@app.route("/api/emotions")
def api_emotions():
    """Return the list of emotions available for manual selection."""
    try:
        emotions = get_emotion_manually()
        return jsonify({"emotions": emotions})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch emotions: {str(e)}"}), 500


@app.route("/api/recommendations", methods=["POST"])
def api_recommendations():
    """
    Accept JSON body with mood, watch_time, and optional city.
    Returns top 10 movies with OTT platform availability and AI explanation cards.
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        mood = data.get("mood", "neutral")
        watch_time = data.get("watch_time", 120)
        city = data.get("city", None)

        # Validate inputs
        if not isinstance(watch_time, (int, float)) or watch_time <= 0:
            watch_time = 120

        # Fetch weather data
        weather_data = get_weather(city)
        # Get movie recommendations
        recommendations = get_recommendations(mood, watch_time)
        if not recommendations:
            return jsonify({"error": "No recommendations found for the given criteria"}), 404

        # Enrich recommendations with platforms and AI cards
        enriched = []
        for movie in recommendations:
            movie_title = movie.get("title", "Unknown")
            movie_genres = movie.get("genres", "")

            # Get OTT platforms
            platforms = get_platforms(movie_title)

            # Format platforms with badge colors
            platform_details = []
            for p in platforms:
                platform_details.append({
                    "name": p,
                    "color": get_platform_badge(p),
                })

            # Build movie dict for the explainer
            # Convert genres string (e.g. "Action|Comedy") to a list
            if isinstance(movie_genres, str):
                genre_list = [g.strip() for g in movie_genres.replace("|", ",").split(",") if g.strip()]
            else:
                genre_list = []

            movie_card_input = {
                "title": movie_title,
                "genres": genre_list,
                "runtime": movie.get("estimated_runtime", 100),
                "score": movie.get("score", 5.0),
            }

            # Generate AI explanation card
            card = generate_ai_card(movie_card_input, mood, weather_data, watch_time)

            enriched.append({
                "title": movie_title,
                "genres": movie_genres,
                "score": movie.get("score", 5.0),
                "estimated_runtime": movie.get("estimated_runtime", 100),
                "platforms": platform_details,
                "ai_card": card,
            })

        return jsonify({
            "mood": mood,
            "weather": weather_data,
            "count": len(enriched),
            "recommendations": enriched,
        })

    except Exception as e:
        return jsonify({"error": f"Recommendations failed: {str(e)}"}), 500


@app.route("/api/similar/<movie_title>")
def api_similar(movie_title):
    """Return up to 5 movies similar to the given title."""
    try:
        similar = get_similar_movies(movie_title)
        if not similar:
            return jsonify({"error": f"No similar movies found for '{movie_title}'"}), 404

        # Enrich with platform info
        enriched = []
        for movie in similar:
            platforms = get_platforms(movie.get("title", ""))
            platform_details = []
            for p in platforms:
                platform_details.append({
                    "name": p,
                    "color": get_platform_badge(p),
                })
            enriched.append({
                "title": movie.get("title", "Unknown"),
                "genres": movie.get("genres", ""),
                "score": movie.get("score", 0),
                "estimated_runtime": movie.get("estimated_runtime", 100),
                "platforms": platform_details,
            })

        return jsonify({
            "movie": movie_title,
            "count": len(enriched),
            "similar": enriched,
        })

    except Exception as e:
        return jsonify({"error": f"Similar movies lookup failed: {str(e)}"}), 500


# -------------------- Error Handlers --------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# -------------------- Main Entry Point --------------------

if __name__ == "__main__":
    print("CineMatch AI Server Starting...")
    app.run(host="0.0.0.0", port=5000, debug=True)
