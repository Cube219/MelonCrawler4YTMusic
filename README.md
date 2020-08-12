# Melon Crawler for Youtube Music


## Getting start

### 1. Installation

#### Using Docker

```bash
$ git clone https://github.com/Cube219/MelonCrawler4YTMusic.git
$ cd MelonCrawler4YTMusic
$ sudo docker build -t cube219/melon-crawler:latest .
```

#### Using Python / pip

```bash
$ git clone https://github.com/Cube219/MelonCrawler4YTMusic.git
$ cd MelonCrawler4YTMusic
$ pip lnstall -r requirements.txt
$ cp -rf ytmusicapi_modified [YOUR_PYTHON_LIB_FOLDER]
```

The last instruction is for supporting Korean language.

### 2. Setting environment variables

| Environment Variable | Default         | Desc                                                         |
| -------------------- | --------------- | ------------------------------------------------------------ |
| COOKIE               | undefined       | A cookie for accessing YouTube Music.</br>You can find this from any POST request header in your YouTube Music web. |
| PLAYLIST_NAME        | Melon Chart 100 | A playlist name to create.                                   |
| UPDATE_INTERVAL      | 86400 *(1 day)* | An interval time to update the song list.                    |

You can use .env*(dotenv)* file to set environment variables.

### 3. Running

#### Using Python

Just execute `main.py`.

ex) `$ python3 main.py`

#### Using Docker

Just run the container you built.

To avoid deleting log data whenever restarting container, mount volumes `/app/MelonCrawler4YTMusic/log` in container.

I recommend to use [docker-compose](https://docs.docker.com/compose/) to run it.

#### Example using docker-compose

```com
version: '3'

services:
  mainserver:
    image: "cube219/melon-crawler:latest"
    container_name: melon-crawler-server
    volumes:
      - ./logs:/app/MelonCrawler4YTMusic/log
    environment:
      COOKIE: [PASTE_YOUR_COOKIE]
      PLAYLIST_NAME: Melon Chart 100
      UPDATE_INTERVAL: 259200 # 3 days
```

In bash:

```bash
$ docker-compose -f compose.yml up -d
```

## License

MIT License

