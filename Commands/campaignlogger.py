import os
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import requests
from utils.utils import *
from utils.variables import *
        
  
# --- API Action Commands ---
class CampaignLoggerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="latest")
    @app_commands.describe(type="Type of log entry to fetch")
    @app_commands.choices(type=[
        app_commands.Choice(name="Latest Session", value="latest"),
        app_commands.Choice(name="Summarize last session", value="summary"),
        app_commands.Choice(name="Latest Adventure", value="adventure")
    ])
    async def latest(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        """Fetch the latest Campaign Logger entry"""
        await interaction.response.defer(thinking=True)
        if type.value == "latest":
            await self.last_session(interaction)
        elif type.value == "summary":
            await self.latest_summary(interaction)
        elif type.value == "adventure":
            await self.latest_adventure(interaction)
    
    async def latest_summary(self, interaction: discord.Interaction):
        data = json.loads(await get_player_log())
        if data:
            raw_texts = []
            
            for entry in data.get("data", []):
                attributes = entry.get("attributes", {})
                raw_text = attributes.get("raw-text")
                if raw_text:
                    raw_texts.append(raw_text.strip())

            summary = await summarize_text_with_genai(raw_texts)
            if len(summary) > 1900:
                await send_long_message(interaction, summary, "Latest Campaign Log Entry")
            else:
                msg = (
                    f"📜 **Latest Campaign Log Entry**\n"
                    f"📝 **Summary:** {summary}"
                )
                await interaction.followup.send(msg)
                log_discord_bot_activity("Fetched latest log entry summary.", "", "N/A")
        else:
            await interaction.followup.send("❌ Could not fetch the latest log entry.")
            log_discord_bot_activity("Failed to fetch latest log entry.", "", "N/A")        

    async def latest_adventure(self, interaction: discord.Interaction):
        data = json.loads(await get_player_log())
        if data:
            raw_texts = []
            for entry in data.get("data", []):
                if entry.get("attributes", {}).get("raw-prefix", "").lower() != "":
                    raw_prefix = entry.get("attributes", {}).get("raw-prefix", "").lower()
                    break
            
            for entry in data.get("data", []):
                attributes = entry.get("attributes", {})
                if attributes.get("raw-prefix", "").lower() == raw_prefix:
                    raw_texts.append(attributes.get("raw-text", "").strip())

            adventure_text = "\n\n".join(raw_texts)
            #summary = await summarize_text_with_genai(adventure_text)
            if len(adventure_text) > 1900:
                await send_long_message(interaction, adventure_text, "Latest Campaign Adventure Entry")
            else:
                msg = (
                    f"📜 **Latest Campaign Adventure Entry**\n"
                    f"📝 **Adventure:** {adventure_text}"
                )
                await interaction.followup.send(msg)
                log_discord_bot_activity("Fetched latest adventure entry.", "", "N/A")
        else:
            await interaction.followup.send("❌ Could not fetch the latest adventure entry.")
            log_discord_bot_activity("Failed to fetch latest adventure entry.", "", "N/A")
        
    async def last_session(self, interaction: discord.Interaction):
        data = json.loads(await get_player_log())
        if data:
            summary = []
            for entry in data.get("data", []):
                attributes = entry.get("attributes", {})
                raw_text = attributes.get("raw-text")
                if raw_text:
                    summary.append(raw_text.strip())
                    break 
            if len(summary) > 1900:
                await send_long_message(interaction, summary, "Last Session")
            else:
                msg = (
                    f"📜 **Last Session**\n"
                    f"📝 **Summary:** {summary}"
                )
                await interaction.followup.send(msg)
                log_discord_bot_activity("Fetched last session log entry.", "", "N/A")
        else:
            await interaction.followup.send("❌ Could not fetch the latest log entry.")
            log_discord_bot_activity("Failed to fetch latest log entry.", "", "N/A")

    @app_commands.command(name="loot_divvy", description="Fetch & summarize the latest Campaign Logger adventure")
    async def loot_divvy(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        data = json.loads(await get_player_log())
        if data:
            raw_texts = []
            for entry in data.get("data", []):
                attributes = entry.get("attributes", {})
                title = attributes.get("title")
                if title and "loot divvy" in title.lower():
                    raw_texts.append(attributes.get("raw-text", "").strip())
                    
            cleaned_lines = []
            adventure_text = "\n".join(raw_texts)
            for line in adventure_text.splitlines():
                line = line.replace("[]!", "").replace("[]2 !", "").strip()
                if not line:
                    continue
                elif line.startswith("###"):
                    cleaned_lines.append(line)
                else:
                    cleaned_lines.append(f"- {line}")
            adventure_text = "\n".join(cleaned_lines)

            if len(adventure_text) > 1900:
                await send_long_message(interaction, adventure_text, "Loot Divvy Summary")
            else:
                msg = (
                    f"📜 **Loot Divvy Summary**\n"
                    f"📝 **Summary:**\n{adventure_text}"
                )
                await interaction.followup.send(msg)
            log_discord_bot_activity("Fetched loot divvy summary from latest adventure.", "", "")
    

    @app_commands.command(name="log_to_campaign", description="Add a log entry to Campaign Logger via API")
    @app_commands.describe(entry_text="Text content of the log entry")
    async def log_to_campaign(self, interaction: discord.Interaction, entry_text: str):
        await interaction.response.defer(thinking=True)
        
        url = f"{API_BASE}/campaigns/{CAMPAIGN_ID}/entries"

        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "content": entry_text,
            # add other fields as required by the API, e.g., title, date
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    data = await response.json()
                    entry_url = data.get("url", None)
                    msg = "✅ Log entry added!"
                    if entry_url:
                        msg += f" [View entry]({entry_url})"
                    await interaction.followup.send(msg)
                    log_discord_bot_activity("Added log entry to Campaign Logger via API.", entry_text, "N/A")
                else:
                    error_text = await response.text()
                    await interaction.followup.send(f"❌ Failed to add log entry. Status: {response.status}\n{error_text}")
                    log_discord_bot_activity("Failed to add log entry to Campaign Logger via API.", entry_text, f"Status: {response.status}\n{error_text}")

        
async def setup(bot):
    await bot.add_cog(CampaignLoggerCommands(bot))