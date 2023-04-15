import requests
import sqlite3

# Set up API and database credentials
apikey = "wxye7zQTvRKhs2EZabVNoOeOVcWAh1gU"
db_file = "ticket_prices.db"

# Define the artists you want to search for
artists = ["Ed Sheeran", "Beyonce", "Taylor Swift", "Drake", "Bruno Mars"]

# Create a SQLite database and table to store the artist-city data
conn = sqlite3.connect(db_file)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS artist_cities (
        artist TEXT,
        city TEXT,
        region TEXT,
        country TEXT,
        PRIMARY KEY (artist, city)
    )
""")

# Loop through each artist
for artist in artists:
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

            # Insert the data into the artist_cities table
            c.execute("INSERT INTO artist_cities VALUES (?, ?, ?, ?) ON CONFLICT(artist, city) DO UPDATE SET region=?, country=?", (artist, city, region, country, region, country))
            conn.commit()
    else:
        print(f"No events found for {artist}")

# Close the database connection
conn.close()
