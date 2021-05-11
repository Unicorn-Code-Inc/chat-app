from main import Server
import asyncio

loop = asyncio.get_event_loop()

async def main():
    async with Server() as server:
        await server.listen()


if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except Exception as exc:
        print(f"An error happened\n{exc.__class__.__name__}: {exc}")
    finally:
        loop.close()