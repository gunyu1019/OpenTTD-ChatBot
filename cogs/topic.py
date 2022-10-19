import json
import os.path
from typing import Optional

import aiohttp
import discord
from discord.ext import interaction
from libottdadmin2.enums import Action, DestType, ChatAction

from client.discord_client import DiscordClient
from config.config import get_config
from utils.directory import directory

parser = get_config()


class Topic:
    def __init__(self, bot: DiscordClient):
        self.bot = bot


def setup(client):
    client.add_interaction_cog(Topic(client))
