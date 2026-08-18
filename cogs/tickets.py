import discord
from discord.ext import commands

import database


class TicketButton(discord.ui.View):
    """زر فتح تذكرة — دائم (Persistent View)"""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 فتح تذكرة", style=discord.ButtonStyle.blurple, custom_id="open_ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        existing = await database.get_open_ticket_for_user(user.id, guild.id)
        if existing:
            channel = guild.get_channel(existing)
            if channel:
                await interaction.response.send_message(
                    f"⚠️ عندك تذكرة مفتوحة أصلاً: {channel.mention}", ephemeral=True
                )
                return

        category_id, log_channel_id, support_role_id = await database.get_ticket_settings(guild.id)
        category = guild.get_channel(category_id) if category_id else None
        support_role = guild.get_role(support_role_id) if support_role_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel_name = f"تذكرة-{user.name}"[:90]
        ticket_channel = await guild.create_text_channel(
            name=channel_name, category=category, overwrites=overwrites
        )

        await database.create_ticket(ticket_channel.id, guild.id, user.id)

        embed = discord.Embed(
            title="📩 تذكرة دعم جديدة",
            description=f"أهلاً {user.mention}! اشرح مشكلتك أو طلبك هنا وفريق الدعم بيرد عليك قريب.",
            color=discord.Color.blurple(),
        )
        await ticket_channel.send(
            content=support_role.mention if support_role else None,
            embed=embed,
            view=CloseTicketButton(),
        )

        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {ticket_channel.mention}", ephemeral=True)

        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"📩 {user.mention} فتح تذكرة جديدة: {ticket_channel.mention}")


class CloseTicketButton(discord.ui.View):
    """زر إغلاق التذكرة — دائم"""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 إغلاق التذكرة", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket = await database.get_ticket(interaction.channel.id)
        if not ticket:
            await interaction.response.send_message("⚠️ هذي مو روم تذكرة.", ephemeral=True)
            return

        guild_id, user_id, status = ticket
        if status == "closed":
            await interaction.response.send_message("⚠️ التذكرة مقفولة أصلاً.", ephemeral=True)
            return

        await database.close_ticket(interaction.channel.id)
        await interaction.response.send_message("🔒 بتقفل التذكرة خلال 5 ثواني...")

        _, log_channel_id, _ = await database.get_ticket_settings(guild_id)
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(
                    f"🔒 تم إغلاق تذكرة {interaction.channel.name} بواسطة {interaction.user.mention}"
                )

        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()


class Tickets(commands.Cog):
    """نظام تذاكر الدعم"""

    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketButton())
        bot.add_view(CloseTicketButton())

    @commands.command(name="تذاكر_اعداد")
    @commands.has_permissions(administrator=True)
    async def تذاكر_اعداد(
        self,
        ctx,
        قسم: discord.CategoryChannel = None,
        روم_السجل: discord.TextChannel = None,
        رتبة_الدعم: discord.Role = None,
    ):
        await database.set_ticket_settings(
            ctx.guild.id,
            category_id=قسم.id if قسم else None,
            log_channel_id=روم_السجل.id if روم_السجل else None,
            support_role_id=رتبة_الدعم.id if رتبة_الدعم else None,
        )
        parts = []
        if قسم:
            parts.append(f"القسم: {قسم.mention}")
        if روم_السجل:
            parts.append(f"روم السجل: {روم_السجل.mention}")
        if رتبة_الدعم:
            parts.append(f"رتبة الدعم: {رتبة_الدعم.mention}")
        await ctx.send("✅ تم حفظ إعدادات التذاكر" + (" — " + "، ".join(parts) if parts else ""))

    @commands.command(name="تذاكر_ارسال")
    @commands.has_permissions(administrator=True)
    async def تذاكر_ارسال(self, ctx):
        embed = discord.Embed(
            title="📩 الدعم الفني",
            description="اضغط الزر تحت عشان تفتح تذكرة وفريقنا يساعدك.",
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed, view=TicketButton())


async def setup(bot):
    await bot.add_cog(Tickets(bot))
