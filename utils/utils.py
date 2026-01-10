import csv
from io import StringIO
from typing import Optional
import aiosqlite
import discord
from discord import app_commands
from discord.ui import Button
import difflib
import requests
from utils.utils import *
from utils.variables import *


class NextPreviousViewWithMore(discord.ui.View):
    def __init__(self, category, item, names, index, interaction, show_button):
        super().__init__()
        self.category = category
        self.interaction = interaction
        self.item = item
        self.names = names # This is the list of all items in the category
        self.index = index
        self.show_button = show_button

    
    @discord.ui.button(label="⬅ Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        name = self.names[(self.index - 1) % len(self.names)]
        await lookupResult(name=name, category=self.category, interaction=interaction)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        name = self.names[(self.index + 1) % len(self.names)]
        await lookupResult(name=name, category=self.category, interaction=interaction)
    

    @discord.ui.button(label="Show more", style=discord.ButtonStyle.primary)
    async def show_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=self.item.get('name', ''), description=self.item.get('description', ''), color=0x00ff00)
        # Add fields dynamically
        fields = DETAIL_FIELDS.get(self.category, [])
        for field in fields:
            value = self.item.get(field)
            if value:
                embed.add_field(
                    name=field.replace('_', ' ').title(),
                    value=format_field(value),
                    inline=True
                )
        # Special: full advancement table for classes
        if self.category == "class" and "advancement_table" in self.item:
            adv = self.item["advancement_table"]
            summary = ""
            summary = "**Lvl | BAB | Fort | Ref | Will | Specials**\n"
            for level_info in adv[5:]:  # levels 6–20 
                specials = ", ".join(level_info.get("special_abilities", [])) or "None"
                summary += (
                    f"{level_info['level']:>3} | "
                    f"{level_info['base_attack_bonus']:>3} | "
                    f"{level_info['fort_save']:>4} | "
                    f"{level_info['ref_save']:>3} | "
                    f"{level_info['will_save']:>4} | "
                    f"{specials}\n"
                )
            embed.add_field(name="Advancement Table (Lv 6–20)", value=summary.strip(), inline=False)

        await interaction.response.edit_message(embed=embed)

class NextPreviousView(discord.ui.View):
    def __init__(self, category, item, names, index, interaction):
        super().__init__()
        self.category = category
        self.interaction = interaction
        self.item = item
        self.names = names # This is the list of all items in the category
        self.index = index
    
    @discord.ui.button(label="⬅ Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        name = self.names[(self.index - 1) % len(self.names)]
        await lookupResult(name=name, category=self.category, interaction=interaction)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        name = self.names[(self.index + 1) % len(self.names)]
        await lookupResult(name=name, category=self.category, interaction=interaction)
    
def log_discord_bot_activity(activity: str, additional_info: str = "", sqlstring: str = ""):
    """Logs bot activity to log.txt"""
    with open(LOG_DIR, "a") as f:
        f.write(activity + additional_info + sqlstring + "\n")

def format_field(value):
    if isinstance(value, dict):
        return "\n".join(f"**{k.title()}**: {v}" for k, v in value.items())
    elif isinstance(value, list):
        return " ".join(value)
    elif value is None:
        return "—"
    else:
        return str(value)
    
def lookupResult(name, category, interaction):
    category_key = category.value
    data, names = lookup_data.get(category_key, ({}, [])) # Names is the list of all keys (all spells)
    count = 0
    index = 0
    for entry in names:
        if entry == name:
            index = count
        count += 1

    query = name.strip().lower() # Specific lookup value ("fireball")
    item = data.get(query) # Item is the entire listing of the lookup value (Fireball: school, level, etc.)
    if not item:
        matches = difflib.get_close_matches(query, names, n=1, cutoff=0.6)
        if matches:
            item = data[matches[0]]   
    
    if item:
        full_desc = item.get('description', '')
        short_desc = full_desc
        show_button = False
        max_len = 700
        if len(full_desc) > max_len:
            short_desc = full_desc[:max_len].rsplit(' ', 1)[0] + '...'
            show_button = True

        embed = discord.Embed(title=item.get('name', name), description=short_desc, color=0x00ff00)

        # Add summary fields with proper formatting
        for field in DETAIL_FIELDS.get(category_key, []):
            value = item.get(field)
            if value:
                embed.add_field(name=field.replace('_', ' ').title(), value=format_field(value), inline=True)
            
        #CLASS
        if category_key == "class" and "advancement_table" in item:
            # Summarize advancement table levels (e.g., show level 1, 10, 20 info)
            adv = item["advancement_table"]
            
            summary = "**Lvl | BAB | Fort | Ref | Will | Specials**\n"
            for level_info in adv:  # first 5 levels
                specials = ", ".join(level_info.get("special_abilities", [])) or "None"
                summary += (
                    f"{level_info['level']:>3} | "
                    f"{level_info['base_attack_bonus']:>3} | "
                    f"{level_info['fort_save']:>4} | "
                    f"{level_info['ref_save']:>3} | "
                    f"{level_info['will_save']:>4} | "
                    f"{specials}\n"
                )
            if len(summary) > 1024:
                summary = summary[:1020] + "..."
                show_button = True
            else:
                show_button = False

            embed.add_field(name="Advancement Table (Lv 1–20)", value=summary, inline=False)
        
        #RACE
        if category_key == "race":
            # Ability modifiers formatting
            ability_mods = item.get("ability_modifiers", {})
            if ability_mods:
                mod_str = ", ".join(f"{k.title()}: {v}" for k, v in ability_mods.items())
                embed.add_field(name="Ability Modifiers", value=mod_str, inline=False)

            # Racial traits (list to string)
            racial_traits = item.get("racial_traits", [])
            if racial_traits:
                # Join each trait with a single newline for better readability
                traits_formatted = "\n\n".join(f"- {trait}" for trait in racial_traits)
                # Optionally, truncate if too long for Discord embed field
                if len(traits_formatted) > 1024:
                    traits_formatted = traits_formatted[:1020] + "..."
                embed.add_field(name="Racial Traits", value=traits_formatted, inline=False)

            # Languages formatting
            languages = item.get("languages", {})
            if languages:
                auto_langs = ", ".join(languages.get("automatic", []))
                bonus_langs = ", ".join(languages.get("bonus", []))
                lang_text = f"Automatic: {auto_langs}\nBonus: {bonus_langs}" if bonus_langs else f"Automatic: {auto_langs}"
                embed.add_field(name="Languages", value=lang_text, inline=False)
        
        #FEATS
        if category_key == "feat":         
            #embed.add_field(name="Prerequisites", value=item.get("prerequisites", "None"), inline=False)
            embed.add_field(name="Benefits", value=item.get("benefits", "None"), inline=False)
            special_notes = item.get("special_notes", None)
            
            if special_notes:
                embed.add_field(name="Special Notes", value=special_notes, inline=False)

            embed.add_field(name="Page", value=f"PHB p. {item.get("page", "N/A")}", inline=True)
            
        #ARMOR
        if category_key == "armor":         
            #embed.add_field(name="Prerequisites", value=item.get("prerequisites", "None"), inline=False)
            embed.description = f"**Category:** {item.get('category', 'Unknown')}"
            embed.add_field(name="Cost", value=f"{item.get('cost_gp', 'N/A')} gp", inline=True)
            embed.add_field(name="Armor Bonus", value=item.get("armor_bonus", "N/A"), inline=True)
            embed.add_field(name="Max Dex Bonus", value=item.get("max_dex_bonus", "N/A"), inline=True)
            embed.add_field(name="Armor Check Penalty", value=item.get("armor_check_penalty", "N/A"), inline=True)
            embed.add_field(name="Arcane Spell Failure", value=item.get("arcane_spell_failure", "N/A"), inline=True)
            embed.add_field(name="Speed (30 ft.)", value=item.get("speed_30ft", "N/A"), inline=True)
            embed.add_field(name="Speed (20 ft.)", value=item.get("speed_20ft", "N/A"), inline=True)
            embed.add_field(name="Weight", value=f"{item.get('weight_lb', 'N/A')} lb", inline=True)
            
            if special_notes:
                embed.add_field(name="Special Notes", value=special_notes, inline=False)

            embed.add_field(name="Page", value=f"PHB p. {item.get("page", "N/A")}", inline=True)
            
        #Show the "Show More" button if the description was truncated or if the item has a lot of details
        if show_button:
            view = NextPreviousViewWithMore(category, item, names, index, interaction, show_button)
        else:
            view = NextPreviousView(category, item, names, index, interaction)

        if view:
            return interaction.response.send_message(embed=embed, view=view)
        else:
            return interaction.response.send_message(embed=embed)

    else:
        return interaction.response.send_message(f"❓ Could not find '{name}' in {category.name}.")

async def name_autocomplete(interaction: discord.Interaction, current: str):
    # Collect all possible names across all categories
    category = None
    # Try to get the selected category to filter autocomplete choices
    for option in interaction.data.get("options", []):
        if option["name"] == "category":
            category = option.get("value")
            break
    if category and category in lookup_data:
        data, names = lookup_data[category]
        choices = [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()]
    else:
        # fallback: search all categories
        choices = [
            app_commands.Choice(name=n, value=n)
            for dataset in lookup_data.values()
            for n in dataset[1] if current.lower() in n.lower()
        ]
    return choices[:20]

def json_to_autocomplete(values: list[str]):
    async def autocomplete(interaction, current: str):
        filtered = [
            app_commands.Choice(name=v, value=v)
            for v in values
            if current.lower() in v.lower()
        ]
        return filtered[:20]
    return autocomplete
      
async def get_player_log():
    url = "https://logger.campaign-logger.com/player-log-entries"
    headers = {
        "api-client": os.getenv("LOGGER_API_CLIENT"),
        "api-secret": os.getenv("LOGGER_API_SECRET"),
    }
    response = requests.get(url, headers=headers)
    log_discord_bot_activity("Fetched player log from Campaign Logger API.", "", "")
    return response.content

async def send_long_message(interaction, text, type):
    # Discord hard limit = 2000 chars
    limit = 1900
    # Break the text into chunks
    chunks = [text[i:i+limit] for i in range(0, len(text), limit)]
    # Send each chunk as a separate followup message
    chunks[0] = (
        f"📜 **{type}**\n"
        f"📝 **Recap**: {chunks[0]}\n\n"
    )

    for chunk in chunks:
        await interaction.followup.send(chunk)
    log_discord_bot_activity(f"Sent long {type} message in chunks.", "", "N/A")

async def summarize_text_with_genai(text: str) -> str:
    print(text)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=f"Summarize this D&D campaign log entry in 2-3 sentences:\n{text}")
    log_discord_bot_activity("Generated summary with Google GenAI.", "", "N/A")
    return response.text.strip()        

async def export_loot_csv(interaction: discord.Interaction, fields: str = "*", where_clause: Optional[str] = ""):
    """SQL Query from the database, convert to CSV, and send as a file."""
    async with aiosqlite.connect("dnd_bot.db") as db:
        if where_clause:
            cursor = await db.execute(f"""
                SELECT {fields}
                FROM party_loot
                WHERE {where_clause}
            """)
        else:
            cursor = await db.execute(f"""
                SELECT {fields}
                FROM party_loot
            """)
        rows = await cursor.fetchall()
    if not rows:
        await interaction.followup.send("No loot found in the database.")
        return

    buffer = StringIO()
    writer = csv.writer(buffer)
    # Header row
    writer.writerow([
        "Name", "Category", "Type", "Hands", "Damage", "Range", "Magical",
        "Crit", "Damage_type", "Description", "Discovery_location",
        "Quantity", "Owner", "Link"
    ])
    # Data rows
    for row in rows:
        writer.writerow(row)
    buffer.seek(0)
    file = discord.File(
        fp=buffer,
        filename="party_loot.csv"
    )
    await interaction.followup.send(
        content="📦 **Here is your loot export (CSV format):**",
        file=file
    )
    log_discord_bot_activity("Exported loot data to CSV.", "", f"SELECT {fields} FROM party_loot" + (f" WHERE {where_clause}" if where_clause else ""))
