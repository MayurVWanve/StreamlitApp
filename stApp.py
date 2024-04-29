import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import base64

st.set_page_config(layout="wide")


def load_css():
    """Load CSS for background image and additional styling."""
    background_image = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://images.unsplash.com/photo-1557844681-316072353e90?q=80&w=2071&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        # https://images.unsplash.com/photo-1535587566541-97121a128dc5?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D
        # https://images.unsplash.com/photo-1557844681-316072353e90?q=80&w=2071&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D
        background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    body {
        background-color: transparent !important;
    }
    .reportview-container .main {
        background: transparent;
        color: #f1f1f1;
    }
    .reportview-container .main .block-container{
        padding-top: 5rem;
        background-color: rgba(0,0,0,0.5);
    }

    /* New styles for title and buttons */
    h1 {
        text-align: center;
        font-family: 'Ariel';
        font-size: 100px; /* Larger font size for the title */
        opacity: 0.7; /* Title opacity */
        margin-top: -80px;
        margin-bottom: 50px;
    }
    
    button {
        font-size: 80px; /* Larger font size for buttons */
        height: 75px; /* Increased button height for better visibility */
        width: 250px; /* Increased button width */
    }
    /* Style for all generic text within the app */
    div[data-testid="stText"] {
        font-size: 50px; /* Increase font size for text */
        color: white; /* Optional: change text color */
    }
    
      /* Styling for Streamlit's text input widget */
    .stTextInput > div > div > input {
        font-size: 25px;  /* Increase font size */
        color: #000; /* Text color */
        background-color: #fff; /* Background color */
        border-radius: 5px; /* Rounded corners for the input box */
        border: 2px solid #4CAF50; /* Green border */
        padding: 10px; /* Padding inside the input box for text */
    }

    /* Placeholder styling */
    ::placeholder {
        color: #888;  /* Placeholder text color */
        opacity: 1; /* Full opacity */
        font-size: 18px; /* Matching font size */
    }

    /* Focus styling to highlight the border when input is active */
    .stTextInput > div > div > input:focus {
        border-color: #FF5722; /* Change border color when focused */
        box-shadow: 0 0 8px 0 rgba(255,87,34,0.2); /* Adding a subtle shadow effect */
    }
    </style>
    """
    st.markdown(background_image, unsafe_allow_html=True)

# Call the load_css function to apply the styles
load_css()

st.title('. H A R M O N Y - D A T A B A S E .')


input_style = """
<style>
input[type="text"] {
    background-color: transparent;
    color: #a19eae;  // This changes the text color inside the input box
}
div[data-baseweb="base-input"] {
    background-color: transparent !important;
}
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}
</style>
"""
st.markdown(input_style, unsafe_allow_html=True)


# Database connection setup
connection_string = 'postgresql://suchitgoyal000:L8DG7RsjNKvl@ep-hidden-forest-a5bes70w.us-east-2.aws.neon.tech/dev?sslmode=require'
engine = create_engine(connection_string)

def run_query(query):
    try:
        with engine.connect() as conn:
            result = pd.read_sql_query(query, conn)
        return result
    except Exception as e:
        st.error(f"Error running query: {str(e)}")
        return None

# st.title('Harmony DB')

# Create a grid of buttons
col1, col2, col3, col4 = st.columns(4)
results = {}

with col1:
    if st.button('Top Artists', key ='1'):
        query = """
        SELECT artists.artist_name, COUNT(t.id) AS num_tracks, AVG(t.popularity) AS avg_popularity
        FROM artists
        JOIN track_artists at ON artists.id = at.artist
        JOIN tracks t ON at.track = t.id
        GROUP BY artists.artist_name
        ORDER BY avg_popularity DESC, num_tracks DESC
        LIMIT 10;
        """
        results['Top Artists'] = run_query(query)

with col2:
    if st.button('Avg Track Duration', key ='2'):
        query = """
        SELECT albums.album_name, AVG(CAST(tracks.duration AS numeric)) AS avg_duration
        FROM albums
        JOIN tracks ON albums.id = tracks.album
        GROUP BY albums.album_name
        ORDER BY avg_duration DESC
        LIMIT 5;
        """
        results['Avg Track Duration'] = run_query(query)

with col3:
    if st.button('Popular Tracks', key ='3'):
        query = """
        SELECT tracks.track_name, artists.artist_name, tracks.popularity
        FROM tracks
        JOIN track_artists ta ON ta.track = tracks.id
        JOIN artists ON ta.artist = artists.id
        ORDER BY tracks.popularity DESC
        LIMIT 10;
        """
        results['Popular Tracks'] = run_query(query)

with col4:
    if st.button('Common Genres',   key ='4'):
        query = """
        SELECT genres.name, COUNT(track_artists.track) AS num_tracks
        FROM genres
        JOIN artist_genres ON genres.id = artist_genres.genre
        JOIN artists ON artist_genres.artist = artists.id
        JOIN track_artists ON artists.id = track_artists.artist
        GROUP BY genres.name
        ORDER BY num_tracks DESC
        LIMIT 10;
        """
        results['Common Genres'] = run_query(query)

st.markdown('<p style="font-size: 30px; color: white; font-family:Ariel;">Retrieve songs by artist : </p>', unsafe_allow_html=True)
artist_name_input = st.text_input("Enter artist name")


if st.button('Show Artist Songs'):
    if artist_name_input:
        # This is a parameterized query to prevent SQL injection
        query_songs_by_artist = """
        SELECT tracks.track_name
        FROM artists
        JOIN track_artists ON artists.id = track_artists.artist
        JOIN tracks ON track_artists.track = tracks.id
        WHERE artists.artist_name ILIKE %s;
        """
        
        # Running the parameterized query
        try:
            with engine.connect() as conn:
                result_songs_by_artist = pd.read_sql_query(query_songs_by_artist, conn, params=(f"%{artist_name_input}%",))
            if not result_songs_by_artist.empty:
                st.subheader(f"Songs by {artist_name_input}")
                st.dataframe(result_songs_by_artist)
            else:
                st.warning("No songs found for this artist.")
        except Exception as e:
            st.error(f"Error running query: {str(e)}")
    else:
        st.warning("Please enter an artist name to search.")

# Display results in a single container
if results:
    with st.container():
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        for title, data in results.items():
            st.subheader(title)
            st.dataframe(data)
        st.markdown("</div>", unsafe_allow_html=True)
