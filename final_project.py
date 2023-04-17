import requests
import sqlite3

# Set up API and database credentials
apikey = "wxye7zQTvRKhs2EZabVNoOeOVcWAh1gU"

# Define the artists you want to search for
artists = ["Taylor Swift", "Ed Sheeran", "Beyonce", "Bruno Mars", "Drake", "Khalid", "Lady Gaga", "Katy Perry", "Bono", "Adele"]

# Create a SQLite database and table to store the artist-city data
conn = sqlite3.connect('finalDatabase.db')
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS ticket_master (
        id INTEGER PRIMARY KEY,
        artist_id INTEGER,
        city TEXT,
        region TEXT,
        country TEXT,
        FOREIGN KEY(artist_id) REFERENCES artists(id),
        UNIQUE(artist_id, city)
    )
""")


c.execute("SELECT COUNT(*) FROM ticket_master")
numArtists = c.fetchone()[0]
artist = ""
artist_id = 1
if numArtists == 0:
    artist = artists[0]
else:
    c.execute("SELECT artist_id FROM ticket_master ORDER BY id DESC LIMIT 1")
    artist_id = c.fetchone()[0]
    artist_id += 1
    c.execute("SELECT name FROM artists WHERE id=?", (artist_id,))
    artist = c.fetchone()[0]

print(f"This is {artist} cities")
# Search for events for the artist
search_url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={apikey}&keyword={artist}"
search_response = requests.get(search_url).json()

# Get the cities where the artist performed and retrieve the pricing details for each event
if "_embedded" in search_response:
    for event in search_response["_embedded"]["events"]:
        city = event["_embedded"]["venues"][0]["city"]["name"]
        region = event["_embedded"]["venues"][0]["state"]["name"]
        country = event["_embedded"]["venues"][0]["country"]["name"]
        
        c.execute("SELECT MAX(id) FROM ticket_master")
        max_id = c.fetchone()[0]
        if max_id is None:
            max_id = 1

        # Insert the data into the artist_cities table
        c.execute("""
            INSERT OR REPLACE INTO ticket_master (id, artist_id, city, region, country)
            VALUES ((SELECT id FROM ticket_master WHERE artist_id=? AND city=?), ?, ?, ?, ?)""", (artist_id, city, artist_id, city, region, country))


        conn.commit()
else:
    print(f"No events found for {artist}")


# Close the database connection
conn.close()