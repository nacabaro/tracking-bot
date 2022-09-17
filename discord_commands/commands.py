from objects.database_object import ShippingCodesDB, DiscordUsers
from objects.tracking_object import TrackingMore
from configs.config import tm_secret, bot_owner
from functions.discord_ipc import Routes
from text.tracking_messages import *
from discord.ext import commands
from functions.debug import time
import asyncio
import discord


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='¡', activity=discord.Game(name="with your packages."), intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.add_cog(Routes(bot))
    print("IPC Ready")


# Adds tracking code to system for user invoking the command:
#   tracking_code: Package tracking code
#   carrier_code: Package carrier code
@bot.command()
async def add(ctx, tracking_code=None, carrier_code=None):
    await add_code(ctx, ctx.author.id, tracking_code, carrier_code)


# Removes code from system for user invoking the command:
#   name: Package's friendly name
@bot.command()
async def remove(ctx, name=None):
    await remove_code(ctx, ctx.author.id, name)


# Asks API to track package:
#   name: Package's friendly name
@bot.command()
async def track(ctx, name=None):
    # Check if the user agreed to the eula
    user_db = DiscordUsers()
    user_db.connect("users_database.db")
    if user_db.check_user(ctx.author.id) is False:
        await agree_eula(ctx)
        user_db.close()
        return
    else:
        user_db.close()

    print(f'{time()} - {ctx.author} got track command')

    # Checks if the user passed the name of the package, otherwise inform the user.
    if name is None:
        print(f'{time()} - {ctx.author} missing name parameter (ln 90)')
        await missing_name(ctx)
        return

    # Saves tracking message object to a variable so that it can be reacted afterwards if any issue happens.
    msg = await tracking(ctx)

    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")

    # Obtains the tracking code from the database
    tracking_code = db_worker.get_code(name, ctx.author.id)

    # Informs the user if the name introduced is wrong or does not exist in the database.
    if tracking_code == -1:
        print(f'{time()} - {ctx.author} unverified user or incorrect name (ln 96)')
        await error_tracking(ctx)
        db_worker.close()
        return

    carrier_code = db_worker.get_carrier_code(ctx.author.id, name)

    # Loads API secret and asks for manual PUSH notification.
    tm_worker = TrackingMore()
    tm_worker.set_secret(tm_secret)
    result = tm_worker.get_shipping_status(tracking_code, carrier_code)

    try:
        # Second security check: checks if the API has the code. If it does not, inform the user.
        tracking_code = result["data"]["accepted"][0]["number"]
    except IndexError:
        await error_tracking(ctx)
        print(f'{time()} - {ctx.author} got error trying to ask for manual push (ln 105)')
        db_worker.close()
        return

    # Reacts to the message to inform the user that the manual PUSH succeeded, and that a notification will arrive
    # shortly.
    await msg.add_reaction("✔️")

    db_worker.close()
    print(f'{time()} - {ctx.author} finished tracking code (ln 136)')


# Lists all tracking codes for the user executing the command:
#   Takes no arguments.
@bot.command()
async def list(ctx):
    # Check if user agreed the eula
    user_db = DiscordUsers()
    user_db.connect("users_database.db")
    if user_db.check_user(ctx.author.id) is False:
        await agree_eula(ctx)
        user_db.close()
        return
    else:
        user_db.close()

    print(f'{time()} - {ctx.author} got list command')

    db_browser = ShippingCodesDB()
    db_browser.connect("shipping_codes.db")
    codes = db_browser.get_all_codes(ctx.author.id)

    code_list = ""

    for shipping_code in codes:
        code_list += f'{shipping_code[0]}\n'

    embed = discord.Embed(title=f'Codes currently registered to {ctx.author}',
                          description=f'''{code_list}''')

    await ctx.send(embed=embed)
    db_browser.close()


# Shows code for a specific package, useful for copying/pasting on mobile:
#   name: Package's friendly name
@bot.command()
async def checkcode(ctx, name):
    # Check if user agreed the eula
    user_db = DiscordUsers()
    user_db.connect("users_database.db")
    if user_db.check_user(ctx.author.id) is False:
        await agree_eula(ctx)
        user_db.close()
        return
    else:
        user_db.close()

    # Connect to database and obtain the shipping code
    db_browser = ShippingCodesDB()
    db_browser.connect("shipping_codes.db")
    code = db_browser.get_code(name, ctx.author.id)
    if code == -1:
        await not_exist(ctx)
        return

    # Send shipping code to user
    await ctx.send(code)

    # Close database connection and do cleanup
    db_browser.close()


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


# -- Chat functions ----
async def agree_eula(ctx):
    print(f'{time()} - {ctx.author} notifying user about eula')
    embed = discord.Embed(title="Please read carefully before using this bot.",
                          description="Tracking codes are something that you should keep to yourself and never publish "
                                      "online. I came up with this bot in order to be used by a single user, "
                                      "nonetheless, it can be shared with other users. **IF you do NOT trust the person"
                                      " hosting the bot, please refrain from using it. I, the creator of this bot, will"
                                      " not be held responsible for any misuses of the bot or any other wrongdoings by"
                                      " other users. This bot is provided as-is and it is not my responsibility for any"
                                      " damages or information leaks.**")
    await ctx.send(embed=embed)
    embed = discord.Embed(title=f'In order to agree with the disclaimer, please type "I agree".')
    msg = await ctx.send(embed=embed)

    try:
        print(f'{time()} - {ctx.author} asking user to agree eula')
        agree_message = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)
        agree = agree_message.content
    except asyncio.TimeoutError:
        print(f'{time()} - {ctx.author} user failed to agree eula')
        await msg.add_reaction("❌")
        return

    if agree == "I agree":
        print(f'{time()} - {ctx.author} user agreed eula')
        user_database = DiscordUsers()
        user_database.connect("users_database.db")
        user_database.add_user(ctx.author.id)
        user_database.commit_changes()
        user_database.close()

        await agree_message.add_reaction("✔️")
        embed = discord.Embed(title=f'Eula agreed. You may now use the bot as normal.')
        await ctx.send(embed=embed)
    else:
        await agree_message.add_reaction("❌")


async def remove_code(ctx, user_id, name=None):
    # Check if the user agreed to the eula
    user_db = DiscordUsers()
    user_db.connect("users_database.db")
    if user_db.check_user(user_id) is False:
        if user_id != ctx.author.id:
            print(f'{time()} - {ctx.author} failed to force remove code because user {user_id} failed to agree eula')
            await failed_eula(ctx)
            return
        print(f'{time()} - {ctx.author} did not agree to the eula.')
        await agree_eula(ctx)
        user_db.close()
        return

    user_db.close()

    print(f'{time()} - {ctx.author} got remove command')

    # Check if the name got passed during the command execution
    if name is None:
        print(f'{time()} - {ctx.author} missing name parameter (ln 247)')
        await missing_name(ctx)
        return

    # Message function
    await removing_code(ctx)

    # Load database and get the shipping code
    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")
    tracking_code = db_worker.get_code(name, user_id)

    # Check if the code exists in the database
    if tracking_code == -1:
        print(f'{time()} - {ctx.author} code does not exist on local database (ln 261)')
        # Message function
        await not_exist(ctx)
        db_worker.close()
        return

    # Obtain the carrier code
    # NOTE: Fix the name of the variable and the object
    carrier_code = db_worker.get_carrier_code(user_id, name)

    # Check if the code exists multiple times in the database, if it does, to only delete it for that specific user
    # instead of deleting it from the API. If only one user has that code, to delete it from the API to stop tracking
    # updates
    if len(db_worker.get_names(tracking_code, carrier_code)) > 1:
        pass
    else:
        print(f'{time()} - {ctx.author} removing the code from the api (ln 277)')
        tm_worker = TrackingMore()
        tm_worker.set_secret(tm_secret)
        result = tm_worker.remove_shipping_code(tracking_code, carrier_code)

        try:
            # Second security check: checks if the code exists in the API, if it does not, send an error message to the
            # user, close the database and clean up.
            tracking_code = result["data"]["accepted"][0]["number"]
        except IndexError:
            print(f'{time()} - {ctx.author} got error removing code (ln 287)')
            await not_exist(ctx)

    # Once we are sure the code got removed in the API, remove it from the local database, inform the user, commit the
    # changes and then cleanup.
    db_worker.remove_shipping_code(user_id, name)
    print(f'{time()} - {ctx.author} removed code from the database (ln 293)')
    db_worker.commit_changes()
    db_worker.close()

    await code_removed(ctx)

    print(f'{time()} - {ctx.author} code removed')

    # In the case the code was force removed by the administrator of the bot, we inform the user that the administrator
    # has performed an action to a code they had saved.
    if user_id != ctx.author.id:
        print(f'{time()} - {ctx.author} notifying user {user_id} about code removal. (ln 304)')
        user_dm = await bot.fetch_user(user_id)
        await force_removed_code(user_dm, name)


async def add_code(ctx, user_id, tracking_code=None, carrier_code=None):
    # Check if the user agreed to the eula
    user_db = DiscordUsers()
    user_db.connect("users_database.db")
    if user_db.check_user(user_id) is False:
        if user_id != ctx.author.id:
            print(f'{time()} - {ctx.author} failed to force remove code because user {user_id} failed to agree eula')
            await failed_eula(ctx)
            return
        print(f'{time()} - {ctx.author} did not agree to the eula.')
        await agree_eula(ctx)
        user_db.close()
        return
    else:
        user_db.close()

    print(f'{time()} - {ctx.author} got add command')

    # Check if the code argument got passed through the command. Inform the user if it was not.
    if tracking_code is None:
        print(f'{time()} - {ctx.author} missing tracking code (ln 25)')
        await missing_code(ctx)
        return

    # Inform the user the code is being checked.
    await check_code(ctx)

    # Check if the carrier code was previously added to the bot's database, this is to avoid getting rate limited on the
    # API and save quota.
    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")

    # Check if the carrier code was passed by the user. If it was, force the tracking to the carrier code passed, else
    # autodetect the carrier code using the API methods.
    if carrier_code is None:
        print(f'{time()} - {ctx.author} courier code was never passed, auto detecting. (ln 37)')
        automatic_detect = "automatic"
    else:
        print(f'{time()} - {ctx.author} courier code has been passed, forcing to {carrier_code}. (ln 37)')
        automatic_detect = "manual"

    tm_worker = TrackingMore()
    tm_worker.set_secret(tm_secret)

    # Read the database and check if the code already had carrier data attached to it.
    carrier_data = db_worker.get_carrier_data(tracking_code, carrier_code)
    if carrier_data is None:
        # If it does not have carrier data, proceed to add the code to the API.
        # Add shipping code to the API
        print(f'{time()} - {ctx.author} adding shipping code to api.')

        result = tm_worker.add_shipping_code(tracking_code, carrier_code)

        # Check if code got accepted into the API, if it was not, inform the user.
        try:
            tracking_code = result["data"]["accepted"][0]["number"]
            carrier_code = result["data"]["accepted"][0]["carrier"]

        except IndexError:
            await not_exist(ctx)
            print(f'{time()} - {ctx.author} got error adding code (does not exist?) (ln 66)')
            return
    else:
        print(f'{time()} - {ctx.author} code already exists on the database, ignoring api')
        carrier_code = carrier_data[0]

    # Obtain the carrier code again in the case it was never passed since the beginning.
    await code_added(ctx, tracking_code)

    # Ask the user to insert a friendly name for the package. If he does insert a name that already exists, ask again
    # until a valid name is provided. If the user does not insert a name in the span of 60 seconds, the code gets
    # removed from the API.
    # NOTE: make it check if the code exists from another user before deleting.
    while True:
        print(f'{time()} - {ctx.author} asking name for package')
        msg = await ask_name(ctx)
        try:
            name = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
            name = name.content
            print(f'{time()} - {ctx.author} sent package name (ln 68)')
        except asyncio.TimeoutError:
            await msg.add_reaction("❌")
            tm_worker.remove_shipping_code(tracking_code, carrier_code)
            print(f'{time()} - {ctx.author} timeout getting name (ln 72)')
            return

        if db_worker.get_code(name, user_id) != -1:
            await name_already_exists(ctx, name)
            print(f'{time()} - {ctx.author} the name inserted already exists (ln 89')
        else:
            print(f'{time()} - {ctx.author} user inserted valid name (ln 91)')
            break

    print(f'{time()} - {ctx.author} adding code to the database')
    db_worker.add_shipping_code(user_id, tracking_code, carrier_code, name, automatic_detect)
    db_worker.commit_changes()
    db_worker.close()

    await code_saved(ctx)
    if user_id != ctx.author.id:
        print(f'{time()} - {ctx.author} notifying user {user_id} about new code')
        user_dm = await bot.fetch_user(user_id)
        await force_added_code(user_dm, name)

    print(f'{time()} - {ctx.author} added code successfully (ln 82)')
