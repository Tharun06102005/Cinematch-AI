"""
Platforms Module - Maps movies to OTT streaming platforms.
"""

# Static mapping of popular movies to their OTT platforms
MOVIE_PLATFORMS = {
    # ---- Hollywood Movies ----
    "Inception": ["Netflix", "Prime Video"],
    "The Dark Knight": ["Netflix", "JioCinema"],
    "Interstellar": ["Netflix", "Prime Video"],
    "Tenet": ["Prime Video", "Hotstar"],
    "Oppenheimer": ["Prime Video", "JioCinema"],
    "Dunkirk": ["Netflix", "Prime Video"],
    "The Prestige": ["Hotstar", "Prime Video"],
    "Memento": ["Hotstar", "Prime Video"],
    "The Shawshank Redemption": ["Netflix", "Prime Video"],
    "The Godfather": ["Netflix", "Prime Video"],
    "Pulp Fiction": ["Netflix", "JioCinema"],
    "Fight Club": ["Netflix", "Hotstar"],
    "Forrest Gump": ["Netflix", "Prime Video"],
    "The Matrix": ["Netflix", "Prime Video"],
    "The Lord of the Rings: The Fellowship of the Ring": ["Netflix", "Prime Video"],
    "The Lord of the Rings: The Two Towers": ["Netflix", "Prime Video"],
    "The Lord of the Rings: The Return of the King": ["Netflix", "Prime Video"],
    "Harry Potter and the Sorcerer's Stone": ["Netflix", "JioCinema"],
    "Harry Potter and the Chamber of Secrets": ["Netflix", "JioCinema"],
    "Harry Potter and the Prisoner of Azkaban": ["Netflix", "JioCinema"],
    "Harry Potter and the Goblet of Fire": ["Netflix", "JioCinema"],
    "Harry Potter and the Order of the Phoenix": ["Netflix", "JioCinema"],
    "Harry Potter and the Half-Blood Prince": ["Netflix", "JioCinema"],
    "Harry Potter and the Deathly Hallows: Part 1": ["Netflix", "JioCinema"],
    "Harry Potter and the Deathly Hallows: Part 2": ["Netflix", "JioCinema"],
    "The Avengers": ["Hotstar", "Prime Video"],
    "Avengers: Endgame": ["Hotstar"],
    "Avengers: Infinity War": ["Hotstar"],
    "Iron Man": ["Hotstar", "Prime Video"],
    "Captain America: The Winter Soldier": ["Hotstar"],
    "Thor: Ragnarok": ["Hotstar"],
    "Black Panther": ["Hotstar"],
    "Spider-Man: No Way Home": ["Netflix", "SonyLIV"],
    "Spider-Man: Across the Spider-Verse": ["Netflix", "SonyLIV"],
    "Joker": ["Netflix", "Prime Video"],
    "The Batman": ["Netflix", "Prime Video"],
    "Parasite": ["Netflix", "Prime Video"],
    "The Social Network": ["Netflix", "Prime Video"],
    "Whiplash": ["Netflix", "Prime Video"],
    "La La Land": ["Netflix", "Hotstar"],
    "Deadpool": ["Netflix", "Hotstar"],
    "John Wick": ["Netflix", "Hotstar"],
    "Mad Max: Fury Road": ["Netflix", "Prime Video"],
    "Gladiator": ["Netflix", "Prime Video"],
    "The Silence of the Lambs": ["Netflix", "Prime Video"],
    "Titanic": ["Hotstar", "Prime Video"],
    "The Wolf of Wall Street": ["Netflix", "Prime Video"],
    "Shutter Island": ["Netflix", "Prime Video"],
    "The Departed": ["Netflix", "Prime Video"],
    "Catch Me If You Can": ["Netflix", "Prime Video"],
    "The Pianist": ["Netflix", "Prime Video"],

    # ---- Bollywood Movies ----
    "3 Idiots": ["Netflix", "Prime Video", "Hotstar"],
    "Dangal": ["Netflix", "Hotstar"],
    "PK": ["Netflix", "Hotstar"],
    "Baahubali: The Beginning": ["Hotstar", "Prime Video"],
    "Baahubali 2: The Conclusion": ["Hotstar", "Netflix"],
    "RRR": ["Netflix", "ZEE5"],
    "KGF Chapter 1": ["Prime Video", "Hotstar"],
    "KGF Chapter 2": ["Prime Video", "Hotstar"],
    "Pathaan": ["Prime Video", "Hotstar"],
    "Jawan": ["Netflix", "Prime Video"],
    "Pushpa: The Rise": ["Netflix", "Prime Video"],
    "Animal": ["Netflix"],
    "Sanju": ["Netflix", "Hotstar"],
    "Bajrangi Bhaijaan": ["Netflix", "Hotstar", "ZEE5"],
    "Sultan": ["Prime Video", "Hotstar"],
    "War": ["Prime Video", "Hotstar"],
    "Tiger Zinda Hai": ["Prime Video", "Hotstar"],
    "Kabir Singh": ["Netflix", "Prime Video"],
    "Dilwale Dulhania Le Jayenge": ["Prime Video", "Hotstar"],
    "Zindagi Na Milegi Dobara": ["Netflix", "Prime Video"],
    "Yeh Jawani Hai Deewani": ["Netflix", "Prime Video", "Hotstar"],
    "Chennai Express": ["Netflix", "Hotstar"],
    "Gully Boy": ["Netflix", "Prime Video"],
    "Andhadhun": ["Netflix", "Prime Video"],
    "Article 15": ["Netflix", "Prime Video"],
    "Tumbbad": ["Prime Video", "Hotstar"],
    "Stree": ["Prime Video", "JioCinema"],
    "Munjya": ["JioCinema", "Prime Video"],
    "12th Fail": ["Hotstar"],
    "Chhichhore": ["Netflix", "Hotstar"],
    "Dream Girl": ["Netflix", "JioCinema"],
    "Luka Chuppi": ["Netflix", "JioCinema", "Prime Video"],
    "Bhool Bhulaiyaa 2": ["Netflix", "Prime Video", "Hotstar"],
    "Drishyam 2": ["Netflix", "Prime Video", "Hotstar"],
    "Vikram Vedha": ["Hotstar", "Prime Video"],
    "Vikram": ["Hotstar", "Prime Video"],
    "Kantara": ["Prime Video"],
}

# Platform badge color mapping
PLATFORM_BADGE_COLORS = {
    "Netflix": "#E50914",
    "Prime Video": "#00A8E1",
    "Hotstar": "#1F80E0",
    "JioCinema": "#6B2D8B",
    "ZEE5": "#8B2FC9",
    "SonyLIV": "#F4A526",
}


def get_platforms(movie_title):
    """
    Takes a movie title and returns a list of OTT platforms it's available on.

    Args:
        movie_title (str): The title of the movie.

    Returns:
        list: A list of platform names, or ["Check JustWatch.com"] if not found.
    """
    try:
        title_clean = movie_title.strip()
        # Case-insensitive lookup: try exact match first
        if title_clean in MOVIE_PLATFORMS:
            return MOVIE_PLATFORMS[title_clean]

        # Try case-insensitive match
        for key, platforms in MOVIE_PLATFORMS.items():
            if key.lower() == title_clean.lower():
                return platforms

        # Try partial match
        for key, platforms in MOVIE_PLATFORMS.items():
            if title_clean.lower() in key.lower() or key.lower() in title_clean.lower():
                return platforms

        return ["Check JustWatch.com"]
    except Exception:
        return ["Check JustWatch.com"]


def get_platform_badge(platform):
    """
    Returns the brand color code for a given OTT platform.

    Args:
        platform (str): The name of the platform.

    Returns:
        str: Hex color code, or "#888888" if platform is unknown.
    """
    try:
        return PLATFORM_BADGE_COLORS.get(platform.strip(), "#888888")
    except Exception:
        return "#888888"


if __name__ == "__main__":
    print("Platforms module loaded successfully")
