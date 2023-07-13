from discord.ext import commands
import json
import time

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