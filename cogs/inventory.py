import discord
from discord.ext import commands

import database


class Inventory(commands.Cog):
    """مخزون الأعضاء"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="مخزوني")
    async def مخزوني(self, ctx, عضو: discord.Member = None):
        عضو = عضو or ctx.author
        items = await database.get_inventory(عضو.id, ctx.guild.id)

        embed = discord.Embed(title=f"🎒 مخزون {عضو.display_name}", color=discord.Color.dark_teal())
        if not items:
            embed.description = "المخزون فاضي."
        else:
            lines = [f"**{name}** × {qty}" for name, qty in items]
            embed.description = "\n".join(lines)
        await ctx.send(embed=embed)

    @commands.command(name="اعطاء_عنصر")
    @commands.has_permissions(administrator=True)
    async def اعطاء_عنصر(self, ctx, عضو: discord.Member, الكمية: int, *, اسم_العنصر):
        if الكمية <= 0:
            await ctx.send("⚠️ الكمية لازم تكون أكبر من صفر.")
            return
        await database.add_inventory_item(عضو.id, ctx.guild.id, اسم_العنصر, الكمية)
        await ctx.send(f"✅ تمت إضافة **{اسم_العنصر}** × {الكمية} لمخزون {عضو.mention}")

    @commands.command(name="سحب_عنصر")
    @commands.has_permissions(administrator=True)
    async def سحب_عنصر(self, ctx, عضو: discord.Member, الكمية: int, *, اسم_العنصر):
        if الكمية <= 0:
            await ctx.send("⚠️ الكمية لازم تكون أكبر من صفر.")
            return
        success = await database.remove_inventory_item(عضو.id, ctx.guild.id, اسم_العنصر, الكمية)
        if success:
            await ctx.send(f"✅ تم سحب **{اسم_العنصر}** × {الكمية} من مخزون {عضو.mention}")
        else:
            await ctx.send("❌ العضو ما عنده كمية كافية من هذا العنصر.")


async def setup(bot):
    await bot.add_cog(Inventory(bot))
