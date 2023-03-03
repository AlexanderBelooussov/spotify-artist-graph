import os
import pickle

import networkx as nx
import spotipy as spotipy
from spotipy import SpotifyOAuth

from config import *

os.environ["SPOTIPY_CLIENT_ID"] = cli_id
os.environ["SPOTIPY_CLIENT_SECRET"] = cli_key
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8888/callback"


def create_tracks_pkl(sp):
    if os.path.exists("tracks.pkl"):
        return
    max = 999999
    found = 0
    all_tracks = []
    while found < max:
        playlist_items = sp.playlist_items(uri, limit=100, offset=found)
        for i, track in enumerate(playlist_items['items']):
            if 'BE' in track['track']['available_markets']:
                all_tracks.append(track['track'])
        found += 100
        max = playlist_items['total']
    pickle.dump(all_tracks, open("tracks.pkl", "wb"))


def get_all_tracks():
    return pickle.load(open("tracks.pkl", "rb"))


def get_artist_dict():
    collabs = {}
    all_artists = {}
    for track in get_all_tracks():
        # all artists from track
        artists = [artist['name'] for artist in track['artists']]
        artists.sort()
        for artist in artists:
            if artist not in all_artists:
                all_artists[artist] = 0
            all_artists[artist] += 1
        # create all possible pairs
        pairs = [(a, b) for idx, a in enumerate(artists) for b in artists[idx + 1:]]
        for pair in pairs:
            if pair not in collabs:
                collabs[pair] = 0
            collabs[pair] += 1

    return collabs, all_artists


def make_graph(collabs, all_artists):
    G = nx.Graph()
    for artist, count in all_artists.items():
        G.add_node(artist, name=artist, size=count)
    for key, value in collabs.items():
        G.add_edge(key[0], key[1], weight=value)
    nx.write_gexf(G, "graph.gexf")
    nx.draw(G)
    return G


if __name__ == '__main__':
    # first this
    scope = ["playlist-read-private", "playlist-modify-public"]
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    create_tracks_pkl(sp)

    # then this
    collabs, all_artists = get_artist_dict()
    make_graph(collabs, all_artists)
