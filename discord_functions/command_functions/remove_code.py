from objects.database_object import ShippingCodesDB
from objects.tracking_object import TrackingMore
from discord_functions.command_functions.check_eula import check_eula
from configs.config import tm_secret
from text.tracking_messages import *
from functions.timestamp import time


async def remove_code(bot, ctx, user_id, name=None):
    # Check if the user agreed to the eula
    if await check_eula(bot, ctx, user_id) is None:
        print(f'checking eula')
        return

    print(f'{time()} - {ctx.author} got remove command')

    # Check if the name got passed during the command execution
    if name is None:
        print(f'{time()} - {ctx.author} missing name parameter (ln 247)')
        await missing_name(ctx)
        return

    # Message function
    await removing_code(ctx)

    # Load database and get the shipping code
    db_worker = ShippingCodesDB()
    db_worker.connect("shipping_codes.db")
    tracking_code = db_worker.get_code(name, user_id)

    # Check if the code exists in the database
    if tracking_code == -1:
        print(f'{time()} - {ctx.author} code does not exist on local database (ln 261)')
        # Message function
        await not_exist(ctx)
        db_worker.close()
        return

    # Obtain the carrier code
    # NOTE: Fix the name of the variable and the object
    carrier_code = db_worker.get_carrier_code(user_id, name)

    # Check if the code exists multiple times in the database, if it does, to only delete it for that specific user
    # instead of deleting it from the API. If only one user has that code, to delete it from the API to stop tracking
    # updates
    if len(db_worker.get_names(tracking_code, carrier_code)) > 1:
        pass
    else:
        print(f'{time()} - {ctx.author} removing the code from the api (ln 277)')
        tm_worker = TrackingMore()
        tm_worker.set_secret(tm_secret)
        result = tm_worker.remove_shipping_code(tracking_code, carrier_code)

        try:
            # Second security check: checks if the code exists in the API, if it does not, send an error message to the
            # user, close the database and clean up.
            tracking_code = result["data"]["accepted"][0]["number"]
        except IndexError:
            print(f'{time()} - {ctx.author} got error removing code (ln 287)')
            await not_exist(ctx)

    # Once we are sure the code got removed in the API, remove it from the local database, inform the user, commit the
    # changes and then cleanup.
    db_worker.remove_shipping_code(user_id, name)
    print(f'{time()} - {ctx.author} removed code from the database (ln 293)')
    db_worker.commit_changes()
    db_worker.close()

    await code_removed(ctx)

    print(f'{time()} - {ctx.author} code removed')

    # In the case the code was force removed by the administrator of the bot, we inform the user that the administrator
    # has performed an action to a code they had saved.
    if user_id != ctx.author.id:
        print(f'{time()} - {ctx.author} notifying user {user_id} about code removal. (ln 304)')
        user_dm = await bot.fetch_user(user_id)
        await force_removed_code(user_dm, name)


