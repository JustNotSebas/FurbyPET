import os
from datetime import datetime
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import addons.exceptions as BotExceptions


class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.support_invite = os.getenv("SUPPORT_INVITE_URL")
        self.support_channel = os.getenv("SUPPORT_CHANNEL_ID")

    system = SlashCommandGroup("feedback", "Commands related to user feedback")

    @system.command(name="support", description="Get a discord invite link for support.")
    async def support(self, ctx):
        if not self.support_invite:
            raise BotExceptions.InstanceNotConfigured(
                "SUPPORT_INVITE_URL not set.")

        embed = discord.Embed(
            title="Need assistance?",
            description="Join the support server for help and feedback!",
            color=discord.Color.nitro_pink(),
        )

        embed.add_field(
            name="Invite Link",
            value=f"[Click here to join the support server.]({self.support_invite})",
            inline=False,
        )

        await ctx.respond(embed=embed, ephemeral=True)

    @system.command(
        name="submit",
        description="Submit a bug report, suggestion, or inquiry"
    )
    async def submit_report(
        self,
        ctx,
        category: Option(
            str,
            "Type of report",
            choices=["Bug/Error", "Suggestion", "Inquiry"],
            required=True
        ),  # pyright: ignore[reportInvalidTypeForm]
        message: Option(
            str,
            "Your report message",
            required=True,
            max_length=1000
        )  # pyright: ignore[reportInvalidTypeForm]
    ):
        await ctx.defer(ephemeral=True)

        if not self.support_channel:
            raise BotExceptions.InstanceNotConfigured(
                "SUPPORT_CHANNEL_ID not set.")

        support_channel = self.bot.get_channel(int(self.support_channel))
        if support_channel is None:
            raise BotExceptions.InstanceNotConfigured(
                f"Support channel {self.support_channel} not found.")

        color_map = {
            "Bug/Error": discord.Color.red(),
            "Suggestion": discord.Color.blue(),
            "Inquiry": discord.Color.gold(),
        }
        embed = discord.Embed(
            title=f"New {category}",
            description=message,
            color=color_map.get(category, discord.Color.greyple()),
            timestamp=datetime.now(self.bot.tz),
        )
        embed.set_author(
            name=f"{ctx.author} ({ctx.author.id})",
            icon_url=ctx.author.display_avatar.url,
        )
        embed.add_field(
            name="Server",
            value=f"{ctx.guild.name} ({ctx.guild.id})" if ctx.guild else "DM",
            inline=False,
        )

        try:
            await support_channel.send(embed=embed)
            await ctx.respond(
                "✓ Report submitted successfully! Thanks for the feedback. "
                "If you need further assistance, use `/feedback support`.",
                ephemeral=True
            )

        except discord.Forbidden:
            raise BotExceptions.InstanceNotConfigured(
                "Couldn't send the report message due to missing permissions.")

        except Exception:
            raise


def setup(bot):
    bot.add_cog(Feedback(bot))
