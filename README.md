# tracking-bot
A Discord bot that is designed to send you tracking updates of packages you order online.

## How does it work?
This bot is designed to work with 17Track API. In order to use it, please refer to creating an API key in 17Track API website. https://api.17track.net/en. This bot works with 17Track ability to send PUSH notifications to a webserver when a package gets a tracking update. The speed of the tracking updates is determined by 17Track, as this bot will send a DM to the user once a tracking update is received by 17Track's PUSH service.

## How to set up?
To set up this bot, you must first a 17Track API key. This can be done for free using the website linked above. You will also need a Discord Bot token. To create it refer to Discord Developer Portal: https://discord.com/developers/applications. After getting both API Key and bot token, go to config.py file located in configs/config.py, being ``tm_secret="<your-17Track-API-key>"`` and ``discord_token="<your-Discord-Bot-Token>"``.

Once that is taken care of, open the port 8080 on your network, so that it's accessible to the outside. After head to https://api.17track.net/en/admin/settings and under webhook settings, set the URL as ``http://<your_public_ip>:8080/apitrack/webhook`` and the version parameter to V 2.0.
 
After that, the bot is ready to launch. First, launch ``main.py`` and once the terminal says "IPC Ready", launch ``server.py``.

## Features
The bot features several commands:
* ``¡add <tracking-code> <carrier-code: optional>``: this command will add a tracking code to the bot database, which will also add it into 17Track systems. Carrier code can be manually specified in the case 17Track fails to identify the carrier or you want to manually specify a carrier code. These tracking code numbers can be found here: https://res.17track.net/asset/carrier/info/apicarrier.all.json. After entering the code, the bot will check if it's a valid code and then prompt you to add a name to it in order to identify it.
* ``¡track <package-name>``: this command will ask 17Track API for any updates in the tracking of the package and will always send the latest update available in 17Track website.
* ``¡remove <package-name>``: this command removes the code attached to the package name from the Discord bot and the 17Track database.
* ``¡list``: this command lists all the codes the bot is taking into account at the current time.

## Disclaimer
Tracking codes are something that you should keep to yourself and never publish online. I came up with this bot in order to be used by a single user, nonetheless, it can be shared with other users. **IF you do NOT trust the person hosting the bot, please refrain from using it. I, the creator of this bot, will not be held responsible for any misuses of the bot or any other wrongdoings by other users. This bot is provided as-is and it is not my responsibility for any damages or information leaks.**

## Future features
* Automatically run the webserver alongside the main bot so that both don't need to be run separately.
* Change the carrier code with some other way to read the original carrier.
* Port to Telegram API (in case that is your thing instead of Discord).

## Credits
* discord.py maintainers.
* https://github.com/MiroslavRosenov/better-ipc Better-IPC project that allows intercommunication in between the web server and discord.py
* https://pgjones.gitlab.io/quart/ Quart web server for receiving PUSH notifications from 17Track
