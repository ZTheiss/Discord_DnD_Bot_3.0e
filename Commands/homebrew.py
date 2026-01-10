import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
from utils.utils import *
from utils.variables import *   
            

# --- Homebrew Management Commands ---

# class HomebrewCommands(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @tree.command(name="homebrew_add", description="Add a new homebrew rule")
#     @app_commands.describe(
#         title="Short title of the rule",
#         description="Detailed description of the rule"
#     )
#     async def homebrew_add(interaction: discord.Interaction, title: str, description: str):
#         async with aiosqlite.connect(DB_FILE) as db:
#             await db.execute("""
#                 INSERT INTO homebrew_rules (title, description, added_by)
#                 VALUES (?, ?, ?)
#             """, (title, description, interaction.user.name))
#             await db.commit()
#         await interaction.response.send_message(f"✅ Homebrew rule **{title}** added.", ephemeral=True)

#     @tree.command(name="homebrew_remove", description="Remove a homebrew rule by title")
#     @app_commands.describe(title="Title of the rule to remove")
#     async def homebrew_remove(interaction: discord.Interaction, title: str):
#         async with aiosqlite.connect(DB_FILE) as db:
#             cursor = await db.execute("SELECT rule_id FROM homebrew_rules WHERE title = ?", (title,))
#             row = await cursor.fetchone()
#             if not row:
#                 await interaction.response.send_message(f"⚠️ No homebrew rule titled **{title}** found.", ephemeral=True)
#                 return
#             await db.execute("DELETE FROM homebrew_rules WHERE rule_id = ?", (row[0],))
#             await db.commit()
#         await interaction.response.send_message(f"✅ Homebrew rule **{title}** removed.", ephemeral=True)

#     @tree.command(name="homebrew_list", description="List all current homebrew rules")
#     async def homebrew_list(interaction: discord.Interaction):
#         async with aiosqlite.connect(DB_FILE) as db:
#             cursor = await db.execute("SELECT title, description, added_by, added_at FROM homebrew_rules ORDER BY added_at DESC")
#             rows = await cursor.fetchall()

#         if not rows:
#             await interaction.response.send_message("No homebrew rules have been added yet.", ephemeral=True)
#             return

#         embed = discord.Embed(title="📜 Homebrew Rules", color=0x00AA00)
#         for title, description, added_by, added_at in rows:
#             embed.add_field(name=title, value=f"{description}\n*Added by {added_by} on {added_at}*", inline=False)

#         await interaction.response.send_message(embed=embed, ephemeral=True)

# async def setup(bot):
#     await bot.add_cog(HomebrewCommands(bot))