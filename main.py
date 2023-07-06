import discord
from discord.ext import commands
from discord import app_commands, ui
import os
import random
import json
import time
import math
import asyncio
import typing
import re
import chess
from discord.interactions import Interaction

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="m!",
    intents=intents,
    activity=discord.Game(name="Calculator for Nintendo Switch"),
    application_id=1119928094418018354,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False)
)

TOKEN = os.environ['token']

recipes = {("Increment", "Increment"): "Addition",
("Increment", "Inverse"): "Decrement",
("One", "Addition"): "Natural Numbers",
("One", "Decrement"): "Zero",
("Natural Numbers", "Zero"): "Whole Numbers",
("Decrement", "Decrement"): "Subtraction",
("Zero", "Subtraction"): "Negative Numbers",
("Whole Numbers", "Negative Numbers"): "Integers",
("Natural Numbers", "Subtraction"): "Integers",
("Addition", "Inverse"): "Subtraction",
("Addition", "Addition"): "Multiplication",
("Multiplication", "Inverse"): "Division",
("Integers", "Division"): "Rational Numbers",
("Rational Numbers", "Inverse"): "Irrational Numbers",
("Rational Numbers", "Irrational Numbers"): "Real Numbers",
("Multiplication", "Multiplication"): "Exponent",
("Exponent", "Inverse"): "Logarithm",
("Division", "One"): "Reciprocal",
("Reciprocal", "Exponent"): "Root",
("Negative Numbers", "Root"): "Imaginary Numbers",
("Imaginary Numbers", "Real Numbers"): "Complex Numbers",
("Reciprocal", "Zero"): "Infinity",
("Point", "Point"): "Line Segment",
("Line Segment", "Infinity"): "Ray",
("Ray", "Infinity"): "Line",
("Ray", "Ray"): "Angle",
("Line", "Infinity"): "Plane",
("Angle", "Real Numbers"): "Radians",
("Line Segment", "Real Numbers"): "Distance",
("Line Segment", "Line Segment"): "Polygon",
("Distance", "Real Numbers"): "Circle",
("Polygon", "Addition"): "Perimeter",
("Polygon", "Multiplication"): "Area",
("Circle", "Division"): "Pi",
("Polygon", "Polygon"): "Solid",
("Solid", "Circle"): "Sphere",
}

base_symbols = ["One", "Increment", "Inverse"]
recycle_results = base_symbols + ["Point"]

bonus_unlocks = {
"Complex Numbers": "Real Numbers",
"Logarithm": "Multiplication"
}

special_symbols = {"Point"}

symbols = list(set(base_symbols) | set(recipes.values()) | special_symbols)
symbols.sort()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

@bot.hybrid_command(brief="Repeats after you", help="Simply repeats your input. It doesn't get much simpler than that.")
async def echo(ctx, *, text):
    await ctx.send(text)

@bot.hybrid_command(brief="Does simple calculations", help="Does the calculation specified. Allowed operators are +, -, *, /, and ^.")
async def calculate(ctx, num1: float, op, num2: float):
    if op in ("+", "plus", "add"):
        await ctx.send(num1 + num2)
    elif op in ("-", "minus", "subtract"):
        await ctx.send(num1 - num2)
    elif op in ("*", "x", "×", "times", "multiply"):
        await ctx.send(num1 * num2)
    elif op in ("/", "÷", "over", "divide"):
        if num2 == 0:
            await ctx.send("dont divide by 0 idiot")
            return
        await ctx.send(num1 / num2)
    elif op in ("^", "**", "exponent"):
        await ctx.send(num1 / num2)
    else:
        await ctx.send("Invalid operation!")

@bot.hybrid_command(brief="A stupider version of calculate.", help="Same parameters as calculate, but it does the calculations wrong.")
async def stupidcalculator(ctx, num1: int, op, num2: int):
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
    elif op in ("*", "x", "×", "times", "multiply"):
        await ctx.send(num1 + num2)
    elif op in ("/", "÷", "over", "divide"):
        await ctx.send(num1 // num2)
    elif op in ("^", "**", "exponent"):
        await ctx.send(str(num1) + str(num2))
    else:
        await ctx.send("Invalid operation!")

@bot.listen("on_message")
async def easter_eggs(message):
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
    if "xnopyt" in message.content.lower():
        await message.reply("If you accept the definition of a word as some letters surrounded by a gap, then \"xnopyt\", \"aaaaaaajjjjjjjjj\", and \"hrrkrkrkrwpfrbbrbrbrlablblblblblblwhitoo'ap\" are all words, despite being pretty much meaningless.")
    if message.content.lower() == "ratio":
        if message.reference is not None and isinstance(message.reference.resolved, discord.Message): # other options are None or DeletedReferencedMessage
            await message.add_reaction("⬆️")
            await message.reference.resolved.add_reaction("⬆️")
            if message.author == message.reference.resolved.author:
                await Achievements.give_ach(message.guild, message.author, "Random", "friendlyfire", message.channel)
    if re.search("\d+\.\d+\.\d+\.\d+", message.content):
        await message.reply(f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}")

@bot.tree.context_menu(name="Quote")
@app_commands.guild_only()
async def msg_quote(interaction: discord.Interaction, message: discord.Message):
    if message.author == interaction.user:
        await interaction.response.send_message("You can't quote yourself")
        return
    guild_db = Database.db[str(interaction.guild.id)]
    if "quotes" not in guild_db.keys():
        guild_db["quotes"] = []
    if {"author": message.author.name, "content": message.content} not in guild_db["quotes"]:
        guild_db["quotes"].append({"author": message.author.name, "content": message.content})
    await interaction.response.send_message(embed=discord.Embed(color=discord.Color.brand_green(), title=f"Quote from {message.author.name}", description=message.content))

@bot.hybrid_command(brief="Displays a random quote", help="Displays a random quote from this server. Add some with the Quote context menu command!")
async def quote(ctx):
    guild_db = Database.db[str(ctx.guild.id)]
    if "quotes" not in guild_db.keys():
        await ctx.send("There are no quotes! Right click or tap an hold on a message, then select Apps > Quote to make a quote.")
        return
    random_quote = random.choice(guild_db["quotes"])
    author = random_quote["author"]
    await ctx.send(embed=discord.Embed(color=discord.Color.brand_green(), title=f"Quote from {author}", description=random_quote["content"]))

@bot.hybrid_command(brief="Get Cat", help="cat")
async def meow(ctx):
    await ctx.send(f"http://placekitten.com/{random.randint(480,520)}/{random.randint(480,520)}")

@bot.hybrid_command(brief="Play a game of chess", help="google en passant")
async def playchess(ctx, opponent: discord.Member):
    if opponent == ctx.author:
        await ctx.send("Nope")
        await Achievements.give_ach(ctx.guild, ctx.author, "Random", "nofriends", ctx.channel)
        return

    board = chess.Board()
    white = ctx.author
    black = opponent # Might change this to either be random or make the challenger black
    game_over = False

    async def process_board(board: chess.Board) -> str:
        board_ranks_str = str(board).splitlines()
        new_str = ""
        for i, v in enumerate(board_ranks_str):
            new_str += str(8 - i) + " " + v + "\n"
        return new_str + "  a b c d e f g h"



    class ChessModal(ui.Modal):
        def __init__(self):
            super().__init__(title="Make a move")

            self.move = ui.TextInput(
                label="Your move",
                placeholder="Nf6",
                min_length=2,
                max_length=10
            )
            self.add_item(self.move)

        async def on_submit(self, interaction):
            move = board.push_san(self.move.value)
            if board.is_en_passant(move):
                await Achievements.give_ach(interaction.guild, interaction.user, "Random", "enpassant", interaction.channel)
            await interaction.response.defer()
            await update_chess_embed(interaction)
    
    async def claim_draw(interaction):
        if not(interaction.user in (white, black)):
            await interaction.response.send_message("Can't do that", ephemeral=True)
        nonlocal game_over
        game_over = True
        interaction.response.defer()
        update_chess_embed()

    async def play_move(interaction):
        if not ((interaction.user == white and board.turn == chess.WHITE) or (interaction.user == black and board.turn == chess.BLACK)):
            await interaction.response.send_message("Either it's not your turn or you aren't playing in this game.", ephemeral=True)
            return
        await interaction.response.send_modal(ChessModal())
        
    async def gen_embed():
        if board.turn == chess.WHITE:
            color = discord.Color.light_embed()
        else:
            color = discord.Color.dark_embed()
        embed = discord.Embed(color=color, title=f"Chess game", description=f"{white.name} plays white (uppercase), {black.name} plays black (lowercase)")
        embed.add_field(name="Board", value=f"```\n{await process_board(board)}\n```", inline=False)
        view = ui.View(timeout=3 * 3600)
        move_button = ui.Button(style=discord.ButtonStyle.primary, label="Move", disabled=board.is_game_over() or game_over)
        move_button.callback = play_move
        view.add_item(move_button)
        claim_draw_button = ui.Button(style=discord.ButtonStyle.secondary, label="Claim Draw", disabled=(not board.can_claim_draw()))
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

async def guild_only(self, ctx):
    if ctx.guild is None:
        raise commands.NoPrivateMessage("No DMs!")
    return True

class Database(commands.Cog):
    @classmethod
    def load(cls):
        with open("db.json", "r") as f:
            Database.db = json.load(f)
    @classmethod
    def save(cls):
        with open("db.json", "w") as f:
            json.dump(Database.db, f)
    @classmethod
    def register_member(cls, server, member):
        db = Database.db
        if not str(server.id) in db.keys():
            db[str(server.id)] = {}
        if not str(member.id) in db[str(server.id)].keys():
            db[str(server.id)][str(member.id)] = {}
            Database.save()
    @classmethod
    def get_member(cls, server, member):
        Database.register_member(server, member)
        return Database.db[str(server.id)][str(member.id)]
    @classmethod
    def add_symbol(cls, server, member, symbol, count=1):
        user_db = Database.get_member(server, member)
        if symbol in user_db.keys():
            user_db[symbol] += count
        else:
            user_db[symbol] = count
        Database.save()
    @classmethod
    def reset_cooldown(cls, server, member, cooldown=600):
        user_db = Database.get_member(server, member)
        user_db["cooldown"] = time.time() + cooldown
        Database.save()
    @classmethod
    def on_cooldown(cls, server, member):
        user_db = Database.get_member(server, member)
        if "cooldown" in user_db.keys():
            return user_db["cooldown"] > time.time()
        else:
            return False
    @classmethod
    def has_symbol(cls, server, member, symbol, count=1):
        user_db = Database.get_member(server, member)
        return symbol in user_db.keys() and user_db[symbol] >= count

class Symbols(commands.Cog):
    class Symbol(commands.Converter):
        async def convert(self, ctx, argument):
            if not argument.title() in symbols:
                raise commands.BadArgument(message=f"{argument} isn't a valid symbol!")
            return argument.title()

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(brief="Displays your inventory.", help="Shows which symbols you have and how many.")
    async def inv(self, ctx, member:typing.Optional[discord.Member]):
        if member is None:
            member = ctx.author
        embed = discord.Embed(color=discord.Color.brand_green(), title=f"{member.name}'s inventory", description="Sample text")
        user = Database.get_member(ctx.guild, member)
        for i in symbols:
            if Database.has_symbol(ctx.guild, member, i):
                embed.add_field(name=i, value=user[i])
        await ctx.send(embed=embed)

    @commands.hybrid_command(brief="Allows you to get symbols.", help="Gives you 5-7 symbols. They can be One, Increment, or Inverse. Has a 10 minute cooldown.")
    async def getsymbol(self, ctx):
        pool = base_symbols * 2
        for i in bonus_unlocks.keys():
            if Database.has_symbol(ctx.guild, ctx.author, i):
                pool.append(bonus_unlocks[i])
        if Database.on_cooldown(ctx.guild, ctx.author):
            user = Database.get_member(ctx.guild, ctx.author)
            await ctx.send("You're on cooldown! Try again <t:" + str(math.ceil(user["cooldown"])) + ":R>.")
        else:
            Database.reset_cooldown(ctx.guild, ctx.author)
            output = ""
            for _ in range(random.randint(5, 7)):
                symbol = random.choice(pool)
                output += symbol + "\n"
                Database.add_symbol(ctx.guild, ctx.author, symbol)
            await ctx.send(embed=discord.Embed(color=discord.Color.brand_green(), title="Here's what you got", description=output))
            await Achievements.give_ach(ctx.guild, ctx.author, "Symbols", "first", ctx.channel)

    @commands.hybrid_command(brief="Crafts two symbols together.", help="Crafts two symbols together to get a new symbol. An optional amount parameter allows you to craft in bulk.")
    async def craft(self, ctx, sym1: Symbol, sym2: Symbol, amt:int=1):
        if amt < 1:
            await ctx.send("Nope")
            return
        if sym1 not in symbols:
            await ctx.send(f"{sym1} isn't a symbol!")
            return
        if sym2 not in symbols:
            await ctx.send(f"{sym2} isn't a symbol!")
            return
        if sym1 == sym2:
            if not Database.has_symbol(ctx.guild, ctx.author, sym1, amt * 2):
                await ctx.send(f"You don't have enough of {sym1}.")
                return
        else:
            if not Database.has_symbol(ctx.guild, ctx.author, sym1, amt):
                await ctx.send(f"You don't have enough of {sym1}.")
                return
            if not Database.has_symbol(ctx.guild, ctx.author, sym2, amt):
                await ctx.send(f"You don't have enough of {sym2}.")
                return
        if (sym1, sym2) in recipes:
            result = recipes[(sym1, sym2)]
        elif (sym2, sym1) in recipes:
            result = recipes[(sym2, sym1)]
        else:
            await ctx.send("I couldn't find that recipe.")
            return
        user = Database.get_member(ctx.guild, ctx.author)
        user[sym1] -= amt
        user[sym2] -= amt
        Database.add_symbol(ctx.guild, ctx.author, result, amt)
        await ctx.send(f"You got {result} x{amt}!")
        await Achievements.give_ach(ctx.guild, ctx.author, "Symbols", "craft", ctx.channel)
        if result in bonus_unlocks.keys():
            await ctx.send(f"Congratulations! Because you have {result}, you can now get {bonus_unlocks[result]} from m!getsymbol!")
            await Achievements.give_ach(ctx.guild, ctx.author, "Symbols", "bonus_unlock", ctx.channel)

    @commands.hybrid_command(brief="Allows you to give symbols to others.", help="Donates symbols. An optional argument allows you to donate in bulk.")
    async def donate(self, ctx, reciever: discord.Member, symbol: Symbol, amount:int=1):
        if amount < 1:
            await ctx.send("You can't do that")
            return
        if not Database.has_symbol(ctx.guild, ctx.author, symbol, amount):
            await ctx.send("You don't have enough!")
            return
        if reciever == ctx.author:
            await ctx.send("That doesn't count")
            await Achievements.give_ach(ctx.guild, ctx.author, "Random", "nofriends", ctx.channel)
            return
        user = Database.get_member(ctx.guild, ctx.author)
        user[symbol] -= amount
        Database.add_symbol(ctx.guild, reciever, symbol, amount)
        await ctx.send(embed=discord.Embed(color=discord.Color.brand_green(), title="Donation successful", description=f"Successfully transferred {symbol} x{amount} to {reciever.name}."))
        await Achievements.give_ach(ctx.guild, ctx.author, "Symbols", "donate", ctx.channel)

    @commands.hybrid_command(brief="Recycle multiple of the same symbol to get other symbols!", help="Recycles multiples of symbols to get others. You will always get one less symbol than you put in.")
    async def recycle(self, ctx, symbol: Symbol, amount:int=2):
        if amount < 2:
            await ctx.send("Amount must be 2 or greater.")
            return
        if not Database.has_symbol(ctx.guild, ctx.author, symbol, amount):
            await ctx.send("You don't have enough!")
        user = Database.get_member(ctx.guild, ctx.author)
        user[symbol] -= amount
        output = "Here's what you got:\n"
        for _ in range(amount - 1):
            new_symbol = random.choice(recycle_results)
            output += new_symbol + "\n"
            Database.add_symbol(ctx.guild, ctx.author, new_symbol)
        await ctx.send(output)

    @commands.hybrid_command(brief="Trade symbols with another member.", help="Does this really need an explanation?")
    async def trade(self, ctx, person2: discord.Member):
        # thanks to milenakos for the code
        person1 = ctx.author
        if person1 == person2:
            await Achievements.give_ach(ctx.guild, ctx.author, "Random", "nofriends", ctx.channel)

        person1accept = False
        person2accept = False

        person1offer = {}
        person2offer = {}

        async def denytrade(interaction):
            nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
            if interaction.user != person1 and interaction.user != person2:
                await interaction.response.send_message("no", ephemeral = True)
                await Achievements.give_ach(interaction.guild, interaction.user, "Random", "nope", ctx.channel)
                return
            person1offer = {}
            person2offer = {}
            await interaction.message.edit(content=f"Trade cancelled by <@{interaction.user.id}>", embed=None, view=None)
        async def accepttrade(interaction):
            nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
            if interaction.user != person1 and interaction.user != person2:
                await interaction.response.send_message("no", ephemeral = True)
                await Achievements.give_ach(interaction.guild, interaction.user, "Random", "nope", ctx.channel)
                return
            if interaction.user == person1:
                person1accept = not person1accept
            if interaction.user == person2:
                person2accept = not person2accept

            await interaction.response.defer()
            await update_trade_embed(interaction)

            if person1accept and person2accept:
                error = False
                for k, v in person1offer.items():
                    if not Database.has_symbol(interaction.guild, person1, k, v):
                        error = True
                        break
                for k, v in person2offer.items():
                    if not Database.has_symbol(interaction.guild, person2, k, v):
                        error = True
                        break
                if error:
                    await interaction.message.edit("Some symbols disappeared during the trade, so the trade couldn't occur.", view=None, embed=None)
                    return

                person1db = Database.get_member(interaction.guild, person1)
                person2db = Database.get_member(interaction.guild, person2)
                for k, v in person1offer.items():
                    Database.add_symbol(interaction.guild, person2, k, v)
                    person1db[k] -= v
                for k, v in person2offer.items():
                    Database.add_symbol(interaction.guild, person1, k, v)
                    person2db[k] -= v
                Database.save()

                await interaction.message.edit(content="Trade finished!", view=None, embed=None)
        async def offertrade(interaction):
            nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
            if interaction.user != person1 and interaction.user != person2:
                await interaction.response.send_message("no", ephemeral = True)
                await Achievements.give_ach(interaction.guild, interaction.user, "Random", "nope", ctx.channel)
                return
            if interaction.user == person1:
                currentuser = 1
            elif interaction.user == person2:
                currentuser = 2
            await handle_modal(currentuser, interaction)

        async def handle_modal(currentuser, interaction):
            modal = TradeModal(currentuser)
            await interaction.response.send_modal(modal)

        async def gen_embed():
            nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
            view = ui.View(timeout=None)

            accept = ui.Button(label="Accept", style=discord.ButtonStyle.green)
            accept.callback = accepttrade

            deny = ui.Button(label="Cancel", style=discord.ButtonStyle.red)
            deny.callback = denytrade

            offer = ui.Button(label="Offer symbols", style=discord.ButtonStyle.blurple)
            offer.callback = offertrade

            view.add_item(accept)
            view.add_item(deny)
            view.add_item(offer)

            trade_embed = discord.Embed(color=discord.Color.brand_green(), title=f"Trade between {person1.name} and {person2.name}", description="trade real???")
            icon = "⬜"
            if person1accept:
                icon = "✅"
            valuestr = ""
            for k, v in person1offer.items():
                valuestr += k + " x" + str(v)
            trade_embed.add_field(name=f"{icon} {person1.name}", inline=True, value=valuestr)
            icon = "⬜"
            if person2accept:
                icon = "✅"
            valuestr = ""
            for k, v in person2offer.items():
                valuestr += k + " x" + str(v)
            trade_embed.add_field(name=f"{icon} {person2.name}", inline=True, value=valuestr)
            return trade_embed, view

        embed, view = await gen_embed()
        await ctx.send(embed=embed, view=view)

        async def update_trade_embed(interaction):
            embed, view = await gen_embed()
            await interaction.message.edit(embed=embed, view=view)

        class TradeModal(ui.Modal):
            def __init__(self, currentuser):
                super().__init__(
                    title = "Add symbols to the trade",
                    timeout = 5 * 60 # 5 minutes
                )
                self.currentuser = currentuser

                self.symbol = ui.TextInput(
                    min_length = 1,
                    max_length = 50,
                    label = "Symbol to offer",
                    placeholder = "One"
                )
                self.add_item(self.symbol)

                self.amount = ui.TextInput(
                    min_length = 1,
                    max_length = 50,
                    label = "Amount to offer",
                    placeholder = "1"
                )
                self.add_item(self.amount)

            async def on_submit(self, interaction):
                nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
                try:
                    if int(self.amount.value) <= 0:
                        raise Exception
                except Exception:
                    return
                if not self.symbol.value.title() in symbols:
                    return
                if self.currentuser == 1:
                    if self.symbol.value.title() in person1offer.keys():
                        current_set = person1offer[self.symbol.value.title()]
                    else:
                        current_set = 0
                else:
                    if self.symbol.value.title() in person2offer.keys():
                        current_set = person2offer[self.symbol.value.title()]
                    else:
                        current_set = 0
                if not Database.has_symbol(interaction.guild, interaction.user, self.symbol.value.title(), current_set + int(self.amount.value)):
                    return
                if self.currentuser == 1:
                    if self.symbol.value.title() in person1offer.keys():
                        person1offer[self.symbol.value.title()] += int(self.amount.value)
                    else:
                        person1offer[self.symbol.value.title()] = int(self.amount.value)
                else:
                    if self.symbol.value.title() in person2offer.keys():
                        person2offer[self.symbol.value.title()] += int(self.amount.value)
                    else:
                        person2offer[self.symbol.value.title()] = int(self.amount.value)
                await interaction.response.defer()
                await update_trade_embed(interaction)
Symbols.cog_check = guild_only

class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load()

    @classmethod
    def load(cls):
        with open("achs.json", "r") as f:
            Achievements.achievements = json.load(f)
    @classmethod
    def register(cls, guild, member):
        user_db = Database.get_member(guild, member)
        if "achs" not in user_db.keys():
            user_db["achs"] = {}
        Database.save()
    @classmethod
    def has_ach(cls, guild, member, ach):
        Achievements.register(guild, member)
        user_db = Database.get_member(guild, member)["achs"]
        if ach not in user_db.keys():
            return False
        return user_db[ach]
    @classmethod
    async def give_ach(cls, guild, member, category, ach, messageable):
        Achievements.register(guild, member)
        new_ach = not Achievements.has_ach(guild, member, ach)
        Database.get_member(guild, member)["achs"][ach] = True
        Database.save()
        ach_data = Achievements.achievements[category][ach]
        if new_ach:
            embed = discord.Embed(color=discord.Color.brand_green(), title="Achievement get: " + ach_data["name"], description=ach_data["desc"])
            embed.set_footer(text=f"Achieved by {member.name}")
            await messageable.send(embed=embed)
    @commands.hybrid_command(brief="See your achievements", help="Lists your achievements by category")
    async def achs(self, ctx):
        Achievements.register(ctx.guild, ctx.author)
        user_db = Database.get_member(ctx.guild, ctx.author)["achs"]
        category = "Symbols"
        async def gen_embed():
            nonlocal category
            embed = discord.Embed(color=discord.Color.brand_green(), title="Achievements", description="Category: " + category)
            for k, v in Achievements.achievements[category].items():
                emoji = "✅" if Achievements.has_ach(ctx.guild, ctx.author, k) else "⬜"
                embed.add_field(name=emoji + " " + v["name"], value=v["desc"])
            view = ui.View()
            async def gen_callback(new_category):
                nonlocal category
                async def callback(interaction):
                    nonlocal category
                    nonlocal new_category
                    category = new_category
                    embed, view = await gen_embed()
                    await interaction.response.edit_message(embed=embed, view=view)
                return callback
            for i in Achievements.achievements.keys():
                if i == category:
                    button = ui.Button(label=i, style=discord.ButtonStyle.green)
                else:
                    button = ui.Button(label=i, style=discord.ButtonStyle.blurple)
                button.callback = await gen_callback(i)
                view.add_item(button)
            return embed, view
        embed, view = await gen_embed()
        await ctx.send(embed=embed, view=view)
Achievements.cog_check = guild_only
        


Database.load()

asyncio.run(bot.add_cog(Symbols(bot)))
asyncio.run(bot.add_cog(Achievements(bot)))

async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("goofy ahh arguments")
    elif isinstance(error, commands.TooManyArguments):
        await ctx.send("thats too many arguments")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("cant do that")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("reinvite the bot")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("not a real command 💀💀💀")
    else:
        await ctx.send(embed=discord.Embed(title="An error occured!", description=error, color=discord.Color.red()))
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.TransformerError):
        await interaction.response.send_message("goofy ahh arguments")
    elif isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("cant do that")
    elif isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message("reinvite the bot")
    else:
        await interaction.response.send_message(embed=discord.Embed(title="An error occured!", description=error, color=discord.Color.red()))
bot.on_command_error = on_command_error
bot.tree.on_error = on_app_command_error

try:
    bot.run(TOKEN)
finally:
    Database.save()
