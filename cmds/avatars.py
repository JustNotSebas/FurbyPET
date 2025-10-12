# This one's the longest
import discord, asyncio, yaml, random # pip install py-cord pyyaml
from discord.ext import commands # part of py-cord
from typing import Union
from addons.user_utils import resolve_user, get_avatar_url
from addons.image_processing import petpet_gen, bonk_gen, explosion_gen

class Avatars(commands.Cog, ):
    def __init__(self, bot):
        self.bot = bot

    async def _generate_media(self,
        ctx: Union[discord.ApplicationContext, commands.Context],
        target: Union[discord.User, discord.Member, discord.Message, str],
        generator_func, effect_type): # 'petpet', 'bonk', or 'explosion'

        user = await resolve_user(
        target=target,
        bot=self.bot,
        guild=getattr(ctx, 'guild', None)
    )
        
        # Determine the response method
        is_app_command_ctx = isinstance(ctx, discord.ApplicationContext)
        send_response = ctx.respond if is_app_command_ctx else ctx.send
        ephemeral_arg = {'ephemeral': True} if is_app_command_ctx else {}

        if user is None: # In the non-zero chance user resolution fails
            await send_response("who's this user? i couldn't resolve their info. maybe try again?", **ephemeral_arg)
            return
        
        avatar_bytes = None # Initialize to None

        try:
            avatar_bytes = await user.display_avatar.with_format("png").read()

        except discord.NotFound: # 404, most likely no avatar set
            await send_response("i can't find their avatar! maybe they don't have one set...", **ephemeral_arg)
            return
        
        except discord.Forbidden: # 403, discord api blocked?
            await send_response("looks like i can't reach this user's avatar, sorry.", **ephemeral_arg)
            return
        
        except discord.HTTPException as e: # Other HTTP errors from Discord API
            status_code = getattr(e, 'status', 'Unknown')
            await send_response(f"discord is acting up. plz try again later. (Debug info: Status code {status_code})", **ephemeral_arg)
            return
        
        except discord.DiscordException as e: # Any other discord related exceptions
            await send_response(f"discord is acting up. plz try again later. (Debug info: Error {e})", **ephemeral_arg)
            return
        except Exception as e: # Catch-all for any non-discord exceptions
            await send_response(f"soooooooomething went wrong :p, try again later! (Debug info: Error {e})", **ephemeral_arg)
            return

        if avatar_bytes is None: # Previous code didn't raise, but avatar_bytes is still None
            await send_response("Looks like there was an error :[ (Debug info: avatar_bytes is none)", **ephemeral_arg)
            return

        try:
            if effect_type == 'bonk':
                filename = f"_bonk.png"
                content = f" BONK!!!!"
            elif effect_type == 'petpet':
                filename = f"_petpet.gif"
                content = f" petsss!!!!!!"
            elif effect_type == 'explosion':
                filename = f"_explosion.gif" 
                content = f" WENT BOOM!"

            else: # Should ideally not be reached
                await send_response("Looks like there was an error :[ (Debug info: Unknown avatar effect)", **ephemeral_arg)
                return

            output = generator_func(avatar_bytes, user.id) # calls the corresponding function in image_processing.py

            if output: # If output is valid
                file = discord.File(output, filename=f"{user.id}{filename}")
                await send_response(file=file, content=f"{user.mention} {content}")
                if hasattr(output, 'close'):
                    output.close()
            else: # If output is None or invalid
                await send_response("Looks like there was an error :[ (Debug info: output was never returned)", **ephemeral_arg)
                return

        except Exception as e: # This catches errors during the image generation (PIL errors, petpetgif errors, etc.)
        
            error_message = f"An error occurred during image generation: {e}"
            print(error_message) # Log the full error to your console

            await send_response("something went wrong while generating the image...", **ephemeral_arg)
            return


    DEFAULT_INTEGRATIONS = {discord.IntegrationType.guild_install, discord.IntegrationType.user_install} # Allow both guild and user context menus

    @commands.user_command(name="Pet the user!", integration_types=DEFAULT_INTEGRATIONS)
    async def petpet_user_command(self, ctx: discord.ApplicationContext, user: discord.User):
        await ctx.defer()
        await self._generate_media(ctx, user, petpet_gen, 'petpet')
        print(f"{ctx.author} pet {user}!")
    
    
    @commands.user_command(name="Explode the user!", integration_types=DEFAULT_INTEGRATIONS)
    async def explosion_user_command(self, ctx: discord.ApplicationContext, user: discord.User):
        await ctx.defer()
        await self._generate_media(ctx, user, explosion_gen, 'explosion')
        print(f"{ctx.author} exploded {user}!")

    @commands.user_command(name="Bonk the user!", integration_types=DEFAULT_INTEGRATIONS)
    async def bonk_user_command(self, ctx: discord.ApplicationContext, user: discord.User):
        await ctx.defer()
        await self._generate_media(ctx, user, bonk_gen, 'bonk')
        print(f"{ctx.author} bonked {user.display_name}!")


def setup(bot):
    bot.add_cog(Avatars(bot))
