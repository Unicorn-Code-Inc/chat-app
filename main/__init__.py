import asyncio
import asyncpg
import pickle
import getpass
import json
import aiohttp
import uuid
import typing
import logging
from playsound import playsound
import functools

__all__ = ("Client", "Server")

log = logging.getLogger(__name__)

async def _get_public_ip(session: aiohttp.ClientSession) -> str:
    async with session.get("https://api.my-ip.io/ip.json") as resp:
        data = await resp.json()

    return data["ip"]


def _load_credentials() -> typing.Dict[str, typing.Any]:
    with open("credentials.dat", "rb") as f:
        creds = pickle.load(f)
    return creds


async def mark_as_read(conn: asyncpg.Connection, message_id: str) -> None:
    try:
        await conn.execute("UPDATE messages SET read = true WHERE message_id = $1", message_id)
    except:
        pass


class Client:
    def __init__(self, *, loop=None):
        self.conn = None # Created on `connect`
        self.ip = None # Also created on `connect`
        self.session = None # Also created on `connect`
        self.loop = loop or asyncio.get_event_loop()


    async def connect(self):
        log.info("logging in into the database")

        self.session = session = aiohttp.ClientSession()
        self.ip = await _get_public_ip(session)

        creds = _load_credentials()
        try:
            conn = await asyncpg.connect(**creds)
        except Exception as exc:
            raise RuntimeError(f"An exception raised when connecting\n{exc.__class__.__name__}: {exc}")
        else:
            log.info("successfully connected into the database")
            self.conn = conn
            await self.identify()
            await self.dispatch_listeners()


    async def identify(self):
        """Identifies the current IP address with the database and creates a user if it doesn't exist"""
        log.info("identifying client user")
        data = await self.conn.fetchrow("SELECT * FROM users WHERE ip_addr = $1;", self.ip)
        if data is None:
            data = await self._register()

        self.user = dict(data)

    
    async def dispatch_listeners(self):
        await self.conn.execute(f"NOTIFY on_connect, '{self.user['name']}'")
        await self.conn.execute("UPDATE users SET connected=true WHERE ip_addr=$1", self.user['ip_addr'])

    
    async def _register(self):
        log.info("user does not exist, creating one")
        name = getpass.getuser()
        data = await self.conn.fetchrow("INSERT INTO users (ip_addr, name, token) VALUES ($1, $2, $3) RETURNING *", self.ip, name, str(uuid.uuid4()))
        return data


    async def send_message(self, message: str):
        """Sends a message through the database"""
        log.info(f"sending message {message}")
        display_name = self.user["nick"] or self.user["name"]
        message_id = str(uuid.uuid4())
        payload = json.dumps({
            "message_id": message_id,
            "author": display_name,
            "author_addr": self.ip,
            "content": message,
        })

        await self.conn.execute(f"NOTIFY message_channel, '{payload}';")
        await self.conn.execute(f"INSERT INTO messages (message_id, author, content, author_name) VALUES ($1, $2, $3, $4);", message_id, self.ip, message, display_name)


    async def logout(self):
        log.info("logging out")
        await self.conn.execute("UPDATE users SET connected=false WHERE ip_addr=$1", self.user['ip_addr'])
        await self.session.close()
        await self.conn.close()
        await asyncio.sleep(0.1) # So no error occurs


    async def get_unread_messages(self):
        """Fetches the unread messages of the current user"""
        messages = await self.conn.fetch("""SELECT (message_id, author_name, content) FROM messages WHERE author != $1 AND read = false AND content != 'exit'""", self.ip)
        log.info(f"fetched unread messages, {len(messages)}")
        print(f"You have {len(messages)} unread messages:")

        for message in messages:
            message_id, author, content = message[0]
            print(f"({author}): {content}")
            await mark_as_read(self.conn, message_id)

        print()


class Server(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fut = None # created on `listen`


    async def __aenter__(self):
        log.info("server startup")
        await self.connect()
        await self.get_unread_messages()
        return self

    
    async def __aexit__(self, exc_type, exc, tb):
        await self.logout()


    async def listen(self):
        log.info("listening to incoming messages")
        await self.conn.add_listener("message_channel", self.receive_message)

        self.fut = self.loop.create_future()
        await self.fut


    async def play_sound(self):
        callback = functools.partial(playsound, "sound_effect.mp3")
        await self.loop.run_in_executor(None, callback)


    def receive_message(self, conn: asyncpg.Connection, pid: int, channel: str, payload: str):
        data = json.loads(payload)
        log.info(f"received message from {data['author']}")
        if data['content'] == 'exit':
            if data["author_addr"] == self.ip: # We're exiting
                # Logout and cleanup
                self.fut.set_result(None)
            else:
                # Someone else exitted
                print(f"{data['author']} disconnected.")
        else:
            print(f"({data['author']}): {data['content']}")

        if data["author_addr"] != self.ip:
            log.info(f"marking {data['message_id']} as read")
            self.loop.create_task(self.play_sound())
            self.loop.create_task(mark_as_read(conn, data['message_id']))

    
    def on_user_connect(self, conn: asyncpg.Connection, pid: int, channel: str, payload: str):
        name = payload
        if name == self.user['name'] or name == self.user['nick']:
            return
        
        print(f"{name} has connected")


    async def identify(self):
        await super().identify()
        await self.conn.add_listener("on_connect", self.on_user_connect)