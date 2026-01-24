import os
import aiohttp
import traceback
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageOps
from yt_dlp import YoutubeDL
from pathlib import Path
from io import BytesIO
import unicodedata
import logging
import shutil
import re


import config


ASSETS_DIR = Path("AnonXMusic/fonts")

ARM_FONTS = [
    "NotoSansArmenian-Regular.ttf",
    "GHEA_Grapalat.ttf",
    "GHEA_Mariam.ttf",
    "Sylfaen.ttf",
    "DejaVuSans.ttf",
    "ArianAMU-Regular.ttf",
    "Webstart.ttf",
    "FreeSans.ttf",
    "Tarumian-Ando-Regular.ttf",
    "LinotypeMaralArmenian.ttf",
    "NotoSansArmenian-Bold.ttf",
    "DejaVuSans-Bold.ttf",
    "ArianAMU-Bold.ttf",
    "Webstart-Bold.ttf",
    "FreeSans-Bold.ttf",
    "Tarumian-Ando-Bold.ttf",
    "NotoSansArmenian-Italic.ttf",
    "NotoSansArmenianMono-Regular.ttf",
    "DejaVuSansMono-Regular.ttf",
    "DejaVuSansMono-Bold.ttf",
]

GLOBAL_FONTS = [
    "NotoSans-Regular.ttf", "NotoSans-Bold.ttf", "NotoSans-Italic.ttf", "NotoSansMono-Regular.ttf", "NotoSansMono-Bold.ttf",
    "NotoSansSymbols-Regular.ttf", "NotoSansSymbols-Bold.ttf", "NotoSansSymbols2-Regular.ttf", "NotoSansSymbols2-Bold.ttf",
    "NotoSansMath-Regular.ttf", "NotoMusic-Regular.ttf",
    "NotoSansAdlam-Regular.ttf", "NotoSansAdlam-Bold.ttf", "NotoSansAdlamUnjoined-Regular.ttf", "NotoSansAdlamUnjoined-Bold.ttf",
    "NotoSansAnatolianHieroglyphs-Regular.ttf",
    "NotoSansArabic-Regular.ttf", "NotoSansArabic-Bold.ttf", "NotoSansArabicUI-Regular.ttf", "NotoSansArabicUI-Bold.ttf",
    "NotoKufiArabic-Regular.ttf", "NotoKufiArabic-Bold.ttf", "NotoNaskhArabic-Regular.ttf", "NotoNaskhArabic-Bold.ttf", "NotoNaskhArabicUI-Regular.ttf", "NotoNaskhArabicUI-Bold.ttf",
    "NotoNastaliqUrdu-Regular.ttf", "NotoNastaliqUrdu-Bold.ttf",
    "NotoSansArmenian-Regular.ttf", "NotoSansArmenian-Bold.ttf",
    "NotoSansAvestan-Regular.ttf",
    "NotoSansBalinese-Regular.ttf", "NotoSansBalinese-Bold.ttf",
    "NotoSansBamum-Regular.ttf", "NotoSansBamum-Bold.ttf",
    "NotoSansBassaVah-Regular.ttf", "NotoSansBassaVah-Bold.ttf",
    "NotoSansBatak-Regular.ttf",
    "NotoSansBengali-Regular.ttf", "NotoSansBengali-Bold.ttf", "NotoSansBengaliUI-Regular.ttf", "NotoSansBengaliUI-Bold.ttf",
    "NotoSansBhaiksuki-Regular.ttf",
    "NotoSansBrahmi-Regular.ttf",
    "NotoSansBuginese-Regular.ttf",
    "NotoSansBuhid-Regular.ttf",
    "NotoSansCanadianAboriginal-Regular.ttf", "NotoSansCanadianAboriginal-Bold.ttf",
    "NotoSansCarian-Regular.ttf",
    "NotoSansCaucasianAlbanian-Regular.ttf",
    "NotoSansChakma-Regular.ttf",
    "NotoSansCham-Regular.ttf", "NotoSansCham-Bold.ttf",
    "NotoSansCherokee-Regular.ttf", "NotoSansCherokee-Bold.ttf",
    "NotoSansChorasmian-Regular.ttf",
    "NotoSansCoptic-Regular.ttf",
    "NotoSansCuneiform-Regular.ttf",
    "NotoSansCypriot-Regular.ttf",
    "NotoSansCyproMinoan-Regular.ttf",
    "NotoSansDeseret-Regular.ttf",
    "NotoSansDevanagari-Regular.ttf", "NotoSansDevanagari-Bold.ttf", "NotoSansDevanagariUI-Regular.ttf", "NotoSansDevanagariUI-Bold.ttf",
    "NotoSansDuployan-Regular.ttf", "NotoSansDuployan-Bold.ttf",
    "NotoSansEgyptianHieroglyphs-Regular.ttf",
    "NotoSansElbasan-Regular.ttf",
    "NotoSansElymaic-Regular.ttf",
    "NotoSansEthiopic-Regular.ttf", "NotoSansEthiopic-Bold.ttf",
    "NotoSansGeorgian-Regular.ttf", "NotoSansGeorgian-Bold.ttf",
    "NotoSansGlagolitic-Regular.ttf",
    "NotoSansGothic-Regular.ttf",
    "NotoSansGrantha-Regular.ttf",
    "NotoSansGujarati-Regular.ttf", "NotoSansGujarati-Bold.ttf", "NotoSansGujaratiUI-Regular.ttf", "NotoSansGujaratiUI-Bold.ttf",
    "NotoSansGunjalaGondi-Regular.ttf", "NotoSansGunjalaGondi-Bold.ttf",
    "NotoSansGurmukhi-Regular.ttf", "NotoSansGurmukhi-Bold.ttf", "NotoSansGurmukhiUI-Regular.ttf", "NotoSansGurmukhiUI-Bold.ttf",
    "NotoSansHanifiRohingya-Regular.ttf", "NotoSansHanifiRohingya-Bold.ttf",
    "NotoSansHanunoo-Regular.ttf",
    "NotoSansHatran-Regular.ttf",
    "NotoSansHebrew-Regular.ttf", "NotoSansHebrew-Bold.ttf", "NotoRashiHebrew-Regular.ttf", "NotoRashiHebrew-Bold.ttf",
    "NotoSansImperialAramaic-Regular.ttf",
    "NotoSansIndicSiyaqNumbers-Regular.ttf",
    "NotoSansInscriptionalPahlavi-Regular.ttf",
    "NotoSansInscriptionalParthian-Regular.ttf",
    "NotoSansJavanese-Regular.ttf", "NotoSansJavanese-Bold.ttf",
    "NotoSansKaithi-Regular.ttf",
    "NotoSansKannada-Regular.ttf", "NotoSansKannada-Bold.ttf", "NotoSansKannadaUI-Regular.ttf", "NotoSansKannadaUI-Bold.ttf",
    "NotoSansKawi-Regular.ttf", "NotoSansKawi-Bold.ttf",
    "NotoSansKayahLi-Regular.ttf", "NotoSansKayahLi-Bold.ttf",
    "NotoSansKharoshthi-Regular.ttf",
    "NotoSansKhmer-Regular.ttf", "NotoSansKhmer-Bold.ttf", "NotoSansKhmerUI-Regular.ttf", "NotoSansKhmerUI-Bold.ttf",
    "NotoSansKhojki-Regular.ttf",
    "NotoSansKhudawadi-Regular.ttf",
    "NotoSansLao-Regular.ttf", "NotoSansLao-Bold.ttf", "NotoSansLaoLooped-Regular.ttf", "NotoSansLaoLooped-Bold.ttf", "NotoSansLaoUI-Regular.ttf",
    "NotoSansLepcha-Regular.ttf",
    "NotoSansLimbu-Regular.ttf",
    "NotoSansLinearA-Regular.ttf", "NotoSansLinearB-Regular.ttf",
    "NotoSansLisu-Regular.ttf", "NotoSansLisu-Bold.ttf",
    "NotoSansLycian-Regular.ttf", "NotoSansLydian-Regular.ttf",
    "NotoSansMahajani-Regular.ttf",
    "NotoSansMalayalam-Regular.ttf", "NotoSansMalayalam-Bold.ttf", "NotoSansMalayalamUI-Regular.ttf", "NotoSansMalayalamUI-Bold.ttf",
    "NotoSansMandaic-Regular.ttf",
    "NotoSansManichaean-Regular.ttf",
    "NotoSansMarchen-Regular.ttf",
    "NotoSansMasaramGondi-Regular.ttf",
    "NotoSansMayanNumerals-Regular.ttf",
    "NotoSansMedefaidrin-Regular.ttf", "NotoSansMedefaidrin-Bold.ttf",
    "NotoSansMeeteiMayek-Regular.ttf", "NotoSansMeeteiMayek-Bold.ttf",
    "NotoSansMendeKikakui-Regular.ttf",
    "NotoSansMeroitic-Regular.ttf",
    "NotoSansMiao-Regular.ttf",
    "NotoSansModi-Regular.ttf",
    "NotoSansMongolian-Regular.ttf",
    "NotoSansMro-Regular.ttf",
    "NotoSansMultani-Regular.ttf",
    "NotoSansMyanmar-Regular.ttf", "NotoSansMyanmar-Bold.ttf", "NotoSansMyanmarUI-Regular.ttf", "NotoSansMyanmarUI-Bold.ttf",
    "NotoSansNabataean-Regular.ttf",
    "NotoSansNagMundari-Regular.ttf", "NotoSansNagMundari-Bold.ttf",
    "NotoSansNandinagarian-Regular.ttf",
    "NotoSansNewTaiLue-Regular.ttf", "NotoSansNewTaiLue-Bold.ttf",
    "NotoSansNewa-Regular.ttf",
    "NotoSansNushu-Regular.ttf",
    "NotoSansNyiakengPuachueHmong-Regular.ttf",
    "NotoSansOgham-Regular.ttf",
    "NotoSansOlChiki-Regular.ttf",
    "NotoSansOldHungarian-Regular.ttf",
    "NotoSansOldItalic-Regular.ttf",
    "NotoSansOldNorthArabian-Regular.ttf",
    "NotoSansOldPermic-Regular.ttf",
    "NotoSansOldSogdian-Regular.ttf",
    "NotoSansOldTurkic-Regular.ttf",
    "NotoSansOriya-Regular.ttf", "NotoSansOriya-Bold.ttf", "NotoSansOriyaUI-Regular.ttf", "NotoSansOriyaUI-Bold.ttf",
    "NotoSansOsage-Regular.ttf",
    "NotoSansOsmanya-Regular.ttf",
    "NotoSansPahawhHmong-Regular.ttf",
    "NotoSansPalmyrene-Regular.ttf",
    "NotoSansPauCinHau-Regular.ttf",
    "NotoSansPhagsPa-Regular.ttf",
    "NotoSansPhoenician-Regular.ttf",
    "NotoSansPhoneticExtensions-Regular.ttf",
    "NotoSansPsalterPahlavi-Regular.ttf",
    "NotoSansRejang-Regular.ttf",
    "NotoSansRunic-Regular.ttf",
    "NotoSansSamaritan-Regular.ttf",
    "NotoSansSaurashtra-Regular.ttf",
    "NotoSansSharda-Regular.ttf",
    "NotoSansShavian-Regular.ttf",
    "NotoSansSharada-Regular.ttf",
    "NotoSansSiddham-Regular.ttf",
    "NotoSansSinhala-Regular.ttf", "NotoSansSinhala-Bold.ttf",
    "NotoSansSogdian-Regular.ttf",
    "NotoSansSoraSompeng-Regular.ttf",
    "NotoSansSoyombo-Regular.ttf",
    "NotoSansSundanese-Regular.ttf", "NotoSansSundanese-Bold.ttf",
    "NotoSansSignWriting-Regular.ttf",
    "NotoSansSylotiNagri-Regular.ttf",
    "NotoSansSyriacEastern-Regular.ttf", "NotoSansSyriacEastern-Bold.ttf", "NotoSansSyriacEstrangela-Regular.ttf", "NotoSansSyriacEstrangela-Bold.ttf", "NotoSansSyriacWestern-Regular.ttf", "NotoSansSyriacWestern-Bold.ttf",
    "NotoSansTagalog-Regular.ttf",
    "NotoSansTagbanwa-Regular.ttf",
    "NotoSansTaiLe-Regular.ttf",
    "NotoSansTaiTham-Regular.ttf", "NotoSansTaiTham-Bold.ttf",
    "NotoSansTaiViet-Regular.ttf",
    "NotoSansTakri-Regular.ttf",
    "NotoSansTamil-Regular.ttf", "NotoSansTamil-Bold.ttf", "NotoSansTamilUI-Regular.ttf", "NotoSansTamilUI-Bold.ttf",
    "NotoSansTangut-Regular.ttf",
    "NotoSansTelugu-Regular.ttf", "NotoSansTelugu-Bold.ttf", "NotoSansTeluguUI-Regular.ttf", "NotoSansTeluguUI-Bold.ttf",
    "NotoSansThaana-Regular.ttf", "NotoSansThaana-Bold.ttf",
    "NotoSansThai-Regular.ttf", "NotoSansThai-Bold.ttf", "NotoSansThaiUI-Regular.ttf", "NotoSansThaiUI-Bold.ttf",
    "NotoSansTibetan-Regular.ttf", "NotoSansTibetan-Bold.ttf",
    "NotoSansTifinagh-Regular.ttf",
    "NotoSansTiro-Regular.ttf",
    "NotoSansUgaritic-Regular.ttf",
    "NotoSansVai-Regular.ttf", "NotoSansVai-Bold.ttf",
    "NotoSansVithkuqi-Regular.ttf",
    "NotoSansWancho-Regular.ttf",
    "NotoSansWarangCiti-Regular.ttf",
    "NotoSansYeziCorbit-Regular.ttf",
    "NotoSansYi-Regular.ttf", "NotoSansYi-Bold.ttf",
    "NotoSansZanabazarSquare-Regular.ttf",
    "NotoColorEmoji.ttf",
    "NotoSansCJK-Regular.ttc", "NotoSansCJK-Bold.ttc",
    "STIXTwoMath-Regular.otf", "FiraMath-Regular.otf", "NotoSansDevanagari-Bold.ttf", "NotoSansArabic-Bold.ttf",
    "GoNotoCurrent-Regular.ttf",
    "GoNotoCurrent-Bold.ttf",
    "GoNotoCurrentSerif.ttf",
    "GoNotoAncient.ttf",
    "GoNotoKurrent-Regular.ttf",
]

ALL_FONTS = GLOBAL_FONTS + ARM_FONTS

FONTS = {'regular': [], 'bold': [], 'italic': [], 'mono': []}

def get_script_name(code):
    script_map = {
        'Cyrl': 'Cyrillic',
        'Armn': 'Armenian', 'Arab': 'Arabic', 'Beng': 'Bengali', 'Deva': 'Devanagari', 'Ethi': 'Ethiopic',
        'Geor': 'Georgian', 'Grek': 'Greek', 'Gujr': 'Gujarati', 'Hebr': 'Hebrew', 'Knda': 'Kannada',
        'Khmr': 'Khmer', 'Laoo': 'Lao', 'Mlym': 'Malayalam', 'Mong': 'Mongolian', 'Mymr': 'Myanmar',
        'Orya': 'Oriya', 'Sinh': 'Sinhala', 'Taml': 'Tamil', 'Telu': 'Telugu', 'Thaa': 'Thaana',
        'Thai': 'Thai', 'Tibt': 'Tibetan', 'Cans': 'CanadianAboriginal', 'Cher': 'Cherokee', 'Copt': 'Coptic',
        'Cprt': 'Cypriot', 'Dsrt': 'Deseret', 'Egyp': 'EgyptianHieroglyphs', 'Ethi': 'Ethiopic', 'Goth': 'Gothic',
        'Hani': 'Han', 'Hira': 'Hiragana', 'Kana': 'Katakana', 'Khar': 'Kharoshthi', 'Limb': 'Limbu',
        'Linb': 'LinearB', 'Lisu': 'Lisu', 'Lyci': 'Lycian', 'Lydi': 'Lydian', 'Mand': 'Mandaic',
        'Mani': 'Manichaean', 'Maya': 'MayanNumerals', 'Mend': 'MendeKikakui', 'Merc': 'Meroitic', 'Nkoo': 'Nko',
        'Ogam': 'Ogham', 'Olck': 'OlChiki', 'Perm': 'OldPermic', 'Phli': 'InscriptionalPahlavi', 'Phlv': 'PsalterPahlavi',
        'Phnx': 'Phoenician', 'Plrd': 'Miao', 'Roro': 'Rongorongo', 'Runr': 'Runic', 'Samr': 'Samaritan',
        'Sara': 'Saurashtra', 'Saur': 'Saurashtra', 'Shrd': 'Sharada', 'Sund': 'Sundanese', 'Syrc': 'Syriac',
        'Tagb': 'Tagbanwa', 'Tale': 'TaiLe', 'Talu': 'NewTaiLue', 'Taml': 'Tamil', 'Tavt': 'TaiViet',
        'Tfng': 'Tifinagh', 'Tglg': 'Tagalog', 'Thaa': 'Thaana', 'Thai': 'Thai', 'Tibt': 'Tibetan',
        'Ugar': 'Ugaritic', 'Vaii': 'Vai', 'Yiii': 'Yi', 'Zinh': 'Inherited', 'Zyyy': 'Common', 'Zzzz': 'Unknown',
        'Adlm': 'Adlam', 'Aghb': 'CaucasianAlbanian', 'Ahom': 'Ahom', 'Armi': 'ImperialAramaic', 'Avst': 'Avestan',
        'Bali': 'Balinese', 'Bamu': 'Bamum', 'Bass': 'BassaVah', 'Batk': 'Batak', 'Bhaiksuki': 'Bhaiksuki',
        'Bopo': 'Bopomofo', 'Brahmi': 'Brahmi', 'Bugi': 'Buginese', 'Buhid': 'Buhid',
        'Cakm': 'Chakma', 'Cans': 'CanadianAboriginal', 'Cari': 'Carian', 'Cham': 'Cham', 'Cherokee': 'Cherokee',
        'Chorasmian': 'Chorasmian', 'Copt': 'Coptic', 'Cprt': 'Cypriot', 'CyproMinoan': 'CyproMinoan', 'Dsrt': 'Deseret',
        'Duployan': 'Duployan', 'Egyp': 'EgyptianHieroglyphs', 'Elbasan': 'Elbasan', 'Elymaic': 'Elymaic', 'Geok': 'Khutsuri',
        'Glagolitic': 'Glagolitic', 'Gothic': 'Gothic', 'Grantha': 'Grantha', 'Gujarati': 'Gujarati', 'GunjalaGondi': 'GunjalaGondi',
        'Gurmukhi': 'Gurmukhi', 'Hani': 'Han', 'Hangul': 'Hangul', 'Hatran': 'Hatran', 'Hebrew': 'Hebrew', 'AnatolianHieroglyphs': 'AnatolianHieroglyphs',
        'PahawhHmong': 'PahawhHmong', 'NyiakengPuachueHmong': 'NyiakengPuachueHmong', 'OldHungarian': 'OldHungarian',
        'OldItalic': 'OldItalic', 'Javanese': 'Javanese', 'Kaithi': 'Kaithi', 'Kannada': 'Kannada', 'KayahLi': 'KayahLi',
        'Kharoshthi': 'Kharoshthi', 'Khmer': 'Khmer', 'Khojki': 'Khojki', 'Limbu': 'Limbu',
        'LinearA': 'LinearA', 'LinearB': 'LinearB', 'Lisu': 'Lisu', 'Loma': 'Loma', 'Lycian': 'Lycian',
        'Lydian': 'Lydian', 'Mahajani': 'Mahajani', 'Makasar': 'Makasar', 'Manichaean': 'Manichaean', 'Marchen': 'Marchen',
        'MeeteiMayek': 'MeeteiMayek', 'Multani': 'Multani', 'Myanmar': 'Myanmar', 'Nabataean': 'Nabataean', 'Nandinagari': 'Nandinagari',
        'OldNorthArabian': 'OldNorthArabian', 'Naskh': 'Naskh', 'Nushu': 'Nushu', 'Nko': 'Nko', 'Ogham': 'Ogham',
        'OlChiki': 'OlChiki', 'Palmyrene': 'Palmyrene', 'OldPermic': 'OldPermic', 'PhagsPa': 'PhagsPa', 'InscriptionalPahlavi': 'InscriptionalPahlavi',
        'PsalterPahlavi': 'PsalterPahlavi', 'InscriptionalParthian': 'InscriptionalParthian', 'Phoenician': 'Phoenician', 'Miao': 'Miao', 'OldSogdian': 'OldSogdian',
        'Rejang': 'Rejang', 'Rongorongo': 'Rongorongo', 'Samaritan': 'Samaritan', 'Saurashtra': 'Saurashtra',
        'SignWriting': 'SignWriting', 'Shavian': 'Shavian', 'Sharada': 'Sharada', 'Siddham': 'Siddham', 'Khudawadi': 'Khudawadi',
        'Sinhala': 'Sinhala', 'Sogdian': 'Sogdian', 'SoraSompeng': 'SoraSompeng', 'Soyombo': 'Soyombo',
        'Sundanese': 'Sundanese', 'SylotiNagri': 'SylotiNagri', 'Syriac': 'Syriac', 'Tagbanwa': 'Tagbanwa', 'Takri': 'Takri',
        'TaiLe': 'TaiLe', 'NewTaiLue': 'NewTaiLue', 'Tamil': 'Tamil', 'Tangut': 'Tangut', 'TaiViet': 'TaiViet',
        'Telugu': 'Telugu', 'Thaana': 'Thaana', 'Thai': 'Thai', 'Tibetan': 'Tibetan', 'Tifinagh': 'Tifinagh',
        'Tirhuta': 'Tirhuta', 'Ugaritic': 'Ugaritic', 'Vai': 'Vai', 'VisibleSpeech': 'VisibleSpeech', 'WarangCiti': 'WarangCiti',
        'Wancho': 'Wancho', 'Yi': 'Yi', 'ZanabazarSquare': 'ZanabazarSquare', 'Inherited': 'Inherited', 'MathematicalNotation': 'MathematicalNotation',
    }
    return script_map.get(code, 'Common')

def classify_font_style(name):
    name_lower = name.lower()
    if any(word in name_lower for word in ['bold', 'heavy', 'black']):
        return 'bold'
    elif any(word in name_lower for word in ['italic', 'oblique']):
        return 'italic'
    elif any(word in name_lower for word in ['mono', 'code', 'fixed']):
        return 'mono'
    elif 'serif' in name_lower:
        return 'regular'
    elif 'ancient' in name_lower or 'kurrent' in name_lower:
        return 'regular'
    else:
        return 'regular'

def load_fonts(font_list, fonts_dict):
    for name in font_list:
        p = ASSETS_DIR / name
        if not p.exists():
            backup = p.with_suffix(".bak")
            if backup.exists():
                shutil.copy(backup, p)
            else:
                continue
        try:
            if 'Emoji' in name or name.endswith('.otf'):
                continue
            font = ImageFont.truetype(str(p), 52, index=0)
            style = classify_font_style(name)
            fonts_dict[style].append(font)
            if not p.with_suffix(".bak").exists():
                shutil.copy(p, p.with_suffix(".bak"))
        except Exception as e:
            if name.endswith('.ttc'):
                for idx in range(8):
                    try:
                        font = ImageFont.truetype(str(p), 52, index=idx)
                        style = classify_font_style(name)
                        fonts_dict[style].append(font)
                        break
                    except:
                        continue

load_fonts(ARM_FONTS, FONTS)
load_fonts(GLOBAL_FONTS, FONTS)

for style in FONTS:
    if not FONTS[style]:
        FONTS[style].append(ImageFont.load_default(size=52))


def load_font_with_fallback(size, style='regular'):
    target_fonts = ALL_FONTS
    for name in target_fonts:
        p = ASSETS_DIR / name
        if p.exists():
            try:
                if 'Emoji' in name or name.endswith('.otf'):
                    continue
                file_style = classify_font_style(name)
                if file_style != style:
                    continue
                return ImageFont.truetype(str(p), size, index=0)
            except:
                if name.endswith('.ttc'):
                    for idx in range(8):
                        try:
                            return ImageFont.truetype(str(p), size, index=idx)
                        except:
                            continue
                continue
    return ImageFont.load_default(size=size)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

W, H = 1320, 760
BG_BLUR = 22
# make bot avatar a bit larger
ICON_SIZE = 120
# increase the circular artwork size for a more prominent thumbnail
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
        from AnonXMusic import app
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
        if len(p) == 3: p = (*p, 255)
        if p[3] < 150: continue
        colors[p] = colors.get(p, 0) + 1
    return max(colors, key=colors.get)[:3] if colors else (40, 40, 80)

def gradient_bg(draw, w, h, color):
    r, g, b = color
    for y in range(h):
        factor = y / h
        col = (int(r * (1 - 0.25 * factor)), int(g * (1 - 0.25 * factor)), int(b * (1 - 0.25 * factor)))
        draw.line([(0, y), (w, y)], fill=(*col, 255))

def get_script(char):
    try:
        codepoint = ord(char)
        
        # Common/Latin
        if (0x0000 <= codepoint <= 0x007F or
            0x00A0 <= codepoint <= 0x017F or
            0x0180 <= codepoint <= 0x024F or
            0x1E00 <= codepoint <= 0x1EFF or
            0x2C60 <= codepoint <= 0x2C7F or
            0xA720 <= codepoint <= 0xA7FF):
            return "Zyyy"
        
        # Armenian
        if 0x0530 <= codepoint <= 0x058F:
            return "Armn"
        
        # Arabic
        if (0x0600 <= codepoint <= 0x06FF or
            0x0750 <= codepoint <= 0x077F or
            0x08A0 <= codepoint <= 0x08FF or
            0xFB50 <= codepoint <= 0xFDFF or
            0xFE70 <= codepoint <= 0xFEFF):
            return "Arab"
        
        # Bengali
        if 0x0980 <= codepoint <= 0x09FF:
            return "Beng"
        
        # Devanagari
        if 0x0900 <= codepoint <= 0x097F:
            return "Deva"
        
        # Ethiopic
        if (0x1200 <= codepoint <= 0x139F or
            0x2D80 <= codepoint <= 0x2DDF or
            0xAB00 <= codepoint <= 0xAB2F):
            return "Ethi"
        
        # Georgian
        if (0x10A0 <= codepoint <= 0x10FF or
            0x2D00 <= codepoint <= 0x2D2F):
            return "Geor"
        
        # Greek
        if (0x0370 <= codepoint <= 0x03FF or
            0x1F00 <= codepoint <= 0x1FFF):
            return "Grek"
        
        # Gujarati
        if 0x0A80 <= codepoint <= 0x0AFF:
            return "Gujr"
        
        # Hebrew
        if (0x0590 <= codepoint <= 0x05FF or
            0xFB1D <= codepoint <= 0xFB4F):
            return "Hebr"
        
        # Kannada
        if 0x0C80 <= codepoint <= 0x0CFF:
            return "Knda"
        
        # Khmer
        if 0x1780 <= codepoint <= 0x17FF:
            return "Khmr"
        
        # Lao
        if 0x0E80 <= codepoint <= 0x0EFF:
            return "Laoo"
        
        # Malayalam
        if 0x0D00 <= codepoint <= 0x0D7F:
            return "Mlym"
        
        # Myanmar
        if 0x1000 <= codepoint <= 0x109F:
            return "Mymr"
        
        # Oriya
        if 0x0B00 <= codepoint <= 0x0B7F:
            return "Orya"
        
        # Sinhala
        if 0x0D80 <= codepoint <= 0x0DFF:
            return "Sinh"
        
        # Tamil
        if 0x0B80 <= codepoint <= 0x0BFF:
            return "Taml"
        
        # Telugu
        if 0x0C00 <= codepoint <= 0x0C7F:
            return "Telu"
        
        # Thaana
        if 0x0780 <= codepoint <= 0x07BF:
            return "Thaa"
        
        # Thai
        if 0x0E00 <= codepoint <= 0x0E7F:
            return "Thai"
        
        # Tibetan
        if 0x0F00 <= codepoint <= 0x0FFF:
            return "Tibt"
        
        # Cyrillic - Fix for й
        if (0x0400 <= codepoint <= 0x04FF or
            0x0500 <= codepoint <= 0x052F or
            0x2DE0 <= codepoint <= 0x2DFF or
            0xA640 <= codepoint <= 0xA69F or
            0x1C80 <= codepoint <= 0x1C88):
            return "Cyrl"
        
        return "Zyyy"
    except Exception:
        return "Zyyy"

def has_glyph(font, char):
    mask = font.getmask(char)
    bbox = mask.getbbox()
    return bbox is not None and bbox[2] > 0 and bbox[3] > 0

def draw_text_with_shadow_multi(draw, xy, text, style='regular', fill=WHITE, stroke=4):
    fonts = FONTS.get(style, FONTS['regular'])
    x, y = xy
    for dx in [-stroke, 0, stroke]:
        for dy in [-stroke, 0, stroke]:
            if dx or dy:
                cx = x + dx
                for char in text:
                    script = get_script(char)
                    script_name = get_script_name(script)
                    script_fonts = fonts
                    font = next((f for f in script_fonts if has_glyph(f, char)), fonts[-1])
                    draw.text((cx, y + dy), char, fill=STROKE_COLOR, font=font)
                    cx += font.getlength(char)
    cx = x + 2
    for char in text:
        script = get_script(char)
        script_name = get_script_name(script)
        script_fonts = fonts
        font = next((f for f in script_fonts if has_glyph(f, char)), fonts[-1])
        draw.text((cx, y + 2), char, fill=TEXT_SHADOW, font=font)
        cx += font.getlength(char)
    cx = x
    for char in text:
        script = get_script(char)
        script_name = get_script_name(script)
        script_fonts = fonts
        font = next((f for f in script_fonts if has_glyph(f, char)), fonts[-1])
        draw.text((cx, y), char, fill=fill, font=font)
        cx += font.getlength(char)

def draw_text_shadow(draw, xy, text, font, fill=WHITE, stroke=2):
    x, y = xy
    for dx in [-stroke, 0, stroke]:
        for dy in [-stroke, 0, stroke]:
            if dx or dy:
                draw.text((x + dx, y + dy), text, fill=STROKE_COLOR, font=font)
    draw.text((x + 1, y + 1), text, fill=TEXT_SHADOW, font=font)
    draw.text((x, y), text, fill=fill, font=font)

def split_text_multi(text, style='regular', max_w=0, max_lines=4):
    if not text or max_w <= 0:
        return [text] if text else []
    
    fonts = FONTS.get(style, FONTS['regular'])
    words = text.split()
    lines = []
    cur_line = []
    cur_width = 0
    
    for word in words:
        space_width = fonts[0].getlength(' ') if cur_line else 0
        word_width = get_text_width_multi(word, style)
        next_width = cur_width + space_width + word_width
        
        if next_width > max_w and cur_line:
            lines.append(' '.join(cur_line))
            cur_line = [word]
            cur_width = word_width
            if len(lines) >= max_lines:
                break
        else:
            cur_line.append(word)
            cur_width = next_width
    
    if cur_line:
        if len(lines) < max_lines:
            lines.append(' '.join(cur_line))
        else:
            last_line = ' '.join(cur_line)
            while get_text_width_multi(last_line, style) > max_w and last_line:
                last_words = last_line.split()
                if len(last_words) > 1:
                    last_line = ' '.join(last_words[:-1])
                else:
                    last_line = last_words[0][:len(last_words[0])-1]
            lines[-1] = last_line
    
    return lines[:max_lines]

def get_text_width_multi(text, style='regular'):
    fonts = FONTS.get(style, FONTS['regular'])
    width = 0
    for char in text:
        script = get_script(char)
        script_name = get_script_name(script)
        script_fonts = fonts
        font = next((f for f in script_fonts if has_glyph(f, char)), fonts[-1])
        width += font.getlength(char)
    return width

import asyncio

def format_views_count(views: int) -> str:
    """Format view count in a readable way (e.g., 1.2K, 12M)"""
    if views >= 1000000000:  # Billions
        return f"{views / 1000000000:.1f}B"
    elif views >= 1000000:  # Millions
        return f"{views / 1000000:.1f}M"
    elif views >= 1000:  # Thousands
        return f"{views / 1000:.1f}K"
    else:
        return str(views)

async def get_thumb(videoid: str, queue_pos: int = 1, title_style: str = 'bold'):
    cache_file = CACHE_DIR / f"{videoid}_thumb.jpg"
    if cache_file.exists():
        return str(cache_file)

    try:
        loop = asyncio.get_event_loop()
        try:
            with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(f"https://youtu.be/{videoid}", download=False)
        except Exception:
            return config.DEFAULT_THUMB
        if not info:
            return config.DEFAULT_THUMB
        title = info.get("title", "Unknown Song")
        title = unicodedata.normalize('NFC', title)
        thumb_url = info.get("thumbnail", "")
        channel_name = info.get('uploader', 'Unknown')
        view_count = info.get('view_count', 0)
        duration = info.get('duration_string', '0:00')

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12)) as s:
            async with s.get(thumb_url) as r:
                if r.status != 200:
                    return None
                img_data = await r.read()

        tmp = CACHE_DIR / f"t_{videoid}.jpg"
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

        title_lines = split_text_multi(title, style=title_style, max_w=max_w, max_lines=4)

        # Title layout
        line_height = 58
        total_h = len(title_lines) * line_height
        # leave room below title for views counter
        t_y = y + (CIRCLE_SIZE - total_h) // 2 + 8

        for i, line in enumerate(title_lines):
            line_w = get_text_width_multi(line, style=title_style)
            tx = info_x + (max_w - line_w) // 2
            draw_text_with_shadow_multi(draw, (tx, t_y + i * line_height), line, style=title_style, stroke=4)

        # draw view count under the title
        try:
            views = int(view_count or 0)
        except:
            views = 0
        views_text = f"{format_views_count(views)} views"
        views_font = load_font_with_fallback(32, style='regular')
        v_w = views_font.getlength(views_text)
        v_x = info_x + (max_w - v_w) // 2
        v_y = t_y + total_h + 8
        draw_text_shadow(draw, (v_x, v_y), views_text, views_font, fill=(230,230,230,230), stroke=2)

        water = "ArmedMusic"
        water_font = load_font_with_fallback(28, style='italic')
        w_w = water_font.getlength(water)
        wx = W - w_w - 30
        wy = 10  # Top right corner
        draw_text_shadow(draw, (wx, wy), water, water_font, fill=(210,210,210,190), stroke=2)

        canvas = canvas.convert("RGB")
        canvas.save(cache_file, "JPEG", quality=99, optimize=True, subsampling=0)

        try: os.remove(tmp)
        except: pass

        return str(cache_file)

    except Exception as e:
        print(f"[Thumb Error] {e}")
        traceback.print_exc()
        return config.DEFAULT_THUMB


class Thumbnail:
    async def generate(self, song, size=None):
        return await get_thumb(song.id)