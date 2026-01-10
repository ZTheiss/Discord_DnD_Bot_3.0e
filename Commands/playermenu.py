
from utils.utils import *
from utils.variables import *
import discord
from discord import app_commands
from discord.ext import commands

# class PlayerMenuCommands(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @app_commands.command(name="player_menu", description="Display the player menu")
#     async def player_menu(self, interaction: discord.Interaction):
#         embed = discord.Embed(title="🎲 Player Menu", description="Select an option from the menu below:", color=0x00AAFF)
#         embed.add_field(name="1. View Character Sheet", value="Display your character sheet details.", inline=False)
#         embed.add_field(name="2. Inventory Management", value="View and manage your inventory items.", inline=False)
#         embed.add_field(name="3. Quest Log", value="Check your current quests and objectives.", inline=False)
#         embed.add_field(name="4. Skills & Abilities", value="Review your skills and abilities.", inline=False)
#         await interaction.response.send_message(embed=embed, ephemeral=True)

class HPTracker():
    def __init__(self, bot, name: str, max_hp: int, current_hp: int):
        self.bot = bot
        self.name = name
        self.max_hp = max_hp
        self.current_hp = current_hp
    
    def damage(self, amount: int):
        self.current_hp = max(0, self.current_hp - amount)

    def heal(self, amount: int):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def to_embed(self):
        embed = discord.Embed(
            title=f"❤️ HP Tracker — {self.name}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Current HP",
            value=f"{self.current_hp}/{self.max_hp}",
            inline=False
        )
        return embed
        
class HPView(discord.ui.View):
    def __init__(self, tracker: HPTracker, allowed_user_id: int):
        super().__init__(timeout=None)
        self.tracker = tracker
        self.allowed_user_id = allowed_user_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.allowed_user_id:
            await interaction.response.send_message(
                "You can't use this panel.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Damage", style=discord.ButtonStyle.danger, emoji="🗡️")
    async def damage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DamageModal(self.tracker, self))

    @discord.ui.button(label="Heal", style=discord.ButtonStyle.success, emoji="💚")
    async def heal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HealModal(self.tracker, self))
        
class DamageModal(discord.ui.Modal, title="Apply Damage"):
    amount = discord.ui.TextInput(label="Damage Amount")

    def __init__(self, tracker: HPTracker, view: HPView):
        super().__init__()
        self.tracker = tracker
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.tracker.damage(int(self.amount.value))
        await interaction.response.edit_message(
            embed=self.tracker.to_embed(),
            view=self.view
        )

class HealModal(discord.ui.Modal, title="Apply Healing"):
    amount = discord.ui.TextInput(label="Healing Amount")

    def __init__(self, tracker: HPTracker, view: HPView):
        super().__init__()
        self.tracker = tracker
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.tracker.heal(int(self.amount.value))
        await interaction.response.edit_message(
            embed=self.tracker.to_embed(),
            view=self.view
        )


class HPCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="hp", description="Open an HP tracker panel.")
    async def hp(self, interaction: discord.Interaction, name: str, max_hp: int):
        tracker = HPTracker(self.bot, name, max_hp, current_hp=max_hp)
        view = HPView(tracker, allowed_user_id=interaction.user.id)

        await interaction.response.send_message(
            embed=tracker.to_embed(),
            view=view,
            ephemeral=True
        )
    
    # @app_commands.command(name="hp_tracker", description="Display the HP tracker menu")
    # async def hp_tracker(self, interaction: discord.Interaction):
    #     embed = discord.Embed(title="❤️ HP Tracker", description="Manage your character's health points (HP):", color=0xFF0000)
    #     embed.add_field(name="1. View Current HP", value="Check your current health points.", inline=False)
    #     embed.add_field(name="2. Adjust HP", value="Increase or decrease your health points.", inline=False)
    #     embed.add_field(name="3. Apply Conditions", value="Add or remove conditions affecting your character.", inline=False)
    #     await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(HPCommands(bot))


