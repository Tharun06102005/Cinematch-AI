# 🎬 CineMatch-AI

### AI-Powered Personalized Movie Recommendation System

CineMatch-AI is an intelligent movie recommendation web application that helps users discover movies based on their preferences, emotional state, weather conditions, and personalized recommendations.

The system combines movie data, recommendation techniques, emotion detection, weather information, and AI-generated explanations to provide a more personalized movie discovery experience.

---

## 🚀 Features

- 🎯 **Personalized Movie Recommendations**
  - Recommends movies based on user preferences and movie characteristics.

- 😊 **Emotion-Based Recommendations**
  - Detects the user's emotional state and suggests movies accordingly.

- 🌦️ **Weather-Based Recommendations**
  - Considers current weather conditions while recommending movies.

- 🧠 **Personalized Explanations**
  - Provides explanations for why a particular movie is recommended.

- 🎭 **Genre-Based Recommendations**
  - Allows users to discover movies based on genres and preferences.

- ⭐ **Movie Rating Data**
  - Uses movie and rating datasets to support the recommendation system.

- 💻 **Interactive Web Interface**
  - Simple and user-friendly web interface for movie discovery.

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- JavaScript

### Machine Learning / AI
- Recommendation algorithms
- Emotion detection
- Personalized recommendation logic

### Data
- Movie dataset
- Movie ratings dataset
- CSV-based data processing

### External Services
- Weather API

---

## 📂 Project Structure

```text
CineMatch-AI/
│
├── app.py                  # Main Flask application
├── emotion.py              # Emotion detection functionality
├── recommender.py          # Movie recommendation logic
├── explainer.py            # Recommendation explanation module
├── platforms.py            # Movie platform-related functionality
├── weather.py              # Weather-based functionality
│
├── data/
│   ├── movies.csv          # Movie dataset
│   └── ratings.csv         # Movie ratings dataset
│
├── static/
│   └── style.css           # Website styling
│
├── templates/
│   └── index.html          # Main web interface
│
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignored files
└── README.md               # Project documentation


