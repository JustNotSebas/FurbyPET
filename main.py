import discord  # pip install py-cord
import os  # part of standard library
from addons.logging import logger
from discord.ext import commands  # part of py-cord
from datetime import datetime, timedelta  # part of standard library
from dotenv import load_dotenv  # pip install python-dotenv
import pytz  # pip install pytz
import traceback  # part of standard library
import aiofiles  # pip install aiofiles

load_dotenv()

bot = commands.Bot(intents=discord.Intents.default(), auto_sync_commands=True)
bot.tz = pytz.timezone(os.getenv("TIMEZONE"))
bot.start_time = datetime.now(bot.tz)
bot.report_id = int(os.getenv("REPORT_ID"))

extensions = [  # Auto-load all command files in cmds/ directory
    f"cmds.{file[:-3]}" for file in os.listdir("cmds") if file.endswith(".py")
]


@bot.event
async def on_connect():  # Load extensions and print bot info on connect
    print(
        f"""
    ★ | Authenticated in Discord.
    User: {bot.user.name}
    ID: {bot.user.id}
        """)
    if not hasattr(bot, 'synced'):
        if extensions:
            print("★ | Loading extensions...")
            for ext in extensions:
                try:
                    bot.load_extension(ext)
                    print(f"✓ | Loaded {ext}")
                except Exception as e:
                    print(f"✗ | Failed to load {ext}: {e}")
            print()


@bot.event
async def on_ready():  # Print bot info on ready
    if not hasattr(bot, 'synced'):
        await bot.sync_commands(force=True)
        bot.synced = True
        print("✓ | Commands synced.")

    print("Guilds:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
    print(f"✓ | Ready! Ping: {round(bot.latency * 1000)}ms")


@bot.event
async def on_application_command_error(ctx, error):
    error = getattr(error, 'original', error)

    # Build error info and log it
    error_info = f"""
User: {ctx.author} ({ctx.author.id})
Guild: {ctx.guild.name or "Unknown Guild / DM" if ctx.guild else "DM"} ({ctx.guild.id if ctx.guild else 'N/A'})
Command: {ctx.command.qualified_name if ctx.command else 'Unknown'}
Error Type: {type(error).__name__}
Error Message: {str(error)}

Traceback:
{''.join(traceback.format_exception(type(error), error, error.__traceback__))}
{'-' * 70}
"""

    # Use async file I/O to avoid blocking
    try:
        async with aiofiles.open("logs/bot_errors.log", "a") as log_file:
            await log_file.write(error_info)
    except Exception as log_error:
        print(f"✗ | Failed to write to log file: {log_error}")

    print(
        f"""
    !! | An error ocurred.
    Date: {datetime.now(bot.tz).strftime('%Y-%m-%d %H:%M:%S %Z')}          
    User: {ctx.author}
    Executed in: {ctx.guild.name or "Unknown Guild / DM" if ctx.guild else "DM"} ({ctx.guild.id if ctx.guild else 'N/A'})
    Command: {ctx.command.qualified_name if ctx.command else 'Unknown'}
    Error: {type(error).__module__}.{type(error).__name__}
""")

    if ctx.interaction.response.is_done():
        return

    try:
        if isinstance(error, commands.NotOwner):
            return
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, (commands.MissingPermissions, commands.BotMissingPermissions)):
            await ctx.send(f"looks like you don't have the permissions to run this command :p")
        elif isinstance(error, discord.Forbidden):
            await ctx.send(f"i don't have the permissions to do that, sorry")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"looks like you missed an argument: {error}\nUsage: `{ctx.command.usage}`" if ctx.command.usage else f"looks like you're missing an argument: {error}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"idk what are you trying to do but you input an invalid argument: {error}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"chill out! you're on cooldown; try again in {error.retry_after:.1f} seconds.")
        elif isinstance(error, discord.NotFound):
            await ctx.send(f"whoops, can't find what you're looking for :b")
        elif isinstance(error, discord.DiscordException):
            await ctx.send(f"discord's acting up as always. try again later! (Debug info: {error})")
        else:
            await ctx.send(f"discord's got something. plz notify this error! (Debug info: {error})")
    except discord.HTTPException:
        try:
            await ctx.send_followup("An error occurred while processing the command.", ephemeral=True)
        except Exception as e:
            print("✗ | Couldn't send the error message to Discord.")

bot.run(os.getenv("TOKEN"))
