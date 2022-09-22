import discord


async def code_renamed(ctx, name, new_name):
    embed = discord.Embed(title="Package name was renamed correctly.",
                          description=f'Package {name} will be now referred as {new_name}')

    await ctx.send(embed=embed)
