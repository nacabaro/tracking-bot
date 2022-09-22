from text.carrier_search_messages import *
from discord_functions.user_prompt import user_prompt
import json


async def carrier_search(bot, ctx):
    msg = await ask_carrier_name(ctx)
    user_input = await user_prompt(bot, ctx, msg)

    if user_input is None:
        return

    with open("carrier_data.json") as carriers_db:
        carrier_data = json.load(carriers_db)

    carriers_matched = []
    index = 1

    for carrier in carrier_data:
        if user_input.content.lower() in carrier["_name"].lower():
            carriers_matched.append([index, carrier])
            index += 1

    if len(carriers_matched) < 1:
        await not_found_carriers(ctx, user_input.content)
        return

    msg = await print_carriers_matched(ctx, carriers_matched, user_input.content)
    if msg is None:
        return

    user_input = await user_prompt(bot, ctx, msg)
    if user_input is None:
        return

    return carriers_matched[int(user_input.content) - 1][1]
