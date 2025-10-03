import streamlit as st
import requests
import pandas as pd
import datetime

# --- FUNGSI-FUNGSI API TMDB ---

def get_full_movie_details(movie_id, api_key):
    """Mengambil detail, credits (cast/crew), dan video dari TMDB."""
    base_url = "https://api.themoviedb.org/3/movie/"
    params = {'api_key': api_key, 'language': 'en-US', 'append_to_response': 'credits,videos'}
    try:
        response = requests.get(f"{base_url}{movie_id}", params=params)
        response.raise_for_status()
        data = response.json()
        director = next((member['name'] for member in data.get('credits', {}).get('crew', []) if member['job'] == 'Director'), "N/A")
        data['director'] = director
        trailer_key = next((video['key'] for video in data.get('videos', {}).get('results', []) if video['type'] == 'Trailer' and video['site'] == 'YouTube'), None)
        data['trailer_key'] = trailer_key
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil detail lengkap film: {e}")
        return None

# MODIFIKASI: Mengambil poster langsung untuk efisiensi
def get_popular_movies(api_key):
    """Mengambil daftar film populer lengkap dengan posternya."""
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        popular_movies = []
        for movie in data.get('results', []):
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750.png?text=No+Image"
            popular_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': poster_url
            })
        return popular_movies
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil daftar film populer: {e}")
        return []

def get_recommendations(movie_id, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}&language=en-US&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        recommended_movies = []
        for movie in data['results'][:5]: # Ambil 5 film teratas
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750.png?text=No+Image"
            recommended_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': poster_url
            })
        return recommended_movies
    except requests.exceptions.RequestException:
        return []

def format_currency(amount):
    if amount == 0:
        return "N/A"
    return f"${amount:,.2f}"

# --- TAMPILAN ANTARMUKA STREAMLIT ---

st.set_page_config(layout="wide")

try:
    API_KEY = st.secrets["tmdb"]["api_key"]
except (KeyError, FileNotFoundError):
    st.error("API Key TMDB tidak ditemukan. Pastikan Anda sudah menambahkannya ke Streamlit Secrets.")
    st.stop()

# MODIFIKASI: Manajemen state untuk tiga tampilan: popular, recommendations, detail
if 'view' not in st.session_state:
    st.session_state.view = 'popular'
    st.session_state.selected_movie_id = None
    st.session_state.recommendations = []
    st.session_state.selected_movie_for_recommendation = ""

def display_popular_page():
    """Menampilkan galeri film populer."""
    st.title('🎬 Sistem Rekomendasi Film')
    st.write("Pilih film yang Anda suka dengan mengklik posternya untuk mendapatkan rekomendasi film serupa!")
    
    popular_movies = get_popular_movies(API_KEY)
    
    if popular_movies:
        st.subheader("Film Terpopuler Saat Ini")
        # Tampilkan 5 film per baris
        num_columns = 5
        rows = [popular_movies[i:i + num_columns] for i in range(0, len(popular_movies), num_columns)]
        
        for row in rows:
            cols = st.columns(num_columns)
            for i, movie in enumerate(row):
                with cols[i]:
                    # Jadikan gambar sebagai tombol
                    if st.button(f"_{movie['title']}_", key=f"popular_{movie['id']}", use_container_width=True):
                        with st.spinner('Mencari rekomendasi untuk Anda...'):
                            st.session_state.recommendations = get_recommendations(movie['id'], API_KEY)
                            st.session_state.selected_movie_for_recommendation = movie['title']
                            st.session_state.view = 'recommendations'
                            st.rerun()
                    st.image(movie['poster_url'])
                    st.caption(movie['title'])
    else:
        st.warning("Tidak dapat memuat film populer saat ini.")

def display_recommendations_page():
    """Menampilkan hasil rekomendasi."""
    if st.button("⬅️ Kembali ke Daftar Populer"):
        st.session_state.view = 'popular'
        st.session_state.recommendations = [] # Kosongkan state
        st.rerun()
        
    st.title("Hasil Rekomendasi")
    st.subheader(f"Berdasarkan pilihan Anda: '{st.session_state.selected_movie_for_recommendation}'")
    
    if st.session_state.recommendations:
        cols = st.columns(5)
        for i, movie in enumerate(st.session_state.recommendations):
            with cols[i]:
                st.image(movie['poster_url'])
                st.caption(movie['title'])
                if st.button("Lihat Detail", key=f"detail_{movie['id']}"):
                    st.session_state.view = 'detail'
                    st.session_state.selected_movie_id = movie['id']
                    st.rerun()
    else:
        st.warning("Maaf, tidak ditemukan rekomendasi untuk film ini.")

def display_detail_page():
    """Menampilkan halaman detail yang sudah disempurnakan."""
    movie_id = st.session_state.selected_movie_id
    details = get_full_movie_details(movie_id, API_KEY)
    if details:
        # Tombol kembali sekarang mengarahkan ke halaman rekomendasi
        if st.button("⬅️ Kembali ke Hasil Rekomendasi"):
            st.session_state.view = 'recommendations'
            st.session_state.selected_movie_id = None
            st.rerun()

        col1, col2 = st.columns([1, 2])
        with col1:
            poster_url = f"https://image.tmdb.org/t/p/w500/{details['poster_path']}" if details.get('poster_path') else "https://via.placeholder.com/500x750.png?text=No+Image"
            st.image(poster_url)
        with col2:
            st.title(details['title'])
            if details.get('tagline'): st.markdown(f"*{details['tagline']}*")
            release_date_str = details.get('release_date', 'N/A')
            release_date = datetime.datetime.strptime(release_date_str, '%Y-%m-%d').strftime('%B %d, %Y') if release_date_str and release_date_str != 'N/A' else ''
            genres = ', '.join([genre['name'] for genre in details.get('genres', [])])
            runtime = f"{details['runtime']} menit" if details.get('runtime') else "N/A"
            st.write(f"**🗓️ Rilis:** {release_date}  |  **🎭 Genre:** {genres}  |  **⏳ Durasi:** {runtime}")
            st.divider()
            st.subheader("Ringkasan")
            st.write(details.get('overview', 'Tidak ada ringkasan.'))
            st.write(f"**Sutradara:** {details.get('director', 'N/A')}")
            st.divider()
            st.subheader("Detail Produksi")
            info_cols = st.columns(4)
            with info_cols[0]:
                st.write("**Status**"); st.write(details.get('status', 'N/A'))
            with info_cols[1]:
                st.write("**Bahasa Asli**"); st.write(details.get('original_language', 'N/A').upper())
            with info_cols[2]:
                st.write("**Anggaran**"); st.write(format_currency(details.get('budget', 0)))
            with info_cols[3]:
                st.write("**Pendapatan**"); st.write(format_currency(details.get('revenue', 0)))
            st.divider()
            st.subheader("Pemeran Utama")
            cast = details.get('credits', {}).get('cast', [])
            if cast:
                cast_cols = st.columns(6)
                for i, actor in enumerate(cast[:6]):
                    with cast_cols[i]:
                        actor_poster = f"https://image.tmdb.org/t/p/w200/{actor['profile_path']}" if actor.get('profile_path') else "https://via.placeholder.com/200x300.png?text=No+Image"
                        st.image(actor_poster)
                        st.caption(f"**{actor['name']}** sebagai {actor['character']}")
            if details.get('trailer_key'):
                st.divider()
                st.subheader("Tonton Trailer")
                st.video(f"https://www.youtube.com/watch?v={details['trailer_key']}")

# --- LOGIKA UTAMA (Router Aplikasi) ---
if st.session_state.view == 'popular':
    display_popular_page()
elif st.session_state.view == 'recommendations':
    display_recommendations_page()
elif st.session_state.view == 'detail':
    display_detail_page()

