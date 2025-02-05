import requests
from datetime import datetime
from flask import session, redirect, url_for
from app import app

# Load Spotify API constants from app config
CLIENT_ID = app.config['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = app.config['SPOTIFY_CLIENT_SECRET']
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

def is_authenticated():
    """Check if the user is authenticated."""
    return 'access_token' in session

def is_token_expired():
    """Check if the access token has expired."""
    return datetime.now().timestamp() > session.get('expires_at', 0)

def refresh_access_token():
    """Refresh the user's Spotify access token."""
    if 'refresh_token' not in session:
        return False

    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    response = requests.post(TOKEN_URL, data=req_body)

    if response.status_code != 200:
        app.logger.error(f"Failed to refresh token: {response.text}")
        return False

    new_token_info = response.json()
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    
    return True

def spotify_get(endpoint):
    """Send a GET request to Spotify API and handle errors."""
    if not is_authenticated():
        return redirect(url_for('login'))

    headers = {'Authorization': f'Bearer {session["access_token"]}'}

    response = requests.get(f'{API_BASE_URL}{endpoint}', headers=headers)

    if response.status_code != 200:
        app.logger.error(f"Spotify API error ({response.status_code}): {response.text}")
        return None

    return response.json()
