from functions.timestamp import time
import asyncio


async def user_prompt(bot, ctx, msg):
    print(f'{time()} -- {ctx.author} user prompt raised')
    try:
        agree_message = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
        return agree_message
    except asyncio.TimeoutError:
        await msg.add_reaction("❌")
        return None
