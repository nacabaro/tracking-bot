from objects.tracking_object import TrackingMore
from objects.database_object import ShippingCodesDB
from functions.discord_ipc import Routes
from configs.config import tm_secret
from text.tracking_messages import *
from discord.ext import commands
from functions.debug import time
import discord
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='¡', activity=discord.Game(name="with your packages."), intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.add_cog(Routes(bot))
    print("IPC Ready")


@bot.command()
async def add(ctx, code=None, carrier=None):
    print(f'{time()} - {ctx.author} got add command')
    if code is None:
        print(f'{time()} - {ctx.author} missing tracking code (ln 25)')
        await missing_code(ctx)
        return

    await check_code(ctx)

    tm_worker = TrackingMore()
    tm_worker.set_secret(tm_secret)

    if carrier is None:
        print(f'{time()} - {ctx.author} courier code was never passed, autodetecting. (ln 37)')
    else:
        print(f'{time()} - {ctx.author} courier code has been passed, forcing to {carrier}. (ln 37)')

    print(f'{time()} - {ctx.author} adding shipping code to tracktry api.')
    result = tm_worker.add_shipping_code(code, carrier)

    try:
        code = result["data"]["accepted"][0]["number"]
    except IndexError:
        await not_exist(ctx)
        print(f'{time()} - {ctx.author} got error adding code (does not exist?) (ln 66)')
        return

    carrier = result["data"]["accepted"][0]["carrier"]
    await code_added(ctx, code)

    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")

    while True:
        msg = await ask_name(ctx)
        try:
            name = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
            name = name.content
            print(f'{time()} - {ctx.author} sent package name (ln 68)')
        except asyncio.TimeoutError:
            await msg.add_reaction("❌")
            tm_worker.remove_shipping_code(code, carrier)
            print(f'{time()} - {ctx.author} timeout getting name (ln 72)')
            return

        if db_worker.get_code(name, ctx.author.id) != -1:
            await name_already_exists(ctx, name)
            print(f'{time()} - {ctx.author} the name inserted already exists (ln 89')
        else:
            print(f'{time()} - {ctx.author} user inserted valid name (ln 91)')
            break

    db_worker.add_shipping_code(ctx.author.id, code, carrier, name, None, None)
    db_worker.commit_changes()
    db_worker.close()

    await code_saved(ctx)
    print(f'{time()} - {ctx.author} added code successfully (ln 82)')


@bot.command()
async def track(ctx, name=None):
    print(f'{time()} - {ctx.author} got track command')
    if name is None:
        print(f'{time()} - {ctx.author} missing name parameter (ln 90)')
        await missing_name(ctx)
        return

    msg = await tracking(ctx)

    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")
    code = db_worker.get_code(name, ctx.author.id)
    if code == -1:
        print(f'{time()} - {ctx.author} unverified user or incorrect name (ln 96)')
        await error_tracking(ctx)
        db_worker.close()
        return

    courier_code = db_worker.get_courier_code(name)

    tm_worker = TrackingMore()
    tm_worker.set_secret(tm_secret)
    result = tm_worker.get_shipping_status(code, courier_code)

    try:
        code = result["data"]["accepted"][0]["number"]
    except IndexError:
        await error_tracking(ctx)
        print(f'{time()} - {ctx.author} got error trying to ask for manual push (ln 105)')
        db_worker.close()
        return

    await msg.add_reaction("✔️")

    db_worker.close()
    print(f'{time()} - {ctx.author} finished tracking code (ln 136)')


@bot.command()
async def remove(ctx, name=None):
    print(f'{time()} - {ctx.author} got remove command')
    if name is None:
        print(f'{time()} - {ctx.author} missing name parameter (ln 153)')
        return

    await removing_code(ctx)

    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")
    code = db_worker.get_code(name, ctx.author.id)

    if code == -1:
        print(f'{time()} - {ctx.author} code does not exist on local database (ln 149)')
        await not_exist(ctx)
        db_worker.close()
        return

    courier_code = db_worker.get_courier_code(name)

    tm_worker = TrackingMore()
    tm_worker.set_secret(tm_secret)
    result = tm_worker.remove_shipping_code(code, courier_code)

    try:
        code = result["data"]["accepted"][0]["number"]
    except IndexError:
        await not_exist(ctx)
        print(f'{time()} - {ctx.author} got error removing code (ln 105)')
        db_worker.close()
        return
    else:
        print("Does this work?")
        db_worker.remove_shipping_code(name)
        db_worker.commit_changes()
        await code_removed(ctx)
        db_worker.close()
        print(f'{time()} - {ctx.author} code removed')


@bot.command()
async def list(ctx):
    print(f'{time()} - {ctx.author} got list command')

    db_browser = ShippingCodesDB()
    db_browser.connect("shipping_codes.db")
    codes = db_browser.get_all_codes(ctx.author.id)

    code_list = "Code - Name\n"

    for code in codes:
        code_list += f'{code[0]} - {code[1]}\n'

    embed = discord.Embed(title=f'Codes currently registered to {ctx.author}',
                          description=f'''{code_list}''')

    await ctx.send(embed=embed)
    db_browser.close()
