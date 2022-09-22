from objects.database_object import ShippingCodesDB
from discord.ext.ipc.errors import IPCError
from discord.ext.ipc.server import route
from discord.ext import commands, ipc
from functions.timestamp import time
import discord


class Routes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not hasattr(bot, "ipc"):
            bot.ipc = ipc.Server(self.bot, host="127.0.0.1", port=2300, secret_key="key")
            bot.ipc.start(self)

    @commands.Cog.listener()
    async def on_ipc_ready(self):
        print("Ipc is ready")

    @commands.Cog.listener()
    async def on_ipc_error(self, endpoint: str, error: IPCError):
        print(f'{time()}' + " Error on endpoint: " + f'{endpoint} {error}')

    @route()
    async def send_status_update(self, ipc_data):
        response = ipc_data.data

        if response["event"] == "TRACKING_UPDATED":
            print(f'{time()} -- tracking info received by server')
            index = response["data"]

            db_worker = ShippingCodesDB()
            db_worker.connect("shipping_codes.db")

            names = db_worker.get_names(index["number"], index["carrier"])
            users = db_worker.get_users(index["number"], index["carrier"])

            for i in range(len(names)):
                tracking_update = {
                    'name': names[i][0],
                    'user': users[i][0],
                    'status': index["track_info"]["latest_status"]["status"],
                    'update_time': index["track_info"]["latest_event"]["time_iso"],
                    'description': index["track_info"]["latest_event"]["description"]
                }

                chat = await self.bot.fetch_user(tracking_update['user'])
                embed = discord.Embed(
                    title=f'An update for {tracking_update["name"]} has been detected! ({tracking_update["status"]})',
                    description=f'{tracking_update["description"]} at {tracking_update["update_time"]}')

                print(f'{time()} -- sending tracking update to corresponding user')
                await chat.send(embed=embed)

            db_worker.close()

        if response["event"] == "TRACKING_STOPPED":
            print(f'{time()} -- tracking stop received by server')
            index = response["data"]

            print(index)

            db_worker = ShippingCodesDB()
            db_worker.connect("shipping_codes.db")

            tracking_stop = {
                'name': db_worker.get_names(index["number"], index["carrier"]),
                'user': db_worker.get_users(index["number"], index["carrier"])[0],
            }

            chat = await self.bot.fetch_user(tracking_stop['user'])
            embed = discord.Embed(
                title=f'Tracking stopped for {tracking_stop["name"]}'
            )

            db_worker.tracking_stop(index["number"], index["carrier"])
            db_worker.commit_changes()

            print(f'{time()} -- sending tracking update to corresponding user')
            await chat.send(embed=embed)

            db_worker.close()
