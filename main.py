import requests
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic
import os
from dotenv import load_dotenv
import pprint
import logging

class MelonCrawler :
    ytmusic: YTMusic
    playlist_name = ""
    melon_song_infos = []

    before_playlist_id = ""
    song_ids = []

    def init_youtube_music_api(self, cookie, playlist_name) :
        logging.info("Initializing youtube music api...")

        if cookie == None :
            raise Exception("Cookie is not set.")
        
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
        
        logging.info("Successfully initialize youtube music api.")

    def update_song_infos(self) -> bool :
        logging.info("Updating Melon chart 100 infos...")

        melon_page_req = requests.get("https://www.melon.com/chart/index.htm", headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"})
        if melon_page_req.ok == False:
            logging.error(f"Failed to get a Melon chart page. (Status Code: {melon_page_req.status_code})")
            return False

        soup = BeautifulSoup(melon_page_req.content, "html.parser")
        song_infos = soup.select(".wrap_song_info")

        self.melon_song_infos = []
        for i in range(0, len(song_infos), 2) :
            tmp = song_infos[i].find_all("div")

            title = tmp[0].span.a.text
            artist = tmp[1].span.a.text
            album = song_infos[i + 1].div.a.text

            self.melon_song_infos.append((title, artist, album))

        logging.info("Successfully update Melon chart 100 infos.")
        return True

    def update_song_ids(self) :
        logging.info("Updating song ids...")

        self.song_ids = []
        update_count = 1

        for song_info in self.melon_song_infos :
            song_title = song_info[0]
            song_artist = song_info[1]
            song_album = song_info[2]

            song_id = "NotFound"

            logging.info(f"Getting song id... ({update_count}/{len(self.melon_song_infos)}) / {song_title}")

            # 곡명으로 검색
            search_res = self.ytmusic.search(song_title)

            # 1. artist가 일치
            for i in range(0, len(search_res)) :
                info = search_res[i]
                if "videoId" not in info :
                    continue

                if "artist" in info :
                    if info["artist"].find(song_artist) != -1 or song_artist.find(info["artist"]) != -1 :
                        song_id = info["videoId"]
                        break

                if "artists" in info :
                    for artist in info["artists"] :
                        artist_name = artist["name"]
                        if artist_name.find(song_artist) != -1 or song_artist.find(artist_name) != -1 :
                            song_id = info["videoId"]
                            break
                
                if song_id != "NotFound":
                    break
            
            if song_id != "NotFound" :
                self.song_ids.append(song_id)
                continue
            
            # 2. album이 일치
            for i in range(0, len(search_res)) :
                info = search_res[i]
                if "videoId" not in info or "album" not in info :
                    continue

                album_name = info["album"]["name"]

                if album_name.find(song_album) != -1 or song_album.find(album_name) != -1 :
                    song_id = info["videoId"]
                    break

            if song_id != "NotFound" :
                self.song_ids.append(song_id)
                continue
            
            # 3. 그냥 맨 앞에 것
            for i in range(0, len(search_res)) :
                info = search_res[i]
                if "videoId" not in info :
                    continue
                
                song_id = info["videoId"]
                break

            self.song_ids.append(song_id)
            update_count = update_count + 1

        logging.info("Successfully update song ids.")

# ----------------------------------------------

if os.path.isdir("log") == False :
    os.mkdir("log")
logging.basicConfig(filename="log/log.log", level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

load_dotenv(verbose=True)

cookie = os.getenv("COOKIE")
playlist_name = os.getenv("PLAYLIST_NAME")
if playlist_name == None :
    playlist_name = "Melon Chart 100"

crawler = MelonCrawler()
crawler.init_youtube_music_api(cookie, playlist_name)
crawler.update_song_infos()
crawler.update_song_ids()
