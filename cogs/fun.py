import random

import discord
from discord.ext import commands


class Fun(commands.Cog):
    """أوامر ترفيهية"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="تصويت")
    async def تصويت(self, ctx, *, سؤال):
        embed = discord.Embed(title="📊 تصويت جديد", description=سؤال, color=discord.Color.blue())
        embed.set_footer(text=f"بواسطة {ctx.author.display_name}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.command(name="كورة_سحرية")
    async def كورة_سحرية(self, ctx, *, سؤال):
        responses = [
            "أكيد ✅", "بالتأكيد لا ❌", "ممكن 🤔", "غير مؤكد، جرب مرة ثانية 🔄",
            "الاحتمال ضعيف", "نعم بدون شك", "لا تعتمد عليه", "اسأل لاحقاً 🕐",
        ]
        embed = discord.Embed(color=discord.Color.dark_purple())
        embed.add_field(name="❓ السؤال", value=سؤال, inline=False)
        embed.add_field(name="🎱 الجواب", value=random.choice(responses), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="نرد")
    async def نرد(self, ctx, عدد_الاوجه: int = 6):
        if عدد_الاوجه < 2:
            await ctx.send("⚠️ لازم يكون عدد الأوجه 2 أو أكثر.")
            return
        result = random.randint(1, عدد_الاوجه)
        await ctx.send(f"🎲 رميت نرد بـ {عدد_الاوجه} أوجه وطلع: **{result}**")

    @commands.command(name="عملة")
    async def عملة(self, ctx):
        result = random.choice(["كتابة 🪙", "صورة 🪙"])
        await ctx.send(f"العملة طلعت: **{result}**")

    @commands.command(name="اختيار")
    async def اختيار(self, ctx, *, خيارات):
        choices = [o.strip() for o in خيارات.split(",") if o.strip()]
        if len(choices) < 2:
            await ctx.send("⚠️ عطني خيارين على الأقل مفصولين بفاصلة، مثال: `!اختيار بيتزا, برجر, سوشي`")
            return
        await ctx.send(f"🎯 اخترت: **{random.choice(choices)}**")

    @commands.command(name="قول")
    async def قول(self, ctx, *, رسالة):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(رسالة)


async def setup(bot):
    await bot.add_cog(Fun(bot))
