import discord
from discord.ext.interaction import Client
from libottdadmin2.constants import NETWORK_ADMIN_PORT
from typing import Any, Optional

from config.config import get_config
from client.openttd_client import OpenTTDClient

parser = get_config()


class DiscordClient(Client):
    def __init__(self, *, intents: discord.Intents, **options: Any):
        self.openttd_client: Optional[OpenTTDClient] = None
        super(DiscordClient, self).__init__(intents=intents, **options)

    async def setup_hook(self) -> None:
        await super(DiscordClient, self).setup_hook()
        self.openttd_client = await OpenTTDClient.connect_from_discord(
            client=self,
            host=parser.get("OpenTTD", "hostname"),
            port=parser.getint("OpenTTD", "port", fallback=NETWORK_ADMIN_PORT),
            password=parser.get("OpenTTD", "password", fallback="")
        )

    async def on_ready(self):
        await super(DiscordClient, self).on_ready()
        await self.openttd_client.client_active