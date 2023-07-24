import discord
from discord.ext import commands
from discord import ui
import json


class Achievements(commands.Cog):
    """Everything relating to giving, getting, viewing, and checking achievements."""

    async def guild_only(self, ctx: commands.Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage("No DMs!")
        return True

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load()

    def load(self):
        with open("achs.json", "r") as f:
            self.achievements = json.load(f)

    def register(self, guild: discord.Guild, member: discord.Member):
        Database = self.bot.get_cog("Database")
        user_db = Database.get_member(guild, member)
        if "achs" not in user_db.keys():
            user_db["achs"] = {}
        Database.save()

    def has_ach(self, guild: discord.Guild, member: discord.Member, ach: str):
        self.register(guild, member)
        Database = self.bot.get_cog("Database")
        user_db = Database.get_member(guild, member)["achs"]
        if ach not in user_db.keys():
            return False
        return user_db[ach]

    async def give_ach(
        self,
        guild: discord.Guild,
        member: discord.Member,
        category: str,
        ach: str,
        messageable: discord.abc.Messageable,
    ):
        self.register(guild, member)
        Database = self.bot.get_cog("Database")
        new_ach = not self.has_ach(guild, member, ach)
        Database.get_member(guild, member)["achs"][ach] = True
        Database.save()
        ach_data = self.achievements[category][ach]
        if new_ach:
            embed = discord.Embed(
                color=discord.Color.brand_green(),
                title="Achievement get: " + ach_data["name"],
                description=ach_data["desc"],
            )
            embed.set_footer(text=f"Achieved by {member.name}")
            await messageable.send(embed=embed)

    @commands.hybrid_command()
    async def achs(self, ctx: commands.Context):
        """See your achievements"""
        Database = self.bot.get_cog("Database")
        self.register(ctx.guild, ctx.author)
        category = "Symbols"

        async def gen_embed():
            nonlocal category
            embed = discord.Embed(
                color=discord.Color.brand_green(),
                title="Achievements",
                description="Category: " + category,
            )
            for k, v in self.achievements[category].items():
                emoji = "✅" if self.has_ach(ctx.guild, ctx.author, k) else "⬜"
                embed.add_field(
                    name=emoji + " " + v["name"],
                    value=v["desc"]
                    if category != "Random" or self.has_ach(ctx.guild, ctx.author, k)
                    else "???",
                )
            view = ui.View()

            async def gen_callback(new_category: str):
                nonlocal category

                async def callback(interaction: discord.Interaction):
                    nonlocal category
                    nonlocal new_category
                    if interaction.user != ctx.author:
                        await interaction.response.send_message(
                            "Not your achievement embed", ephemeral=True
                        )
                        await self.give_ach(
                            interaction.guild,
                            interaction.user,
                            "Random",
                            "nope",
                            interaction.channel,
                        )
                    category = new_category
                    embed, view = await gen_embed()
                    await interaction.response.edit_message(embed=embed, view=view)

                return callback

            for i in self.achievements.keys():
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Achievements(bot))
