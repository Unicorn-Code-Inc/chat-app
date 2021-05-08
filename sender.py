import models
import asyncio
import asyncpg
from aioconsole import ainput
import pickle

loop = asyncio.get_event_loop()

async def send_message(conn: asyncpg.Connection, message: models.Message):
    ...

async def connect():
    with open("credentials.dat", "rb") as f:
        creds = pickle.load(f)

    print("Connecting to the database...")

    try:
        conn = await asyncpg.connect(**creds) # Create the connection
    except Exception as exc:
        exit(f"{exc.__class__.__name__}: {exc}")
    else:
        print("Connected successfully.")
        return conn

async def main():
    conn = await connect()
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