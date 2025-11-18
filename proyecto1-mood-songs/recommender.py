# recommender.py
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 1 Cargar CSV

df = pd.read_csv("songs.csv", encoding='latin1')

# 2 Conectar con Spotify (seguro para GitHub)
load_dotenv()  # Carga variables del archivo .env

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Función para obtener link de Spotify
def get_spotify_link(name, artist):
    try:
        results = sp.search(q=f"track:{name} artist:{artist}", type="track", limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            return track['external_urls']['spotify']
        else:
            return "Link no encontrado"
    except:
        return "Error al buscar link"


# 3 Función por mood

def recommend_by_mood(mood, n=5):
    mood_songs = df[df['Mood'] == mood]
    if mood_songs.empty:
        print("No hay canciones para ese mood.")
        return
    print("\nCanciones recomendadas:")
    for i, row in mood_songs.head(n).iterrows():
        link = get_spotify_link(row['Name'], row['Artist'])
        print(f"{row['Name']} - {row['Artist']} - {row['Genre']} - {link}")


 # 4 Función por canción similar

def recommend_similar(song_name, n=5):
    if song_name not in df['Name'].values:
        print("La canción no está en la base de datos.")
        return
    features = ['Energy', 'Valence', 'Danceability']
    X = df[features]
    similarity_matrix = cosine_similarity(X)
    idx = df.index[df['Name'] == song_name][0]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    print(f"\nCanciones similares a {song_name}:")
    for i, score in sim_scores[1:n+1]:
        row = df.loc[i]
        link = get_spotify_link(row['Name'], row['Artist'])
        print(f"{row['Name']} - {row['Artist']} - {row['Genre']} - {link}")


# 5 Menú interactivo

choice = input("Escribe 'mood' para recomendar por mood o 'song' para canciones similares: ").lower()
if choice == 'mood':
    mood = input("Escribe el mood (happy, sad, energetic, etc.): ").lower()
    recommend_by_mood(mood)
elif choice == 'song':
    song = input("Escribe el nombre de la canción: ")
    recommend_similar(song)
else:
    print("Opción no válida")
