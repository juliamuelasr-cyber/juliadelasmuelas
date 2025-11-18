import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- Configuración página ---
st.set_page_config(page_title="Mood Song Recommender", page_icon="🎧")
st.title("🎧 Mood Song Recommender")

# --- Cargar CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("songs.csv", encoding='latin1')
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# --- Preparar matriz de características ---
features = ['Energy','Valence','Danceability']
X = df[features].fillna(0).to_numpy()
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# --- Conexión Spotify ---
def get_spotify_client():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if client_id and client_secret:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        return spotipy.Spotify(auth_manager=auth_manager)
    return None

sp = get_spotify_client()

def get_spotify_link(name, artist):
    if sp is None: return None
    try:
        res = sp.search(q=f"track:{name} artist:{artist}", type="track", limit=1)
        items = res.get('tracks', {}).get('items', [])
        if items:
            return items[0]['external_urls']['spotify']
    except: return None
    return None

# --- Interfaz ---
st.sidebar.header("Filtros")
selected_mood = st.sidebar.selectbox("Mood", ["(any)"] + sorted(df['Mood'].dropna().unique()))
selected_genre = st.sidebar.selectbox("Género", ["(any)"] + sorted(df['Genre'].dropna().unique()))
min_energy, max_energy = float(df['Energy'].min()), float(df['Energy'].max())
energy_range = st.sidebar.slider("Energy", min_energy, max_energy, (min_energy, max_energy))
show_spotify = st.sidebar.checkbox("Mostrar enlaces Spotify")

# --- Filtrar canciones ---
mask = pd.Series(True, index=df.index)
if selected_mood != "(any)": mask &= df['Mood'] == selected_mood
if selected_genre != "(any)": mask &= df['Genre'] == selected_genre
mask &= df['Energy'].between(energy_range[0], energy_range[1])
filtered = df[mask]

st.subheader("Canciones filtradas")
st.write(f"{len(filtered)} coincidencias de {len(df)} canciones")
st.dataframe(filtered[['Name','Artist','Genre','Energy','Valence','Danceability','Mood']].reset_index(drop=True))

# --- Recomendación por canción ---
st.subheader("Canciones similares")
song_name = st.selectbox("Elige canción base", options=sorted(df['Name'].dropna()))
if song_name:
    idx = df.index[df['Name']==song_name][0]
    sim_scores = cosine_similarity(X)[idx]
    top_idx = sim_scores.argsort()[::-1][1:6]
    st.write("🎵 Canciones similares:")
    for i in top_idx:
        row = df.iloc[i]
        link = get_spotify_link(row['Name'], row['Artist'])
        if show_spotify and link: row_name = f"[{row['Name']}]({link})"
        else: row_name = row['Name']
        st.write(f"{row_name} - {row['Artist']} - {row['Mood']}")
