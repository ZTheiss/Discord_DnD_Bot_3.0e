
from utils.utils import *
from utils.variables import *
import discord
from discord import app_commands
from discord.ext import commands



class LookupTracker:
    def __init__(self, title: str, fields: dict):
        self.title = title
        self.fields = fields

    def to_embed(self):
        embed = discord.Embed(
            title=self.title,
            color=discord.Color.blurple()
        )
        for key, value in self.fields.items():
            embed.add_field(name=key, value=value, inline=False)
        return embed

class LookupView(discord.ui.View):
    def __init__(self, tracker: LookupTracker, allowed_user_id: int):
        super().__init__(timeout=None)
        self.tracker = tracker
        self.allowed_user_id = allowed_user_id

    async def interaction_check(self, interaction):
        if interaction.user.id != self.allowed_user_id:
            await interaction.response.send_message(
                "You can't use this panel.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="More Info", style=discord.ButtonStyle.primary)
    async def more_info(self, interaction, button):
        await interaction.response.send_message(
            "Additional details coming soon.",
            ephemeral=True
        )


class LookupCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="spells", description="Look up a spell")
    @app_commands.describe(name="Name of the spell")
    @app_commands.autocomplete(name=name_autocomplete)
    async def spells(self, interaction: discord.Interaction, name: str):
        # Lookup the spell data  
        spell_list = (list(lookup_data["spell"][0].keys()))
        for item in spell_list:
            if item == "name":
                continue
        
        try:
            tracker = LookupTracker(
                title=f"✨ {lookup_data["spell"][0][name]["name"]}",
                fields={
                    "School": lookup_data["spell"][0][name]["school"],
                    "Level": lookup_data["spell"][0][name]["level"],
                    "Components": lookup_data["spell"][0][name]["components"],                   
                    "Casting Time": lookup_data["spell"][0][name]["casting_time"],
                    "Range": lookup_data["spell"][0][name]["range"],
                    "Target": lookup_data["spell"][0][name]["target"],
                    "Effect": lookup_data["spell"][0][name]["effect"],
                    "Duration": lookup_data["spell"][0][name]["duration"],
                    "Saving Throw": lookup_data["spell"][0][name]["saving_throw"],
                    "Spell Resistance": lookup_data["spell"][0][name]["spell_resistance"],                    
                    "Description": lookup_data["spell"][0][name]["description"]
                }                
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Spell **{name}** not found.",
                ephemeral=True
            )
            return
        view = LookupView(tracker, interaction.user.id)
        await interaction.response.send_message(
            embed=tracker.to_embed(),
            view=view,
            ephemeral=True
        )


    @app_commands.command(name="race", description="Look up a race")
    async def race(self, interaction, name: str):
        tracker = LookupTracker(
            title=f"🧬 {race['name']}",
            fields={
                "Ability Bonuses": race["ability_bonuses"],
                "Speed": race["speed"],
                "Traits": race["traits"],
                "Languages": race["languages"]
            }
        )
        view = LookupView(tracker, interaction.user.id)
        await interaction.response.send_message(
            embed=tracker.to_embed(),
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="class", description="Look up a class")
    async def class_lookup(self, interaction, name: str):
        tracker = LookupTracker(
            title=f"⚔️ {class_data['name']}",
            fields={
                "Hit Die": class_data["hit_die"],
                "Primary Ability": class_data["primary_ability"],
                "Saving Throws": class_data["saving_throws"],
                "Proficiencies": class_data["proficiencies"],
                "Features": class_data["features"]
            }
        )
        view = LookupView(tracker, interaction.user.id)
        await interaction.response.send_message(
            embed=tracker.to_embed(),
            view=view,
            ephemeral=True
        )
        
async def setup(bot):
    await bot.add_cog(LookupCommands(bot))