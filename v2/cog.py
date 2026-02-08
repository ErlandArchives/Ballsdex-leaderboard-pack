import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from tortoise.functions import Count
from ballsdex.core.models import Player
from ballsdex.core.utils.paginator import FieldPageSource, Pages
from ballsdex.core.bot import BallsDexBot
from ballsdex.settings import settings


class Leaderboard(commands.Cog):
    """
    Leaderboard command :skull:
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description=f"Show the top players of {settings.bot_name}!")
    async def leaderboard(self, interaction: discord.Interaction["BallsDexBot"]):
        """
        Displays the most addicted i mean best players of this dex
        """
        await interaction.response.defer(ephemeral=True, thinking=True)

        players = await Player.annotate(ball_count=Count("balls")).order_by("-ball_count").limit(10)
        if not players:
            await interaction.followup.send("No players found.", ephemeral=True)
            return

        entries = []
        for i, player in enumerate(players):
            user = self.bot.get_user(player.discord_id) or await self.bot.fetch_user(player.discord_id)
            entries.append((f"{i + 1}. {user.name}", f"{settings.collectible_name}: {getattr(player, 'ball_count', 0)}"))

        source = FieldPageSource(entries, per_page=5, inline=False)
        source.embed.title = "top 10 players"
        source.embed.color = discord.Color.gold() # you can change this color however much you want, personally, gold and blurple are my favs.
        source.embed.set_thumbnail(url=interaction.user.display_avatar.url) # This can also be changed, but i recommend keeping it at the users avatar.

        pages = Pages(source=source, interaction=interaction)
        await pages.start(ephemeral=True)
