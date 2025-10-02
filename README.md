# 🎬 Streamlit Movie Recommender

A simple and interactive web application built with Python and Streamlit that provides movie recommendations based on user selection. This app fetches real-time movie data from [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api).

*(This is a sample GIF, you can replace it with a screenshot of your running app)*

## ✨ Features

* **Browse Popular Movies**: The app starts by showing a dropdown list of currently popular movies.
* **Get Recommendations**: Select a movie you like, click the button, and get 5 similar movie recommendations.
* **Visual Interface**: Displays movie posters for a rich user experience.
* **Secure API Key Handling**: Uses Streamlit's built-in secrets management to keep your TMDB API key safe and out of the source code.
* **Responsive Design**: Works on both desktop and mobile browsers.

## 🛠️ Technology Stack

* **Backend**: Python
* **Web Framework**: Streamlit
* **Data Handling**: Pandas
* **API Communication**: Requests
* **Data Source**: The Movie Database (TMDB) API

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

* Python 3.8 or higher
* `pip` (Python package installer)
* A free API Key from [The Movie Database (TMDB)](https://www.themoviedb.org/signup).

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/movie-recommender.git](https://github.com/your-username/movie-recommender.git)
    cd movie-recommender
    ```

2.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your TMDB API Key:**
    This project uses Streamlit's secrets management. You need to create a special file to store your key.

    * Create a new folder named `.streamlit` in the root of your project directory.
    * Inside the `.streamlit` folder, create a new file named `secrets.toml`.
    * Open `secrets.toml` and add your API key in the following format:
        ```toml
        # .streamlit/secrets.toml
        
        [tmdb]
        api_key = "YOUR_TMDB_API_KEY_GOES_HERE"
        ```
    Replace `"YOUR_TMDB_API_KEY_GOES_HERE"` with the actual v3 API key you obtained from TMDB.

4.  **Run the Streamlit application:**
    Open your terminal in the project's root directory and run the following command:
    ```bash
    streamlit run app.py
    ```
    Your web browser should automatically open with the application running.

## 🔧 How It Works

1.  **Fetch Popular Movies**: On startup, the app calls the `/movie/popular` endpoint of the TMDB API to populate the dropdown selector.
2.  **User Selection**: The user chooses a movie from the list.
3.  **Get Recommendations**: When the "Get Recommendation" button is clicked, the app retrieves the ID of the selected movie.
4.  **API Call**: It then makes a request to the `/movie/{movie_id}/recommendations` TMDB endpoint using that ID.
5.  **Display Results**: The app processes the API response, fetches the poster for each recommended movie, and displays them in a clean 5-column layout.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## 📄 License

This project is open-source. Feel free to use and modify it.
