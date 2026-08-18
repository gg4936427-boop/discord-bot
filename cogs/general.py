import platform
import time

import discord
from discord.ext import commands

start_time = time.time()


class General(commands.Cog):
    """أوامر عامة عن البوت والسيرفر والأعضاء"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="مساعدة")
    async def مساعدة(self, ctx):
        embed = discord.Embed(
            title="📖 قائمة الأوامر",
            description="كل الأوامر تبدأ بعلامة `!`",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="🔧 عامة",
            value=(
                "`!سرعة` سرعة الاستجابة\n"
                "`!معلومات_البوت` معلومات البوت\n"
                "`!معلومات_عضو [@عضو]` معلومات عضو\n"
                "`!معلومات_السيرفر` معلومات السيرفر\n"
                "`!صورة [@عضو]` صورة العضو"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎉 ترفيهية",
            value=(
                "`!تصويت <سؤال>` تصويت\n"
                "`!كورة_سحرية <سؤال>` كرة سحرية\n"
                "`!نرد [عدد_الاوجه]` نرد\n"
                "`!عملة` قلب عملة\n"
                "`!اختيار <خيارات>` اختيار عشوائي\n"
                "`!قول <رسالة>` يكرر رسالتك"
            ),
            inline=False,
        )
        embed.add_field(
            name="💰 اقتصاد",
            value=(
                "`!رصيد [@عضو]` عرض الرصيد\n"
                "`!يومي` مكافأة يومية\n"
                "`!تحويل @عضو مبلغ` تحويل رصيد\n"
                "`!المتصدرين` ترتيب الأغنياء"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛡️ إدارة",
            value=(
                "`!مسح <عدد>` مسح رسائل\n"
                "`!طرد @عضو` طرد عضو\n"
                "`!حظر @عضو` حظر عضو\n"
                "`!اسكات @عضو [دقايق]` إسكات عضو\n"
                "`!ترحيب #روم` روم الترحيب"
            ),
            inline=False,
        )
        embed.add_field(
            name="📩 تذاكر",
            value=(
                "`!تذاكر_اعداد [قسم] [روم_سجل] [رتبة]` (أدمن)\n"
                "`!تذاكر_ارسال` يرسل رسالة فيها زر فتح تذكرة (أدمن)"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛒 متجر ومخزون",
            value=(
                "`!المتجر` عرض المتجر\n"
                "`!شراء <اسم العنصر>` شراء عنصر\n"
                "`!مخزوني [@عضو]` عرض المخزون\n"
                "`!اضافة_عنصر <اسم> <سعر> [وصف]` (أدمن)\n"
                "`!حذف_عنصر <اسم>` (أدمن)\n"
                "`!اعطاء_عنصر @عضو <كمية> <اسم>` (أدمن)\n"
                "`!سحب_عنصر @عضو <كمية> <اسم>` (أدمن)"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(name="سرعة")
    async def سرعة(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! السرعة: `{latency}ms`")

    @commands.command(name="معلومات_البوت")
    async def معلومات_البوت(self, ctx):
        uptime_seconds = int(time.time() - start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(title="🤖 معلومات البوت", color=discord.Color.green())
        embed.add_field(name="عدد السيرفرات", value=str(len(self.bot.guilds)))
        embed.add_field(name="مدة التشغيل", value=f"{hours}س {minutes}د {seconds}ث")
        embed.add_field(name="Python", value=platform.python_version())
        embed.add_field(name="discord.py", value=discord.__version__)
        await ctx.send(embed=embed)

    @commands.command(name="معلومات_عضو")
    async def معلومات_عضو(self, ctx, عضو: discord.Member = None):
        عضو = عضو or ctx.author
        embed = discord.Embed(title=f"معلومات {عضو.display_name}", color=عضو.color)
        embed.set_thumbnail(url=عضو.display_avatar.url)
        embed.add_field(name="اليوزر", value=str(عضو), inline=True)
        embed.add_field(name="الآيدي", value=عضو.id, inline=True)
        embed.add_field(
            name="تاريخ الانضمام",
            value=عضو.joined_at.strftime("%Y-%m-%d") if عضو.joined_at else "غير معروف",
            inline=True,
        )
        embed.add_field(
            name="تاريخ إنشاء الحساب", value=عضو.created_at.strftime("%Y-%m-%d"), inline=True
        )
        roles = [role.mention for role in عضو.roles if role.name != "@everyone"]
        embed.add_field(name="الرتب", value=" ".join(roles) if roles else "لا يوجد", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="معلومات_السيرفر")
    async def معلومات_السيرفر(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"معلومات سيرفر {guild.name}", color=discord.Color.orange())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="المالك", value=str(guild.owner), inline=True)
        embed.add_field(name="عدد الأعضاء", value=guild.member_count, inline=True)
        embed.add_field(name="تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="عدد الرومات النصية", value=len(guild.text_channels), inline=True)
        embed.add_field(name="عدد الرومات الصوتية", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="عدد الرتب", value=len(guild.roles), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="صورة")
    async def صورة(self, ctx, عضو: discord.Member = None):
        عضو = عضو or ctx.author
        embed = discord.Embed(title=f"صورة {عضو.display_name}", color=discord.Color.purple())
        embed.set_image(url=عضو.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
