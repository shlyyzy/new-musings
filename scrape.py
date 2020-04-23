import requests
import sys
import os
import json
import spotipy
import spotipy.util as util
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

if len(sys.argv) == 5:
    username = sys.argv[1]
    client_id = sys.argv[2]
    client_secret = sys.argv[3]
    playlist_uri = sys.argv[4]
    token = util.prompt_for_user_token(
                                username=username,
                                scope='playlist-read-private playlist-modify-private',
                                client_id=client_id,
                                client_secret=client_secret,
                                redirect_uri='https://localhost:8080')
else:
    print("Ensure that the arguments you supply are 'username' 'client_id' 'client_secret' 'playlist_uri'")
    sys.exit(1)

url = "https://www.albumoftheyear.org/releases"
page = requests.get(url)

bsoup = BeautifulSoup(page.content, 'html.parser')

content = bsoup.find(id='centerContent')

albums = content.find_all('div', class_='albumBlock')

ids = []

if token:
    sp = spotipy.Spotify(auth=token)
    for album in albums:
        artist = album.find('div', class_='artistTitle').text
        title = album.find('div', class_='albumTitle').text

        ratingContainer = album.find('div', class_='ratingRowContainer')
        rating = ratingContainer.find('div', class_='rating')
        if rating is not None:
            rating = rating.text
            if (int(rating) > 70):
                link = url + album.find('a')['href'].strip()
                info = {"artist": artist, "title": title, "rating": rating, "link": link}
                #print (artist + '\n' + title + '\n' + 'rating: ' + rating + '\n' + link + '\n')
                results = sp.search(q=artist + "+" + title, type='album', limit=1, offset=0)
                for i in results['albums']['items']:
                    albumTracks = sp.album_tracks(i['uri'])
                    for item in albumTracks['items']:
                        if len(ids) < 100:
                            ids.append(item['uri'])


    end = sp.user_playlist_add_tracks(username, playlist_uri, ids)
    print(end)
