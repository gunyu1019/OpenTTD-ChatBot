import os.path
import re
import json
import discord
from discord.ext import interaction
from libottdadmin2.enums import Action, DestType, ChatAction
from typing import List, Optional, Dict, Any

from client.discord_client import DiscordClient
from config.config import get_config
from utils.directory import directory

parser = get_config()


class Chatting:
    def __init__(self, bot: DiscordClient):
        self.bot = bot

        self.is_enabled = False
        self.webhook: Optional[discord.Webhook] = None
        self.webhook_url = parser.get("Discord", "webhook_url", fallback=None)
        if self.webhook_url is not None:
            m = re.search(
                r'discord(?:app)?.com/api/webhooks/(?P<id>[0-9]{17,20})/(?P<token>[A-Za-z0-9\.\-\_]{60,68})',
                self.webhook_url
            )
            if m is None:
                raise ValueError('Invalid webhook URL given.')

            data: Dict[str, Any] = m.groupdict()
            self.webhook_id = data['id']

        with open(os.path.join(directory, "config", "profile_image.json"), "r") as fp:
            self.profile_json = json.load(fp)

    def get_avatar_url(self, username: str):
        user_info = None
        for profile in self.profile_json:
            if username in profile['username']:
                user_info = profile
                break
        else:
            return

        if username['profileType'] == 0:
            member = self.bot.get_user(user_info['discordId'])
            return member.display_avatar.url

    @interaction.listener()
    async def on_ready(self):
        if self.webhook_url is not None:
            self.is_enabled = True
            self.webhook = self.bot.fetch_webhook(self.webhook_id)

    @interaction.listener()
    async def on_server_chat(self, action: Action, type: DestType, client_id: int, message: str, extra: int):
        client = self.bot.openttd_client.clients.get(client_id, client_id)
        client = getattr(client, "name", client)
        if type == DestType.BROADCAST and action == ChatAction.CHAT and self.is_enabled:
            await self.webhook.send(username=client, avatar_url=self.get_avatar_url(client), content=message)
        return


def setup(client):
    client.add_interaction_cog(Chatting(client))
