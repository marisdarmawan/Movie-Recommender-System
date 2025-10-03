import streamlit as st
import requests
import pandas as pd
import datetime

# --- FUNGSI-FUNGSI API TMDB ---

# FUNGSI BARU: Mengambil semua detail sebuah film berdasarkan ID
def get_movie_details(movie_id, api_key):
    """Mengambil detail lengkap sebuah film dari TMDB."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil detail film: {e}")
        return None

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
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750.png?text=Error"

# MODIFIKASI: Sekarang mengembalikan ID film juga
def get_recommendations(movie_id, api_key):
    """Mengambil rekomendasi film berdasarkan ID film."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}&language=en-US&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        recommended_movies = []
        # Loop untuk mengambil nama, poster, dan ID
        for movie in data['results'][:5]:
            recommended_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': fetch_poster(movie['id'], api_key)
            })
        return recommended_movies
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil rekomendasi: {e}")
        return []

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

# Mengambil API key dari secrets
try:
    API_KEY = st.secrets["tmdb"]["api_key"]
except (KeyError, FileNotFoundError):
    st.error("API Key TMDB tidak ditemukan. Pastikan Anda sudah menambahkannya ke Streamlit Secrets.")
    st.stop()

# BAGIAN BARU: Inisialisasi session state untuk navigasi
if 'view' not in st.session_state:
    st.session_state.view = 'main'
    st.session_state.selected_movie_id = None

# --- FUNGSI UNTUK MENAMPILKAN HALAMAN ---

def display_main_page():
    """Menampilkan halaman utama untuk memilih dan melihat rekomendasi."""
    st.title('🎬 Sistem Rekomendasi Film')
    st.write("Pilih film yang Anda suka, dan kami akan merekomendasikan film serupa!")

    movie_list_df = get_popular_movies(API_KEY)

    if not movie_list_df.empty:
        selected_movie_title = st.selectbox(
            'Pilih sebuah film dari daftar film populer:',
            movie_list_df['title'].values
        )

        if st.button('Dapatkan Rekomendasi', type="primary"):
            movie_id = movie_list_df[movie_list_df['title'] == selected_movie_title].iloc[0]['id']
            
            with st.spinner('Mencari rekomendasi untuk Anda...'):
                recommended_movies = get_recommendations(movie_id, API_KEY)

                if recommended_movies:
                    st.subheader(f"Rekomendasi film berdasarkan '{selected_movie_title}':")
                    cols = st.columns(5)
                    for i, movie in enumerate(recommended_movies):
                        with cols[i]:
                            st.image(movie['poster_url'])
                            st.caption(movie['title'])
                            # BAGIAN BARU: Tombol untuk melihat detail
                            if st.button("Lihat Detail", key=f"detail_{movie['id']}"):
                                st.session_state.view = 'detail'
                                st.session_state.selected_movie_id = movie['id']
                                st.rerun() # Memaksa skrip jalan ulang untuk ganti view
                else:
                    st.warning("Maaf, tidak ditemukan rekomendasi untuk film ini.")
    else:
        st.error("Gagal memuat daftar film. Periksa kembali API Key Anda atau koneksi internet.")

def display_detail_page():
    """Menampilkan halaman detail untuk film yang dipilih."""
    movie_id = st.session_state.selected_movie_id
    details = get_movie_details(movie_id, API_KEY)

    if details:
        # Tombol kembali
        if st.button("⬅️ Kembali ke Rekomendasi"):
            st.session_state.view = 'main'
            st.rerun()

        # Layout Halaman Detail
        col1, col2 = st.columns([1, 2])

        with col1:
            poster_url = f"https://image.tmdb.org/t/p/w500/{details['poster_path']}" if details['poster_path'] else "https://via.placeholder.com/500x750.png?text=No+Image"
            st.image(poster_url)

        with col2:
            st.title(details['title'])
            
            # Info rilis dan genre
            release_date = details.get('release_date', 'N/A')
            try:
                release_date = datetime.datetime.strptime(release_date, '%Y-%m-%d').strftime('%B %d, %Y')
            except (ValueError, TypeError):
                pass

            genres = ', '.join([genre['name'] for genre in details.get('genres', [])])
            st.write(f"**🗓️ Rilis:** {release_date}")
            st.write(f"**🎭 Genre:** {genres}")

            # User Score / Rating
            vote_average = details.get('vote_average', 0)
            st.write(f"**⭐ Rating Pengguna:** {vote_average:.1f} / 10")
            st.progress(vote_average / 10)

            # Overview
            st.subheader("Ringkasan")
            st.write(details.get('overview', 'Tidak ada ringkasan.'))

# --- LOGIKA UTAMA: Mengatur view mana yang ditampilkan ---
if st.session_state.view == 'main':
    display_main_page()
elif st.session_state.view == 'detail':
    display_detail_page()
