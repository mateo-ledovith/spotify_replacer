def extract_tracks(data):
    '''
    Extracts track details from the playlist's JSON data.
    Each track includes its name, main artist, and album photo URL.

    Args:
        data (dict): JSON response from the Spotify API containing playlist tracks.

    Returns:
        list: A list of dictionaries, each containing track details (name, artist, album image).
    '''
    tracks = []

    # Extract track details from the items list
    for item in data.get('items', []):
        track = item.get('track', {})
        
        # Extract main track info
        track_name = track.get('name', 'Unknown Track')
        album = track.get('album', {})
        album_image_url = album.get('images', [{}])[0].get('url', None)

        # Extract the main artist's name (first in the list of artists)
        artists = track.get('artists', [])
        artist_name = artists[0].get('name', 'Unknown Artist') if artists else 'Unknown Artist'

        # Append track details to the list
        tracks.append({
            'track_name': track_name,
            'artist': artist_name,
            'album_photo_url': album_image_url
        })

    return tracks
