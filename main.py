import discord, platform, sys, psutil, os # pip install py-cord psutil
from discord.ext import commands # part of py-cord
from datetime import datetime, timedelta # part of standard library
from dotenv import load_dotenv # pip install python-dotenv

load_dotenv()

token = os.getenv("TOKEN") # Set on .env file or environment variable
intents = discord.Intents.all() # For convenience; adjust as needed
bot = commands.Bot(command_prefix=commands.when_mentioned_or("."), intents=intents, auto_sync_commands=True)
bot.start_time = datetime.now()

extensions = [ # Auto-load all command files in cmds/ directory
    f"cmds.{file[:-3]}" for file in os.listdir("cmds") if file.endswith(".py")
]

@bot.event
async def on_connect(): # Load extensions and print bot info on connect
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connected as {bot.user.name} ({bot.user.id})")
    if extensions:
        print("Loading extensions...")
        for ext in extensions:
            try:
                bot.load_extension(ext)
                print(f"✓ Loaded {ext}")
            except Exception as e:
                print(f"✗ Failed to load {ext}: {e}")

@bot.event
async def on_ready(): # Print bot info on ready
    if not hasattr(bot, 'synced'):
        await bot.sync_commands(force=True)
        bot.synced = True
        print("✓ Commands synced.")

    print("Guilds:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
    print(f"✓ Ready! Ping: {round(bot.latency * 1000)}ms")

@bot.event
async def on_command_error(ctx, error): # Global error handler
        if isinstance(error, commands.NotOwner):
            return
        elif isinstance(error, commands.CommandNotFound) or isinstance(error, discord.ext.commands.errors.CommandNotFound):
            print(f"[bot info]: {ctx.author} attempted command '{ctx.invoked_with}' but it doesn't exist.")
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.BotMissingPermissions):
            print(f"[bot warning]: Permissions error for {ctx.author} with command {ctx.command}: {error}")
            await ctx.send(f"looks like you don't have the permissions to run this command :p")
        elif isinstance(error, commands.MissingRequiredArgument):
            print(f"[bot warning]: Missing argument for {ctx.author} with command {ctx.command}: {error}")
            await ctx.send(f"looks like you missed an argument: {error}\nUsage: `{ctx.command.usage}`" if ctx.command.usage else f"looks like you're missing an argument: {error}")
        elif isinstance(error, commands.BadArgument):
            print(f"[bot warning]: Bad argument for {ctx.author} with command {ctx.command}: {error}")
            await ctx.send(f"idk what are you trying to do but you input an invalid argument: {error}")
        elif isinstance(error, commands.CommandOnCooldown):
            print(f"[bot info]: Command {ctx.command} on cooldown for {ctx.author}: {error}")
            await ctx.send(f"chill out! you're on cooldown; try again in {error.retry_after:.1f} seconds.")
        elif isinstance(error, discord.DiscordException):
            print(f"[bot exception]: A Discord API error occurred for {ctx.author} with command {ctx.command}: {error}")
            await ctx.send(f"discord's acting up as always. try again later! (Debug info: {error})")
        else:
            print(f"[bot exception]: An unhandled error occurred with command '{ctx.invoked_with}': {error}")
            await ctx.send(f"discord's got something. plz notify this error! (Debug info: {error})")


bot.run(token)