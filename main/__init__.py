import typing
import asyncio
import os
import aiohttp
import logging
import socket 

MAX_READ_BYTES = 1024

logger = logging.getLogger(__name__)

class Server:
    def __init__(self, *, loop: typing.Optional[asyncio.AbstractEventLoop]=None):
        self._loop = loop or asyncio.get_event_loop()
        self._server = None # Started on `self.listen`
        self._session = None # Started on `self.start`
        self._pool = None # Started on `self.start`
    

    async def handle_incoming_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handles new connections"""
        ...


    async def start(self):
        """Starts the connection pool to the database and an HTTP session"""
        ...


    async def listen(self):
        """Listens to incoming connections"""
        host, port = os.environ.get("HOST", "localhost"), int(os.environ.get("PORT", 8080))
        self._server = server = self._loop.start_server(
            self.handle_incoming_connection, host, port
        )
        logger.info(f"Server started on {host}:{port}")

        async with server:
            try:
                await server.server_forever()
            except asyncio.CancelledError:
                logger.info("Server is down, cleaning up...")
                await self.cleanup()


    async def cleanup(self):
        """Clean ups all the connections/sessions"""
        await self._session.close()
        await self._pool.close()

    
    @property
    def sockets(self) -> typing.List[socket.socket]:
        return self._server.sockets


    async def __aenter__(self):
        await self.start()
        await self.listen()
        return self

    
    async def __aexit__(self, exc_type, exc, tb):
        await self.cleanup()