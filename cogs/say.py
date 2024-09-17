import discord
import asyncio
import uuid
from discord.ext import commands
from cogs.utils.embeds import NicknameSuccessEmbed, ErrorEmbed, PermissionDeniedEmbed
from cogs.utils.errors import send_error_embed
from cogs.utils.constants import MerxConstants


constants = MerxConstants()


class SayCommandCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx


    # This is a say command that allows users to say things using the bot.

    @commands.hybrid_command(description="Use this command to say things to people using the bot.", with_app_command=True, extras={"category": "General"})
    async def say(self, ctx, *, message: str):
        

        try:
            await ctx.message.delete()
            await ctx.send(message)
        except Exception as e:
            error_id = str(uuid.uuid4())
            await send_error_embed(interaction, e, error_id)
            
            
            
    async def handle_permission_denied(self, ctx):
        embed = PermissionDeniedEmbed()
        await ctx.send(embed=embed)



    async def handle_error(self, ctx, error):
        error_id = str(uuid.uuid4())
        if isinstance(ctx, discord.Interaction):
            await send_error_embed(ctx, error, error_id)
        else:
            await ctx.send(embed=ErrorEmbed(error=error, error_id=error_id))


    # These are the cog error handlers they determine how the error is sent.

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self.handle_error(ctx, error.original if isinstance(error, commands.CommandInvokeError) else error)


    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        await self.handle_error(interaction, error)


async def setup(merx):
    await merx.add_cog(SayCommandCog(merx))
