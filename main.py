import requests
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic
import os
from dotenv import load_dotenv
import pprint

class MelonCrawler :
    ytmusic: YTMusic
    playlist_name = ""
    melon_song_infos = []

    def init_youtube_music_api(self, cookie, playlist_name) :
        if cookie == None :
            print("Cookie is not set.")
            return
        
        json_str = """{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "X-Goog-AuthUser": "0",
            "x-origin": "https://music.youtube.com",
            "Cookie" : "%s"
        }""" % cookie

        self.ytmusic = YTMusic(json_str)
        self.playlist_name = playlist_name

    def update_song_infos(self) :
        melon_page_req = requests.get("https://www.melon.com/chart/index.htm", headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"})
        if melon_page_req.ok == False:
            print(f"Failed to get a Melon chart page. (Status Code: {melon_page_req.status_code})")
            return

        soup = BeautifulSoup(melon_page_req.content, "html.parser")
        song_infos = soup.select(".wrap_song_info")

        self.melon_song_infos = []
        for i in range(0, len(song_infos), 2) :
            tmp = song_infos[i].find_all("div")

            title = tmp[0].span.a.text
            artist = tmp[1].span.a.text
            album = song_infos[i + 1].div.a.text

            self.melon_song_infos.append((title, artist, album))

# ----------------------------------------------

load_dotenv(verbose=True)

cookie = os.getenv("COOKIE")
playlist_name = os.getenv("PLAYLIST_NAME")
if playlist_name == None :
    playlist_name = "Melon Chart 100"

crawler = MelonCrawler()
crawler.init_youtube_music_api(cookie, playlist_name)
crawler.update_song_infos()
