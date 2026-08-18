import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """أوامر إدارية للمشرفين"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="مسح")
    @commands.has_permissions(manage_messages=True)
    async def مسح(self, ctx, عدد: int = 5):
        if عدد < 1 or عدد > 100:
            await ctx.send("⚠️ اختر رقم بين 1 و 100.")
            return
        deleted = await ctx.channel.purge(limit=عدد + 1)
        msg = await ctx.send(f"🧹 تم مسح {len(deleted) - 1} رسالة.")
        await msg.delete(delay=3)

    @commands.command(name="طرد")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def طرد(self, ctx, عضو: discord.Member, *, السبب="ما فيه سبب محدد"):
        if عضو.top_role >= ctx.author.top_role:
            await ctx.send("❌ ما تقدر تطرد عضو رتبته أعلى منك أو تساويك.")
            return
        await عضو.kick(reason=السبب)
        await ctx.send(f"👢 تم طرد {عضو.mention} — السبب: {السبب}")

    @commands.command(name="حظر")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def حظر(self, ctx, عضو: discord.Member, *, السبب="ما فيه سبب محدد"):
        if عضو.top_role >= ctx.author.top_role:
            await ctx.send("❌ ما تقدر تحظر عضو رتبته أعلى منك أو تساويك.")
            return
        await عضو.ban(reason=السبب)
        await ctx.send(f"🔨 تم حظر {عضو.mention} — السبب: {السبب}")

    @commands.command(name="اسكات")
    @commands.has_permissions(moderate_members=True)
    async def اسكات(self, ctx, عضو: discord.Member, دقايق: int = 10, *, السبب="ما فيه سبب محدد"):
        import datetime

        duration = datetime.timedelta(minutes=دقايق)
        await عضو.timeout(duration, reason=السبب)
        await ctx.send(f"🔇 تم إسكات {عضو.mention} لمدة {دقايق} دقيقة — السبب: {السبب}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
