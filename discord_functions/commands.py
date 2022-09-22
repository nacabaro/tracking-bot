from discord_functions.command_functions.remove_code import remove_code
from discord_functions.command_functions.rename_code import rename_code
from discord_functions.command_functions.track_code import track_code
from discord_functions.command_functions.check_code import check_code
from discord_functions.command_functions.list_codes import list_codes
from discord_functions.command_functions.add_code import add_code
from discord_functions.carrier_search import carrier_search
from functions.discord_ipc import Routes
from configs.config import bot_owner
from functions.timestamp import time
from discord.ext import commands
import discord


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='¡', activity=discord.Game(name="with your packages."), intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.add_cog(Routes(bot))
    print("INIT -- IPC Ready")


# Adds tracking code to system for user invoking the command:
#   tracking_code: Package tracking code
#   carrier_code: Package carrier code
@bot.command()
async def add(ctx, tracking_code=None, carrier_code=None):
    await add_code(bot, ctx, ctx.author.id, tracking_code, carrier_code)


# Removes code from system for user invoking the command:
#   name: Package's friendly name
@bot.command()
async def remove(ctx, name=None):
    await remove_code(bot, ctx, ctx.author.id, name)


# Asks API to track package:
#   name: Package's friendly name
@bot.command()
async def track(ctx, name=None):
    await track_code(bot, ctx, name)


# Lists all tracking codes for the user executing the command:
#   Takes no arguments.
@bot.command()
async def list(ctx):
    await list_codes(ctx, bot)


# Renames a tracking code.
#   name: Package's friendly name to be renamed
@bot.command()
async def rename(ctx, name):
    await rename_code(bot, ctx, name)


# Shows code for a specific package, useful for copying/pasting on mobile:
#   name: Package's friendly name
@bot.command()
async def checkcode(ctx, name):
    await check_code(bot, ctx, name)


# Shows the GitHub link for the source code of this bot:
#   Takes no arguments.
@bot.command()
async def source(ctx):
    await ctx.send("https://github.com/nacabaro/tracking-bot")


# -- Admin commands ----
# Adds a command to a user list specified by the administrator of the bot:
#   user_id: Discord's user ID for the user who you want to add the code to.
#   tracking_code: Package tracking code.
#   carrier_code: Package carrier code.
@bot.command()
async def forceadd(ctx, user_id, tracking_code=None, carrier_code=None):
    # Checks if the user who executed the command is the bot administrator. If the user is not the bot administrator,
    # react to the message with a cross emoji.
    print(f'{time()} - {ctx.author} issued forceadd command')
    if ctx.author.id == bot_owner:
        print(f'{time()} - {ctx.author} admin validation complete')
        await add_code(ctx, user_id, tracking_code, carrier_code)
    else:
        print(f'{time()} - {ctx.author} admin validation failed')
        await ctx.message.add_reaction("❌")


# Removes a command from an user list specified by the administrator of the bot:
#   user_id: Discord's user ID for the user you want to remove the code from.
#   name: Package's friendly name
@bot.command()
async def forceremove(ctx, user_id, name=None):
    # Checks if the user who executed the command is the bot administrator. If the user is not the bot administrator,
    # react to the message with a cross emoji.
    print(f'{time()} - {ctx.author} issued forceremove command')
    if ctx.author.id == bot_owner:
        print(f'{time()} - {ctx.author} admin validation complete')
        await remove_code(ctx, user_id, name)
    else:
        print(f'{time()} - {ctx.author} admin validation failed')
        await ctx.message.add_reaction("❌")
