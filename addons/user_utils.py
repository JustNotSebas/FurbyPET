import discord # pip install py-cord
from typing import Union, Optional # part of standard library

async def resolve_user(target: Optional[Union[discord.User, discord.Member, discord.Message, str]], bot, guild: Optional[discord.Guild] = None):
    # Resolves an user's info from any given input:
    # discord.User, discord.Member, discord.Message, or a provided user ID 
    if target is None: # No target provided
        return None
    
    if isinstance(target, discord.Member): # Directly return Member if already one
        return target
    
    if isinstance(target, discord.User): # If User, try to get Member if guild provided
        if guild:
            user_id = int(target.id)
            member = guild.get_member(user_id)
            if member is None:
                try:
                    member = await guild.fetch_member(user_id)
                except discord.HTTPException:
                    pass
            return member or target # Return member if found, otherwise the User object
        return target # If no guild, just return the User object directly
    
    if isinstance(target, discord.Message): # If Message, resolve the author by recursion
        return await resolve_user(target.author, bot, guild) 
    
    try: # Else...
        user_id = int(target)
        if guild: # Try to get Member if guild provided
            member = guild.get_member(user_id) # Check cache first
            if member is None:
                try:
                    member = await guild.fetch_member(user_id) # Fetch if not in cache
                except discord.HTTPException:
                    pass
            return member
        return await bot.fetch_user(user_id) # Fetch User if no guild
    
    except (ValueError, discord.NotFound, discord.Forbidden):
        raise Exception("Failed to resolve user")

async def get_avatar_url(ctx: discord.ApplicationContext, target: Optional[Union[discord.User, discord.Member, discord.Message, str]]):
    # Gets the avatar URL of a user from any given input:
    user = await resolve_user(target, ctx.bot, ctx.guild)
    if user is None:
        await ctx.respond("Couldn't resolve that user.", ephemeral=True)
        return
    avatar_url = user.display_avatar.with_format("png").url
    await ctx.respond(f"{user.name}'s avatar: {avatar_url}", ephemeral=True)
