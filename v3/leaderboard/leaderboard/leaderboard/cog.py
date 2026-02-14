import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from bd_models.models import Player
from django.db.models import Count
from ballsdex.core.bot import BallsDexBot
from ballsdex.settings import settings
from asgiref.sync import sync_to_async

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
        
        players = await sync_to_async(
            lambda: list(
                Player.objects.annotate(ball_count=Count("balls")).order_by("-ball_count")[:10]
            )
        )()

        if not players:
            await interaction.followup.send("No players found.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Top 10 players of {settings.bot_name}",
            color=discord.Color.gold()
        )

        text = ""
        for i, player in enumerate(players, start=1):
            user = self.bot.get_user(player.discord_id) or await self.bot.fetch_user(player.discord_id)
            text += f"**{i}. {user.name}** — {settings.plural_collectible_name}: {player.ball_count}\n"


        embed.description = text
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed, ephemeral=True)
