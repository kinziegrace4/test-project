# app.py
from flask import Flask, redirect, request, session, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'b4c8b05454bb42089878bd3ae1f648a4'
SPOTIPY_CLIENT_SECRET = '2584b9880d5c4573aa7b1da540ef2128'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

# Spotify API scope for playlist creation
SPOTIPY_SCOPE = 'playlist-modify-public playlist-modify-private'

# Spotipy OAuth handler
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SPOTIPY_SCOPE)

# Spotify Web Playback SDK script
SPOTIFY_PLAYER_SCRIPT = 'https://sdk.scdn.co/spotify-player.js'

class AddSongForm(FlaskForm):
    track_uri = StringField('Spotify Track URI', validators=[DataRequired()])
    submit = SubmitField('Add Song')


@app.route('/')
def index():
    token_info = session.get('token_info', None)
    user_info = None

    if token_info:
        sp = Spotify(auth=token_info['access_token'])
        user_info = sp.me()

    return render_template('index.html', user_info=user_info)


@app.route('/login')
def login():
    return redirect(sp_oauth.get_authorize_url())


@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    session.permanent = True
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # # Clear user's session
    session.clear()
    # Clear the user's session
    session.pop('token_info', None)

    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    token_info = session.get('token_info', None)
    playlist_id = session.get('playlist_id', None)

    if not token_info or not playlist_id:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    # Get the playlist details
    playlist = sp.playlist(playlist_id)

    # Create an instance of the AddSongForm
    add_song_form = AddSongForm()

    # Handle form submission
    if add_song_form.validate_on_submit():
        # Example: Add a song to the playlist
        track_uri = add_song_form.track_uri.data
        sp.playlist_add_items(playlist_id, [track_uri])

        # # Redirect back to the playlist page
        # return redirect(url_for('playlist'))

    return render_template('playlist.html', playlist=playlist, add_song_form=add_song_form,
                           spotify_player_script=SPOTIFY_PLAYER_SCRIPT)


@app.route('/add_song', methods=['POST'])
def add_song():
    token_info = session.get('token_info', None)
    playlist_id = session.get('playlist_id', None)

    if not token_info or not playlist_id:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    # Example: Add a song to the playlist
    track_uri = request.form.get('track_uri')
    sp.playlist_add_items(playlist_id, [track_uri])

    # Redirect back to the playlist page
    return redirect(url_for('playlist'))

if __name__ == '__main__':
    app.run(debug=True)