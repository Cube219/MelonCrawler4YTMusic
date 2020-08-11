import requests
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic
import os
from dotenv import load_dotenv
import pprint

def GetSongInfos() :
    melonPageReq = requests.get("https://www.melon.com/chart/index.htm", headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"})
    if melonPageReq.ok == False:
        print(f"Failed to get a Melon chart page. (Status Code: {melonPageReq.status_code})")
        return []

    soup = BeautifulSoup(melonPageReq.content, "html.parser")
    songInfos = soup.select(".wrap_song_info")

    songs = []
    for i in range(0, len(songInfos), 2) :
        tmp = songInfos[i].find_all("div")

        title = tmp[0].span.a.text
        artist = tmp[1].span.a.text
        album = songInfos[i + 1].div.a.text

        songs.append((title, artist, album))

    return songs

# ----------------------------------------------

load_dotenv(verbose=True)

cookie = os.getenv("COOKIE")

if cookie == None :
    print("Cookie is not set.")
    # return

jsonStr = """{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "X-Goog-AuthUser": "0",
    "x-origin": "https://music.youtube.com",
    "Cookie" : "%s"
}""" % cookie

ytmusic = YTMusic(jsonStr)

search_results = ytmusic.get_library_playlists()
