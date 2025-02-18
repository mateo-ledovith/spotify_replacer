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

    # Extract track details from the 'items' list in the response data
    # Using .get() to safely handle potential missing keys in the JSON response
    for item in data.get('items', []):  
        track = item.get('track', {})  # Get the 'track' dictionary for each item
        
        # Extract track name, default to 'Unknown Track' if missing
        track_name = track.get('name', 'Unknown Track')
        
        # Extract album information, including album cover image URL
        album = track.get('album', {})
        album_image_url = album.get('images', [{}])[0].get('url', None)  # Handle possible missing 'images' key

        # Extract the main artist's name (first in the list of artists)
        artists = track.get('artists', [])
        artist_name = artists[0].get('name', 'Unknown Artist') if artists else 'Unknown Artist'

        # Append the track details to the list
        tracks.append({
            'track_name': track_name,
            'artist': artist_name,
            'album_photo_url': album_image_url
        })

    return tracks
