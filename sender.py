import asyncio
from aioconsole import ainput
from main import Client

loop = asyncio.get_event_loop()
client = Client(loop=loop)

async def main():
    await client.connect()

    while True:
        message = await ainput(">>> ")
        if not message: # If the message is empty
            continue

        if message.lower() != "exit":
            await client.send_message(message) # sending the message
        else:
            break # Break out of the for-loop

    await client.logout() # Tidying up (close the conn)


if __name__ == "__main__":
    loop.run_until_complete(main())
    loop.close()