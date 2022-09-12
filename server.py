from quart import Quart, request, Response
from discord.ext.ipc import Client
import asyncio

app = Quart(__name__)
IPC = Client(
    host="127.0.0.1",
    port=2300,
    secret_key="key"
)


@app.route('/apitrack/webhook', methods=['POST'])
async def main():
    response = await request.json
    await IPC.request("send_status_update", data=response)
    return "", 200


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app.ipc = loop.run_until_complete(IPC.start(loop=loop)) # `Client.start()` returns new Client instance
        app.run(loop=loop, host="0.0.0.0", port=8080)
    finally:
        loop.run_until_complete(app.ipc.close()) # Closes the session, doesn't close the loop
        loop.close()
