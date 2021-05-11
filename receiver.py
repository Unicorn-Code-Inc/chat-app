from main import Server
import asyncio

loop = asyncio.get_event_loop()

async def main():
    async with Server() as server:
        await server.get_unread_messages()
        await server.listen()


if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()