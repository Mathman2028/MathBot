import discord
from discord.ext import commands
from discord import app_commands, ui
import os
import random
import asyncio
import typing
import re
import chess
from symbols import DUNGEON_RESULTS
import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="m!",
    intents=intents,
    activity=discord.Game(name="Calculator for Nintendo Switch"),
    application_id=1119928094418018354,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False),
)

TOKEN = os.environ["mathbot_token"]


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.tree.sync()


@bot.hybrid_command()
async def echo(ctx: commands.Context, *, text: str):
    """Repeats after you"""
    await ctx.send(text)


@bot.hybrid_command()
async def calculate(
    ctx: commands.Context,
    num1: float,
    op: typing.Literal["+", "-", "\u00d7", "÷", "^"],
    num2: float,
):
    """Does simple calculations"""
    if op == "+":
        await ctx.send(num1 + num2)
    elif op == "-":
        await ctx.send(num1 - num2)
    elif op == "\u00d7":
        await ctx.send(num1 * num2)
    elif op == "÷":
        if num2 == 0:
            await ctx.send("dont divide by 0 idiot")
            return
        await ctx.send(num1 / num2)
    elif op == "^":
        await ctx.send(num1 ** num2)
    else:
        await ctx.send("Invalid operation!")

@bot.hybrid_command()
async def complexcalculate(
    ctx: commands.Context,
    num1real: float,
    num1imag: float,
    op: typing.Literal["+", "-", "*", "/", "^"],
    num2real: float,
    num2imag: float
):
    """Does simple calculations...but complex."""
    num1 = num1real + num1imag * 1j
    num2 = num2real + num2imag * 1j
    if op == "+":
        await ctx.send(num1 + num2)
    elif op == "-":
        await ctx.send(num1 - num2)
    elif op == "\u00d7":
        await ctx.send(num1 * num2)
    elif op == "÷":
        if num2 == 0:
            await ctx.send("dont divide by 0 idiot")
            return
        await ctx.send(num1 / num2)
    elif op == "^":
        await ctx.send(num1 ** num2)
    else:
        await ctx.send("Invalid operation!")

@bot.hybrid_command()
async def stupidcalculator(
    ctx: commands.Context,
    num1: int,
    op: typing.Literal["+", "-", "*", "/", "^"],
    num2: int,
):
    """Idiot calculator"""
    if num1 < 0 or num2 < 0:
        await ctx.send("huh?")
        return
    if op in ("+", "plus", "add"):
        if num1 == num2 == 1:
            await ctx.send("window")
        elif num1 == num2 == 2:
            await ctx.send("Fish")
        elif num1 == num2 == 3:
            await ctx.send("8")
        elif num1 == 9 and num2 == 10:
            await ctx.send("21")
        else:
            await ctx.send(str(num1) + str(num2))
    elif op in ("-", "minus", "subtract"):
        if num2 > num1:
            await ctx.send("hey you can't do that")
        else:
            if random.randint(0, 1) == 1:
                await ctx.send(num1)
            else:
                await ctx.send(num2)
    elif op in ("*", "x", "\u00d7", "times", "multiply"):
        await ctx.send(num1 + num2)
    elif op in ("/", "÷", "over", "divide"):
        await ctx.send(num1 // num2)
    elif op in ("^", "**", "exponent"):
        await ctx.send(str(num1) + str(num2))
    else:
        await ctx.send("Invalid operation!")


@bot.listen("on_message")
async def easter_eggs(message: discord.Message):
    achievements = bot.get_cog("Achievements")
    if message.author == bot.user:
        return
    if "cellua bad" in message.content.lower():
        await message.reply("cellua good")
    if "new cells cause cancer" in message.content.lower():
        await message.reply("new cells cure cancer")
    if "cellua good" in message.content.lower():
        await message.add_reaction("👍")
    if "who asked" in message.content.lower():
        await message.reply("i asked")
    if "google en passant" in message.content.lower():
        await message.reply("holy hell")
        await achievements.give_ach(
            message.guild,
            message.author,
            "Random",
            "enpassant",
            message.channel,
        )
    if "xnopyt" in message.content.lower():
        await message.reply(
            'If you accept the definition of a word as some letters surrounded by a gap, then "xnopyt", "aaaaaaajjjjjjjjj", and "hrrkrkrkrwpfrbbrbrbrlablblblblblblwhitoo\'ap" are all words, despite being pretty much meaningless.'
        )
    if "chess battle advanced" in message.content.lower():
        await message.reply("https://streamable.com/1z7eh")
    if message.content.lower() == "ratio":
        if message.reference is not None and isinstance(
            message.reference.resolved, discord.Message
        ):  # other options are None or DeletedReferencedMessage
            await message.add_reaction("⬆️")
            await message.reference.resolved.add_reaction("⬆️")
            if message.author == message.reference.resolved.author:
                await achievements.give_ach(
                    message.guild,
                    message.author,
                    "Random",
                    "friendlyfire",
                    message.channel,
                )
    if re.search("\d+\.\d+\.\d+\.\d+", message.content):
        await message.reply(
            f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        )


@bot.tree.context_menu(name="Quote")
@app_commands.guild_only()
async def msg_quote(interaction: discord.Interaction, message: discord.Message):
    """Quote someone and have it be preserved in the quote command for the rest of time"""
    database = bot.get_cog("Database")
    if message.author == interaction.user:
        await interaction.response.send_message("You can't quote yourself")
        return
    guild_db = database.db[str(interaction.guild.id)]
    if "quotes" not in guild_db.keys():
        guild_db["quotes"] = []
    quotes: list = guild_db["quotes"]
    if {"author": message.author.name, "content": message.content, "time": int(message.created_at.timestamp())} not in quotes:
        if {"author": message.author.name, "content": message.content} in quotes:
            quotes.remove({"author": message.author.name, "content": message.content})
        quotes.append({"author": message.author.name, "content": message.content, "time": int(message.created_at.timestamp())})
    await interaction.response.send_message(
        embed=discord.Embed(
            color=discord.Color.brand_green(),
            title=f"Quote from {message.author.name}",
            description=message.content,
        )
    )
    await database.save()


@bot.hybrid_command()
async def quote(ctx: commands.Context, choose: typing.Literal["random", "list"]):
    """Displays a random quote from your server selected by the Quote context menu command"""
    database = bot.get_cog("Database")
    guild_db = database.db[str(ctx.guild.id)]
    if "quotes" not in guild_db.keys():
        await ctx.send(
            "There are no quotes! Right click or tap and hold on a message, then select Apps > Quote to make a quote."
        )
        return
    if choose == "list":
        embed = discord.Embed(
            color=discord.Color.brand_green(),
            title=f"{ctx.guild.name}'s quotes",
        )
        for i in guild_db["quotes"]:
            author = i["author"]
            embed.add_field(
                name=author,
                value=i["content"] + "\n" + (f"<t:{i['time']}:f>" if "time" in i.keys() else "")
            )
        await ctx.send(embed=embed)
    else:
        random_quote = random.choice(guild_db["quotes"])
        author = random_quote["author"]
        embed = discord.Embed(
            color=discord.Color.brand_green(),
            title=f"Quote from {author}",
            description=random_quote["content"],
        )
        if "time" in random_quote.keys():
            embed.set_footer(text=f"{str(datetime.datetime.fromtimestamp(random_quote['time']))}")
        await ctx.send(embed=embed)


@bot.hybrid_command()
async def meow(ctx: commands.Context):
    """Get Cat"""
    await ctx.send(
        f"http://placekitten.com/{random.randint(480,520)}/{random.randint(480,520)}"
    )


@bot.hybrid_command()
async def playchess(ctx: commands.Context, opponent: discord.Member):
    """Play a game of chess"""
    achievements = bot.get_cog("Achievements")
    if opponent == ctx.author:
        await ctx.send("Nope")
        await achievements.give_ach(
            ctx.guild, ctx.author, "Random", "nofriends", ctx.channel
        )
        return

    board = chess.Board()
    white = ctx.author
    black = opponent
    game_over = False

    async def process_board(board: chess.Board) -> str:
        EMPTY = "⊙"
        final = ""
        for rank in range(7, -1, -1):
            rank_str = ""
            for file in range(8):
                piece = board.piece_at(chess.square(file, rank))
                rank_str += piece.unicode_symbol() if piece is not None else EMPTY
            final += rank_str + "\n"
        return final

    class ChessModal(ui.Modal):
        def __init__(self):
            super().__init__(title="Make a move")

            self.move = ui.TextInput(
                label="Your move", placeholder="Nf6", min_length=2, max_length=10
            )
            self.add_item(self.move)

        async def on_submit(self, interaction):
            move = board.push_san(self.move.value)
            if board.is_en_passant(move):
                await achievements.give_ach(
                    interaction.guild,
                    interaction.user,
                    "Random",
                    "enpassant",
                    interaction.channel,
                )
            await interaction.response.defer()
            await update_chess_embed(interaction)

    async def claim_draw(interaction):
        if not (interaction.user in (white, black)):
            await interaction.response.send_message("Can't do that", ephemeral=True)
        nonlocal game_over
        game_over = True
        interaction.response.defer()
        update_chess_embed()

    async def play_move(interaction):
        if not (
            (interaction.user == white and board.turn == chess.WHITE)
            or (interaction.user == black and board.turn == chess.BLACK)
        ):
            await interaction.response.send_message(
                "Either it's not your turn or you aren't playing in this game.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(ChessModal())

    async def gen_embed():
        embed = discord.Embed(
            color=0x000000 if board.turn == chess.BLACK else 0xFFFFFF,
            title=f"Chess game",
            description=f"{white.name} plays white (uppercase), {black.name} plays black (lowercase)",
        )
        embed.add_field(
            name="Board", value=f"```\n{await process_board(board)}\n```", inline=False
        )
        view = ui.View(timeout=3 * 3600)
        move_button = ui.Button(
            style=discord.ButtonStyle.primary,
            label="Move",
            disabled=board.is_game_over() or game_over,
        )
        move_button.callback = play_move
        view.add_item(move_button)
        claim_draw_button = ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Claim Draw",
            disabled=(not board.can_claim_draw()),
        )
        claim_draw_button.callback = claim_draw
        view.add_item(claim_draw_button)
        if game_over:
            embed.add_field(name="Result", value="1/2-1/2")
        elif board.is_game_over():
            embed.add_field(name="Result", value=board.outcome().result())
        return embed, view

    async def update_chess_embed(interaction):
        embed, view = await gen_embed()
        await interaction.message.edit(embed=embed, view=view)

    embed, view = await gen_embed()
    await ctx.send(embed=embed, view=view)


@bot.hybrid_command()
async def dungeon(ctx: commands.Context):
    """Enter a random dungeon"""
    database = bot.get_cog("Database")
    achievements = bot.get_cog("Achievements")
    roomtypes = ["Enemy"] * 10 + ["Empty"] * 5 + ["Heal"] * 4
    emojis = {"Enemy": "💀", "Empty": "⬛", "Boss": "☠️", "Heal": "❤️"}
    desc = {
        "Empty": "You find yourself in an empty room. There's no danger here...but you feel like you should keep moving.",
        "Enemy": "You find some monsters in this room. You have taken 1 HP of damage from fighting them.",
        "Heal": "This room seems safe. You take some time to rest, healing 1 HP.",
        "Boss": "You see treasure, but a boss guards it. Good luck!",
    }
    health = 7
    bossfound = False

    class Room:
        def __init__(
            self,
            parent: "Room",
            type: typing.Optional[str] = None,
            exitcount: typing.Optional[int] = None,
        ):
            nonlocal bossfound
            self.parent = parent
            if type == None:
                self.type = random.choice(
                    roomtypes + ["Boss"] if not bossfound else roomtypes
                )
            else:
                self.type = type
            if self.type == "Boss":
                bossfound = True
            if exitcount == None:
                if self.type == "Boss":
                    self.exitcount = 0
                elif bossfound:
                    self.exitcount = random.randint(0, 1)
                else:
                    self.exitcount = random.randint(1, 2)
            else:
                self.exitcount = exitcount
            self.exits = None

        async def gen_exits(self):
            if self.exits is not None:
                return
            self.exits = []
            for _ in range(self.exitcount):
                self.exits.append(Room(self))

    currentroom = Room(None, "Empty", 2)

    async def gen_callback(room: Room):
        nonlocal currentroom

        async def callback(interaction: discord.Interaction):
            nonlocal currentroom, room
            if interaction.user != ctx.author:
                await interaction.response.send_message(
                    "Start your own dungeon", ephemeral=True
                )
                await achievements.give_ach(
                    ctx.guild, interaction.user, "Random", "nope", ctx.channel
                )
                return
            currentroom = room
            embed, view = await gen_embed()
            await interaction.response.defer()
            await interaction.message.edit(embed=embed, view=view)

        return callback

    async def gen_embed():
        nonlocal health, currentroom
        embed = discord.Embed(
            color=discord.Color.darker_gray(),
            title="The Dungeon",
            description=desc[currentroom.type],
        )
        if currentroom.type == "Enemy":
            health -= 1
            currentroom.type = "Empty"
        elif currentroom.type == "Heal":
            health += 1
            currentroom.type = "Empty"
        elif currentroom.type == "Boss":
            health -= random.randint(3, 6)
        if health <= 0:
            health = 0
            embed.add_field(
                name="HP", value="Your health has reached 0. You have failed!"
            )
        else:
            health = health if health < 10 else 10
            embed.add_field(name="HP", value=f"{health}/10")
        if currentroom.type == "Boss":
            view = ui.View()

            async def victory(interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message(
                        "Start your own dungeon", ephemeral=True
                    )
                    await achievements.give_ach(
                        ctx.guild, interaction.user, "Random", "nope", ctx.channel
                    )
                    return
                await interaction.response.defer()
                await achievements.give_ach(
                    ctx.guild, ctx.author, "Random", "dungeon", ctx.channel
                )
                embed = discord.Embed(
                    title="The Dungeon", description="You have won! Good job."
                )
                reward_text = ""
                num_symbols = ((health + 2) // 3) * 2
                for _ in range(num_symbols):
                    symbol = random.choice(DUNGEON_RESULTS)
                    database.add_symbol(ctx.guild, ctx.author, symbol)
                    reward_text += symbol + "\n"
                embed.add_field(name="Results", value=reward_text)
                await interaction.message.edit(embed=embed, view=None)

            win_button = ui.Button(emoji="💎", disabled=health == 0)
            win_button.callback = victory
            view.add_item(win_button)
            return embed, view
        view = ui.View()
        backtrack = ui.Button(
            emoji="↩️", disabled=(currentroom.parent is None) or health == 0
        )
        if currentroom.parent is not None:
            backtrack.callback = await gen_callback(currentroom.parent)
        view.add_item(backtrack)
        await currentroom.gen_exits()
        for i in currentroom.exits:
            button = ui.Button(emoji=emojis[i.type], disabled=health == 0)
            button.callback = await gen_callback(i)
            view.add_item(button)
        return embed, view

    embed, view = await gen_embed()
    await ctx.send(embed=embed, view=view)


@commands.is_owner()
@bot.hybrid_command()
async def reload(ctx: commands.Context, ext: str):
    await bot.reload_extension(ext)
    await bot.tree.sync()
    await ctx.send("Reloaded!")

@commands.is_owner()
@bot.hybrid_command()
async def pull(ctx: commands.Context):
    os.system('git pull')
    await ctx.send("Pulled!")

asyncio.run(bot.load_extension("symbols"))
asyncio.run(bot.load_extension("achievements"))
asyncio.run(bot.load_extension("database"))

bot.get_cog("Database").load()
bot.get_cog("Achievements").load()


async def on_command_error(ctx: commands.Context, error: Exception):
    print(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error.args[0])
    elif isinstance(error, commands.TooManyArguments):
        await ctx.send("thats too many arguments")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("cant do that")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("reinvite the bot")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("not a real command 💀💀💀")
    else:
        await ctx.send(
            embed=discord.Embed(
                title="An error occured!", description=error, color=discord.Color.red()
            )
        )


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    print(error)
    if isinstance(error, app_commands.TransformerError):
        await interaction.response.send_message("goofy ahh arguments")
    elif isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("cant do that")
    elif isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message("reinvite the bot")
    else:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="An error occured!", description=error, color=discord.Color.red()
            )
        )


bot.on_command_error = on_command_error

try:
    bot.run(TOKEN)
finally:
    bot.get_cog("Database").save()