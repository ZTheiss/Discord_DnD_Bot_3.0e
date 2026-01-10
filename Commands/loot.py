import discord
from discord import app_commands
import csv
from io import StringIO
import aiosqlite
from typing import Optional
import json
from utils.utils import *
from utils.variables import *
       
# --- Loot Management Commands ---


class LootCommands(commands.GroupCog, name="loot"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="all", description="Display all items in the loot database")
    async def loot_all(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await export_loot_csv(interaction, "*")

    @app_commands.command(name="search", description="Display all items in the loot database")
    @app_commands.describe(category="Category to search by", name="Name of the selection")
    @app_commands.choices(category=[
        app_commands.Choice(name="Name", value="loot_name"),
        app_commands.Choice(name="Category", value="loot_category"),
        app_commands.Choice(name="Type", value="loot_type"),
        app_commands.Choice(name="Magical", value="loot_magical"),
        app_commands.Choice(name="Owner", value="loot_owner")  
    ])
    @app_commands.autocomplete(name=name_autocomplete)
    async def loot_search(self, interaction: discord.Interaction, category: app_commands.Choice[str], name: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if category.value == "loot_name":
            where_clause = f"name LIKE '%{name}%'"
        elif category.value == "loot_category":
            where_clause = f"category LIKE '%{name}%'"
        elif category.value == "loot_type":
            where_clause = f"type LIKE '%{name}%'"
        elif category.value == "loot_magical":
            where_clause = "magical = TRUE"
        elif category.value == "loot_owner":
            where_clause = f"owner LIKE '%{name}%'"
        await export_loot_csv(interaction, "*", where_clause)
        log_discord_bot_activity(f"Loot search by {category.value}: ", name, f"SELECT * FROM party_loot WHERE {where_clause}")

    @app_commands.command(name="assign", description="Assign loot to a player")
    @app_commands.describe(loot_name="Name of the item", name="Name of the player")
    @app_commands.autocomplete(loot_name=json_to_autocomplete(loot_name))
    @app_commands.autocomplete(name=json_to_autocomplete(loot_owner))
    async def loot_assign(self, interaction: discord.Interaction, loot_name: str, name: str):
        async with aiosqlite.connect("dnd_bot.db") as db:
            cursor = await db.execute("""
                UPDATE party_loot
                SET owner = ?
                WHERE name = ?
            """, (name, loot_name))
            await db.commit()
            log_discord_bot_activity(f"Assigning loot item: ", name + loot_name, "UPDATE party_loot SET owner = name WHERE name = loot_name")
            if cursor.rowcount > 0:
                await interaction.response.send_message(f"✅ Loot **{loot_name}** assigned to **{name}**.")
            else:
                await interaction.response.send_message(f"❌ No loot found named **{loot_name}**.")

    @app_commands.command(name="unassign", description="Unassign loot from a player")
    @app_commands.describe(loot_name="Name of the item")
    @app_commands.autocomplete(loot_name=json_to_autocomplete(loot_name))
    async def loot_unassign(self, interaction: discord.Interaction, loot_name: str):
        async with aiosqlite.connect("dnd_bot.db") as db:
            cursor = await db.execute("""
                UPDATE party_loot
                SET owner = ""
                WHERE name = ?
            """, (loot_name))
            await db.commit()
            log_discord_bot_activity(f"Unassigning loot item: ", loot_name, "UPDATE party_loot SET owner = '' WHERE name = loot_name")
            if cursor.rowcount > 0:
                await interaction.response.send_message(f"✅ Loot **{loot_name}** unassigned.")
            else:
                await interaction.response.send_message(f"❌ No loot found named **{loot_name}**.")

    @app_commands.command(name="remove", description="Remove loot from the database")
    @app_commands.describe(loot_name="Name of the item")
    @app_commands.autocomplete(loot_name=json_to_autocomplete(loot_name))
    async def loot_remove(self, interaction: discord.Interaction, loot_name: str):
        async with aiosqlite.connect("dnd_bot.db") as db:
            cursor = await db.execute("""
                DELETE FROM party_loot
                WHERE name = ?
            """, (loot_name))
            await db.commit()
            log_discord_bot_activity(f"Removing loot item: ", loot_name, "DELETE FROM party_loot WHERE name = loot_name")
            if cursor.rowcount > 0:
                await interaction.response.send_message(f"✅ Loot **{loot_name}** removed.")
            else:
                await interaction.response.send_message(f"❌ No loot found named **{loot_name}**.")

    @app_commands.command(name="add", description="Add loot to the database")
    @app_commands.describe(loot_name="Name of the item")
    @app_commands.autocomplete(loot_name=json_to_autocomplete(loot_name))
    async def loot_add(self, interaction: discord.Interaction, loot_name: str):
        async with aiosqlite.connect("dnd_bot.db") as db:
            cursor = await db.execute("""
                INSERT INTO party_loot (name)
                VALUES (?)
            """, (loot_name))
            await db.commit()
            log_discord_bot_activity(f"Adding loot item: ", loot_name, "INSERT INTO party_loot (name) VALUES (loot_name)")
            if cursor.rowcount > 0:
                await interaction.response.send_message(f"✅ Loot **{loot_name}** added.")
            else:
                await interaction.response.send_message(f"❌ Failed to add loot **{loot_name}**.")
            
    @app_commands.command(name="upload", description="Upload a JSON file to import loot")
    @app_commands.describe(file="Upload a JSON file")
    async def loot_upload(self, interaction: discord.Interaction, file: discord.Attachment):
        if not file.filename.lower().endswith(".json") or not file.filename.lower().endswith(".txt"):
            await interaction.response.send_message("❌ Please upload a `.json` or `.txt` file.")
            return
        content = await file.read()
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            await interaction.response.send_message("❌ Invalid JSON format.")
            return
        async with aiosqlite.connect("dnd_bot.db") as db:
            for item in data.values():
                cursor = await db.execute(
                    """
                    INSERT OR IGNORE INTO party_loot
                    (name, category, type, hands, damage, range, magical, crit,
                    damage_type, description, discovery_location, quantity, owner, link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.get("name"),
                        item.get("category", ""),
                        item.get("type", ""),
                        item.get("hands", ""),
                        item.get("damage", ""),
                        item.get("range", ""),
                        item.get("magical", False),
                        item.get("crit", ""),
                        item.get("damage_type", ""),
                        item.get("description", ""),
                        item.get("discovery_location", ""),
                        item.get("quantity", 1),
                        item.get("owner", ""),
                        item.get("link", "")
                    )
                )
            await db.commit()
            log_discord_bot_activity(f"Uploading loot item from file: ", loot_name, "INSERT INTO party_loot (name) VALUES (loot_name)")
            if cursor.rowcount > 0:
                await interaction.response.send_message(f"✅ Loot **{loot_name}** added.")
            else:
                await interaction.response.send_message(f"❌ Failed to add loot **{loot_name}**.")
            
            
async def setup(bot):
    await bot.add_cog(LootCommands(bot))   