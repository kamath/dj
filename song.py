from time import sleep
import requests
import os
import threading
import json

'''
TODO:

- Localize all constants in one place
- Add methods to refresh tokens
'''

class Song:
    def __init__(self):
        self.q = 0
        self.timer = threading.Timer(0, lambda: print('Timer started'))

    def queue(self):
        playback_data = json.loads(requests.get('https://api.spotify.com/v1/me/player', headers=self.header).text)

        self.wait((playback_data['item']['duration_ms'] - playback_data['progress_ms']) // 1000)

        print(playback_data)
        return playback_data

    def add(self, song, header):
        self.q += 1

        params = (
            ('uris', song),
        )

        response = requests.post('https://api.spotify.com/v1/playlists/2CbUu1gLjkiPb1OnEvfvt8/tracks', headers=header,
                                 params=params)
        song_id = song.split(':')[-1]
        song_data = json.loads(requests.get(f'https://api.spotify.com/v1/tracks/{song_id}', headers=header).text)

        self.header = header
        self.display(song_data)
        return self.queue()

    def display(self, song_data):
        print(song_data)

    def play(self):
        print('reached')
        print(self.q)
        if self.q == 0:
            requests.put('https://api.spotify.com/v1/me/player/shuffle?state=true', headers=self.header)
            party_playlist = 'spotify:playlist:5xu64XCQFMAZJG20Lv1y7t'
            data = '{"context_uri":"' + party_playlist + '"}'
            response = requests.put('https://api.spotify.com/v1/me/player/play', headers=self.header, data=data)
            self.timer.cancel()
            self.timer = threading.Timer(0, lambda: print('Timer started'))

        else:
            requests.put('https://api.spotify.com/v1/me/player/shuffle?state=false', headers=self.header)
            items = json.loads(requests.get('https://api.spotify.com/v1/playlists/2CbUu1gLjkiPb1OnEvfvt8/tracks', headers=self.header).text)
            items = len(items['items'])
            print(items)
            queue_playlist = 'spotify:playlist:2CbUu1gLjkiPb1OnEvfvt8'
            data = '{"context_uri":"' + queue_playlist + '", "offset": {"position": ' + str(items - self.q) + '}}'

            response = requests.put('https://api.spotify.com/v1/me/player/play', headers=self.header, data=data)

            self.q -= 1
            print(response, response.text)
        self.timer.cancel()
        self.queue()

    def update(self, header):
        self.header = header
        self.updated = True

    def wait(self, time: int):
        self.timer = threading.Timer(time, self.play)
        self.timer.start()

    def next(self):
        self.timer.cancel()
        self.timer = threading.Timer(0, lambda: print('fake timer'))
        self.play()