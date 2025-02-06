# 🎵 Spotify Replacer

**Spotify Replacer** is a web application that allows you to download the songs from a Spotify playlist quickly, efficiently, and easily — all for free.


## 🏗️ Deployment

The repository can be cloned and run locally using the following steps:

```sh
git clone https://github.com/mateo-ledovith/spotify-replacer.git
cd spotify-replacer

bash run_docker.sh
```

Then, access the application in your browser at http://127.0.0.1:5000/.

**Note:** To run this application, you must have **Docker** installed on your system. Please ensure that Docker is properly installed before proceeding with the deployment steps.


## 🚀 How It Works

1. **Login:**  
   - The user visits the web app and authenticates via **OAuth 2.0** using their Spotify account.
   
2. **Playlist Selection:**  
   - The application sends a request to the **Spotify API** to retrieve all of the user's playlists.  
   - The playlists are displayed on screen, and the user selects the one they wish to download.

3. **Track Search:**  
   - The list of songs and corresponding artists from the selected playlist is retrieved.  
   - The third-party library **Youtube Search Python** is used to search for a corresponding YouTube link for each song.

4. **Download and Conversion:**  
   - The audio is downloaded using **yt_dlp**.  
   - The downloaded file is converted to the appropriate format with **FFmpeg**.

5. **Compression and Delivery:**  
   - Once all songs have been downloaded, they are packaged into a **ZIP file**.  
   - The user can then download the ZIP file containing all the songs.  
   - Temporary files are automatically removed from the server.

## 🛠️ Technologies Used

- **Python** (with **Flask** and **Flask-SocketIO**)
- **HTML5**, **CSS3**, **Jinja2** for the frontend
- **JavaScript** for client-side interactivity
- **OAuth 2.0** for Spotify authentication
- **Spotify API** to fetch playlists and tracks
- **Youtube Search Python** to find YouTube links for tracks
- **yt_dlp** to download audio from YouTube
- **Docker** for containerization and deployment
- **Bash scripting** for process automation
- **FFmpeg** for post-processing audio files

## ⚠️ Disclaimer

This project was created for educational purposes and is not intended to be used for the illegal download of copyrighted material.  
Using this application to obtain music without proper authorization may violate the terms of service of **Spotify** and **YouTube**.  
The author of this software is not responsible for any misuse.
