import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", "27638882"))
API_HASH = getenv("API_HASH", "f745cdd5ddb46cf841d6990048f52935")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "7598831470:AAGWu2nDC89r3EyZCpNoC1KW9r-9ylNkcT8")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb://mongo:bBlGbsiXVMUFsiXTYOEXuGAnEHfCbNyn@mongodb.railway.internal:27017/armedmusic?authSource=admin")

# Vars For API End Pont.
YTPROXY_URL = getenv("YTPROXY_URL", None) ## xBit Music Endpoint. Set to None to disable AI features
YOUTUBE_PROXY = getenv("YOUTUBE_PROXY", None) ## Proxy for YouTube downloads, e.g. http://proxy_ip:port
YT_API_KEY = getenv("YT_API_KEY" , "AIzaSyAyFW-9snpxGwFa5cu-p81jjE8Fg1h_6rk" ) ## Your API key like: xbit_10000000xx0233 Get from  https://t.me/tgmusic_apibot

## Other vaes
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", "-1003142281080"))

# Get this value from @FallenxBot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", "7976004718"))

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))
ASSISTANT_LEAVE_TIME = int(getenv("ASSISTANT_LEAVE_TIME",  5400))


# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 204857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 2073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes

PRIVATE_BOT_MODE_MEM = int(getenv("PRIVATE_BOT_MODE_MEM", 1))


CACHE_DURATION = int(getenv("CACHE_DURATION" , "86400"))  #60*60*24
CACHE_SLEEP = int(getenv("CACHE_SLEEP" , "3600"))   #60*60


# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = getenv("STRING_SESSION", "AgGlvGIAOTbpAfHjFV0qNLBBliSZuE5EPB0sq8AyRKZRjEa6Cn1O0VtDMj2qC0Ugi35lmM1U45sUn9dEsN9b6n0EuHoNUAllXmHHzrd_hUiZ1MPWahbZuzJMA1qdeGgZkb4bFaCrTdlglNAzZfUT4V-uBW11QK9svP7fDumkTzTn0Di6PM_GeprgZHM2v2xEHdQ9vItN3wCviLh9jS1U_kXqnCYxrPoeK_QErlLB5iRM5Q_jpjUKg6eAO-h-mA5tLQ2Kp51dC7_wRKRdfcKMrJElrAdOELd4u0My3hwZOWxTYHA7CWuv9UIp7oz6q83YLxA8w3KqgM5gltss1LYRb4TxzqEnkgAAAAHya_vDAA")
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
file_cache: dict[str, float] = {}

START_IMG_URL = [
    "https://image2url.com/r2/default/images/1769269338835-d5ce1f25-55d6-45fc-b9ad-c04ae647827e.jpg",
    "https://image2url.com/r2/default/images/1769269355185-77c5d002-ce9a-47ce-aba1-d1b033e60472.jpg",
    "https://image2url.com/r2/default/images/1769269377267-3084111d-b3fe-4e5e-be58-418b26f25c4d.jpg",
    "https://image2url.com/r2/default/images/1769269399286-a06b9ba6-3f29-47a5-9a32-9f0c3e0a905c.jpg",
    "https://image2url.com/r2/default/images/1769269443873-5d739aec-a837-45be-aa83-409ae4259c5e.jpg",
    "https://image2url.com/r2/default/images/1769269553883-e7fa9182-2d84-4961-a2bf-4ae63e810b1e.jpg"
]
    
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://image2url.com/r2/default/images/1768792821746-ad62ab76-1fdc-45d7-8b5e-a5343577d6bb.jpg"
)
PLAYLIST_IMG_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
TELEGRAM_AUDIO_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
TELEGRAM_VIDEO_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
STREAM_IMG_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
SOUNCLOUD_IMG_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
YOUTUBE_IMG_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://image2url.com/r2/default/images/1768793789039-2d4017a9-b0a3-43ec-837c-82855012c3fb.jpg"

DEFAULT_THUMB = START_IMG_URL[0]  # Default thumbnail for streams



def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:360"))
