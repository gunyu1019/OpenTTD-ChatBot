from typing import Tuple, Any

import discord
from libottdadmin2.client.asyncio import OttdAdminProtocol
from libottdadmin2.client.tracking import TrackingMixIn
from libottdadmin2.enums import UpdateType, UpdateFrequency
from libottdadmin2.packets import Packet
from libottdadmin2.util import camel_to_snake


class OpenTTDClient(TrackingMixIn, OttdAdminProtocol):
    discord_client: discord.Client
    update_types = {
        **TrackingMixIn.update_types,
        **{
            UpdateType.CONSOLE: UpdateFrequency.AUTOMATIC,
            UpdateType.CHAT: UpdateFrequency.AUTOMATIC,
            UpdateType.NAMES: UpdateFrequency.POLL,
            UpdateType.LOGGING: UpdateFrequency.AUTOMATIC,
        },
    }

    @classmethod
    async def connect_from_discord(
        cls,
        *,
        client: discord.Client,
        host: str,
        port: int,
        **kwargs
    ):
        loop = client.loop
        cls.discord_client = client
        transport, protocol = await loop.create_connection(
            lambda: cls(loop, **kwargs), host, port
        )
        return protocol

    def packet_received(self, packet: Packet, data: Tuple[Any, ...]) -> None:
        super(OpenTTDClient, self).packet_received(packet=packet, data=data)
        func_name = camel_to_snake(packet.__class__.__name__)
        self.discord_client.dispatch(func_name, **data._asdict())
        self.discord_client.dispatch("{}_raw".format(func_name), data=data)
        return
