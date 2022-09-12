from objects.database_object import ShippingCodesDB
from configs.config import discord_token, tm_secret
from discord_commands.commands import bot
from functions.discord_ipc import Routes
import os


async def setup(bot_ctx):
    await bot_ctx.add_cog(Routes(bot_ctx))


db_worker = ShippingCodesDB()

if discord_token is None or tm_secret is None:
    print("Error, missing tokens. Cannot proceed.")

if not os.path.isfile("shipping_codes.db"):
    print("Database not found. Creating one.")
    db_worker.connect(name="shipping_codes.db")
    db_worker.init_database()
else:
    print("Connecting to database...")
    db_worker.connect(name="shipping_codes.db")


if __name__ == "__main__":
    bot.run(discord_token)
