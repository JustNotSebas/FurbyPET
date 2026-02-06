# pyright: ignore[reportInvalidTypeForme]
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from datetime import datetime


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    report = SlashCommandGroup(
        "report", "Report bugs, suggest features, or ask questions")

    @report.command(name="submit", description="Submit a bug report, suggestion, or inquiry")
    async def submit_report(
        self,
        ctx,
        category: Option(
            str,
            "Type of report",
            choices=["Bug/Error", "Suggestion", "Inquiry"],
            required=True
        ),
        message: Option(
            str,
            "Your report message",
            required=True,
            max_length=1000
        )
    ):
        await ctx.defer(ephemeral=True)

        # Get the owner (you)
        owner = await self.bot.fetch_user(int(self.bot.report_id))

        # Color based on category
        color_map = {
            "Bug/Error": discord.Color.red(),
            "Suggestion": discord.Color.blue(),
            "Inquiry": discord.Color.gold()
        }

        # Build embed
        embed = discord.Embed(
            title=f"New {category}",
            description=message,
            color=color_map.get(category, discord.Color.greyple()),
            timestamp=datetime.now(self.bot.tz)
        )
        embed.set_author(
            name=f"{ctx.author} ({ctx.author.id})",
            icon_url=ctx.author.display_avatar.url
        )
        embed.add_field(
            name="Server",
            value=f"{ctx.guild.name} ({ctx.guild.id})" if ctx.guild else "DM",
            inline=False
        )

        try:
            await owner.send(embed=embed)
            await ctx.respond("✓ Report submitted successfully! Thanks for the feedback.", ephemeral=True)
        except discord.Forbidden as e:
            await ctx.respond("✗ Couldn't send report - DMs are disabled. Please contact the bot owner directly.", ephemeral=True)
            raise e
        except Exception as e:
            await ctx.respond(f"✗ Failed to send report: {e}", ephemeral=True)
            raise e


def setup(bot):
    bot.add_cog(Report(bot))
