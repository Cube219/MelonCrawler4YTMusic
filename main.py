import requests
from bs4 import BeautifulSoup

melonPageReq = requests.get("https://www.melon.com/chart/index.htm", headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"})
if melonPageReq.ok == False:
    print(f"Failed to get a Melon chart page. (Status Code: {melonPageReq.status_code})")

soup = BeautifulSoup(melonPageReq.content, "html.parser")

songInfos = soup.select(".wrap_song_info")

songs = []
for i in range(0, len(songInfos), 2) :
    tmp = songInfos[i].find_all("div")

    title = tmp[0].span.a.text
    artist = tmp[1].span.a.text
    album = songInfos[i + 1].div.a.text

    songs.append((title, album))

    print(f"{title} / {artist} / {album}")
