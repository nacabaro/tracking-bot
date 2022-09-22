import discord


async def prompt_automatic_carrier(ctx):
    embed = discord.Embed(title="Would you like to autodetect package carrier?")
    await ctx.send(embed=embed)
