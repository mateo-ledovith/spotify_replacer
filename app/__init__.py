from flask import Flask
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

load_dotenv()  # Load the environment variables from the .env fil

socketio = SocketIO()
app = Flask(__name__)  # 💡 Crea la instancia de la app aquí

# Configuración de la app
app.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY'),
    SPOTIFY_CLIENT_ID=os.environ.get('SPOTIFY_CLIENT_ID'),
    SPOTIFY_CLIENT_SECRET=os.environ.get('SPOTIFY_CLIENT_SECRET'),
    DOWNLOADS_FOLDER = '/app/tmp/downloads'
)

print(app.config['DOWNLOADS_FOLDER'])

socketio.init_app(app)

# Importa las rutas para que se registren con `app.route()`
from app import routes  # 💡 Se importa al final para evitar errores de importación


