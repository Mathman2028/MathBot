import discord
from discord.ext import commands
import json
import time


class Database(commands.Cog):
    """The base functions dealing with handling the database."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _load(self):
        with open("db.json", "r") as f:
            self.db = json.load(f)

    def save(self):
        with open("db.json", "w") as f:
            json.dump(self.db, f)

    def _register_member(self, server: discord.Guild, member: discord.Member):
        db = self.db
        if not str(server.id) in db.keys():
            db[str(server.id)] = {}
        if not str(member.id) in db[str(server.id)].keys():
            db[str(server.id)][str(member.id)] = {}
            self.save()

    def _get_member(self, server: discord.Guild, member: discord.Member):
        self._register_member(server, member)
        return self.db[str(server.id)][str(member.id)]

    def get_server(self, server: discord.Guild):
        db = self.db
        if not str(server.id) in db.keys():
            db[str(server.id)] = {}
            self.save()
        return db[str(server.id)]
    
    def add_symbol(
        self, server: discord.Guild, member: discord.Member, symbol: str, count: int = 1
    ):
        user_db = self._get_member(server, member)
        if symbol in user_db.keys():
            user_db[symbol] += count
        else:
            user_db[symbol] = count
        self.save()

    def get_symbol(self, server: discord.Guild, member: discord.Member, symbol: str):
        user_db = self._get_member(server, member)
        return user_db.get(symbol, 0)
    
    def reset_cooldown(
        self, server: discord.Guild, member: discord.Member, cooldown: int = 600
    ):
        user_db = self._get_member(server, member)
        user_db["cooldown"] = time.time() + cooldown
        self.save()

    def on_cooldown(self, server: discord.Guild, member: discord.Member):
        user_db = self._get_member(server, member)
        if "cooldown" in user_db.keys():
            return user_db["cooldown"] > time.time()
        else:
            return False

    def get_cooldown_end(self, server: discord.Guild, member: discord.Member):
        user_db = self._get_member(server, member)
        if "cooldown" in user_db.keys():
            return user_db["cooldown"]
        else:
            return None

    def has_symbol(
        self, server: discord.Guild, member: discord.Member, symbol: str, count: int = 1
    ):
        user_db = self._get_member(server, member)
        return symbol in user_db.keys() and user_db[symbol] >= count

    @commands.hybrid_command()
    async def cleardata(self, ctx: commands.Context):
        """Clears your data. CANNOT BE UNDONE."""
        del self.db[str(ctx.guild.id)][str(ctx.author.id)]
        self.save()
        await ctx.send("Your data has been deleted. I hope you don't regret this...")


async def setup(bot: commands.Bot):
    database = Database(bot)
    database._load()
    await bot.add_cog(database)
