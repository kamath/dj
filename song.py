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
        self.timer = threading.Timer(0, self.play)

    '''
    If nothing is playing, it plays the song in the queue. Otherwise, it starts a timer to wait until the song is done 
    '''
    def queue(self):
        try:
            playback_data: dict = self.display()
            self.wait((playback_data['item']['duration_ms'] - playback_data['progress_ms']) // 1000)
            print(playback_data)
        except:
            self.play()


    def add(self, song, header):
        self.q += 1

        params = (
            ('uris', song),
        )

        response = requests.post('https://api.spotify.com/v1/playlists/2CbUu1gLjkiPb1OnEvfvt8/tracks', headers=header,
                                 params=params)
        print(response.text)
        song_id = song.split(':')[-1]
        song_data = json.loads(requests.get(f'https://api.spotify.com/v1/tracks/{song_id}', headers=header).text)

        print('added song to playlist')

        self.header = header
        self.queue()
        return song_data

    def display(self):
        try:
            playback_data = requests.get('https://api.spotify.com/v1/me/player', headers=self.header).text
            playback_data = json.loads(playback_data)
            return playback_data
        except json.decoder.JSONDecodeError:
            return "-1"

    def play(self):
        print(f'Playing {self.q} songs next')
        print(self.q)
        if self.q == 0:
            requests.put('https://api.spotify.com/v1/me/player/shuffle?state=true', headers=self.header)
            party_playlist = 'spotify:playlist:5xu64XCQFMAZJG20Lv1y7t'
            data = '{"context_uri":"' + party_playlist + '"}'
            response = requests.put('https://api.spotify.com/v1/me/player/play', headers=self.header, data=data)

        else:
            requests.put('https://api.spotify.com/v1/me/player/shuffle?state=false', headers=self.header)
            items = self.get_queue()
            items = len(items['items'])
            print(items)
            queue_playlist = 'spotify:playlist:2CbUu1gLjkiPb1OnEvfvt8'
            data = '{"context_uri":"' + queue_playlist + '", "offset": {"position": ' + str(items) + '}}'

            response = requests.put('https://api.spotify.com/v1/me/player/play', headers=self.header, data=data)

            self.q -= 1
            print(response, response.text)

        self.timer.cancel()
        self.queue()

    def update(self, header):
        self.header = header
        self.updated = True

    def wait(self, time: int):
        self.timer = threading.Timer(time - 1, self.play)
        self.timer.start()

    def next(self):
        self.timer.cancel()
        self.play()

    def search(self, song, access):
        self.header = access
        params = (
            ('q', song),
            ('type', 'track'),
        )
        response = requests.get('https://api.spotify.com/v1/search', headers=self.header, params=params)
        return json.loads(response.text)

    def get_queue(self):
        if self.q > 0:
            tor = json.loads(requests.get('https://api.spotify.com/v1/playlists/2CbUu1gLjkiPb1OnEvfvt8/tracks',
                                    headers=self.header).text)['items'][-self.q:]
        else:
            tor = []
        print(self.q, tor)
        return {'items': tor}