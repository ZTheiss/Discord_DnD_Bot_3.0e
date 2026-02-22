import discord
from discord import app_commands
from discord.ext import commands
from utils.utils import *

class MenuCommands(commands.GroupCog, name="menu"):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="start", description="Open the main menu")
    async def menu(self, interaction):
        await interaction.response.send_message(
            "Main Menu",
            view=MainMenu(),
            ephemeral=True
        )


class MainMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Lookup", style=discord.ButtonStyle.primary)
    async def lookup(self, interaction, button):
        await interaction.response.edit_message(
            content="Lookup Menu",
            view=LookupMenu()
        )

    @discord.ui.button(label="Player", style=discord.ButtonStyle.secondary)
    async def player(self, interaction, button):
        await interaction.response.edit_message(
            content="Player",
            view=PlayerMenu()
        )

    @discord.ui.button(label="Scheduling", style=discord.ButtonStyle.success)
    async def scheduling(self, interaction, button):
        await interaction.response.edit_message(
            content="Scheduling Menu",
            view=SchedulingMenu()
        )

    @discord.ui.button(label="Loot", style=discord.ButtonStyle.blurple)
    async def loot(self, interaction, button):
        await interaction.response.edit_message(
            content="Loot Menu",
            view=LootMenu()
        )

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit(self, interaction, button):
        await interaction.response.edit_message(
            content="Menu closed.",
            view=None
        )


####### LOOKUP MENU #######        

class LookupMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Search Class", style=discord.ButtonStyle.primary)
    async def search_class(self, interaction, button):
        await interaction.response.edit_message(
            content="Choose a class:",
            view=ClassSelectMenu()
        )

    @discord.ui.button(label="Search by Category", style=discord.ButtonStyle.secondary)
    async def search_category(self, interaction, button):
        await interaction.response.send_message(
            "Category search coming soon...", ephemeral=True
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="Main Menu",
            view=MainMenu()
        )
        
class ClassSelectMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ClassDropdown())
        
        
class ClassDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Barbarian"),
            discord.SelectOption(label="Bard"),
            discord.SelectOption(label="Cleric"),
            discord.SelectOption(label="Druid"),
            discord.SelectOption(label="Fighter"),
            discord.SelectOption(label="Monk"),
            discord.SelectOption(label="Paladin"),
            discord.SelectOption(label="Ranger"),
            discord.SelectOption(label="Rogue"),
            discord.SelectOption(label="Sorcerer"),
            discord.SelectOption(label="Warlock"),
            discord.SelectOption(label="Wizard"),
        ]

        super().__init__(
            placeholder="Choose a class...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        class_name = self.values[0]

        # Call your lookup logic directly
        await lookupResult(
            interaction,
            category="class",
            name=class_name
        )
  


######## END OF LOOKUP MENU #######

######## PLAYER MENU #######

class PlayerMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="View Character", style=discord.ButtonStyle.primary)
    async def view_char(self, interaction, button):
        await interaction.response.send_message(
            "Character sheet coming soon...", ephemeral=True
        )

    @discord.ui.button(label="Inventory", style=discord.ButtonStyle.secondary)
    async def inventory(self, interaction, button):
        await interaction.response.send_message(
            "Inventory coming soon...", ephemeral=True
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="Main Menu",
            view=MainMenu()
        )


######## END OF PLAYER MENU #######

######## SCHEDULING MENU #######

class SchedulingMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Session", style=discord.ButtonStyle.primary)
    async def create_session(self, interaction, button):
        await interaction.response.send_message(
            "Session creation coming soon...", ephemeral=True
        )

    @discord.ui.button(label="View Calendar", style=discord.ButtonStyle.secondary)
    async def view_calendar(self, interaction, button):
        await interaction.response.send_message(
            "Calendar coming soon...", ephemeral=True
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="Main Menu",
            view=MainMenu()
        )
        
        
######## END OF SCHEDULING MENU #######

######## LOOT MENU #######

class LootMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Add Loot", style=discord.ButtonStyle.primary)
    async def add_loot(self, interaction, button):
        await interaction.response.send_message(
            "Loot adding coming soon...", ephemeral=True
        )

    @discord.ui.button(label="View Loot", style=discord.ButtonStyle.secondary)
    async def view_loot(self, interaction, button):
        await interaction.response.send_message(
            "Loot list coming soon...", ephemeral=True
        )

    @discord.ui.button(label="Distribute Loot", style=discord.ButtonStyle.success)
    async def distribute_loot(self, interaction, button):
        await interaction.response.send_message(
            "Loot distribution coming soon...", ephemeral=True
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="Main Menu",
            view=MainMenu()
        )

######## END OF LOOT MENU #######


async def setup(bot):
    await bot.add_cog(MenuCommands(bot))   