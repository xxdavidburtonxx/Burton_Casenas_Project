import requests
import sqlite3

def gather_and_store(c, conn, apikey, artists):
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
            region_country = region + "," + country
            c.execute("SELECT COUNT(*) FROM ticket_master")
            max_id = c.fetchone()[0]
            curr_id = max_id + 1
            c.execute('INSERT OR IGNORE INTO region_country (name) VALUES (?)', (region_country,))
            c.execute('INSERT OR IGNORE INTO cities (name) VALUES (?)', (city,))
            # Insert the data into the artist_cities table
            c.execute("""
                INSERT OR IGNORE INTO ticket_master (id, artist_id, city_id, region_country_id)
                VALUES (?, ?, (SELECT id FROM cities WHERE name = ?), (SELECT id FROM region_country WHERE name = ?) )""", (curr_id, artist_id, city, region_country))


            conn.commit()
    else:
        print(f"No events found for {artist}")

def main():
    # Set up API and database credentials
    apikey = "wxye7zQTvRKhs2EZabVNoOeOVcWAh1gU"

    # Define the artists you want to search for
    artists = ["Taylor Swift", "Ed Sheeran", "Beyonce", "Bruno Mars", "Drake", "Khalid", "Lady Gaga", "Katy Perry", "Bono", "Adele"]

    # Create a SQLite database and table to store the artist-city data
    conn = sqlite3.connect('finalDatabase.db')
    c = conn.cursor()
    # c.execute('''DROP TABLE IF EXISTS ticket_master''')
    # c.execute('''DROP TABLE IF EXISTS region_country''')
    # c.execute('''DROP TABLE IF EXISTS cities''')
    c.execute('''CREATE TABLE IF NOT EXISTS region_country
                    (id integer PRIMARY KEY, name text , UNIQUE(name))''')
    c.execute('''CREATE TABLE IF NOT EXISTS cities
                    (id integer PRIMARY KEY, name text , UNIQUE(name))''')
    c.execute("""
        CREATE TABLE IF NOT EXISTS ticket_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER,
            city_id INTEGER,
            region_country_id INTEGER,
            FOREIGN KEY(artist_id) REFERENCES artists(id), 
            FOREIGN KEY(region_country_id) REFERENCES region_country(id), 
            FOREIGN KEY(city_id) REFERENCES cities(id)
            UNIQUE(artist_id, city_id)
        )
    """)

    gather_and_store(c, conn, apikey, artists)
    # Close the database connection
    conn.close()
if __name__ == "__main__":
    main()