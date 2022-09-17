from objects.database_object import ShippingCodesDB, DiscordUsers
from configs.config import discord_token, tm_secret
from functions.agree_eula import agree_eula
from discord_commands.commands import bot
from functions.discord_ipc import Routes
from server import app, IPC
import asyncio
import time
import os


async def setup(bot_ctx):
    await bot_ctx.add_cog(Routes(bot_ctx))


# -- Check eula
if agree_eula() is False:
    exit(-1)
    
# -- Fork the bot to run the web server
pid = os.fork()
if pid > 0:
    pass
else:
    print(f'Waiting 10 seconds until IPC becomes ready...')
    time.sleep(10)
    if __name__ == '__main__':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            app.ipc = loop.run_until_complete(IPC.start(loop=loop))  # `Client.start()` returns new Client instance
            app.run(loop=loop, host="0.0.0.0", port=8080)
        finally:
            loop.run_until_complete(app.ipc.close())  # Closes the session, doesn't close the loop
            loop.close()

# -- Check tokens
if discord_token is None or tm_secret is None:
    print("Error, missing tokens. Cannot proceed.")
    exit(-1)

# -- Init db classes
db_worker = ShippingCodesDB()
userdb_worker = DiscordUsers()

# -- Create and connect to shipping codes database
if not os.path.isfile("shipping_codes.db"):
    print("Shipping codes database not found. Creating one.")
    db_worker.connect(name="shipping_codes.db")
    db_worker.init_database()
else:
    print("Connecting to shipping codes database...")
    db_worker.connect(name="shipping_codes.db")

# -- Create and connect to users database
if not os.path.isfile("users_database.db"):
    print("Users database not found. Creating one.")
    userdb_worker.connect(name="users_database.db")
    userdb_worker.init_database()
else:
    print("Connecting to users database...")
    userdb_worker.connect(name="users_database.db")

# -- Run the Discord bot
if __name__ == "__main__":
    bot.run(discord_token)
