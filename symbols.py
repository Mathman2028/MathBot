import discord
from discord.ext import commands
import random
import math
from discord import ui
from discord import app_commands
import typing

if typing.TYPE_CHECKING:
    from database import Database

RECIPES = {
    ("Increment", "Increment"): "Addition",
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
    ("Circle", "Line"): "Cone",
    ("Cone", "Plane"): "Conic Section",
    ("Plane", "Infinity"): "Space",
    ("Set", "Addition"): "Union",
    ("Set", "Multiplication"): "Intersection",
    ("Real Numbers", "Real Numbers"): "Ordered Pair",
    ("Set", "Ordered Pair"): "Function",
    ("Ordered Pair", "Point"): "Cartesian Plane",
    ("Cartesian Plane", "Real Numbers"): "X-Axis",
    ("Cartesian Plane", "Imaginary Numbers"): "Y-Axis",
    ("Circle", "Function"): "Trig Function",
    ("Trig Function", "X-Axis"): "Cosine",
    ("Trig Function", "Y-Axis"): "Sine",
    ("Trig Function", "Division"): "Tangent",
    ("Reciprocal", "Cosine"): "Secant",
    ("Reciprocal", "Sine"): "Cosecant",
    ("Line", "Division"): "Slope",
    ("Slope", "Function"): "Derivative",
    ("Derivative", "Inverse"): "Integral"
}

BASE_SYMBOLS = ("One", "Increment", "Inverse")
RECYCLE_RESULTS = BASE_SYMBOLS + ("Point",)
DUNGEON_RESULTS = BASE_SYMBOLS + ("Set",)

BONUS_UNLOCKS = {
    "Complex Numbers": "Real Numbers",
    "Logarithm": "Multiplication",
    "Pi": "Point",
    "Space": "Infinity",
}

SPECIAL_SYMBOLS = {"Point", "Set"}

SYMBOLS = sorted(list(set(BASE_SYMBOLS) | set(RECIPES.values()) | SPECIAL_SYMBOLS))

VALUES = {i: 1 for i in BASE_SYMBOLS} | {i: 3 for i in SPECIAL_SYMBOLS}
for (k1, k2), v in RECIPES.items():
    VALUES[v] = min(VALUES.get(v, 1_000_000), VALUES[k1] + VALUES[k2] + 1)
# The value of a symbol is 1 for base symbols, 3 for special symbols, and the value of its two parts plus one otherwise.
# If multiple recipes exist, the lowest value is chosen.


class Symbols(commands.GroupCog, group_name="symbol"):
    """All the commands relating to the bot's symbol system."""

    async def guild_only(self, ctx: commands.Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage("No DMs!")
        return True

    class Symbol(commands.Converter):
        async def convert(self, ctx: commands.Context, argument: str):
            if not argument.title() in SYMBOLS:
                possible = []
                for i in SYMBOLS:
                    if i.startswith(argument.title()):
                        possible.append(i)
                if len(possible) == 1:
                    return possible[0]
                else:
                    raise commands.BadArgument(
                        message=f"{argument} isn't a valid symbol!"
                    )
            return argument.title()

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def inv(self, ctx: commands.Context, member: discord.Member | None):
        """Displays your inventory"""
        if ctx.interaction:
            await ctx.interaction.response.defer()
        database: "Database" = self.bot.get_cog("Database")
        achievements = self.bot.get_cog("Achievements")
        if member is None:
            member = ctx.author
        discovered = len(tuple(None for i in SYMBOLS if database.has_symbol(ctx.guild, member, i, 0))) # not having 0 of a symbol = not discovered
        if discovered == len(SYMBOLS):
            await achievements.give_ach(
                ctx.guild, member, "Symbols", "everything", ctx.channel
            )
        embed = discord.Embed(
            color=discord.Color.brand_green(),
            title=f"{member.name}'s inventory",
            description=f"Symbols discovered: {discovered}/{len(SYMBOLS)}",
        )
        value = 0
        for i in SYMBOLS:
            if database.has_symbol(ctx.guild, member, i):
                amt = database.get_symbol(ctx.guild, member, i)
                embed.add_field(name=i, value=amt)
                value += VALUES[i] * amt
        embed.set_footer(text=f"Total value: {value}")
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def get(self, ctx: commands.Context):
        """Get some base symbols every 10 minutes"""
        database: "Database" = self.bot.get_cog("Database")
        achievements = self.bot.get_cog("Achievements")
        pool = BASE_SYMBOLS * 3
        for i in BONUS_UNLOCKS.keys():
            if database.has_symbol(ctx.guild, ctx.author, i):
                pool += (BONUS_UNLOCKS[i],)
        if database.on_cooldown(ctx.guild, ctx.author):
            await ctx.send(
                f"You're on cooldown! Try again <t:{str(math.ceil(database.get_cooldown_end(ctx.guild, ctx.author)))}:R>."
            )
        else:
            database.reset_cooldown(ctx.guild, ctx.author)
            output = ""
            value = 0
            for _ in range(random.randint(5, 7)):
                symbol = random.choice(pool)
                output += symbol + "\n"
                database.add_symbol(ctx.guild, ctx.author, symbol)
                value += VALUES[symbol]
            await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.brand_green(),
                    title="Here's what you got",
                    description=output,
                ).set_footer(text=f"Total value: {value}")
            )
            await achievements.give_ach(
                ctx.guild, ctx.author, "Symbols", "first", ctx.channel
            )

    @commands.hybrid_command()
    async def craft(
        self, ctx: commands.Context, sym1: Symbol, sym2: Symbol, amt: int = 1
    ):
        """Craft symbols to get better symbols"""
        database: "Database" = self.bot.get_cog("Database")
        achievements = self.bot.get_cog("Achievements")
        if amt < 1:
            await ctx.send("Nope")
            return
        if sym1 not in SYMBOLS:
            await ctx.send(f"{sym1} isn't a symbol!")
            return
        if sym2 not in SYMBOLS:
            await ctx.send(f"{sym2} isn't a symbol!")
            return
        if sym1 == sym2:
            if not database.has_symbol(ctx.guild, ctx.author, sym1, amt * 2):
                await ctx.send(f"You don't have enough of {sym1}.")
                return
        else:
            if not database.has_symbol(ctx.guild, ctx.author, sym1, amt):
                await ctx.send(f"You don't have enough of {sym1}.")
                return
            if not database.has_symbol(ctx.guild, ctx.author, sym2, amt):
                await ctx.send(f"You don't have enough of {sym2}.")
                return
        if (sym1, sym2) in RECIPES:
            result = RECIPES[(sym1, sym2)]
        elif (sym2, sym1) in RECIPES:
            result = RECIPES[(sym2, sym1)]
        else:
            await ctx.send("I couldn't find that recipe.")
            return
        database.add_symbol(ctx.guild, ctx.author, sym1, -amt)
        database.add_symbol(ctx.guild, ctx.author, sym2, -amt)
        database.add_symbol(ctx.guild, ctx.author, result, amt)
        await ctx.send(f"You got {result} x{amt}!")
        await achievements.give_ach(
            ctx.guild, ctx.author, "Symbols", "craft", ctx.channel
        )
        if result in BONUS_UNLOCKS.keys():
            await ctx.send(
                f"Congratulations! Because you have {result}, you can now get {BONUS_UNLOCKS[result]} from </symbol get:1133587417534836818>!"
            )
            await achievements.give_ach(
                ctx.guild, ctx.author, "Symbols", "bonus_unlock", ctx.channel
            )

    @commands.hybrid_command()
    async def recipes(self, ctx: commands.Context, symbol: Symbol):
        """Tells you what can be crafted with or to make a certain symbol"""
        database: "Database" = self.bot.get_cog("Database")
        output = ""

        async def process_symbol(symbol):
            if database.has_symbol(ctx.guild, ctx.author, symbol, 0): # this checks if the symbol is discovered
                return symbol
            else:
                return "???"

        for k, v in RECIPES.items():
            if symbol not in k and symbol != v:
                continue
            output += f"{await process_symbol(k[0])} + {await process_symbol(k[1])} = {await process_symbol(v)}\n"
        await ctx.send(
            embed=discord.Embed(
                color=discord.Color.brand_green(),
                title=f"Recipes with {symbol}",
                description=output,
            )
        )

    @commands.hybrid_command()
    async def hint(self, ctx: commands.Context):
        """Shows a list of recipes you should try next"""
        database: "Database" = self.bot.get_cog("Database")
        output = ""
        for k, v in RECIPES.items():
            if (
                database.has_symbol(ctx.guild, ctx.author, k[0], 0) # check for 0 of a symbol = discovered the symbol
                and database.has_symbol(ctx.guild, ctx.author, k[1], 0)
                and not database.has_symbol(ctx.guild, ctx.author, v, 0)
            ):
                output += f"{k[0]} + {k[1]}\n"
        output = "Nothing." if not output else output
        await ctx.send(
            embed=discord.Embed(
                color=discord.Color.brand_green(),
                title="New recipes",
                description=output,
            )
        )

    @commands.hybrid_command()
    async def donate(
        self,
        ctx: commands.Context,
        reciever: discord.Member,
        symbol: Symbol,
        amount: int = 1,
    ):
        """Give away your symbols"""
        database: "Database" = self.bot.get_cog("Database")
        achievements = self.bot.get_cog("Achievements")
        if amount < 1:
            await ctx.send("You can't do that")
            return
        if not database.has_symbol(ctx.guild, ctx.author, symbol, amount):
            await ctx.send("You don't have enough!")
            return
        if reciever == ctx.author:
            await ctx.send("That doesn't count")
            await achievements.give_ach(
                ctx.guild, ctx.author, "Random", "nofriends", ctx.channel
            )
            return
        database.add_symbol(ctx.guild, ctx.author, symbol, -amount)
        database.add_symbol(ctx.guild, reciever, symbol, amount)
        await ctx.send(
            embed=discord.Embed(
                color=discord.Color.brand_green(),
                title="Donation successful",
                description=f"Successfully transferred {symbol} x{amount} to {reciever.name}.",
            )
        )
        await achievements.give_ach(
            ctx.guild, ctx.author, "Symbols", "donate", ctx.channel
        )

    @commands.hybrid_command()
    async def recycle(self, ctx: commands.Context, symbol: Symbol, amount: int = 2):
        """Recycle n symbols, get n-1 symbols"""
        database: "Database" = self.bot.get_cog("Database")
        if amount < 2:
            await ctx.send("Amount must be 2 or greater.")
            return
        if not database.has_symbol(ctx.guild, ctx.author, symbol, amount):
            await ctx.send("You don't have enough!")
        database.add_symbol(ctx.guild, ctx.author, symbol, -amount)
        value = VALUES[symbol] * amount * -1
        output = ""
        for _ in range(amount - 1):
            new_symbol = random.choice(RECYCLE_RESULTS)
            while new_symbol == symbol:
                new_symbol = random.choice(RECYCLE_RESULTS)
            output += new_symbol + "\n"
            database.add_symbol(ctx.guild, ctx.author, new_symbol)
            value += VALUES[new_symbol]
        await ctx.send(
            embed=discord.Embed(
                color=discord.Color.brand_green(),
                title="Recycle results",
                description=output,
            ).set_footer(text=f"Value {'gained' if value > 0 else 'lost'}: {abs(value)}")
        )

    @commands.hybrid_command()
    async def trade(self, ctx: commands.Context, person2: discord.Member):
        database: "Database" = self.bot.get_cog("Database")
        achievements = self.bot.get_cog("Achievements")
        """Trade your symbols"""
        # thanks to milenakos for the code
        person1 = ctx.author
        if person1 == person2:
            await achievements.give_ach(
                ctx.guild, ctx.author, "Random", "nofriends", ctx.channel
            )

        person1accept = False
        person2accept = False

        person1offer = {}
        person2offer = {}

        async def denytrade(interaction: discord.Interaction):
            nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
            if interaction.user != person1 and interaction.user != person2:
                await interaction.response.send_message("no", ephemeral=True)
                await achievements.give_ach(
                    interaction.guild, interaction.user, "Random", "nope", ctx.channel
                )
                return
            person1offer = {}
            person2offer = {}
            await interaction.message.edit(
                content=f"Trade cancelled by <@{interaction.user.id}>",
                embed=None,
                view=None,
            )

        async def accepttrade(interaction: discord.Interaction):
            nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
            if interaction.user != person1 and interaction.user != person2:
                await interaction.response.send_message("no", ephemeral=True)
                await achievements.give_ach(
                    interaction.guild, interaction.user, "Random", "nope", ctx.channel
                )
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
                    if not database.has_symbol(interaction.guild, person1, k, v):
                        error = True
                        break
                for k, v in person2offer.items():
                    if not database.has_symbol(interaction.guild, person2, k, v):
                        error = True
                        break
                if error:
                    await interaction.message.edit(
                        "Some symbols disappeared during the trade, so the trade couldn't occur.",
                        view=None,
                        embed=None,
                    )
                    return

                for k, v in person1offer.items():
                    database.add_symbol(interaction.guild, person2, k, v)
                    database.add_symbol(interaction.guild, person1, k, -v)
                for k, v in person2offer.items():
                    database.add_symbol(interaction.guild, person1, k, v)
                    database.add_symbol(interaction.guild, person2, k, -v)
                database.save()

                await interaction.message.edit(
                    content="Trade finished!", view=None, embed=None
                )

        async def offertrade(interaction: discord.Interaction):
            nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
            if interaction.user != person1 and interaction.user != person2:
                await interaction.response.send_message("no", ephemeral=True)
                await achievements.give_ach(
                    interaction.guild, interaction.user, "Random", "nope", ctx.channel
                )
                return
            if interaction.user == person1:
                currentuser = 1
            elif interaction.user == person2:
                currentuser = 2
            await handle_modal(currentuser, interaction)

        async def handle_modal(currentuser: int, interaction: discord.Interaction):
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

            trade_embed = discord.Embed(
                color=discord.Color.brand_green(),
                title=f"Trade between {person1.name} and {person2.name}",
                description="trade real???",
            )
            icon = "⬜"
            if person1accept:
                icon = "✅"
            valuestr = ""
            for k, v in person1offer.items():
                valuestr += k + " x" + str(v)
            trade_embed.add_field(
                name=f"{icon} {person1.name}", inline=True, value=valuestr
            )
            icon = "⬜"
            if person2accept:
                icon = "✅"
            valuestr = ""
            for k, v in person2offer.items():
                valuestr += k + " x" + str(v)
            trade_embed.add_field(
                name=f"{icon} {person2.name}", inline=True, value=valuestr
            )
            return trade_embed, view

        embed, view = await gen_embed()
        await ctx.send(embed=embed, view=view)

        async def update_trade_embed(interaction: discord.Interaction):
            embed, view = await gen_embed()
            await interaction.message.edit(embed=embed, view=view)

        class TradeModal(ui.Modal):
            def __init__(self, currentuser: int):
                super().__init__(
                    title="Add symbols to the trade", timeout=5 * 60  # 5 minutes
                )
                self.currentuser = currentuser

                self.symbol = ui.TextInput(
                    min_length=1,
                    max_length=50,
                    label="Symbol to offer",
                    placeholder="One",
                )
                self.add_item(self.symbol)

                self.amount = ui.TextInput(
                    min_length=1,
                    max_length=50,
                    label="Amount to offer",
                    placeholder="1",
                )
                self.add_item(self.amount)

            async def on_submit(self, interaction: discord.Interaction):
                nonlocal person1, person2, person1accept, person2accept, person1offer, person2offer
                try:
                    if int(self.amount.value) <= 0:
                        raise Exception
                except Exception:
                    return
                if not self.symbol.value.title() in SYMBOLS:
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
                if not database.has_symbol(
                    interaction.guild,
                    interaction.user,
                    self.symbol.value.title(),
                    current_set + int(self.amount.value),
                ):
                    return
                if self.currentuser == 1:
                    if self.symbol.value.title() in person1offer.keys():
                        person1offer[self.symbol.value.title()] += int(
                            self.amount.value
                        )
                    else:
                        person1offer[self.symbol.value.title()] = int(self.amount.value)
                else:
                    if self.symbol.value.title() in person2offer.keys():
                        person2offer[self.symbol.value.title()] += int(
                            self.amount.value
                        )
                    else:
                        person2offer[self.symbol.value.title()] = int(self.amount.value)
                await interaction.response.defer()
                await update_trade_embed(interaction)

    @commands.hybrid_command()
    async def create(self, ctx: commands.Context, symbol: Symbol, count: int = 1):
        """Generate symbols out of thin air. Only useable by Mathman, don't even try."""
        database: "Database" = self.bot.get_cog("Database")
        if not await self.bot.is_owner(ctx.author):
            await ctx.send("You aren't Mathman so you get an hour cooldown lmao")
            database.reset_cooldown(ctx.guild, ctx.author, 3600)
            return
        database.add_symbol(ctx.guild, ctx.author, symbol, count)
        await ctx.send("ok")
        
    @commands.hybrid_command()
    async def leaderboard(self, ctx: commands.Context):
        database: "Database" = self.bot.get_cog("Database")
        server_db = database.get_server(ctx.guild)
        values = {}
        for i in server_db:
            if not i.isdigit():
                continue
            user_id = int(i)
            values[user_id] = 0
            for j in SYMBOLS:
                values[user_id] += server_db[i].get(j, 0)
        sorted_users = sorted(tuple(values), key=lambda x: values[x], reverse=True)
        top_10 = sorted_users[:min(len(values), 10)]
        embed = discord.Embed(color=discord.Color.brand_green(), title="Value Leaderboard")
        for i, v in enumerate(top_10):
            embed.add_field(name=f"{i + 1}. {(await self.bot.fetch_user(v)).name}", value=str(values[v]), inline=False)
        if ctx.author.id not in top_10:
            embed.add_field(name=f"{sorted_users.index(ctx.author.id) + 1}. <@{ctx.author.name}>", value=values[ctx.author.id], inline=False)
        await ctx.send(embed=embed)
        
            

    @craft.autocomplete("sym1")
    @craft.autocomplete("sym2")
    @recipes.autocomplete("symbol")
    @donate.autocomplete("symbol")
    @recycle.autocomplete("symbol")
    @create.autocomplete("symbol")
    async def symbol_autocomplete(self, interaction: discord.Interaction, current: str):
        database: "Database" = self.bot.get_cog("Database")
        return [
            app_commands.Choice(
                name=symbol
                + " (x"
                + str(database.get_symbol(interaction.guild, interaction.user, symbol))
                + ")",
                value=symbol,
            )
            for symbol in SYMBOLS
            if current.lower() in symbol.lower()
            and database.has_symbol(interaction.guild, interaction.user, symbol)
        ]


Symbols.cog_check = Symbols.guild_only


async def setup(bot: commands.Bot):
    await bot.add_cog(Symbols(bot))
