from time import sleep
import requests
import os
import threading
import json

class Song:
    def __init__(self):
        self.q = []
        self.updated = False
        self.playing = False

    def add(self, song):
        params = (
            ('uris', song),
        )

        response = requests.post('https://api.spotify.com/v1/playlists/2CbUu1gLjkiPb1OnEvfvt8/tracks', headers=self.header,
                                 params=params)
        self.q.insert(0, song)
        song_id = song.split(':')[-1]
        song_data = requests.get(f'https://api.spotify.com/v1/tracks/{song_id}', headers=self.header).text
        playback_data = requests.get('https://api.spotify.com/v1/me/player', headers=self.header).text
        return playback_data

    def display(self, song_data):
        print(song_data)

    def play(self):
        if self.playing:
            print(self.q)
            return {'swager': 'swagger?'}
        song = self.q.pop()
        print('reached here')
        print(song)
        data = '{"uris":["' + song + '"]}'

        response = requests.put('https://api.spotify.com/v1/me/player/play', headers=self.header, data=data)

        if len(self.q) > 0:
            data = dict(json.loads(response.text))
            self.timer = threading.Timer(10, self.queue)

        print(response, response.text)

    def update(self, header):
        self.header = header
        self.updated = True