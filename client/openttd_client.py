import discord
from libottdadmin2.client.tracking import TrackingMixIn
from libottdadmin2.enums import Action, DestType, UpdateType, UpdateFrequency
from libottdadmin2.client.asyncio import OttdAdminProtocol


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

    def on_server_chat(
        self, action: Action, type: DestType, client_id: int, message: str, extra: int
    ):
        client = self.clients.get(client_id, client_id)
        client = getattr(client, "name", client)  # Fallback to client id
        self.log.debug(
            "Chat: [%s@%s] %s > %s",
            Action(action).name,
            DestType(type).name,
            client,
            message,
        )
        self.discord_client.dispatch(
            "server_chat", action=action, type=type, client=client, message=message, extra=extra
        )

    def on_server_cmd_logging(
        self,
        client_id: int,
        company_id: int,
        command_id: int,
        param1: int,
        param2: int,
        tile: int,
        text: str,
        frame: int,
    ):
        client = self.clients.get(client_id, client_id)
        client = getattr(client, "name", client)  # Fallback to client id
        company = self.companies.get(company_id, company_id)
        company = getattr(company, "name", company)  # Fallback to company id
        command = self.commands.get(command_id, command_id)
        self.log.debug(
            "Command: [%s/%s] %s > 0x%x 0x%x Tile 0x%x (%s) on frame %d",
            client,
            company,
            command,
            param1,
            param2,
            tile,
            text,
            frame,
        )

