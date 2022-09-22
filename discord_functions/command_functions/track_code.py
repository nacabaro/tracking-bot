from functions.timestamp import time
from discord_functions.command_functions.check_eula import check_eula
from text.tracking_messages import *
from objects.database_object import ShippingCodesDB
from objects.tracking_object import TrackingMore
from configs.config import tm_secret


async def track_code(bot, ctx, name):
    if await check_eula(bot, ctx, ctx.author.id) is None:
        return

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