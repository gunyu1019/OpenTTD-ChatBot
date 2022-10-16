import logging
import json
import discord
from discord.ext import interaction
from libottdadmin2.enums import Action, DestType, ChatAction
from typing import List, Optional

from client.discord_client import DiscordClient
from config.config import get_config

parser = get_config()


class Chatting:
    def __init__(self, bot: DiscordClient):
        self.bot = bot

        self.is_enabled = False
        self.guild_id = -1
        self.channel_id: List[int] = []

        self.guild: Optional[discord.Guild] = None
        self.channels: List[discord.abc.MessageableChannel] = []

    @interaction.listener()
    async def on_ready(self):
        self.is_enabled = parser.has_option("Discord", "guild_id") and parser.has_option("Discord", "channel_id")
        if self.is_enabled:
            self.guild_id = parser.getint("Discord", "guild_id")
            self.channel_id = list(
                    map(int, list(
                        json.loads(parser.get("Discord", "channel_id", fallback="[]"))
                    )
                )
            )

            self.guild = self.bot.get_guild(self.guild_id)
            self.channels = [
                self.guild.get_channel(x) for x in self.channel_id
            ]

    @interaction.listener()
    async def on_server_chat(self, action: Action, type: DestType, client_id: int, message: str, extra: int):
        client = self.bot.openttd_client.clients.get(client_id, client_id)
        client = getattr(client, "name", client)
        if type == DestType.BROADCAST and action == ChatAction.CHAT and self.is_enabled:
            for channel in self.channels:
                await channel.send("**[{0}]**: {1}".format(client, message))
        return


def setup(client):
    client.add_interaction_cog(Chatting(client))
