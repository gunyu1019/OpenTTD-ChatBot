import asyncio
import logging
import discord

from config.config import get_config
from client.discord_client import DiscordClient
from utils.directory import directory


parser = get_config()
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    client = DiscordClient(intents=discord.Intents.all())
    client.load_extensions("cogs", directory)
    client.run(token=parser.get("Default", "token"))
