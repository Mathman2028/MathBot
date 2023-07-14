import discord
from discord.ext import commands
from discord import ui
import json
from database import Database

class Achievements(commands.Cog):
    @classmethod
    async def guild_only(_, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage("No DMs!")
        return True
    
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
    @commands.hybrid_command()
    async def achs(self, ctx):
        """See your achievements"""
        Achievements.register(ctx.guild, ctx.author)
        user_db = Database.get_member(ctx.guild, ctx.author)["achs"]
        category = "Symbols"
        async def gen_embed():
            nonlocal category
            embed = discord.Embed(color=discord.Color.brand_green(), title="Achievements", description="Category: " + category)
            for k, v in Achievements.achievements[category].items():
                emoji = "✅" if Achievements.has_ach(ctx.guild, ctx.author, k) else "⬜"
                embed.add_field(name=emoji + " " + v["name"], value=v["desc"] if category != "Random" or Achievements.has_ach(ctx.guild, ctx.author, k) else "???")
            view = ui.View()
            async def gen_callback(new_category):
                nonlocal category
                async def callback(interaction):
                    nonlocal category
                    nonlocal new_category
                    if interaction.user != ctx.author:
                        await interaction.response.send_message("Not your achievement embed", ephemeral=True)
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
Achievements.cog_check = Achievements.guild_only

async def setup(bot):
    await bot.add_cog(Achievements(bot))
