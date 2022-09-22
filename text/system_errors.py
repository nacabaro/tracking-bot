import discord


async def general_error(ctx):
    embed = discord.Embed(title="An error has occurred while trying to write to database.",
                          description="Please contact the bot administrator.")

    await ctx.send(embed=embed)
