import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3

def main():
    # set up found in spotipy guide 
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    conn = sqlite3.connect('finalDatabase.db')
    cursor = conn.cursor()

    # artists we are using
    artists = ["Taylor Swift", "Ed Sheeran", "Beyonce", "Bruno Mars", "Drake", "Khalid", "Lady Gaga", "Katy Perry", "Bono", "Adele"]
    # create tables artists, songs, and spotify
    cursor.execute('''CREATE TABLE IF NOT EXISTS artists
                 (id integer PRIMARY KEY, name text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS songs
                 (id integer PRIMARY KEY, name text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS spotify
                 (id integer PRIMARY KEY, artist_id integer, song_id integer, popularity integer,
                 FOREIGN KEY(artist_id) REFERENCES artists(id), FOREIGN KEY(song_id) REFERENCES songs(id))''')
    
    # Check if the artist table is empty
    cursor.execute("SELECT COUNT(*) FROM artists")
    numArtists = cursor.fetchone()[0]
    if numArtists == 0:
        #on the first run only fill artists table
        for artist in artists:
            cursor.execute("INSERT INTO artists (name) VALUES (?)", (artist,))
            conn.commit()
    else:
    # Loop through the artists and get their top tracks
        cursor.execute("SELECT COUNT(*) FROM spotify")
        numSongs = cursor.fetchone()[0]
        artist_id = numSongs // 10 +1 
        artist = artists[artist_id - 1]

        #taken from spotipy guide 
        info = sp.search(q=artist, type="artist")
        if info["artists"]["items"]:
            # Insert the artist data into the database
            songs = sp.artist_top_tracks(info["artists"]["items"][0]["id"])["tracks"][:10]
            for song in songs:
                name = song['name']
                popularity = song['popularity']

                #check if the song already occurs
                cursor.execute("SELECT COUNT(*) FROM spotify")
                numSongs = cursor.fetchone()[0]
                song_id = numSongs + 1
                cursor.execute("SELECT id FROM songs WHERE name=?", (name,))
                songNumber = cursor.fetchone()
                if songNumber is not None:
                    song_id = songNumber[0]
                
                # Insert songs and data into spotify table
                cursor.execute("INSERT INTO songs (name) VALUES (?)", (name,))
                cursor.execute("INSERT INTO spotify (artist_id, song_id, popularity) VALUES (?, ?, ?)", (artist_id, song_id, popularity))
                conn.commit()
        else:
            print(f"Error finding songs for artist {artist}")

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()