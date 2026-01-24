import os
import re
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

import yt_dlp
from pyrogram import filters
from pyrogram.types import Message
from ytSearch import VideosSearch

from ArmedMusic import app
from config import BANNED_USERS, YOUTUBE_PROXY
from ArmedMusic import LOGGER

logger = LOGGER(__name__)

def is_youtube_url(url: str) -> bool:
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return bool(re.match(youtube_regex, url))

async def download_thumbnail(url: str, filename: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    os.makedirs("downloads", exist_ok=True)
                    filepath = f"downloads/{filename}"
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    return filepath
    except Exception as e:
        logger.error(f"Thumbnail download failed: {e}")
    return None

@app.on_message(filters.command(["song"]) & ~BANNED_USERS)
async def song_download(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a song name or YouTube URL.\n\nExample: `/song Believer` or `/song https://www.youtube.com/watch?v=7wtfhZwyrcc`")

    query = message.text.split(None, 1)[1].strip()

    # Check if it's a YouTube URL
    if is_youtube_url(query):
        video_url = query
    else:
        # Search for the song
        search = VideosSearch(query, limit=1)
        try:
            results = await search.next()
            if not results["result"]:
                return await message.reply_text("No results found for this song.")
            video = results["result"][0]
            video_url = video["link"]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return await message.reply_text("Failed to search for the song.")

    # Send processing message
    processing_msg = await message.reply_text("🔄 Downloading song... Please wait.")

    try:
        # Get video info
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
        }
        if YOUTUBE_PROXY:
            ydl_opts['proxy'] = YOUTUBE_PROXY

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            info = await loop.run_in_executor(executor, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(video_url, download=False))

        title = info.get('title', 'Unknown')
        uploader = info.get('uploader', 'Unknown Artist')
        duration = info.get('duration', 0)
        thumbnail_url = info.get('thumbnail', '')

        # Clean filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', f"{title} - {uploader}")
        filepath = f"downloads/{safe_title}.mp3"

        # Download audio
        ydl_opts_audio = {
            'format': 'bestaudio[ext=m4a]/bestaudio[acodec=mp4a]/140/bestaudio/best[ext=mp4]/best',
            'outtmpl': f"downloads/{safe_title}",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
        }
        if YOUTUBE_PROXY:
            ydl_opts_audio['proxy'] = YOUTUBE_PROXY

        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, lambda: yt_dlp.YoutubeDL(ydl_opts_audio).download([video_url]))

        if not os.path.exists(filepath):
            await processing_msg.edit_text("❌ Failed to download the song.")
            return

        # Get thumbnail
        thumb_path = None
        if thumbnail_url:
            thumb_filename = f"{safe_title}_thumb.jpg"
            thumb_path = await download_thumbnail(thumbnail_url, thumb_filename)

        # Send the file
        await message.reply_audio(
            audio=filepath,
            caption="@ArmedMusicBot",
            title=title,
            performer=uploader,
            duration=duration,
            thumb=thumb_path,
        )

        # Clean up
        try:
            os.remove(filepath)
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
        except:
            pass

        await processing_msg.delete()

    except Exception as e:
        logger.error(f"Song download failed: {e}")
        await processing_msg.edit_text("❌ Failed to download the song.")
