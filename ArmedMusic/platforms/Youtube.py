import asyncio
import glob
import json
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Union
import string
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ytSearch import VideosSearch, CustomSearch
import base64
from ArmedMusic import LOGGER
from ArmedMusic.utils.database import is_on_off
from ArmedMusic.utils.formatters import time_to_seconds
ITALIC_TO_REGULAR = str.maketrans({119860: 'A', 119861: 'B', 119862: 'C', 119863: 'D', 119864: 'E', 119865: 'F', 119866: 'G', 119867: 'H', 119868: 'I', 119869: 'J', 119870: 'K', 119871: 'L', 119872: 'M', 119873: 'N', 119874: 'O', 119875: 'P', 119876: 'Q', 119877: 'R', 119878: 'S', 119879: 'T', 119880: 'U', 119881: 'V', 119882: 'W', 119883: 'X', 119884: 'Y', 119885: 'Z', 119886: 'a', 119887: 'b', 119888: 'c', 119889: 'd', 119890: 'e', 119891: 'f', 119892: 'g', 119893: 'h', 119894: 'i', 119895: 'j', 119896: 'k', 119897: 'l', 119898: 'm', 119899: 'n', 119900: 'o', 119901: 'p', 119902: 'q', 119903: 'r', 119904: 's', 119905: 't', 119906: 'u', 119907: 'v', 119908: 'w', 119909: 'x', 119910: 'y', 119911: 'z', 120328: 'A', 120329: 'B', 120330: 'C', 120331: 'D', 120332: 'E', 120333: 'F', 120334: 'G', 120335: 'H', 120336: 'I', 120337: 'J', 120338: 'K', 120339: 'L', 120340: 'M', 120341: 'N', 120342: 'O', 120343: 'P', 120344: 'Q', 120345: 'R', 120346: 'S', 120347: 'T', 120348: 'U', 120349: 'V', 120350: 'W', 120351: 'X', 120352: 'Y', 120353: 'Z', 120354: 'a', 120355: 'b', 120356: 'c', 120357: 'd', 120358: 'e', 120359: 'f', 120360: 'g', 120361: 'h', 120362: 'i', 120363: 'j', 120364: 'k', 120365: 'l', 120366: 'm', 120367: 'n', 120368: 'o', 120369: 'p', 120370: 'q', 120371: 'r', 120372: 's', 120373: 't', 120374: 'u', 120375: 'v', 120376: 'w', 120377: 'x', 120378: 'y', 120379: 'z', 120380: 'A', 120381: 'B', 120382: 'C', 120383: 'D', 120384: 'E', 120385: 'F', 120386: 'G', 120387: 'H', 120388: 'I', 120389: 'J', 120390: 'K', 120391: 'L', 120392: 'M', 120393: 'N', 120394: 'O', 120395: 'P', 120396: 'Q', 120397: 'R', 120398: 'S', 120399: 'T', 120400: 'U', 120401: 'V', 120402: 'W', 120403: 'X', 120404: 'Y', 120405: 'Z', 120406: 'a', 120407: 'b', 120408: 'c', 120409: 'd', 120410: 'e', 120411: 'f', 120412: 'g', 120413: 'h', 120414: 'i', 120415: 'j', 120416: 'k', 120417: 'l', 120418: 'm', 120419: 'n', 120420: 'o', 120421: 'p', 120422: 'q', 120423: 'r', 120424: 's', 120425: 't', 120426: 'u', 120427: 'v', 120428: 'w', 120429: 'x', 120430: 'y', 120431: 'z'})

def convert_italic_unicode(text):
    return text.translate(ITALIC_TO_REGULAR)
from config import YT_API_KEY, YTPROXY_URL as YTPROXY, YOUTUBE_PROXY
logger = LOGGER(__name__)

def cookie_txt_file():
    try:
        folder_path = f'{os.getcwd()}/cookies'
        filename = f'{os.getcwd()}/cookies/logs.csv'
        txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
        if not txt_files:
            raise FileNotFoundError('No .txt files found in the specified folder.')
        cookie_txt_file = random.choice(txt_files)
        with open(filename, 'a') as file:
            file.write(f'Choosen File : {cookie_txt_file}\n')
        return f"cookies/{str(cookie_txt_file).split('/')[-1]}"
    except:
        return None

async def check_file_size(link):

    async def get_format_info(link):
        cmd = ['yt-dlp', '--cookies', cookie_txt_file(), '-J', link]
        if YOUTUBE_PROXY:
            cmd.extend(['--proxy', YOUTUBE_PROXY])
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size
    info = await get_format_info(link)
    if info is None:
        return None
    formats = info.get('formats', [])
    if not formats:
        print('No formats found.')
        return None
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, errorz = await proc.communicate()
    if errorz:
        if 'unavailable videos are hidden' in errorz.decode('utf-8').lower():
            return out.decode('utf-8')
        else:
            return errorz.decode('utf-8')
    return out.decode('utf-8')

class YouTubeAPI:

    def __init__(self):
        self.base = 'https://www.youtube.com/watch?v='
        self.regex = '(?:youtube\\.com|youtu\\.be)'
        self.status = 'https://www.youtube.com/oembed?url='
        self.listbase = 'https://youtube.com/playlist?list='
        self.reg = re.compile('\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])')
        self.dl_stats = {'total_requests': 0, 'okflix_downloads': 0, 'cookie_downloads': 0, 'existing_files': 0}

    async def exists(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ''
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = (entity.offset, entity.length)
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset:offset + length]

    async def details(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())['result']:
            title = result['title']
            title = convert_italic_unicode(title)
            duration_min = result['duration']
            thumbnail = result['thumbnails'][0]['url'].split('?')[0]
            vidid = result['id']
            if str(duration_min) == 'None':
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return (title, duration_min, duration_sec, thumbnail, vidid)

    async def title(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())['result']:
            title = result['title']
            title = convert_italic_unicode(title)
        return title

    async def duration(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())['result']:
            duration = result['duration']
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())['result']:
            thumbnail = result['thumbnails'][0]['url'].split('?')[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        proc = await asyncio.create_subprocess_exec('yt-dlp', '--cookies', cookie_txt_file(), '-g', '-f', 'best[height<=?720][width<=?1280]', f'{link}', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stdout:
            return (1, stdout.decode().split('\n')[0])
        else:
            return (0, stderr.decode())

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str]=None):
        if videoid:
            link = self.listbase + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        playlist = await shell_cmd(f'yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} --playlist-end {limit} --skip-download {link}')
        try:
            result = playlist.split('\n')
            for key in result:
                if key == '':
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())['result']:
            title = result['title']
            duration_min = result['duration']
            vidid = result['id']
            yturl = result['link']
            thumbnail = result['thumbnails'][0]['url'].split('?')[0]
        track_details = {'title': title, 'link': yturl, 'vidid': vidid, 'duration_min': duration_min, 'thumb': thumbnail}
        return (track_details, vidid)

    async def formats(self, link: str, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        ytdl_opts = {'quiet': True, 'cookiefile': cookie_txt_file(), 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-us,en;q=0.5', 'Sec-Fetch-Mode': 'navigate'}}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r['formats']:
                try:
                    str(format['format'])
                except:
                    continue
                if not 'dash' in str(format['format']).lower():
                    try:
                        format['format']
                        format['filesize']
                        format['format_id']
                        format['ext']
                        format['format_note']
                    except:
                        continue
                    formats_available.append({'format': format['format'], 'filesize': format['filesize'], 'format_id': format['format_id'], 'ext': format['ext'], 'format_note': format['format_note'], 'yturl': link})
        return (formats_available, link)

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str]=None):
        if videoid:
            link = self.base + link
        if '&' in link:
            link = link.split('&')[0]
        if '?si=' in link:
            link = link.split('?si=')[0]
        elif '&si=' in link:
            link = link.split('&si=')[0]
        try:
            results = []
            search = VideosSearch(link, limit=10)
            search_results = (await search.next()).get('result', [])
            for result in search_results:
                duration_str = result.get('duration', '0:00')
                try:
                    parts = duration_str.split(':')
                    duration_secs = 0
                    if len(parts) == 3:
                        duration_secs = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    elif len(parts) == 2:
                        duration_secs = int(parts[0]) * 60 + int(parts[1])
                    if duration_secs <= 3600:
                        results.append(result)
                except (ValueError, IndexError):
                    continue
            if not results or query_type >= len(results):
                raise ValueError('No suitable videos found within duration limit')
            selected = results[query_type]
            return (selected['title'], selected['duration'], selected['thumbnails'][0]['url'].split('?')[0], selected['id'])
        except Exception as e:
            LOGGER(__name__).error(f'Error in slider: {str(e)}')
            raise ValueError('Failed to fetch video details')

    async def download(self, link: str, mystic, video: Union[bool, str]=None, videoid: Union[bool, str]=None, songaudio: Union[bool, str]=None, songvideo: Union[bool, str]=None, format_id: Union[bool, str]=None, title: Union[bool, str]=None) -> str:
        if videoid:
            vid_id = link
            link = self.base + link
        loop = asyncio.get_running_loop()

        def create_session():
            session = requests.Session()
            retries = Retry(total=10, backoff_factor=0.1)
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))
            return session

        async def download_with_requests(url, filepath, headers=None):
            try:
                session = create_session()
                response = session.get(url, headers=headers, stream=True, timeout=60, allow_redirects=True)
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 1024 * 1024
                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                return filepath
            except Exception as e:
                logger.error(f'Requests download failed: {str(e)}')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
            finally:
                session.close()

        async def audio_dl(vid_id):
            try:
                filepath = os.path.join('downloads', f'{vid_id}.mp3')
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                if os.path.exists(filepath):
                    return filepath
                try:
                    info_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': False, 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-us,en;q=0.5', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1'}, 'extractor_args': {'youtube': {'player_client': ['ios', 'android', 'web'], 'player_skip': ['js', 'webpage'], 'innertube_client': 'ios'}}}
                    with yt_dlp.YoutubeDL(info_opts) as ydl:
                        info = ydl.extract_info(f'https://www.youtube.com/watch?v={vid_id}', download=False)
                        formats = info.get('formats', [])
                        audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                        logger.info(f'Available pure audio formats for {vid_id}: {len(audio_formats)} formats')
                        if audio_formats:
                            logger.info(f'First pure audio format: {audio_formats[0]}')
                        else:
                            audio_formats = [f for f in formats if f.get('acodec') != 'none']
                            logger.info(f'Available audio+video formats for {vid_id}: {len(audio_formats)} formats')
                            if audio_formats:
                                logger.info(f'First audio+video format: {audio_formats[0]}')
                except Exception as info_e:
                    logger.error(f'Failed to get info for {vid_id}: {str(info_e)}')
                cookie_file = cookie_txt_file()
                ydl_opts_list = [
                    {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 5,
                        'fragment_retries': 5,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1'
                        },
                        'extractor_args': {'youtube': {'player_client': ['web'], 'player_skip': ['js'], 'innertube_client': 'web'}}
                    },
                    {
                        'format': 'bestaudio[ext=m4a]/bestaudio[acodec=mp4a]/140/bestaudio/best[ext=mp4]/best',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 5,
                        'fragment_retries': 5,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1'
                        },
                        'extractor_args': {'youtube': {'player_client': ['ios'], 'player_skip': ['js'], 'innertube_client': 'ios'}}
                    },
                    {
                        'format': 'bestaudio',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 3,
                        'fragment_retries': 3,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1',
                            'DNT': '1',
                            'Sec-Fetch-User': '?1',
                            'Sec-Ch-Ua-Mobile': '?1',
                            'Sec-Ch-Ua-Platform': '"Android"'
                        },
                        'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['js'], 'innertube_client': 'android'}}
                    },
                    {
                        'format': '140/171/251/bestaudio[ext=m4a]/bestaudio',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 3,
                        'fragment_retries': 3,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/133.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1'
                        }
                    },
                    {
                        'format': 'bestaudio',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 3,
                        'fragment_retries': 3,
                        'skip_unavailable_fragments': True
                    },
                    {
                        'format': 'bestaudio[ext=m4a]/bestaudio[acodec=mp4a]/140/bestaudio/best[ext=mp4]/best',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 5,
                        'fragment_retries': 5,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'com.google.android.youtube/19.09.36 (Linux; U; Android 11; SM-G973F) gzip',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5'
                        },
                        'extractor_args': {'youtube': {'player_client': ['android_music'], 'player_skip': ['js'], 'innertube_client': 'android_music'}}
                    },
                    {
                        'format': 'bestaudio[ext=m4a]/bestaudio[acodec=mp4a]/140/bestaudio/best[ext=mp4]/best',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 5,
                        'fragment_retries': 5,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1'
                        },
                        'extractor_args': {'youtube': {'player_client': ['web_embedded'], 'player_skip': ['js'], 'innertube_client': 'web_embedded'}}
                    },
                    {
                        'format': 'bestaudio[ext=m4a]/bestaudio[acodec=mp4a]/140/bestaudio/best[ext=mp4]/best',
                        'outtmpl': os.path.join('downloads', f'{vid_id}'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 5,
                        'fragment_retries': 5,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1'
                        },
                        'extractor_args': {'youtube': {'player_client': ['web_safari'], 'player_skip': ['js'], 'innertube_client': 'web_safari'}}
                    }
                ]
                    try:
                        logger.info(f'Trying download configuration {i + 1} for {vid_id}')
                        if cookie_file and 'cookiefile' not in ydl_opts:
                            ydl_opts['cookiefile'] = cookie_file
                        if YOUTUBE_PROXY and 'proxy' not in ydl_opts:
                            ydl_opts['proxy'] = YOUTUBE_PROXY
                        loop = asyncio.get_running_loop()
                        with ThreadPoolExecutor() as executor:
                            result = await loop.run_in_executor(executor, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f'https://www.youtube.com/watch?v={vid_id}']))
                            logger.info(f'yt_dlp download result for {vid_id} (config {i + 1}): {result}')
                        logger.info(f'Checking for file at {filepath}')
                        if os.path.exists(filepath):
                            logger.info(f'File found: {filepath}')
                            return filepath
                        else:
                            logger.warning(f'Download config {i + 1} completed but file not found at {filepath}')
                    except Exception as e:
                        error_msg = str(e)
                        logger.warning(f'Download config {i + 1} failed for {vid_id}: {error_msg}')
                        continue
                logger.error(f'All download configurations failed for {vid_id}')
                return None
            except Exception as e:
                logger.error(f'yt_dlp audio download failed for {vid_id}: {str(e)}')
                return None

        async def video_dl(vid_id):
            try:
                filepath = os.path.join('downloads', f'{vid_id}.mp4')
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                if os.path.exists(filepath):
                    return filepath
                ydl_opts = {'format': 'best[height<=720]/best', 'outtmpl': filepath, 'quiet': True, 'no_warnings': True, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-us,en;q=0.5', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1'}, 'extractor_args': {'youtube': {'player_client': ['web'], 'player_skip': ['js'], 'innertube_client': 'web'}}}}
                if YOUTUBE_PROXY:
                    ydl_opts['proxy'] = YOUTUBE_PROXY
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f'https://www.youtube.com/watch?v={vid_id}']))
                if os.path.exists(filepath):
                    return filepath
                else:
                    logger.error('Video download failed, file not found')
                    return None
            except Exception as e:
                logger.error(f'yt_dlp video download failed for {vid_id}: {str(e)}')
                return None

        async def song_video_dl():
            try:
                filepath = f'downloads/{title}.mp4'
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                if os.path.exists(filepath):
                    return filepath
                ydl_opts = {'format': 'best[height<=720]/best', 'outtmpl': filepath, 'quiet': True, 'no_warnings': True, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-us,en;q=0.5', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1'}, 'extractor_args': {'youtube': {'player_client': ['web'], 'player_skip': ['js'], 'innertube_client': 'web'}}}
                if YOUTUBE_PROXY:
                    ydl_opts['proxy'] = YOUTUBE_PROXY
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f'https://www.youtube.com/watch?v={vid_id}']))
                if os.path.exists(filepath):
                    return filepath
                else:
                    logger.error('Song video download failed, file not found')
                    return None
            except Exception as e:
                logger.error(f'yt_dlp song video download failed for {vid_id}: {str(e)}')
                return None

        async def song_audio_dl():
            try:
                filepath = f'downloads/{title}.mp3'
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                if os.path.exists(filepath):
                    return filepath
                cookie_file = cookie_txt_file()
                ydl_opts_list = [
                    {
                        'format': 'bestaudio/best',
                        'outtmpl': f'downloads/{title}',
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 5,
                        'fragment_retries': 5,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1'
                        },
                        'extractor_args': {'youtube': {'player_client': ['web'], 'player_skip': ['js'], 'innertube_client': 'web'}}
                    },
                    {
                        'format': 'bestaudio[ext=m4a]/bestaudio[acodec=mp4a]/140/bestaudio/best[ext=mp4]/best',
                        'outtmpl': f'downloads/{title}',
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 5,
                        'fragment_retries': 5,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1'
                        },
                        'extractor_args': {'youtube': {'player_client': ['ios'], 'player_skip': ['js'], 'innertube_client': 'ios'}}
                    },
                    {
                        'format': 'bestaudio',
                        'outtmpl': f'downloads/{title}',
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}],
                        'quiet': True,
                        'no_warnings': True,
                        'retries': 3,
                        'fragment_retries': 3,
                        'skip_unavailable_fragments': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1',
                            'DNT': '1',
                            'Sec-Fetch-User': '?1',
                            'Sec-Ch-Ua-Mobile': '?1',
                            'Sec-Ch-Ua-Platform': '"Android"'
                        },
                        'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['js'], 'innertube_client': 'android'}}
                    }
                ]
                for i, ydl_opts in enumerate(ydl_opts_list):
                    try:
                        logger.info(f'Trying song audio download configuration {i + 1} for {vid_id}')
                        if cookie_file and 'cookiefile' not in ydl_opts:
                            ydl_opts['cookiefile'] = cookie_file
                        if YOUTUBE_PROXY and 'proxy' not in ydl_opts:
                            ydl_opts['proxy'] = YOUTUBE_PROXY
                        loop = asyncio.get_running_loop()
                        with ThreadPoolExecutor() as executor:
                            await loop.run_in_executor(executor, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f'https://www.youtube.com/watch?v={vid_id}']))
                        if os.path.exists(filepath):
                            return filepath
                        else:
                            logger.warning(f'Song audio download config {i + 1} completed but file not found at {filepath}')
                    except Exception as e:
                        error_msg = str(e)
                        logger.warning(f'Song audio download config {i + 1} failed for {vid_id}: {error_msg}')
                        if 'page needs to be reloaded' not in error_msg and 'Requested format is not available' not in error_msg:
                            break
                        continue
                logger.error(f'All song audio download configurations failed for {vid_id}')
                return None
            except Exception as e:
                logger.error(f'yt_dlp song audio download failed for {vid_id}: {str(e)}')
                return None
        if songvideo:
            fpath = await song_video_dl()
            return fpath
        elif songaudio:
            fpath = await song_audio_dl()
            return fpath
        elif video:
            direct = True
            downloaded_file = await video_dl(vid_id)
        else:
            direct = True
            downloaded_file = await audio_dl(vid_id)
        return (downloaded_file, direct)
