FROM python:3.8-alpine

WORKDIR /app/MelonCrawler4YTMusic
COPY main.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY ytmusicapi_modified /usr/local/lib/python3.8/site-packages/ytmusicapi

CMD [ "python3", "main.py" ]
