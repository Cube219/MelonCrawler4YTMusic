import requests
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic
import os, traceback
from dotenv import load_dotenv
import pprint
import logging
from time import sleep

class MelonCrawler :
    ytmusic: YTMusic
    playlist_name = ""
    melon_song_infos = []

    playlist_id = ""
    song_ids = []

    def init_youtube_music_api(self, cookie, playlist_name) :
        logging.info("Initializing youtube music api...")

        if cookie == None :
            raise Exception("Cookie is not set.")
        
        json_str = """{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
            "Accept": "*/*",
            "Accept-Language": "ko,en-US,en;q=0.5",
            "Content-Type": "application/json",
            "X-Goog-AuthUser": "0",
            "x-origin": "https://music.youtube.com",
            "Cookie" : "%s"
        }""" % cookie

        self.ytmusic = YTMusic(json_str, language='ko')
        self.playlist_name = playlist_name
        
        logging.info("Successfully initialize youtube music api.")

    def get_chart_infos(self) :
        logging.info("Getting Melon chart infos...")

        melon_page_req = requests.get("https://www.melon.com/chart/index.htm", headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"})
        if melon_page_req.ok == False:
            raise Exception(f"Failed to get a Melon chart page. (Status Code: {melon_page_req.status_code})")

        soup = BeautifulSoup(melon_page_req.content, "html.parser")
        song_infos = soup.select(".wrap_song_info")

        self.melon_song_infos = []
        for i in range(0, len(song_infos), 2) :
            tmp = song_infos[i].find_all("div")

            title = tmp[0].span.a.text
            artist = tmp[1].span.a.text
            album = song_infos[i + 1].div.a.text

            self.melon_song_infos.append((title, artist, album))

        logging.info("Successfully get Melon chart infos.")

    def get_song_ids(self) :
        logging.info("Getting song ids...")

        self.song_ids = []
        update_count = 0
        skip_num = 0

        for song_info in self.melon_song_infos :
            update_count = update_count + 1

            song_title = song_info[0]
            song_artist = song_info[1]
            song_album = song_info[2]

            song_id = "NotFound"

            logging.info(f"Getting song id... ({update_count}/{len(self.melon_song_infos)}) / {song_title} - {song_artist}")

            # Search by title
            search_res = self.ytmusic.search(song_title, filter="songs")

            # 1. Check album
            for i in range(0, len(search_res)) :
                info = search_res[i]
                if "videoId" not in info or "album" not in info :
                    continue
                if info["album"] is None :
                    continue

                album_name = info["album"]["name"]

                if album_name.find(song_album) != -1 or song_album.find(album_name) != -1 :
                    song_id = info["videoId"]
                    break

            if song_id != "NotFound" :
                if song_id not in self.song_ids :
                    self.song_ids.append(song_id)
                else :
                    skip_num += 1
                continue

            # 2. Check artist
            for i in range(0, len(search_res)) :
                info = search_res[i]
                if "videoId" not in info :
                    continue

                if "artist" in info and info["artist"] is not None :
                    if info["artist"].find(song_artist) != -1 or song_artist.find(info["artist"]) != -1 :
                        song_id = info["videoId"]
                        break

                if "artists" in info and info["artists"] is not None :
                    for artist in info["artists"] :
                        artist_name = artist["name"]
                        if artist_name.find(song_artist) != -1 or song_artist.find(artist_name) != -1 :
                            song_id = info["videoId"]
                            break
                
                if song_id != "NotFound":
                    break
            
            if song_id != "NotFound" :
                if song_id not in self.song_ids :
                    self.song_ids.append(song_id)
                else :
                    skip_num += 1
                continue
            
            # 3. Just first element
            for i in range(0, len(search_res)) :
                info = search_res[i]
                if "videoId" not in info :
                    continue
                
                song_id = info["videoId"]
                break

            if song_id not in self.song_ids :
                self.song_ids.append(song_id)
            else :
                skip_num += 1

        logging.info(f"Successfully get song ids. (Skip num: {skip_num})")

    def update_playlist(self) :
        logging.info("Updating playlist...")

        if self.playlist_id == "" :
            playlists = self.ytmusic.get_library_playlists()

            for playlist in playlists :
                if playlist["title"] == self.playlist_name :
                    self.playlist_id = playlist["playlistId"]
                    break

        if self.playlist_id == "" :
            new_playlist_id = self.ytmusic.create_playlist(self.playlist_name, "", video_ids=self.song_ids)
            if type(new_playlist_id) is not str :
                raise Exception(f"Failed to create a new playlist\n{new_playlist_id}")

            self.playlist_id = new_playlist_id

        playlist_info = self.ytmusic.get_playlist(self.playlist_id, 200)

        track_list = playlist_info["tracks"]
        if len(track_list) > 0 :
            self.ytmusic.remove_playlist_items(self.playlist_id, track_list)

        self.ytmusic.add_playlist_items(self.playlist_id, self.song_ids)

        logging.info("Successfully update playlist.")

# ----------------------------------------------

if os.path.isdir("log") == False :
    os.mkdir("log")

logging.basicConfig(handlers=[logging.FileHandler(f"log/logs.log"), logging.StreamHandler()], level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

load_dotenv(verbose=True)

cookie = os.getenv("COOKIE")
playlist_name = os.getenv("PLAYLIST_NAME")
if playlist_name == None :
    playlist_name = "Melon Chart 100"
update_interval = os.getenv("UPDATE_INTERVAL")
if update_interval == None :
    update_interval = 24 * 60 * 60 # 1 day
else :
    update_interval = int(update_interval)

crawler = MelonCrawler()
crawler.init_youtube_music_api(cookie, playlist_name)

fail_num = 0

while True :
    try :
        crawler.get_chart_infos()
        crawler.get_song_ids()
        crawler.update_playlist()

        fail_num = 0

        sleep(update_interval)
    except Exception as e :
        logging.error(f"An exception occurred!\n{traceback.format_exc()}")
        logging.error("Will try again in 10 minutes...")

        fail_num += 1

        if fail_num >= 5 :
            logging.error("Failed to update music chart 5 times continuously. Exit the program.")
            break

        sleep(10 * 60) # 10 min
