import discord
from discord.ext import commands
import typing
import random
import math
from discord import ui
from discord import app_commands

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
("Circle", "Line"): "Cone",
("Cone", "Plane"): "Conic Section",
("Plane", "Infinity"): "Space",
("Set", "Addition"): "Union",
("Set", "Multiplication"): "Intersection",
("Real Numbers", "Real Numbers"): "Ordered Pair",
("Set", "Ordered Pair"): "Function",
}

base_symbols = ["One", "Increment", "Inverse"]
recycle_results = base_symbols + ["Point"]
dungeon_results = base_symbols + ["Set"]

bonus_unlocks = {
"Complex Numbers": "Real Numbers",
"Logarithm": "Multiplication",
"Pi": "Point",
"Space": "Infinity",
}

special_symbols = {"Point", "Set"}

symbols = list(set(base_symbols) | set(recipes.values()) | special_symbols)
symbols.sort()

class Symbols(commands.Cog):
    """All the commands relating to the bot's symbol system."""
    async def guild_only(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage("No DMs!")
        return True
    
    class Symbol(commands.Converter):
        async def convert(self, ctx, argument):
            if not argument.title() in symbols:
                possible = []
                for i in symbols:
                    if i.startswith(argument.title()):
                        possible.append(i)
                if len(possible) == 1:
                    return possible[0]
                else:
                    raise commands.BadArgument(message=f"{argument} isn't a valid symbol!")
            return argument.title()

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def inv(self, ctx, member:typing.Optional[discord.Member]):
        """Displays your inventory"""
        Database = self.bot.get_cog("Database")
        if member is None:
            member = ctx.author
        user = Database.get_member(ctx.guild, member)
        discovered = len(set(symbols) & set(user.keys()))
        embed = discord.Embed(color=discord.Color.brand_green(), title=f"{member.name}'s inventory", description=f"Symbols discovered: {discovered}/{len(symbols)}")
        for i in symbols:
            if Database.has_symbol(ctx.guild, member, i):
                embed.add_field(name=i, value=user[i])
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def getsymbol(self, ctx):
        """Get some base symbols every 10 minutes"""
        Database = self.bot.get_cog("Database")
        Achievements = self.bot.get_cog("Achievements")
        pool = base_symbols * 3
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

    @commands.hybrid_command()
    async def craft(self, ctx, sym1: Symbol, sym2: Symbol, amt:int=1):
        """Craft symbols to get better symbols"""
        Database = self.bot.get_cog("Database")
        Achievements = self.bot.get_cog("Achievements")
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
            await ctx.send(f"Congratulations! Because you have {result}, you can now get {bonus_unlocks[result]} from getsymbol!")
            await Achievements.give_ach(ctx.guild, ctx.author, "Symbols", "bonus_unlock", ctx.channel)

    @commands.hybrid_command()
    async def recipes(self, ctx, symbol: Symbol):
        """Tells you what can be crafted with or to make a certain symbol"""
        Database = self.bot.get_cog("Database")
        output = ""
        user_db = Database.get_member(ctx.guild, ctx.author)
        async def process_symbol(symbol):
            if symbol in user_db.keys():
                return symbol
            else:
                return "???"
        for k, v in recipes.items():
            if symbol not in k and symbol != v:
                continue
            output += f"{await process_symbol(k[0])} + {await process_symbol(k[1])} = {await process_symbol(v)}\n"
        await ctx.send(embed=discord.Embed(color=discord.Color.brand_green(), title=f"Recipes with {symbol}", description=output))

    @commands.hybrid_command()
    async def hint(self, ctx):
        """Shows a list of recipes you should try next"""
        Database = self.bot.get_cog("Database")
        output = ""
        user_db = Database.get_member(ctx.guild, ctx.author)
        for k, v in recipes.items():
            if k[0] in user_db.keys() and k[1] in user_db.keys() and v not in user_db.keys():
                output += f"{k[0]} + {k[1]}\n"
        output = "Nothing." if not output else output
        await ctx.send(embed=discord.Embed(color=discord.Color.brand_green(), title="New recipes", description=output))

    @commands.hybrid_command()
    async def donate(self, ctx, reciever: discord.Member, symbol: Symbol, amount:int=1):
        """Give away your symbols"""
        Database = self.bot.get_cog("Database")
        Achievements = self.bot.get_cog("Achivements")
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

    @commands.hybrid_command()
    async def recycle(self, ctx, symbol: Symbol, amount:int=2):
        """Recycle n symbols, get n-1 symbols"""
        Database = self.bot.get_cog("Database")
        if amount < 2:
            await ctx.send("Amount must be 2 or greater.")
            return
        if not Database.has_symbol(ctx.guild, ctx.author, symbol, amount):
            await ctx.send("You don't have enough!")
        user = Database.get_member(ctx.guild, ctx.author)
        user[symbol] -= amount
        output = ""
        for _ in range(amount - 1):
            new_symbol = random.choice(recycle_results)
            while new_symbol == symbol:
                new_symbol = random.choice(recycle_results)
            output += new_symbol + "\n"
            Database.add_symbol(ctx.guild, ctx.author, new_symbol)
        await ctx.send(embed=discord.Embed(color=discord.Color.brand_green(), title="Recycle results", description=output))

    @commands.hybrid_command()
    async def trade(self, ctx, person2: discord.Member):
        Database = self.bot.get_cog("Database")
        Achievements = self.bot.get_cog("Achievements")
        """Trade your symbols"""
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

Symbols.cog_check = Symbols.guild_only

async def setup(bot):
    await bot.add_cog(Symbols(bot))
    Database = bot.get_cog("Database")
    @Symbols.craft.autocomplete("sym1")
    @Symbols.craft.autocomplete("sym2")
    @Symbols.recipes.autocomplete("symbol")
    @Symbols.donate.autocomplete("symbol")
    @Symbols.recycle.autocomplete("symbol")
    async def symbol_autocomplete(interaction, current):
        return [app_commands.Choice(name=symbol + " (x" + str(Database.get_member(interaction.guild, interaction.user)[symbol]) + ")", value=symbol) for symbol in symbols if current.lower() in symbol.lower() and Database.has_symbol(interaction.guild, interaction.user, symbol)]
    