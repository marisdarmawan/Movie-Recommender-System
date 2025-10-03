# 🎬 Sistem Rekomendasi Film Interaktif dengan Streamlit

Sebuah aplikasi web modern dan visual yang dibuat menggunakan Python dan Streamlit untuk memberikan rekomendasi film. Aplikasi ini tidak lagi menggunakan dropdown, melainkan galeri poster interaktif untuk pengalaman pengguna yang lebih menarik. Data film diambil secara *real-time* dari [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api).

### Demo Alur Kerja Aplikasi
**Halaman Utama: Pengguna memilih film dari galeri populer**
<img width="1722" height="804" alt="image" src="https://github.com/user-attachments/assets/66c5af68-67cf-46bd-af55-859c793b68c3" />

**Halaman Rekomendasi: Aplikasi menampilkan 5 film serupa**
<img width="1722" height="804" alt="image" src="https://github.com/user-attachments/assets/05fed961-9961-4795-bb24-55b36b9a51e9" />

**Halaman Detail: Pengguna dapat melihat info lengkap dari film yang direkomendasikan**
<img width="1722" height="804" alt="image" src="https://github.com/user-attachments/assets/39f5eed8-e6de-4981-940c-2813b487cc62" />


## ✨ Fitur Utama

* **Galeri Visual**: Menampilkan daftar film terpopuler dalam bentuk galeri poster yang menarik, bukan lagi dropdown menu yang statis.
* **Alur Kerja Multi-Halaman**: Aplikasi terasa seperti memiliki tiga halaman berbeda (Populer -> Rekomendasi -> Detail) yang dikelola secara cerdas menggunakan `st.session_state`.
* **Rekomendasi Sekali Klik**: Pengguna cukup mengklik poster film yang mereka suka untuk langsung mendapatkan 5 rekomendasi film serupa.
* **Halaman Detail yang Kaya Informasi**: Menampilkan informasi lengkap film termasuk:
    * Poster, judul, dan tagline.
    * Ringkasan, sutradara, genre, dan durasi.
    * Detail produksi (status, anggaran, pendapatan).
    * Daftar pemeran utama beserta foto.
    * Trailer film dari YouTube (jika tersedia).
* **Penanganan API Key yang Aman**: Menggunakan fitur Streamlit Secrets untuk menjaga kerahasiaan API Key Anda, baik saat pengembangan lokal maupun saat di-deploy.
* **Desain Responsif**: Tampilan rapi dan berfungsi dengan baik di perangkat desktop maupun mobile.

## 🛠️ Tumpukan Teknologi

* **Backend**: Python
* **Framework Web**: Streamlit
* **Manajemen Data**: Pandas
* **Komunikasi API**: Requests
* **Sumber Data**: The Movie Database (TMDB) API

## 🚀 Panduan Memulai

Ikuti langkah-langkah berikut untuk menjalankan proyek ini di mesin lokal Anda.

### Prasyarat

* Python 3.8 atau versi lebih baru.
* `pip` (Package installer untuk Python).
* API Key gratis dari [The Movie Database (TMDB)](https://www.themoviedb.org/signup).

### Instalasi & Pengaturan

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/username-anda/nama-repositori.git](https://github.com/marisdarmawan/Movie-Recommender-System.git)
    cd nama-repositori
    ```

2.  **Instal semua library yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Siapkan API Key Anda (Rahasia):**
    Aplikasi ini menggunakan Streamlit Secrets. Anda perlu membuat sebuah file khusus untuk menyimpan API Key Anda.

    * Buat folder baru bernama `.streamlit` di direktori utama proyek.
    * Di dalam folder `.streamlit`, buat file baru bernama `secrets.toml`.
    * Buka file `secrets.toml` dan tambahkan API Key Anda dengan format berikut:
        ```toml
        # .streamlit/secrets.toml
        
        [tmdb]
        api_key = "MASUKKAN_API_KEY_TMDB_ANDA_DI_SINI"
        ```
    Ganti teks placeholder dengan API Key v3 valid yang Anda dapatkan dari TMDB.

4.  **Jalankan aplikasi Streamlit:**
    Buka terminal Anda di direktori utama proyek, lalu jalankan perintah:
    ```bash
    streamlit run app.py
    ```
    Browser Anda akan terbuka secara otomatis dan menampilkan aplikasi yang sedang berjalan.

## 🔧 Cara Kerja & Alur Aplikasi

Aplikasi ini dikendalikan oleh sebuah *state machine* sederhana menggunakan `st.session_state` untuk mengatur tiga tampilan utama:

1.  **Tampilan `popular` (Halaman Awal)**:
    * Aplikasi memanggil endpoint `/movie/popular` dari TMDB.
    * Hasilnya ditampilkan sebagai galeri poster film.
    * Setiap poster adalah sebuah tombol. Saat diklik, aplikasi menyimpan `ID` film yang dipilih, memanggil fungsi rekomendasi, lalu mengubah `state` ke `recommendations` dan menjalankan ulang skrip.

2.  **Tampilan `recommendations`**:
    * Aplikasi kini menampilkan hasil rekomendasi yang sudah disimpan di `session_state`.
    * Pengguna bisa melihat 5 film serupa atau kembali ke halaman populer.
    * Setiap film rekomendasi memiliki tombol "Lihat Detail" yang akan mengubah `state` ke `detail`.

3.  **Tampilan `detail`**:
    * Aplikasi menggunakan `ID` film yang tersimpan untuk memanggil beberapa *endpoint* TMDB sekaligus (`/movie/{id}`, `/credits`, `/videos`) untuk mendapatkan informasi lengkap.
    * Semua detail ditampilkan dengan tata letak yang rapi.
    * Pengguna dapat kembali ke halaman rekomendasi.

## 🤝 Berkontribusi

Kontribusi, isu, dan permintaan fitur sangat diterima! Silakan periksa halaman *issues* jika Anda ingin berkontribusi.

## 📄 Lisensi

Proyek ini bersifat *open-source*. Jangan ragu untuk menggunakan dan memodifikasinya.
