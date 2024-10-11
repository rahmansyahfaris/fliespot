CHANGES:
Environment variables and config overhaul, now using yaml instead of .env
Now using shared dictionary with manager that contains the events centralized in main
All events are now centralized in main
Arguments are now more wrapped using dictionaries
Other changes and future plans that I don't remember
Events will be deleted in the future, we are going to use queue to differentiate states and phases

somethings need to be added before properly using the code (because it is gitignored)

first file is config/telegram_info.yaml, it contains:

bot_username: <@your_telegram_bot_name>
bot_token: <your_telegram_bot_token>
username: <your_telegram_username_this_is_still_non_functional>

second file is config/uri.yaml, it contains:

uri: <your_crazyflie_drone_uri>