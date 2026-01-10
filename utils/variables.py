import os
import discord
from discord.ext import commands
from google import genai
from pathlib import Path
import json


DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GOOGLEAI_API_KEY = os.getenv("GOOGLEAI_API_KEY")
DB_FILE = "dnd_bot.db"
API_BASE = "https://logger.campaign-logger.com/api"
API_TOKEN = os.getenv("CAMPAIGN_LOGGER_API_TOKEN")  # Your token set as env var
CAMPAIGN_ID = os.getenv("CAMPAIGN_ID")  # Your campaign ID

client = genai.Client(api_key=GOOGLEAI_API_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

tree = bot.tree

DATA_DIR = Path("./data")
LOG_DIR = Path("./log.txt")

def load_json_file(filename):
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

#Loaded JSON Files
spell = load_json_file("spells.json")
feat = load_json_file("feats.json")
class_data = load_json_file("classes.json")
race = load_json_file("race.json")
armor = load_json_file("armor.json")
loot_name = load_json_file("loot.json")
loot_category = {"Weapon", "Armor", "Magic Item", "Consumable", "Miscellaneous"}
loot_type = {"Short Sword", "Bastard Sword", "Great Sword", "Staff", "Bracers", "Cloak", "Ring", "Amulet", "Wand", "Scroll", "Consumable", "Spellbook", "Shield"}
loot_owner = {"Al", "Alex", "Daniel", "Earl", "Heather", "Jon", "Keith", "Ken", "Kristen", "Lisa", "Lori", "Roger", "Scott", "Stefan", "TJ", "Zach"}
loot_magical = {"True", "False"}

# --- Spell Parsing Code ---
# categories = ["spell", "class", "feat", "race", "armor"]

#Used for auto_complete on searching parameters, see line 357
lookup_data = {
    "spell": (load_json_file("spells.json"), []),
    "feat": (load_json_file("feats.json"), []),
    "class": (load_json_file("classes.json"), []),
    "race": (load_json_file("race.json"), []),
    "armor": (load_json_file("armor.json"), []),
    "loot_name": (load_json_file("loot.json"), []),
    "loot_category": ({"Weapon", "Armor", "Magic Item", "Consumable", "Miscellaneous"}, []),
    "loot_type": ({"Short Sword", "Bastard Sword", "Great Sword", "Staff", "Bracers", "Cloak", "Ring", "Amulet", "Wand", "Scroll", "Consumable", "Spellbook", "Shield"}, []),
    "loot_owner": ({"Al", "Alex", "Daniel", "Earl", "Heather", "Jon", "Keith", "Ken", "Kristen", "Lisa", "Lori", "Roger", "Scott", "Stefan", "TJ", "Zach"}, []),
    "loot_magical": ({"True", "False"}, [])
}

for key, value in lookup_data.items():
    data, _ = value
    if isinstance(data, dict):
        data, _ = lookup_data[key]
        lookup_data[key] = (data, list(data.keys()))
    elif isinstance(data, (set, list)):
        data, _ = lookup_data[key]
        lookup_data[key] = (data, list(data))

SUMMARY_FIELDS = {
    "spell": ['school', 'level', 'components', 'casting_time', 'range', 'target', 'effect', 'duration', 'saving_throw', 'spell_resistance'],
    "feat": ['type', 'prerequisites', 'benefit', 'normal', 'special'],
    "class": ['hit_die', 'skill_points', 'base_attack_bonus', 'fort_save', 'ref_save', 'will_save', 'special_abilities'],
    "race": ["size", "type", "base_speed", "ability_modifiers", "racial_traits", "favored_class", "languages", "alignment_tendencies"],
    "armor": ["name", "category", "cost_gp", "armor_bonus", "max_dex_bonus", "armor_check_penalty", "arcane_spell_failure", "speed_30ft", "speed_20ft", "weight_lb"]
}

DETAIL_FIELDS = {
    "spell": ['school', 'level', 'components', 'casting_time', 'range', 'target', 'effect', 'duration', 'saving_throw', 'spell_resistance'],
    "feat": ['type', 'prerequisites', 'benefit', 'normal', 'special'],
    "class": ["hit_die", "skill_points", "class_skills", "proficiencies", "special_abilities", "alignment", "spell_list"],
    "race": ["size", "type", "base_speed", "ability_modifiers", "racial_traits", "favored_class", "languages", "alignment_tendencies"],
    "armor": ["name", "category", "cost_gp", "armor_bonus", "max_dex_bonus", "armor_check_penalty", "arcane_spell_failure", "speed_30ft", "speed_20ft", "weight_lb"]
}