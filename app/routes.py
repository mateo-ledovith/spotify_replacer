from datetime import datetime
import requests
from flask import redirect, request, jsonify, session, render_template, url_for, jsonify, send_file, after_this_request
import urllib.parse
from .downloads import download_youtube_audio, find_youtube_link
from .utils import extract_tracks
import os
import shutil
from app.zip import create_zip
from app import app, socketio


CLIENT_ID = app.config['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = app.config['SPOTIFY_CLIENT_SECRET']
FLASK_SECRET_KEY = app.config['SECRET_KEY']
DOWNLOADS_FOLDER = app.config['DOWNLOADS_FOLDER']

REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'
SCOPE = 'playlist-read-private playlist-read-collaborative'



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    scope = SCOPE
    
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
        'show_dialog': False, # If set to True the user has to login every time they want to use the app
    }
    
    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']}), 400  

    if 'code' not in request.args:
        return jsonify({"error": "Authorization code missing"}), 400  

    req_body = {
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    try:
        response = requests.post(TOKEN_URL, data=req_body, timeout=10)  # 10 seconds timeout
    except:
        return jsonify({"error": "Failed to retrieve access token"}), 400    
    

    token_info = response.json()
    
    if 'access_token' not in token_info:
        return jsonify({"error": "Failed to retrieve access token", "details": token_info}), 400

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info.get('refresh_token', '')  # Not always returned
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    return redirect('/playlists')
    
@app.route('/playlists', methods=['GET', 'POST'])
def playlists():
    # Check if user is authenticated
    if 'access_token' not in session:
        return redirect('/login')
    
    # Check if the token has expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

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
        playlist_data = []

    if request.method == 'POST':
        selected_playlist_id = request.form.get('playlist')  # Get the playlist ID from the form
        
        
        if selected_playlist_id:  # Ensure the ID is not None
            return redirect(url_for('download_playlist', playlist_id=selected_playlist_id))

            
    return render_template('playlists.html', playlists=playlist_data, success=False)


@app.route('/download-playlist/<playlist_id>', methods=['GET', 'POST'])
def download_playlist(playlist_id):
        
    # Check if user is authenticated
    if 'access_token' not in session:
        return redirect('/login')

    # Check if the token has expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f'Bearer {session["access_token"]}',
    }
    tracks_response = requests.get(f'{API_BASE_URL}playlists/{playlist_id}/tracks', headers=headers)
    tracks = extract_tracks(tracks_response.json())

    # Handle GET: Render the HTML view
    playlist_response = requests.get(f'{API_BASE_URL}playlists/{playlist_id}', headers=headers)
    
    if playlist_response.status_code != 200 or tracks_response.status_code != 200:
        return redirect('/playlists')

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
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    try:
        temp_dir = f'{DOWNLOADS_FOLDER}/{socketid}'
        
        os.makedirs(temp_dir, exist_ok=True)
                
        tracks = request.json['tracks']
        total_tracks = len(tracks)
        
        for index, track in enumerate(tracks):
            youtube_link = find_youtube_link(f"{track['track_name']} {track['artist']}")
            try:
                download_youtube_audio(youtube_link, temp_dir)
            except Exception as e:
                print(f"Failed to download {track['track_name']}: {str(e)}")
                continue
            progress = int((index + 1) / total_tracks * 100)
            socketio.emit('update progress', progress, to=socketid)
        
        zip_filename = os.path.join(DOWNLOADS_FOLDER, f'{socketid}.zip')
        
        create_zip(temp_dir, zip_filename)
        
        if not os.path.exists(zip_filename):
            raise Exception("Failed to create zip file")

        playlist_name = request.json['playlist_name']
        
        return send_file(zip_filename, as_attachment=True, download_name=f'{playlist_name}', mimetype='application/zip')

    except Exception as e:
        app.logger.error(f"Error in download process: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Cleanup code remains the same
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
        
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        
        return redirect('/playlists') 

if __name__ == '__main__':
    socketio.run(app=app, host='0.0.0.0', debug=True, port=5000)