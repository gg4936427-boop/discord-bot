import discord
from discord.ext import commands

import database


class Settings(commands.Cog):
    """إعدادات السيرفر"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ترحيب")
    @commands.has_permissions(administrator=True)
    async def ترحيب(self, ctx, روم: discord.TextChannel):
        await database.set_welcome_channel(ctx.guild.id, روم.id)
        await ctx.send(f"✅ تم تعيين روم الترحيب إلى {روم.mention}")


async def setup(bot):
    await bot.add_cog(Settings(bot))
