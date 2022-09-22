from objects.database_object import ShippingCodesDB
from discord_functions.command_functions.check_eula import check_eula
from functions.timestamp import time
import discord


async def list_codes(ctx, bot):
    # Check if user agreed the eula
    if await check_eula(bot, ctx, ctx.author.id) is None:
        return

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
