import streamlit as st
import requests
import pandas as pd

# --- FUNGSI UNTUK MENGAMBIL DATA DARI API TMDB ---
# Fungsi-fungsi ini tidak perlu diubah, karena mereka menerima api_key sebagai argumen.

def fetch_poster(movie_id, api_key):
    """Mengambil URL poster film berdasarkan ID film."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Image"
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil poster: {e}")
        return None

def get_recommendations(movie_id, api_key):
    """Mengambil rekomendasi film berdasarkan ID film."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}&language=en-US&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        recommended_movies = []
        poster_urls = []
        for movie in data['results'][:5]:
            recommended_movies.append(movie['title'])
            poster_urls.append(fetch_poster(movie['id'], api_key))
        return recommended_movies, poster_urls
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil rekomendasi: {e}")
        return [], []

def get_popular_movies(api_key):
    """Mengambil daftar film populer untuk ditampilkan di dropdown."""
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['results'])
        return df[['id', 'title']]
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil daftar film populer: {e}")
        return pd.DataFrame()

# --- TAMPILAN ANTARMUKA STREAMLIT ---

# Konfigurasi halaman
st.set_page_config(layout="wide")

# Cek apakah API Key ada di Streamlit Secrets
if "tmdb" in st.secrets and "api_key" in st.secrets["tmdb"]:
    API_KEY = st.secrets["tmdb"]["api_key"]
else:
    st.error("API Key TMDB tidak ditemukan. Pastikan Anda sudah menambahkannya ke file .streamlit/secrets.toml")
    st.stop() # Menghentikan eksekusi aplikasi jika key tidak ada

st.title('🎬 Sistem Rekomendasi Film')
st.write("Pilih film yang Anda suka, dan kami akan merekomendasikan film serupa!")

# Ambil daftar film
movie_list_df = get_popular_movies(API_KEY)

if not movie_list_df.empty:
    # Buat dropdown untuk memilih film
    selected_movie_title = st.selectbox(
        'Pilih sebuah film dari daftar film populer:',
        movie_list_df['title'].values
    )

    # Tombol untuk memicu rekomendasi
    if st.button('Dapatkan Rekomendasi', type="primary"):
        # Cari ID film yang dipilih dari dataframe
        movie_id = movie_list_df[movie_list_df['title'] == selected_movie_title].iloc[0]['id']
        
        with st.spinner('Mencari rekomendasi untuk Anda...'):
            # Dapatkan rekomendasi dan posternya
            recommended_names, recommended_posters = get_recommendations(movie_id, API_KEY)

            if recommended_names:
                st.subheader(f"Rekomendasi film berdasarkan '{selected_movie_title}':")
                
                # Tampilkan hasil rekomendasi dalam 5 kolom
                cols = st.columns(5)
                for i in range(len(recommended_names)):
                    with cols[i]:
                        st.image(recommended_posters[i])
                        st.caption(recommended_names[i])
            else:
                st.warning("Maaf, tidak ditemukan rekomendasi untuk film ini.")
else:
    st.error("Gagal memuat daftar film. Periksa kembali API Key Anda atau koneksi internet.")
