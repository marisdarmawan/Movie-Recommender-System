import streamlit as st
import requests
import pandas as pd
import datetime

# --- FUNGSI-FUNGSI API TMDB ---

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

def get_recommendations(movie_id, api_key):
    """Mengambil rekomendasi film berdasarkan ID film."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}&language=en-US&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        recommended_movies = []
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

st.set_page_config(layout="wide")

try:
    API_KEY = st.secrets["tmdb"]["api_key"]
except (KeyError, FileNotFoundError):
    st.error("API Key TMDB tidak ditemukan. Pastikan Anda sudah menambahkannya ke Streamlit Secrets.")
    st.stop()

# MODIFIKASI: Tambahkan 'recommendations' ke session_state
if 'view' not in st.session_state:
    st.session_state.view = 'main'
    st.session_state.selected_movie_id = None
    st.session_state.recommendations = [] # Untuk menyimpan hasil rekomendasi
    st.session_state.selected_movie_for_recommendation = ""


def display_main_page():
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
                # MODIFIKASI: Simpan hasil ke session_state
                st.session_state.recommendations = get_recommendations(movie_id, API_KEY)
                st.session_state.selected_movie_for_recommendation = selected_movie_title

    # Tampilkan rekomendasi jika ada di session_state
    if st.session_state.recommendations:
        st.subheader(f"Rekomendasi film berdasarkan '{st.session_state.selected_movie_for_recommendation}':")
        cols = st.columns(5)
        for i, movie in enumerate(st.session_state.recommendations):
            with cols[i]:
                st.image(movie['poster_url'])
                st.caption(movie['title'])
                if st.button("Lihat Detail", key=f"detail_{movie['id']}"):
                    st.session_state.view = 'detail'
                    st.session_state.selected_movie_id = movie['id']
                    st.rerun()
    elif not get_popular_movies(API_KEY).empty and 'recommendations' not in st.session_state:
         st.info("Pilih film dan klik tombol 'Dapatkan Rekomendasi' untuk memulai.")


def display_detail_page():
    """Menampilkan halaman detail untuk film yang dipilih."""
    movie_id = st.session_state.selected_movie_id
    details = get_movie_details(movie_id, API_KEY)

    if details:
        if st.button("⬅️ Kembali ke Rekomendasi"):
            st.session_state.view = 'main'
            st.session_state.selected_movie_id = None # Hapus id film yg dipilih
            st.rerun()

        col1, col2 = st.columns([1, 2])
        with col1:
            poster_url = f"https://image.tmdb.org/t/p/w500/{details['poster_path']}" if details.get('poster_path') else "https://via.placeholder.com/500x750.png?text=No+Image"
            st.image(poster_url)

        with col2:
            st.title(details['title'])
            release_date_str = details.get('release_date', 'N/A')
            release_date = ''
            if release_date_str != 'N/A' and release_date_str:
                try:
                    release_date = datetime.datetime.strptime(release_date_str, '%Y-%m-%d').strftime('%B %d, %Y')
                except ValueError:
                    release_date = release_date_str

            genres = ', '.join([genre['name'] for genre in details.get('genres', [])])
            st.write(f"**🗓️ Rilis:** {release_date}")
            st.write(f"**🎭 Genre:** {genres}")

            vote_average = details.get('vote_average', 0)
            st.write(f"**⭐ Rating Pengguna:** {vote_average:.1f} / 10")
            if vote_average > 0:
                st.progress(vote_average / 10)

            st.subheader("Ringkasan")
            st.write(details.get('overview', 'Tidak ada ringkasan.'))

# --- LOGIKA UTAMA ---
if st.session_state.view == 'main':
    display_main_page()
elif st.session_state.view == 'detail':
    display_detail_page()

