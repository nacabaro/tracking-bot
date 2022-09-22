from discord_functions.user_prompt import user_prompt
from objects.database_object import ShippingCodesDB
from text.tracking_messages import ask_name, name_already_exists
from text.rename_messages import code_renamed
from text.system_errors import general_error


async def rename_code(bot, ctx, name):
    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")

    msg = await ask_name(ctx)
    while True:
        new_name = await user_prompt(bot, ctx, msg)
        if db_worker.get_code(new_name.content, ctx.author.id) != -1:
            await name_already_exists(ctx, new_name.content)
        else:
            await msg.add_reaction("✔")
            break

    if db_worker.rename_code(name, new_name.content, ctx.author):
        await code_renamed(ctx, name, new_name.content)
    else:
        await general_error(ctx)
