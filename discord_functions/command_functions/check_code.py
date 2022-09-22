from discord_functions.command_functions.check_eula import check_eula
from objects.database_object import ShippingCodesDB
from text.tracking_messages import *


async def check_code(bot, ctx, name):
    # Check if user agreed the eula
    if await check_eula(bot, ctx, ctx.author.id) is None:
        return

    # Connect to database and obtain the shipping code
    db_browser = ShippingCodesDB()
    db_browser.connect("shipping_codes.db")
    code = db_browser.get_code(name, ctx.author.id)
    if code is None:
        await not_exist(ctx)
        return

    # Send shipping code to user
    await ctx.send(code)

    # Close database connection and do cleanup
    db_browser.close()
