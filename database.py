import discord
from discord.ext import commands
from discord import ui
import json
import time

class Database(commands.Cog):
    """The base functions dealing with handling the database."""
    def __init__(self, bot):
        self.bot = bot
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
    @commands.hybrid_command()
    async def cleardata(self, ctx):
        """Clears your data. CANNOT BE UNDONE."""
        del Database.db[str(ctx.guild.id)][str(ctx.author.id)]
        Database.save()
        await ctx.send("Your data has been deleted. I hope you don't regret this...")

async def setup(bot):
    await bot.add_cog(Database(bot))