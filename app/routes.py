import os
import shutil
import requests
import urllib.parse
from datetime import datetime
from flask import redirect, request, session, render_template, url_for, send_file, g
from app.zip import create_zip
from app import app, socketio
from .downloads import download_youtube_media, find_youtube_link
from .utils import extract_tracks
from .helpers import is_authenticated, refresh_access_token, is_token_expired


# Load configuration from app instance
CLIENT_ID = app.config['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = app.config['SPOTIFY_CLIENT_SECRET']
FLASK_SECRET_KEY = app.config['SECRET_KEY']
DOWNLOADS_FOLDER = app.config['DOWNLOADS_FOLDER']

# Spotify API constants
REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'
SCOPE = 'playlist-read-private playlist-read-collaborative'

@app.before_request
def check_authentication():
    """Global authentication and token expiration check before each request."""
    # Skip authentication check for specific endpoints
    if getattr(g, 'skip_auth', False):
        return None  # Just continue with the request handling
    
    if not is_authenticated():
        return redirect(url_for('login'))
    if is_token_expired():
        return redirect(url_for('refresh_token'))


### Flask Routes ###

@app.route('/')
def index():
    g.skip_auth = True  # Skip authentication check for this route
    
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect user to Spotify authorization page."""
    
    g.skip_auth = True  # Skip authentication check for this route
    
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'show_dialog': True,
    }
    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback."""
    if 'error' in request.args:
        return redirect(url_for('error_page', error_code=400, error_message=request.args['error']))

    if 'code' not in request.args:
        return redirect(url_for('error_page', error_code=400, error_message="Authorization code missing"))

    req_body = {
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    try:
        response = requests.post(TOKEN_URL, data=req_body, timeout=10)
        token_info = response.json()
    except requests.RequestException:
        return redirect(url_for('error_page', error_code=500, error_message="Failed to retrieve access token"))

    if 'access_token' not in token_info:
        return redirect(url_for('error_page', error_code=500, error_message="Failed to retrieve access token"))

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info.get('refresh_token', '')
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    return redirect(url_for('playlists'))
    
@app.route('/playlists', methods=['GET', 'POST'])
def playlists():
    """Display the user's Spotify playlists."""
    
    # Get the playlists from Spotify
    headers = {
        'Authorization': f'Bearer {session["access_token"]}',
    }
    response = requests.get(f'{API_BASE_URL}me/playlists', headers=headers)
    
    try:
        playlists = response.json()
        playlist_data = [
            {"name": playlist['name'], "id": playlist['id'], "images": playlist['images'], "song_list": playlist['tracks']['href']}
            for playlist in playlists['items']
        ]
    except ValueError:
        return redirect(url_for('error_page', error_code=500, error_message="Failed to fetch playlists"))

    if request.method == 'POST':
        selected_playlist_id = request.form.get('playlist')  # Get the playlist ID from the form
        
        if selected_playlist_id:  # Ensure the ID is not None
            return redirect(url_for('download_playlist', playlist_id=selected_playlist_id))

    return render_template('playlists.html', playlists=playlist_data, success=False)


@app.route('/download-playlist/<playlist_id>', methods=['GET', 'POST'])
def download_playlist(playlist_id):

    headers = {
        'Authorization': f'Bearer {session["access_token"]}',
    }
    tracks_response = requests.get(f'{API_BASE_URL}playlists/{playlist_id}/tracks', headers=headers)
    tracks = extract_tracks(tracks_response.json())

    # Handle GET: Render the HTML view
    playlist_response = requests.get(f'{API_BASE_URL}playlists/{playlist_id}', headers=headers)
    
    if playlist_response.status_code != 200 or tracks_response.status_code != 200:
        return redirect(url_for('error_page', error_code=500, error_message="Failed to fetch playlist details or tracks"))

    playlist_data = playlist_response.json()
    playlist_name = playlist_data.get('name', 'Unknown Playlist')
    playlist_image_url = playlist_data['images'][0]['url'] if playlist_data['images'] else None

    
    return render_template(
        'download_playlist.html',
        playlist_name=playlist_name,
        playlist_image_url=playlist_image_url,
        playlist_id=playlist_id,
        tracks=tracks
    )

@app.route('/download-playlist/progress/<socketid>', methods=['POST'])
def download_playlist_progress(socketid):
    """Handles downloading a Spotify playlist and sending it as a zip file."""

    # Use a context manager for file cleanup
    temp_dir = os.path.join(DOWNLOADS_FOLDER, socketid)
    zip_filename = os.path.join(DOWNLOADS_FOLDER, f'{socketid}.zip')

    try:
        os.makedirs(temp_dir, exist_ok=True)  # Create a unique folder for downloads
        tracks = request.json.get('tracks', [])
        playlist_name = request.json.get('playlist_name', 'playlist')

        if not tracks:
            return redirect(url_for('error_page', error_code=400, error_message="No tracks received for download"))

        # Download tracks
        for index, track in enumerate(tracks):
            try:
                youtube_link = find_youtube_link(f"{track['track_name']} {track['artist']} audio")
                download_youtube_media(youtube_link, temp_dir)
            except Exception as e:
                app.logger.error(f"Failed to download {track['track_name']}: {str(e)}")
                continue  # Skip failed downloads

            # Update progress via WebSocket
            progress = int((index + 1) / len(tracks) * 100)
            socketio.emit('update progress', progress, to=socketid)

        # Create ZIP archive
        create_zip(temp_dir, zip_filename)
        if not os.path.exists(zip_filename):
            return redirect(url_for('error_page', error_code=500, error_message="ZIP creation failed"))

        return send_file(zip_filename, as_attachment=True, download_name=f'{playlist_name}.zip', mimetype='application/zip')

    except Exception as e:
        app.logger.error(f"Error in download process: {str(e)}")
        return redirect(url_for('error_page', error_code=500, error_message=f"Error in download process: {str(e)}"))

    finally:
        # Cleanup temporary files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)

@app.route('/refresh-token')
def refresh_token():
    """Manually refresh the Spotify access token if expired."""
    if refresh_access_token():
        return redirect(url_for('playlists'))
    return redirect(url_for('error_page', error_code=500, error_message="Failed to refresh access token"))

### Error Handlers ###

@app.route('/error/<int:error_code>/<error_message>')
def error_page(error_code, error_message):
    """Custom error page."""
    return render_template('error.html', error_code=error_code, error_message=error_message), error_code

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404