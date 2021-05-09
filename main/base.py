import asyncio
import asyncpg
import pickle
import requests

__all__ = ("Base",)

async def _get_public_ip(loop: asyncio.AbstractEventLoop):
    def getter():
        resp = requests.get("https://api.my-ip.io/ip.json").json()
        return resp["ip"]
    return await loop.run_in_executor(None, getter)


def _load_credentials():
    with open("credentials.dat", "rb") as f:
        creds = pickle.load(f)
    return creds


class Base:
    def __init__(self, *, loop=None):
        self.conn = None # Created on `connect`
        self.ip = None # Also created on `connect`
        self.loop = loop or asyncio.get_event_loop()


    async def connect(self):
        self.ip = await _get_public_ip(self.loop)

        creds = _load_credentials()
        try:
            conn = await asyncpg.connect(**creds)
        except Exception as exc:
            raise RuntimeError(f"An exception raised when connecting\n{exc.__class__.__name__}: {exc}")
        else:
            self.conn = conn


    async def send_message(self, message: str):
        """Sends a message through the database"""
        ...


    async def logout(self):
        await self.conn.close()