from main import Server
import asyncio

loop = asyncio.get_event_loop()

async def main():
    async with Server() as server:
        await server.listen()


if __name__ == "__main__":
    loop.run_until_complete(main())
    loop.close()