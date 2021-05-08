import models
import asyncio
import asyncpg
from aioconsole import ainput

loop = asyncio.get_event_loop()

async def send_message(conn: asyncpg.Connection, message: "models.Message"):
    ...

async def main():
    conn = None # Create the connection
    if conn is None: # creating the connection failed, exit
        return

    while True:
        content = await ainput(">>> ")
        message = content # Create the class from the content
        if not message: # If the message is empty
            continue

        if message.lower() != "exit":
            await send_message(conn, message) # sending the message
        else:
            await conn.close() # Tidying up (close the conn)
            break # Break out of the for-loop

if __name__ == "__main__":
    loop.run_until_complete(main())
    loop.close()