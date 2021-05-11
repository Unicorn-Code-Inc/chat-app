import asyncio
import asyncpg
import pickle
import getpass
import requests
import json
from datetime import datetime
import uuid

__all__ = ("Base", "Client", "Server")

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
            await self.identify()


    async def identify(self):
        """Identifies the current IP address with the database and creates one if it doesn't exist"""
        data = await self.conn.fetchrow("SELECT * FROM users WHERE ip_addr = $1;", self.ip)
        if data is None:
            data = await self._register()

        self.user = dict(data)

    
    async def _register(self):
        name = getpass.getuser()
        data = await self.conn.fetchrow("INSERT INTO users (ip_addr, name) VALUES ($1, $2) RETURNING *", self.ip, name)
        return data


    async def send_message(self, message: str):
        """Sends a message through the database"""
        display_name = self.user["nick"] or self.user["name"]
        message_id = str(uuid.uuid4())
        payload = json.dumps({
            "message_id": message_id,
            "author": display_name,
            "content": message,
        })

        await self.conn.execute(f"NOTIFY message_channel, '{payload}';")
        await self.conn.execute(f"INSERT INTO messages (message_id, author, content) VALUES ($1, $2, $3);", message_id, self.ip, message)


    async def logout(self):
        await self.conn.close()


class Client(Base):
    ...


async def mark_as_read(conn, message_id="62259a55-8797-4a71-8429-c1c71f478ae2"):
    await conn.execute("UPDATE messages SET read = true WHERE message_id = $1", message_id)


def _listen_messages(conn, pid, channel, payload):
    data = json.loads(payload)
    print(f"({data['author']}): {data['content']}")

    loop = conn._loop
    loop.create_task(mark_as_read(conn, data['message_id'],))


class Server(Base):
    async def __aenter__(self):
        await self.connect()
        return self

    
    async def __aexit__(self, exc_type, exc, tb):
        await self.logout()


    async def listen(self, listener=None):
        """Listens to incoming messages"""
        if listener is None:
            listener = _listen_messages
        
        await self.conn.add_listener("message_channel", listener)

        self.fut = fut = self.loop.create_future()
        await mark_as_read(self.conn)
        await fut   