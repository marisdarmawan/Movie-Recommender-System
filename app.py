import streamlit as st
import requests
import pandas as pd
import datetime

# --- FUNGSI-FUNGSI API TMDB (Tidak ada perubahan) ---

def get_full_movie_details(movie_id, api_key):
    """Mengambil detail, credits (cast/crew), dan video dari TMDB."""
    base_url = "https://api.themoviedb.org/3/movie/"
    params = {
        'api_key': api_key,
        'language': 'en-US',
        'append_to_response': 'credits,videos'
    }
    try:
        response = requests.get(f"{base_url}{movie_id}", params=params)
        response.raise_for_status()
        data = response.json()
        director = "N/A"
        for member in data.get('credits', {}).get('crew', []):
            if member['job'] == 'Director':
                director = member['name']
                break
        data['director'] = director
        trailer_key = None
        for video in data.get('videos', {}).get('results', []):
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                trailer_key = video['key']
                break
        data['trailer_key'] = trailer_key
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil detail lengkap film: {e}")
        return None

def fetch_poster(movie_id, api_key):
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

if 'view' not in st.session_state:
    st.session_state.view = 'main'
    st.session_state.selected_movie_id = None
    st.session_state.recommendations = []
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
                st.session_state.recommendations = get_recommendations(movie_id, API_KEY)
                st.session_state.selected_movie_for_recommendation = selected_movie_title
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

def display_detail_page():
    movie_id = st.session_state.selected_movie_id
    details = get_full_movie_details(movie_id, API_KEY)
    if details:
        if st.button("⬅️ Kembali ke Rekomendasi"):
            st.session_state.view = 'main'
            st.session_state.selected_movie_id = None
            st.rerun()

        col1, col2 = st.columns([1, 2])
        with col1:
            poster_url = f"https://image.tmdb.org/t/p/w500/{details['poster_path']}" if details.get('poster_path') else "https://via.placeholder.com/500x750.png?text=No+Image"
            st.image(poster_url)

        with col2:
            st.title(details['title'])
            if details.get('tagline'):
                st.markdown(f"*{details['tagline']}*")
            
            release_date_str = details.get('release_date', 'N/A')
            release_date = ''
            if release_date_str != 'N/A' and release_date_str:
                release_date = datetime.datetime.strptime(release_date_str, '%Y-%m-%d').strftime('%B %d, %Y')
            
            genres = ', '.join([genre['name'] for genre in details.get('genres', [])])
            runtime = f"{details['runtime']} menit" if details.get('runtime') else "N/A"
            st.write(f"**🗓️ Rilis:** {release_date}  |  **🎭 Genre:** {genres}  |  **⏳ Durasi:** {runtime}")
            
            st.divider()

            st.subheader("Ringkasan")
            st.write(details.get('overview', 'Tidak ada ringkasan.'))
            st.write(f"**Sutradara:** {details.get('director', 'N/A')}")
            
            st.divider()
            
            st.subheader("Detail Produksi")
            # --- PERUBAHAN DI SINI ---
            # Mengganti st.metric dengan st.write untuk font yang lebih kecil
            info_cols = st.columns(4)
            with info_cols[0]:
                st.write("**Status**")
                st.write(details.get('status', 'N/A'))
            with info_cols[1]:
                st.write("**Bahasa Asli**")
                st.write(details.get('original_language', 'N/A').upper())
            with info_cols[2]:
                st.write("**Anggaran**")
                st.write(format_currency(details.get('budget', 0)))
            with info_cols[3]:
                st.write("**Pendapatan**")
                st.write(format_currency(details.get('revenue', 0)))
            # --- AKHIR PERUBAHAN ---

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
            else:
                st.write("Informasi pemeran tidak tersedia.")

            if details.get('trailer_key'):
                st.divider()
                st.subheader("Tonton Trailer")
                st.video(f"https://www.youtube.com/watch?v={details['trailer_key']}")

# --- LOGIKA UTAMA ---
if st.session_state.view == 'main':
    display_main_page()
elif st.session_state.view == 'detail':
    display_detail_page()
