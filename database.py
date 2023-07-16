import discord
from discord.ext import commands
from discord import ui
import json
import time

class Database(commands.Cog):
    """The base functions dealing with handling the database."""
    def __init__(self, bot):
        self.bot = bot
    def load(self):
        with open("db.json", "r") as f:
            self.db = json.load(f)
    def save(self):
        with open("db.json", "w") as f:
            json.dump(self.db, f)
    def register_member(self, server, member):
        db = self.db
        if not str(server.id) in db.keys():
            db[str(server.id)] = {}
        if not str(member.id) in db[str(server.id)].keys():
            db[str(server.id)][str(member.id)] = {}
            self.save()
    def get_member(self, server, member):
        self.register_member(server, member)
        return self.db[str(server.id)][str(member.id)]
    def add_symbol(self, server, member, symbol, count=1):
        user_db = self.get_member(server, member)
        if symbol in user_db.keys():
            user_db[symbol] += count
        else:
            user_db[symbol] = count
        self.save()
    def reset_cooldown(self, server, member, cooldown=600):
        user_db = self.get_member(server, member)
        user_db["cooldown"] = time.time() + cooldown
        self.save()
    def on_cooldown(self, server, member):
        user_db = self.get_member(server, member)
        if "cooldown" in user_db.keys():
            return user_db["cooldown"] > time.time()
        else:
            return False
    def has_symbol(self, server, member, symbol, count=1):
        user_db = self.get_member(server, member)
        return symbol in user_db.keys() and user_db[symbol] >= count
    @commands.hybrid_command()
    async def cleardata(self, ctx):
        """Clears your data. CANNOT BE UNDONE."""
        del self.db[str(ctx.guild.id)][str(ctx.author.id)]
        self.save()
        await ctx.send("Your data has been deleted. I hope you don't regret this...")

async def setup(bot):
    database = Database(bot)
    database.load()
    await bot.add_cog(database)