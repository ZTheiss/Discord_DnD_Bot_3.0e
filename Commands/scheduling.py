import discord
from discord import app_commands
import aiosqlite
from datetime import datetime
from datetime import timedelta
from utils.utils import *
from utils.variables import *


# --- Scheduling Commands ---

class SchedulingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="session_schedule", description="Schedule a new game session")
    @app_commands.describe(
        title="Session title or notes",
        session_time="Session date and time (YYYY-MM-DD HH:MM in 24h CST)"
    )
    async def session_schedule(self, interaction: discord.Interaction, title: str, session_time: str):
        # Validate datetime format
        try:
            scheduled_time = datetime.strptime(session_time, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.now().astimezone().tzinfo)  # Set timezone to local CST
        except ValueError:
            await interaction.response.send_message("❌ Invalid datetime format! Use `YYYY-MM-DD HH:MM` in 24h CST.", ephemeral=True)
            return

        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                INSERT INTO sessions (title, scheduled_for, created_by)
                VALUES (?, ?, ?)
            """, (title, scheduled_time.isoformat(), interaction.user.name))
            await db.commit()
            
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("❌ Could not find guild context.", ephemeral=True)
            return

        try:
            scheduled_event = await guild.create_scheduled_event(
                name=title,
                start_time=scheduled_time,
                end_time=scheduled_time + timedelta(hours=4),
                description=f"📌 In-person session at: 16610 Hardee St, Belton, MO 64012 \nScheduled by {interaction.user.display_name}",
                location="16610 Hardee St, Belton, MO 64012",
                entity_type=discord.EntityType.external,
                privacy_level=discord.PrivacyLevel.guild_only
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to create Discord event: {e}", ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Session **{title}** scheduled for {scheduled_time} UTC!\nDiscord event created: {scheduled_event.url}",
            ephemeral=False
        )


    @app_commands.command(name="session_list", description="List upcoming scheduled sessions")
    async def session_list(self, interaction: discord.Interaction):
        # Use US Central Standard Time (CST, UTC-6)
        from datetime import timezone, timedelta

        CST = timezone(timedelta(hours=-6))
        now = datetime.now(CST).isoformat()
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT session_id, title, scheduled_for, created_by FROM sessions WHERE scheduled_for > ? ORDER BY scheduled_for ASC",
                (now,))
            rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message("No upcoming sessions scheduled.", ephemeral=True)
            return

        embed = discord.Embed(title="📅 Upcoming Sessions", color=0x0099FF)
        for session_id, title, sched_for, created_by in rows:
            dt_obj = datetime.fromisoformat(sched_for).astimezone(CST)
            embed.add_field(
                name=title,
                value=f"Scheduled for: {dt_obj.strftime('%Y-%m-%d %H:%M')} CST\nCreated by: {created_by}\nID: {session_id}",
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="session_remove", description="Remove a scheduled session by ID")
    @app_commands.describe(session_id="ID of the session to remove")
    async def session_remove(self, interaction: discord.Interaction, session_id: int):
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("SELECT title FROM sessions WHERE session_id = ?", (session_id,))
            row = await cursor.fetchone()
            if not row:
                await interaction.response.send_message(f"⚠️ Session with ID {session_id} not found.", ephemeral=True)
                return
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            await db.commit()

        await interaction.response.send_message(f"✅ Removed session **{row[0]}** (ID: {session_id}).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SchedulingCommands(bot))   