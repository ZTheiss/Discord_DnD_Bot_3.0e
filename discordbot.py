import discord
from discord import app_commands
import aiosqlite
import json
import asyncio
from utils.utils import *
from utils.variables import *


# --- Database Setup ---
async def setup_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS party_loot (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                type TEXT,
                hands TEXT,
                damage TEXT,
                range TEXT,
                magical BOOLEAN DEFAULT 0,
                crit TEXT,
                damage_type TEXT,
                description TEXT,
                discovery_location TEXT,
                quantity INTEGER DEFAULT 1,
                owner TEXT,
                link TEXT
            )
        """)
        with open("./data/loot.json", "r") as f:
            items = json.load(f)
        for item in items.values():
            await db.execute(
                "INSERT OR IGNORE INTO party_loot (name, category, type, hands, damage, range, magical, crit, damage_type, description, discovery_location, quantity, owner, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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

@bot.event
async def on_ready():
    await setup_db()
    print(f"Bot connected as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

async def main():
    # await bot.load_extension("Commands.homebrew")
    await bot.load_extension("Commands.campaignlogger")
    await bot.load_extension("Commands.loot")
    await bot.load_extension("Commands.scheduling")
    await bot.load_extension("Commands.playermenu")
    await bot.load_extension("Commands.lookup")
    await bot.start(DISCORD_TOKEN)
# --- Spell, Armor, Class, Feat, Race Lookup Command ---

# @tree.command(name="lookup", description="Look up a spell, armor set, class, feat, or race feature")
# @app_commands.describe(category="Category to search in", name="Name of the item")
# @app_commands.choices(category=[
#     app_commands.Choice(name="Class", value="class"),
#     app_commands.Choice(name="Feat", value="feat"),
#     app_commands.Choice(name="Race", value="race"),
#     app_commands.Choice(name="Armor", value="armor"),
#     app_commands.Choice(name="Spell", value="spell")  
# ])
# @app_commands.autocomplete(name=name_autocomplete)
# async def lookup(interaction: discord.Interaction, category: app_commands.Choice[str], name: str):
#     log_discord_bot_activity(f"Lookup command invoked for {category.name}: ", name, "N/A")
#     await lookupResult(name, category, interaction)
        
        
asyncio.run(main())