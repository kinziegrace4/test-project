# app.py
from flask import Flask, redirect, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure random key

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'b4c8b05454bb42089878bd3ae1f648a4'
SPOTIPY_CLIENT_SECRET = '2584b9880d5c4573aa7b1da540ef2128'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

# Spotify API scope for playlist creation
SPOTIPY_SCOPE = 'playlist-modify-public playlist-modify-private'

# Spotipy OAuth handler
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SPOTIPY_SCOPE)


@app.route('/')
def index():
    return 'Welcome to the Spotify Playlist Creator! <a href="/login">Login with Spotify</a>'


@app.route('/login')
def login():
    return redirect(sp_oauth.get_authorize_url())


@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('create_playlist'))


@app.route('/create_playlist')
def create_playlist():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    # Example: Create a new playlist
    playlist_name = 'My Awesome Playlist'
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True)

    return f'Playlist "{playlist_name}" created!'


if __name__ == '__main__':
    app.run(debug=True)