import discord  # pip install py-cord
from typing import Union, Optional  # part of standard library


async def resolve_user(
    target: Optional[Union[discord.User, discord.Member, discord.Message, str]],
    bot,
    guild: Optional[discord.Guild] = None
):
    if target is None:
        return None

    if isinstance(target, discord.Member):
        return await target.guild.fetch_member(target.id)

    if isinstance(target, discord.User):
        if guild:
            try:
                return await guild.fetch_member(target.id)
            except (discord.HTTPException, discord.NotFound):
                pass
        return await bot.fetch_user(target.id)

    if isinstance(target, discord.Message):
        return await resolve_user(target.author, bot, guild)

    try:
        user_id = int(target)
        if guild:
            try:
                return await guild.fetch_member(user_id)
            except (discord.HTTPException, discord.NotFound):
                pass
        return await bot.fetch_user(user_id)

    except ValueError:
        raise Exception("Invalid user ID format")
    except (discord.NotFound, discord.Forbidden) as e:
        raise Exception("Failed to resolve user") from e


async def get_avatar_url(ctx: discord.ApplicationContext, target: Optional[Union[discord.User, discord.Member, discord.Message, str]]):
    # Gets the avatar URL of a user from any given input:
    user = await resolve_user(target, ctx.bot, ctx.guild)
    if user is None:
        await ctx.respond("Couldn't resolve that user.", ephemeral=True)
        return
    avatar_url = user.display_avatar.with_format("png").url
    await ctx.respond(f"{user.name}'s avatar: {avatar_url}", ephemeral=True)
