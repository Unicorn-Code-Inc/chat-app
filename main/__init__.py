import typing
import asyncio

MAX_READ_BYTES = 1024

class Server:
    def __init__(self, *, loop: typing.Optional[asyncio.AbstractEventLoop]=None):
        self._loop = loop or asyncio.get_event_loop()
    
    async def handle_incoming_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handles new connections"""
        ...