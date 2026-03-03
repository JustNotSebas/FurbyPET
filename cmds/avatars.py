# This one's the longest
import discord
from discord.ext import commands  # part of py-cord
from typing import Union
from addons.user_utils import resolve_user
from addons.image_processing import petpet_gen, bonk_gen, explosion_gen


class Avatars(commands.Cog, ):
    def __init__(self, bot):
        self.bot = bot

    async def _generate_media(self,
                              ctx: discord.ApplicationContext,
                              target: Union[discord.User, discord.Member, discord.Message, str],
                              generator_func, effect_type):  # 'petpet', 'bonk', or 'explosion'

        user = await resolve_user(
            target=target,
            bot=self.bot,
        )

        if user is None:  # In the non-zero chance user resolution fails
            await ctx.respond("who's this user? i couldn't resolve their info. maybe try again?", ephemeral=True)
            return
        try:
            avatar_bytes = await user.display_avatar.with_format("png").read()
        except discord.NotFound:  # 404, most likely no avatar set
            await ctx.respond("i couldn't find this avatar! maybe they don't have one set?", ephemeral=True)
            return
        except discord.HTTPException as e:  # Other HTTP errors from Discord API
            status_code = getattr(e, 'status', 'Unknown')
            await ctx.respond(f"looks like discord couldn't handle this. try again later! (Debug info: Status code {status_code})", ephemeral=True)
            return
        except Exception as e:  # Catch-all for any non-discord exceptions
            await ctx.respond(f"looks like something went wrong, try again later! (Debug info: Error {e})", ephemeral=True)
            return
        try:
            if effect_type == 'bonk':
                filename = "_bonk.png"
                content = "BONK!!!!"
            elif effect_type == 'petpet':
                filename = "_petpet.gif"
                content = "petsss!!!!!!"
            elif effect_type == 'explosion':
                filename = "_explosion.gif"
                content = "WENT BOOM!"
            else:  # Should ideally not be reached
                await ctx.respond("Looks like there was an error :[ (Debug info: Unknown avatar effect)", ephemeral=True)
                return
            # calls the corresponding function in image_processing.py
            output = generator_func(avatar_bytes)
            file = discord.File(output, filename=f"{user.id}{filename}")
            await ctx.respond(file=file, content=f"{user.mention} {content}")
            if hasattr(output, 'close'):
                output.close()
        # This catches errors during the image generation (PIL errors, petpetgif errors, etc.)
        except Exception as e:
            await ctx.respond("something went wrong while generating the image...", ephemeral=True)
            raise e

    # Allow both guild and user context menus
    DEFAULT = {discord.IntegrationType.guild_install,
               discord.IntegrationType.user_install}

    @commands.user_command(name="Pet the user!", integration_types=DEFAULT)
    async def petpet_user_command(self, ctx: discord.ApplicationContext, user: discord.User):
        await ctx.defer()
        await self._generate_media(ctx, user, petpet_gen, 'petpet')
        print(f"{ctx.author} pet {user}!")

    @commands.message_command(name="Pet the user!", integration_types=DEFAULT)
    async def petpet_msg_command(self, ctx: discord.ApplicationContext, message: discord.Message):
        await ctx.defer()
        await self._generate_media(ctx, message, petpet_gen, 'petpet')
        print(f"{ctx.author} pet {message.author}!")

    @commands.user_command(name="Explode the user!", integration_types=DEFAULT)
    async def explosion_user_command(self, ctx: discord.ApplicationContext, user: discord.User):
        await ctx.defer()
        await self._generate_media(ctx, user, explosion_gen, 'explosion')
        print(f"{ctx.author} exploded {user}!")

    @commands.message_command(name="Explode the user!", integration_types=DEFAULT)
    async def explosion_msg_command(self, ctx: discord.ApplicationContext, message: discord.Message):
        await ctx.defer()
        await self._generate_media(ctx, message, explosion_gen, 'explosion')
        print(f"{ctx.author} exploded {message.author}!")

    @commands.user_command(name="Bonk the user!", integration_types=DEFAULT)
    async def bonk_user_command(self, ctx: discord.ApplicationContext, user: discord.User):
        await ctx.defer()
        await self._generate_media(ctx, user, bonk_gen, 'bonk')
        print(f"{ctx.author} bonked {user}!")

    @commands.message_command(name="Bonk the user!", integration_types=DEFAULT)
    async def bonk_msg_command(self, ctx: discord.ApplicationContext, message: discord.Message):
        await ctx.defer()
        await self._generate_media(ctx, message, bonk_gen, 'bonk')
        print(f"{ctx.author} bonked {message.author}!")


def setup(bot):
    bot.add_cog(Avatars(bot))
