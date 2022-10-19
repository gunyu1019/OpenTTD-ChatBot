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


class Chatting:
    def __init__(self, bot: DiscordClient):
        self.bot = bot

        self.is_enabled = False
        self.webhook_url = parser.get("Discord", "webhook_url", fallback=None)
        if self.webhook_url is not None:
            self.is_enabled = True

        with open(os.path.join(directory, "config", "profile_image.json"), "r", encoding='utf8') as fp:
            self.profile_json = json.load(fp)

    def get_avatar_url(self, username: str, guild: Optional[discord.Guild] = None) -> Optional[str]:
        user_info = None
        for profile in self.profile_json:
            if username in profile['username']:
                user_info = profile
                break
        else:
            return user_info

        if user_info['type'] == 0 and 'discordId' in user_info:
            member = (
                self.bot.get_user(user_info['discordId'])
                if guild is None else
                guild.get_member(user_info['discordId'])
            )
            return member.display_avatar.url

    @interaction.listener()
    async def on_server_chat(self, action: Action, type: DestType, client_id: int, message: str, extra: int):
        client = self.bot.openttd_client.clients.get(client_id, client_id)
        client = getattr(client, "name", client)
        if type == DestType.BROADCAST and action == ChatAction.CHAT and self.is_enabled:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(self.webhook_url, session=session)
                await webhook.send(username=client, avatar_url=self.get_avatar_url(client), content=message)
        return


def setup(client):
    client.add_interaction_cog(Chatting(client))
