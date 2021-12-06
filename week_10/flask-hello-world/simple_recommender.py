import random

movies = [
    "The Shawshank Redemption",
    "Star Wars: Episode IV - A New Hope",
    "Pulp Fiction",
    "The Dark Knight",
    "Forrest Gump",
    "Inception",
    "The Matrix",
    "Saving Private Ryan",
    "Casablanca",
    "The Lion King"
]


def get_recommendations():
    random.shuffle(movies)
    return movies[:3]
