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

