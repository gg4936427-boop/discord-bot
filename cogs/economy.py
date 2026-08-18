from datetime import datetime, timedelta

import discord
from discord.ext import commands

import database


class Economy(commands.Cog):
    """نظام اقتصاد بسيط بالعملة داخل السيرفر"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="رصيد")
    async def رصيد(self, ctx, عضو: discord.Member = None):
        عضو = عضو or ctx.author
        bal = await database.get_balance(عضو.id, ctx.guild.id)
        embed = discord.Embed(
            title=f"💰 رصيد {عضو.display_name}",
            description=f"**{bal}** عملة",
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="يومي")
    async def يومي(self, ctx):
        last = await database.get_last_daily(ctx.author.id, ctx.guild.id)
        now = datetime.utcnow()

        if last:
            last_dt = datetime.fromisoformat(last)
            if now - last_dt < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last_dt)
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes = remainder // 60
                await ctx.send(f"⏳ سبق واخذت مكافأتك اليوم. تعال بعد {hours}س {minutes}د.")
                return

        reward = self.bot.config.DAILY_REWARD
        await database.update_balance(ctx.author.id, ctx.guild.id, reward)
        await database.set_last_daily(ctx.author.id, ctx.guild.id, now.isoformat())
        await ctx.send(f"✅ حصلت على **{reward}** عملة! تعال بكرة تاخذ مكافأة ثانية.")

    @commands.command(name="تحويل")
    async def تحويل(self, ctx, عضو: discord.Member, مبلغ: int):
        if مبلغ <= 0:
            await ctx.send("⚠️ المبلغ لازم يكون أكبر من صفر.")
            return
        if عضو.id == ctx.author.id:
            await ctx.send("⚠️ ما تقدر تحول لنفسك.")
            return

        sender_balance = await database.get_balance(ctx.author.id, ctx.guild.id)
        if sender_balance < مبلغ:
            await ctx.send("❌ رصيدك ما يكفي.")
            return

        await database.update_balance(ctx.author.id, ctx.guild.id, -مبلغ)
        await database.update_balance(عضو.id, ctx.guild.id, مبلغ)
        await ctx.send(f"✅ حولت **{مبلغ}** عملة إلى {عضو.mention}")

    @commands.command(name="المتصدرين")
    async def المتصدرين(self, ctx):
        top = await database.get_leaderboard(ctx.guild.id, limit=10)
        if not top:
            await ctx.send("ما فيه بيانات بعد.")
            return

        lines = []
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, balance) in enumerate(top):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"مستخدم ({user_id})"
            prefix = medals[i] if i < 3 else f"{i + 1}."
            lines.append(f"{prefix} **{name}** — {balance} عملة")

        embed = discord.Embed(
            title=f"🏆 ترتيب الأغنياء في {ctx.guild.name}",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
