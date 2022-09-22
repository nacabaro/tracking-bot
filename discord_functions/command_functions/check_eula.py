from discord_functions.user_prompt import user_prompt
from objects.database_object import DiscordUsers
from functions.timestamp import time
from text.tracking_messages import *
import discord


async def check_eula(bot, ctx, user_id):
    # Check if the user agreed to the eula
    user_db = DiscordUsers()
    user_db.connect("users_database.db")

    if user_db.check_user(user_id) is False:
        if user_id != ctx.author.id:
            print(f'{time()} - {ctx.author} failed to force remove code because user {user_id} failed to agree eula')
            await failed_eula(ctx)
            return None

        print(f'{time()} - {ctx.author} did not agree to the eula.')
        await agree_eula(bot, ctx)
        user_db.close()
        return None

    else:
        user_db.close()
        return user_id


async def agree_eula(bot, ctx):
    print(f'{time()} - {ctx.author} notifying user about eula')
    embed = discord.Embed(title="Please read carefully before using this bot.",
                          description="Tracking codes are something that you should keep to yourself and never publish "
                                      "online. I came up with this bot in order to be used by a single user, "
                                      "nonetheless, it can be shared with other users. **IF you do NOT trust the person"
                                      " hosting the bot, please refrain from using it. I, the creator of this bot, will"
                                      " not be held responsible for any misuses of the bot or any other wrongdoings by"
                                      " other users. This bot is provided as-is and it is not my responsibility for any"
                                      " damages or information leaks.**")
    await ctx.send(embed=embed)
    embed = discord.Embed(title=f'In order to agree with the disclaimer, please type "I agree".')
    msg = await ctx.send(embed=embed)

    agree_message = await user_prompt(bot, ctx, msg)
    if agree_message is None:
        return

    if agree_message.content == "I agree":
        print(f'{time()} - {ctx.author} user agreed eula')
        user_database = DiscordUsers()
        user_database.connect("users_database.db")
        user_database.add_user(ctx.author.id)
        user_database.commit_changes()
        user_database.close()

        await agree_message.add_reaction("✔️")
        embed = discord.Embed(title=f'Eula agreed. You may now use the bot as normal.')
        await ctx.send(embed=embed)

