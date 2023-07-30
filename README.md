# MathBot [![Discord server](https://img.shields.io/discord/1119928044811976744?label=discord&logo=discord)](https://discord.gg/c3TxDj6DYa) [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

A fun discord bot made by @mathman2028. [Discord Server](https://discord.gg/c3TxDj6DYa) [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=1119928094418018354&permissions=3136&scope=bot)

## Setup

1. Clone the repository
2. Install discord.py
3. Create a system environment variable called "mathbot_token" to store your token, put your bot's token in it
4. Create a db.json file, just put `{}` there
5. Run the bot

## Customization

### New symbols

To add new symbols, simply create a recipe for them in the `recipes` dictionary in `symbols.py`. If you would like to have a special way of obtaining this symbol, add it to the `special_symbols` set.

> **Note**
>
> All symbols must be title cased.

### New achievements

If you want to add new achievements, first add your achievement to `achs.json`. The format there should be pretty self-explanatory.
Then, in order to grant the achievement to someone, call `Achievements.give_ach(guild, member, category, ach, messageable)`. You can look at examples in the code if any of these parameters are unclear.
