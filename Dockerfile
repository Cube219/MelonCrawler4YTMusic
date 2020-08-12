FROM python:alpine

WORKDIR /app/MelonCrawler4YTMusic
COPY main.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD [ "python3", "main.py" ]
