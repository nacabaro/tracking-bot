import discord


async def ask_carrier_name(ctx):
    embed = discord.Embed(title="Type in the carrier name")
    await ctx.send(embed=embed)


async def print_carriers_matched(ctx, carriers, search):
    found_carriers = ""

    for carrier in carriers:
        found_carriers += f'{carrier[0]}. {carrier[1]["_name"]}\n'

    embed = discord.Embed(title=f'Carriers that match the search criteria for {search}',
                          description=found_carriers)
    embed.set_footer(text="Type in the number of the carrier you want to use.")

    try:
        msg = await ctx.send(embed=embed)
    except discord.errors.HTTPException:
        await message_too_large(ctx)
        return None
    else:
        return msg


async def not_found_carriers(ctx, search):
    embed = discord.Embed(title=f'No carrier was found for {search}')
    await ctx.send(embed=embed)


async def message_too_large(ctx):
    embed = discord.Embed(title="Your search criteria is too vague.",
                          description="Try searching for something more specific next time.")
    await ctx.send(embed=embed)
