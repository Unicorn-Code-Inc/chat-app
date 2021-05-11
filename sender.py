import asyncio
from aioconsole import ainput
from main import Client

loop = asyncio.get_event_loop()
client = Client(loop=loop)

async def main():
    try:
        await client.connect()
    except RuntimeError as exc:
        exit(f"An error happened during connection\n{exc.__class__.__name__}: {exc}")

    while True:
        message = await ainput(">>> ")
        if not message: # If the message is empty
            print("Cannot send an empty message")
            continue

        if message.lower() != "exit":
            await client.send_message(message.replace("'", "")) # sending the message
        else:
            break # Break out of the for-loop

    await client.logout() # Tidying up (close the conn)


if __name__ == "__main__":
    loop.run_until_complete(main())
    loop.close()