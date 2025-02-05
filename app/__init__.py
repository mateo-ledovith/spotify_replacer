import os
from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Create the Flask app instance
app = Flask(__name__)

# Configure the app
app.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'default_secret_key'),  # Default for security
    SPOTIFY_CLIENT_ID=os.environ.get('SPOTIFY_CLIENT_ID'),
    SPOTIFY_CLIENT_SECRET=os.environ.get('SPOTIFY_CLIENT_SECRET'),
    DOWNLOADS_FOLDER=os.path.join(os.getcwd(), 'tmp', 'downloads'),  # Ensures compatibility
    FFMPEG_PATH=os.environ.get('FFMPEG_PATH', '/usr/bin/ffmpeg'),  # Default for Linux
)

# Initialize Flask-SocketIO with the app
socketio = SocketIO(app)

# Import routes at the end to avoid circular imports
from app import routes
