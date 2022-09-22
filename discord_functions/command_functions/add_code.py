from objects.database_object import ShippingCodesDB
from discord_functions.user_prompt import user_prompt
from discord_functions.command_functions.check_eula import check_eula
from objects.tracking_object import TrackingMore
from configs.config import tm_secret
from text.tracking_messages import *
from text.add_code_messages import *
from functions.timestamp import time
from discord_functions.carrier_search import carrier_search


async def add_code(bot, ctx, user_id, tracking_code=None, carrier_code=None):
    if await check_eula(bot, ctx, user_id) is None:
        return

    print(f'{time()} - {ctx.author} got add command')

    # Check if the code argument got past through the command. Inform the user if it was not.
    if tracking_code is None:
        print(f'{time()} - {ctx.author} missing tracking code (ln 25)')
        await missing_code(ctx)
        return

    # Inform the user the code is being checked.
    await check_code(ctx)

    # Check if the carrier code was previously added to the bot database, this is to avoid getting rate limited on the
    # API and save quota.
    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")

    # Check if the carrier code was passed by the user. If it was, force the tracking to the carrier code passed, else
    # autodetect the carrier code using the API methods.

    msg = await prompt_automatic_carrier(ctx)
    response = await user_prompt(bot, ctx, msg)
    if response.content is None:
        return

    if "y" in response.content.lower():
        print(f'{time()} - {ctx.author} courier code was never passed, auto detecting. (ln 37)')
        automatic_detect = "automatic"
    else:
        print(f'{time()} - {ctx.author} courier code has been passed, forcing to {carrier_code}. (ln 37)')
        automatic_detect = "manual"

        carrier_info = await carrier_search(bot, ctx)
        carrier_code = carrier_info["key"]
        print(carrier_code)

    tm_worker = TrackingMore()
    tm_worker.set_secret(tm_secret)

    # Read the database and check if the code already had carrier data attached to it.
    carrier_data = db_worker.get_carrier_data(tracking_code, carrier_code)
    if carrier_data is None:
        # If it does not have carrier data, proceed to add the code to the API.
        # Add shipping code to the API
        print(f'{time()} - {ctx.author} adding shipping code to api.')

        result = tm_worker.add_shipping_code(tracking_code, carrier_code)

        # Check if code got accepted into the API, if it was not, inform the user.
        try:
            tracking_code = result["data"]["accepted"][0]["number"]
            carrier_code = result["data"]["accepted"][0]["carrier"]

        except IndexError:
            await not_exist(ctx)
            print(f'{time()} - {ctx.author} got error adding code (does not exist?) (ln 66)')
            return
    else:
        print(f'{time()} - {ctx.author} code already exists on the database, ignoring api')
        carrier_code = carrier_data[0]

    # Obtain the carrier code again in the case it was never passed since the beginning.
    await code_added(ctx, tracking_code)

    # Ask the user to insert a friendly name for the package. If he does insert a name that already exists, ask again
    # until a valid name is provided. If the user does not insert a name in the span of 60 seconds, the code gets
    # removed from the API.
    # NOTE: make it check if the code exists from another user before deleting.
    while True:
        print(f'{time()} - {ctx.author} asking name for package')
        msg = await ask_name(ctx)
        name = await user_prompt(bot, ctx, msg)
        if name is None:
            tm_worker.remove_shipping_code(tracking_code, carrier_code)


        if db_worker.get_code(name.content, user_id) != -1:
            await name_already_exists(ctx, name.content)
            print(f'{time()} - {ctx.author} the name inserted already exists (ln 89')
        else:
            print(f'{time()} - {ctx.author} user inserted valid name (ln 91)')
            break

    print(f'{time()} - {ctx.author} adding code to the database')
    db_worker.add_shipping_code(user_id, tracking_code, carrier_code, name.content, automatic_detect)
    db_worker.commit_changes()
    db_worker.close()

    await code_saved(ctx)
    if user_id != ctx.author.id:
        print(f'{time()} - {ctx.author} notifying user {user_id} about new code')
        user_dm = await bot.fetch_user(user_id)
        await force_added_code(user_dm, name.content)

    print(f'{time()} - {ctx.author} added code successfully (ln 82)')
