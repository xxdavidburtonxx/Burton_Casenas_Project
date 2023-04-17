import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


conn = sqlite3.connect('finalDatabase.db')
c = conn.cursor()

# SQL statement to get the concerts_performed column
c.execute("SELECT ticket_master.artist_id, COUNT(*) as concerts_performed FROM ticket_master GROUP BY ticket_master.artist_id")

concerts_performed_data = c.fetchall()

# SQL statement to get the artist name and average popularity
c.execute("SELECT artists.name, AVG(spotify.popularity) as popularity FROM artists JOIN spotify ON artists.id = spotify.artist_id GROUP BY artists.name")

artist_data = c.fetchall()

# Merge the two data sets on artist_id
result = []
for artist in artist_data:
    artist_id = c.execute("SELECT id FROM artists WHERE name = ?", (artist[0],)).fetchone()[0]
    concerts_performed = [row[1] for row in concerts_performed_data if row[0] == artist_id][0]
    result.append((artist[0], artist[1], concerts_performed))

df = pd.DataFrame(result, columns=['artist', 'popularity', 'concerts_performed'])


# Create linear regression plot comparing popularity to amount of concerts performed
sns.regplot(x='concerts_performed', y='popularity', data=df)
plt.xlabel('Concerts Performed')
plt.ylabel('Popularity')
plt.title('Popularity vs. Concerts Performed')

# Show the plot
plt.show()

# sort the DataFrame by popularity in descending order
sorted_df = df.sort_values(by='popularity', ascending=False)

# create Barchart of the different artists and their popularity
plt.subplots(figsize=(10, 7))
sns.barplot(x='artist', y='popularity', data=sorted_df)
plt.xticks(rotation=45, ha='right')
plt.xlabel('Artist')
plt.ylabel('Popularity')
plt.title('Popularity of Different Artists')
plt.show()

new_sorted_df = df.sort_values(by='concerts_performed', ascending=False)
#Creating bar chart of the different artists and amount of concerts they played
plt.subplots(figsize=(10, 7))
sns.barplot(x='artist', y='concerts_performed', data=new_sorted_df)
plt.xticks(rotation=45, ha='right')
plt.xlabel('Artist')
plt.ylabel('Number of concerts performed')
plt.title('Number of concerts performed by each artist')
# Show the plot
plt.show()

