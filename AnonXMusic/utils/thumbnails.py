import os
import aiohttp
import traceback
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from yt_dlp import YoutubeDL
from pathlib import Path
from io import BytesIO
import unicodedata
import shutil

from AnonXMusic import app
from config import YOUTUBE_IMG_URL


ASSETS_DIR = Path("fonts")

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

W, H = 1320, 760
BG_BLUR = 22
ICON_SIZE = 120
CIRCLE_SIZE = 560

WHITE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 100)
TEXT_SHADOW = (0, 0, 0, 130)
STROKE_COLOR = (0, 0, 0, 255)

BOT_AVATAR_CACHE = None


async def _load_bot_avatar():
    global BOT_AVATAR_CACHE
    if BOT_AVATAR_CACHE is not None:
        return BOT_AVATAR_CACHE
    try:
        photos = [p async for p in app.get_chat_photos("me", limit=1)]
        if photos:
            file = await app.download_media(photos[0].file_id, in_memory=True)
            data = file.getvalue()
            img = Image.open(BytesIO(data)).convert("RGBA")
            img = img.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
            mask = Image.new("L", (ICON_SIZE, ICON_SIZE), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, ICON_SIZE, ICON_SIZE), fill=255)
            img.putalpha(mask)
            BOT_AVATAR_CACHE = img
            return img
    except Exception as e:
        print(f"[Avatar Error] {e}")
    return None


def resize_fit(img, w, h):
    r = min(w / img.width, h / img.height)
    return img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)


def dominant_color(img):
    img = img.resize((60, 60))
    pixels = list(img.getdata())
    colors = {}
    for p in pixels:
        if len(p) == 3:
            p = (*p, 255)
        if p[3] < 150:
            continue
        colors[p] = colors.get(p, 0) + 1
    return max(colors, key=colors.get)[:3] if colors else (40, 40, 80)


def gradient_bg(draw, w, h, color):
    r, g, b = color
    for y in range(h):
        factor = y / h
        col = (int(r * (1 - 0.25 * factor)), int(g * (1 - 0.25 * factor)), int(b * (1 - 0.25 * factor)))
        draw.line([(0, y), (w, y)], fill=(*col, 255))


def format_views_count(views: int) -> str:
    if views >= 1000000000:
        return f"{views / 1000000000:.1f}B"
    elif views >= 1000000:
        return f"{views / 1000000:.1f}M"
    elif views >= 1000:
        return f"{views / 1000:.1f}K"
    else:
        return str(views)


async def get_thumb(videoid: str, user_id: str):
    cache_file = CACHE_DIR / f"{videoid}_{user_id}.png"
    if cache_file.exists():
        return str(cache_file)

    try:
        try:
            with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(f"https://youtu.be/{videoid}", download=False)
        except Exception:
            return YOUTUBE_IMG_URL
        if not info:
            return YOUTUBE_IMG_URL

        title = info.get("title", "Unknown Song")
        title = unicodedata.normalize('NFC', title)
        thumb_url = info.get("thumbnail", "")
        channel_name = info.get('uploader', 'Unknown')
        view_count = info.get('view_count', 0)
        duration = info.get('duration_string', '0:00')

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12)) as s:
            async with s.get(thumb_url) as r:
                if r.status != 200:
                    return YOUTUBE_IMG_URL
                img_data = await r.read()

        tmp = CACHE_DIR / f"t_{videoid}.img"
        tmp.write_bytes(img_data)
        art = Image.open(tmp).convert("RGBA")

        dom = dominant_color(art)
        bg_art = resize_fit(art, W, H).filter(ImageFilter.GaussianBlur(BG_BLUR))
        bg_art = ImageEnhance.Brightness(bg_art).enhance(0.88)
        bg_art = ImageEnhance.Contrast(bg_art).enhance(1.05)

        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        gradient_bg(draw, W, H, dom)
        canvas.paste(bg_art.convert("RGB"), (0, 0), bg_art.split()[3] if bg_art.mode == "RGBA" else None)

        x, y = 80, (H - CIRCLE_SIZE) // 2

        r = max(CIRCLE_SIZE / art.width, CIRCLE_SIZE / art.height)
        circle_w = int(art.width * r)
        circle_h = int(art.height * r)
        circle = art.resize((circle_w, circle_h), Image.LANCZOS)

        mask = Image.new("L", (CIRCLE_SIZE, CIRCLE_SIZE), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0, 0, CIRCLE_SIZE, CIRCLE_SIZE), fill=255)

        circle.putalpha(mask.resize((circle_w, circle_h), Image.LANCZOS))

        circle_canvas = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE), (0,0,0,0))
        circle_canvas.paste(circle, ((CIRCLE_SIZE - circle_w) // 2, (CIRCLE_SIZE - circle_h) // 2))
        circle_canvas.putalpha(mask)

        shadow = Image.new("RGBA", (CIRCLE_SIZE + 100, CIRCLE_SIZE + 100), (0,0,0,0))
        sdraw = ImageDraw.Draw(shadow)
        sdraw.ellipse((50, 50, CIRCLE_SIZE + 50, CIRCLE_SIZE + 50), fill=SHADOW)
        shadow = shadow.filter(ImageFilter.GaussianBlur(35))
        canvas.paste(shadow, (x - 50, y - 50), shadow)
        canvas.paste(circle_canvas, (x, y), circle_canvas)

        avatar = await _load_bot_avatar()
        if avatar:
            ax, ay = 28, 16
            canvas.paste(avatar, (ax, ay), avatar)

        info_x = x + CIRCLE_SIZE + 80
        max_w = W - info_x - 70

        # simple split for title to fit in box
        def split_title(t, max_w, font):
            words = t.split()
            lines = []
            cur = []
            cur_w = 0
            for w in words:
                w_w = font.getlength(w + ' ')
                if cur_w + w_w > max_w and cur:
                    lines.append(' '.join(cur))
                    cur = [w]
                    cur_w = w_w
                else:
                    cur.append(w)
                    cur_w += w_w
                if len(lines) >= 4:
                    break
            if cur and len(lines) < 4:
                lines.append(' '.join(cur))
            return lines

        title_font = ImageFont.truetype(str(ASSETS_DIR / "GoNotoCurrent-Bold.ttf"), 52) if (ASSETS_DIR / "GoNotoCurrent-Bold.ttf").exists() else ImageFont.load_default()
        title_lines = split_title(title, max_w, title_font)

        line_height = 58
        total_h = len(title_lines) * line_height
        t_y = y + (CIRCLE_SIZE - total_h) // 2 + 8

        for i, line in enumerate(title_lines):
            line_w = title_font.getlength(line)
            tx = info_x + (max_w - line_w) // 2
            # shadow
            draw.text((tx-3, t_y + i * line_height-3), line, font=title_font, fill=STROKE_COLOR)
            draw.text((tx+2, t_y + i * line_height+2), line, font=title_font, fill=TEXT_SHADOW)
            draw.text((tx, t_y + i * line_height), line, font=title_font, fill=WHITE)

        try:
            views = int(view_count or 0)
        except:
            views = 0
        views_text = f"{format_views_count(views)} views"
        views_font = ImageFont.truetype(str(ASSETS_DIR / "GoNotoCurrent-Regular.ttf"), 32) if (ASSETS_DIR / "GoNotoCurrent-Regular.ttf").exists() else ImageFont.load_default()
        v_w = views_font.getlength(views_text)
        v_x = info_x + (max_w - v_w) // 2
        v_y = t_y + total_h + 8
        draw.text((v_x-2, v_y-2), views_text, font=views_font, fill=STROKE_COLOR)
        draw.text((v_x+1, v_y+1), views_text, font=views_font, fill=TEXT_SHADOW)
        draw.text((v_x, v_y), views_text, font=views_font, fill=(230,230,230,230))

        water = "Powered by Armed Music"
        water_font = ImageFont.truetype(str(ASSETS_DIR / "GoNotoCurrent-Italic.ttf"), 28) if (ASSETS_DIR / "GoNotoCurrent-Italic.ttf").exists() else ImageFont.load_default()
        w_w = water_font.getlength(water)
        wx = W - w_w - 30
        wy = H - water_font.getbbox(water)[3] - 5
        draw.text((wx-2, wy-2), water, font=water_font, fill=STROKE_COLOR)
        draw.text((wx+1, wy+1), water, font=water_font, fill=TEXT_SHADOW)
        draw.text((wx, wy), water, font=water_font, fill=(210,210,210,190))

        canvas = canvas.convert("RGB")
        canvas.save(cache_file, "PNG")

        try:
            os.remove(tmp)
        except:
            pass

        return str(cache_file)

    except Exception as e:
        print(f"[Thumb Error] {e}")
        traceback.print_exc()
        return YOUTUBE_IMG_URL
