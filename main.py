import discord
from discord.ext import commands
from dotenv import load_dotenv
import pytz
from addons.logging import logger  # addons/logging.py
import addons.exceptions as BotExceptions  # addons/exceptions.py
import os
from datetime import datetime
import traceback

load_dotenv()

bot = commands.Bot(intents=discord.Intents.default(), auto_sync_commands=True)
bot.tz = pytz.timezone(os.getenv("TIMEZONE"))
bot.start_time = datetime.now(bot.tz)

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


# Build detailed error info and optionally include traceback
def error_builder(ctx, error, tb=False):
    if tb:
        error_traceback = f"""
    User: {ctx.author} ({ctx.author.id})
    Guild: {ctx.guild.name or "Unknown Guild / DM" if ctx.guild else "DM"} ({ctx.guild.id if ctx.guild else 'N/A'})
    Command: {ctx.command.qualified_name if ctx.command else 'Unknown'}
    Error Type: {type(error).__name__}
    Error Message: {str(error)}
Traceback:
{''.join(traceback.format_exception(type(error), error, error.__traceback__))}
{'-' * 70}
"""
        return error_traceback

    error_info = f"""
    Date: {datetime.now(bot.tz).strftime('%Y-%m-%d %H:%M:%S %Z')}          
    User: {ctx.author}
    Executed in: {ctx.guild.name or "Unknown Guild / DM" if ctx.guild else "DM"} ({ctx.guild.id if ctx.guild else 'N/A'})
    Command: {ctx.command.qualified_name if ctx.command else 'Unknown'}
    Error: {type(error).__module__}.{type(error).__name__}
    """
    return error_info


@bot.event
async def on_application_command_error(ctx, error):
    error = getattr(error, 'original', error)

    if isinstance(error, discord.NotFound) and error.code == 10062:
        # I have come to terms with the fact that I can't fight Discord's API
        return
    error_traceback = error_builder(ctx, error, tb=True)
    logger.error(error_traceback)

    error_info = error_builder(ctx, error, tb=False)
    print(
        f"""
    !! | An error occurred.
    {error_info}""")

    if not ctx.response.is_done():
        try:
            if isinstance(error, discord.NotFound):
                await ctx.respond(f"whoops, can't find what you're looking for :b")
            elif isinstance(error, commands.NotOwner):
                return
            elif isinstance(error, commands.CommandNotFound):
                return
            elif isinstance(error, BotExceptions.InstanceNotConfigured):
                extra = f" details: {error}" if str(error) else ""
                await ctx.respond(f"this instance of the bot is not properly configured. please contact the instance's administrator." + extra, ephemeral=True)
            elif isinstance(error, (commands.MissingPermissions, commands.BotMissingPermissions)):
                await ctx.respond(f"looks like you don't have the permissions to run this command :p")
            elif isinstance(error, discord.Forbidden):
                await ctx.respond(f"i don't have the permissions to do that, sorry")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.respond(f"looks like you missed an argument: {error}\nUsage: `{ctx.command.usage}`" if ctx.command.usage else f"looks like you're missing an argument: {error}")
            elif isinstance(error, commands.BadArgument):
                await ctx.respond(f"idk what are you trying to do but you input an invalid argument: {error}")
            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.respond(f"chill out! you're on cooldown; try again in {error.retry_after:.1f} seconds.")
            elif isinstance(error, discord.DiscordException):
                await ctx.respond(f"discord's acting up as always. try again later! (Debug info: {error})")
            else:
                await ctx.respond(f"discord's got something. plz notify this error! (Debug info: {error})")
        except discord.HTTPException:
            try:
                await ctx.respond("An error occurred while processing the command.", ephemeral=True)
            except Exception as e:
                print("✗ | Couldn't send the error message to Discord.")

try:
    bot.run(os.getenv("TOKEN"))
except discord.LoginFailure as e:
    logger.critical(f"Failed to authenticate: {e}")
    print("✗ | Invalid or missing token. Check your .env file.")
except Exception as e:
    logger.critical(f"Failed to start the bot: {e}")
    print(f"✗ | Failed to start the bot: {e}")
