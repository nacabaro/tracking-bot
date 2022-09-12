import discord


async def check_code(ctx):
    embed = discord.Embed(title="Checking code...")
    await ctx.send(embed=embed)


async def detect_courier(ctx, courier_name):
    embed = discord.Embed(title=f'Detected courier as {courier_name}...',
                          description=f'If your package courier was not detected correctly, please remove the shipping code and add it again specifying the carrier in the command.')
    await ctx.send(embed=embed)


async def code_added(ctx, code):
    embed = discord.Embed(title=f'Tracking number {code} has been added.')
    msg = await ctx.send(embed=embed)
    return msg


async def name_already_exists(ctx, name):
    embed = discord.Embed(title=f'The package {name} already exists. Please add a different name.')
    await ctx.send(embed=embed)


async def grab_status(ctx):
    embed = discord.Embed(title=f'Grabbing status...')
    await ctx.send(embed=embed)


async def ask_name(ctx):
    embed = discord.Embed(title=f'Next type in the name of the package:')
    msg = await ctx.send(embed=embed)
    return msg


async def missing_name(ctx):
    embed = discord.Embed(title=f'Missing package name.',
                          description=f'Insert the package name when running the command.')
    msg = await ctx.send(embed=embed)


async def missing_code(ctx):
    embed = discord.Embed(title=f'Missing package tracking code.',
                          description=f'Insert the package tracking code when running the command.')
    msg = await ctx.send(embed=embed)


async def code_saved(ctx):
    embed = discord.Embed(title=f'The code has been successfully saved!',
                          description="You'll receive updates next time the package moves.")
    await ctx.send(embed=embed)


async def tracking(ctx):
    embed = discord.Embed(title=f'Tracking package...')
    msg = await ctx.send(embed=embed)
    return msg


async def error_tracking(ctx):
    embed = discord.Embed(title=f'There was an error tracking the package.',
                          description="Make sure the tracking code was added previously using the add command.")
    await ctx.send(embed=embed)


async def removing_code(ctx):
    embed = discord.Embed(title=f'Removing tracking number from the system...')
    await ctx.send(embed=embed)


async def not_exist(ctx):
    embed = discord.Embed(title=f'Error, code does not exist.')
    await ctx.send(embed=embed)


async def code_removed(ctx):
    embed = discord.Embed(title=f'Code removed from the system.')
    await ctx.send(embed=embed)


async def too_soon(ctx):
    embed = discord.Embed(title=f'The package has no updates.')
    await ctx.send(embed=embed)


async def extra_tracking(ctx):
    embed = discord.Embed(title=f'This package supports additional tracking.')
    await ctx.send(embed=embed)


async def insert_arg(ctx):
    embed = discord.Embed(title=f'Please supply an argument.',
                          description="Valid options are modify_name and modify_courier")
    await ctx.send(embed=embed)


async def not_implemented(ctx):
    embed = discord.Embed(title=f'Not implemented yet.')
    await ctx.send(embed=embed)


async def changed_courier_code(ctx, courier_code, code):
    if code == 200:
        embed = discord.Embed(title=f'Changed courier code to {courier_code}.')
    if code == 204:
        embed = discord.Embed(title=f'Changed courier code to {courier_code}.',
                              description=f'Note: The package has no data with this courier. You might want to change couriers to the one before.')
    await ctx.send(embed=embed)
