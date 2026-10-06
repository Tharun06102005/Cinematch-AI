"""
Emotion Detection Module for CineMatch-AI

Uses DeepFace and OpenCV to detect user emotions via webcam,
and maps detected emotions to movie genres.
"""

import cv2
from deepface import DeepFace
import time

# Mood to genre mapping
MOOD_TO_GENRES = {
    "Happy": ["Comedy", "Animation", "Family"],
    "Sad": ["Drama", "Romance"],
    "Angry": ["Action", "Thriller"],
    "Stressed": ["Comedy", "Music", "Animation"],
    "Surprised": ["Mystery", "Sci-Fi", "Fantasy"],
    "Neutral": ["Adventure", "Documentary"],
}

# Mapping from DeepFace raw emotions to our simplified emotions
EMOTION_MAP = {
    "happy": "Happy",
    "sad": "Sad",
    "angry": "Angry",
    "surprise": "Surprised",
    "neutral": "Neutral",
    "fear": "Stressed",
    "disgust": "Stressed",
}


def detect_emotion():
    """
    Opens webcam using OpenCV, captures a frame, and uses DeepFace.analyze()
    to detect the user's emotion.

    Returns:
        str: Detected emotion string. Returns "Neutral" on failure.
    """
    cap = None
    try:
        # Open webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[WARNING] Could not open webcam. Defaulting to Neutral.")
            return "Neutral"

        # Allow camera to warm up
        time.sleep(0.5)

        # Capture a single frame
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARNING] Could not capture frame from webcam. Defaulting to Neutral.")
            return "Neutral"

        # Analyze emotion using DeepFace
        analysis = DeepFace.analyze(
            img_path=frame,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )

        # DeepFace returns a list; get the first face analyzed
        if isinstance(analysis, list):
            analysis = analysis[0]

        raw_emotion = analysis.get("dominant_emotion", "neutral").lower()

        # Map to our simplified emotions
        detected = EMOTION_MAP.get(raw_emotion, "Neutral")

        # Show the captured frame briefly with the emotion label
        label = f"Detected Emotion: {detected}"
        cv2.putText(
            frame,
            label,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3,
            cv2.LINE_AA,
        )
        cv2.imshow("CineMatch - Emotion Detection", frame)
        cv2.waitKey(2000)  # Display for 2 seconds

        print(f"[INFO] Detected emotion: {detected}")
        return detected

    except Exception as e:
        print(f"[ERROR] Emotion detection failed: {e}. Defaulting to Neutral.")
        return "Neutral"

    finally:
        # Clean up
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()


def get_emotion_manually():
    """
    Returns a list of emotions available for manual selection.

    Returns:
        list: List of emotion strings.
    """
    return ["Happy", "Sad", "Angry", "Stressed", "Surprised", "Neutral"]


def get_genre_from_emotion(emotion):
    """
    Maps an emotion string to a list of suggested movie genres.

    Args:
        emotion (str): The detected or selected emotion.

    Returns:
        list: List of genre strings corresponding to the emotion.
               Returns ["Adventure", "Documentary"] for unknown emotions.
    """
    try:
        return MOOD_TO_GENRES.get(emotion, MOOD_TO_GENRES["Neutral"])
    except Exception:
        return ["Adventure", "Documentary"]


if __name__ == "__main__":
    print("Emotion module loaded successfully")
