import discord
from discord.ext import commands

import database


class Shop(commands.Cog):
    """متجر بسيط مرتبط برصيد الأعضاء"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="المتجر")
    async def المتجر(self, ctx):
        items = await database.get_shop_items(ctx.guild.id)
        if not items:
            await ctx.send("المتجر فاضي حالياً. لو أدمن، ضيف عنصر بـ `!اضافة_عنصر`.")
            return

        embed = discord.Embed(title=f"🛒 متجر {ctx.guild.name}", color=discord.Color.teal())
        for name, price, description in items:
            value = f"💰 {price} عملة"
            if description:
                value += f"\n{description}"
            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(text="اشتري بأمر !شراء <اسم العنصر>")
        await ctx.send(embed=embed)

    @commands.command(name="شراء")
    async def شراء(self, ctx, *, اسم_العنصر):
        item = await database.get_shop_item(ctx.guild.id, اسم_العنصر)
        if not item:
            await ctx.send("❌ ما فيه عنصر بهذا الاسم بالمتجر. اكتب `!المتجر` عشان تشوف كل العناصر.")
            return

        name, price, description = item
        balance = await database.get_balance(ctx.author.id, ctx.guild.id)

        if balance < price:
            await ctx.send(f"❌ رصيدك ما يكفي. تحتاج {price} عملة وعندك {balance}.")
            return

        await database.update_balance(ctx.author.id, ctx.guild.id, -price)
        await database.add_inventory_item(ctx.author.id, ctx.guild.id, name, 1)

        await ctx.send(f"✅ اشتريت **{name}** مقابل {price} عملة! تفقد مخزونك بـ `!مخزوني`")

    @commands.command(name="اضافة_عنصر")
    @commands.has_permissions(administrator=True)
    async def اضافة_عنصر(self, ctx, اسم_العنصر, السعر: int, *, الوصف=""):
        if السعر <= 0:
            await ctx.send("⚠️ السعر لازم يكون أكبر من صفر.")
            return
        await database.add_shop_item(ctx.guild.id, اسم_العنصر, السعر, الوصف)
        await ctx.send(f"✅ تمت إضافة **{اسم_العنصر}** للمتجر بسعر {السعر} عملة.")

    @commands.command(name="حذف_عنصر")
    @commands.has_permissions(administrator=True)
    async def حذف_عنصر(self, ctx, *, اسم_العنصر):
        removed = await database.remove_shop_item(ctx.guild.id, اسم_العنصر)
        if removed:
            await ctx.send(f"✅ تم حذف **{اسم_العنصر}** من المتجر.")
        else:
            await ctx.send("❌ ما لقيت عنصر بهذا الاسم.")


async def setup(bot):
    await bot.add_cog(Shop(bot))
