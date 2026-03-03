import discord  # pip install py-cord
from typing import Union, Optional  # part of standard library


async def resolve_user(
    target: Optional[Union[discord.User, discord.Member, discord.Message, str]],
    bot,
    guild: Optional[discord.Guild] = None,
):
    if target is None:
        return None

    if isinstance(target, discord.Message):
        if target.webhook_id is not None:
            return target.author
        return await resolve_user(target.author, bot, guild)

    if isinstance(target, discord.Member):
        guild = target.guild
        try:
            return await guild.fetch_member(target.id)
        except (discord.HTTPException, discord.NotFound):
            print(
                f"Failed to fetch {target.name} ({target.id}) from guild {guild.id}. Fetching user object.")
        try:
            return await bot.fetch_user(target.id)
        except (discord.HTTPException, discord.NotFound) as e:
            raise Exception("Failed to resolve user") from e

    if isinstance(target, discord.User):
        try:
            return await bot.fetch_user(target.id)
        except (discord.HTTPException, discord.NotFound) as e:
            raise Exception("Failed to resolve user") from e
    try:
        user_id = int(target)
        try:
            return await bot.fetch_user(user_id)
        except (discord.HTTPException, discord.NotFound) as e:
            raise Exception("Failed to resolve user") from e
    except ValueError as e:
        raise Exception("Invalid user ID format") from e
    except (discord.NotFound, discord.Forbidden) as e:
        raise Exception("Failed to resolve user") from e
