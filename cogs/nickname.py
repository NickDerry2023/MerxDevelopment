import discord
import asyncio
import uuid
import shortuuid
from discord.ext import commands
from cogs.utils.embeds import ErrorEmbed, PermissionDeniedEmbed
from cogs.utils.constants import MerxConstants


constants = MerxConstants()


class NickCommandCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx


    # This is the command that you can use to nickname users. You can enter the user you want to nickname
    # followed by the new name. To clear a nickname you can do m-nick @User followed by no new name.
    # You can also use User IDs instead of pinging the user.

    @commands.hybrid_command(description="Allows you to nickname a user in a server to whatever you want.", with_app_command=True, extras={"category": "General"})
    @commands.has_permissions(administrator=True)
    async def nick(self, ctx, member: discord.Member, *, nickname: str = None):


        previous_nickname = member.display_name


        try:
            
            await member.edit(nick=nickname if nickname else None)

            embed = NicknameSuccessEmbed(
                user=member,
                previous_name=previous_nickname,
                new_name=nickname if nickname else "Cleared"
            )
            
            await ctx.send(embed=embed)


        # Checks permissions and for common command errors.

        except discord.Forbidden:
            await self.handle_permission_denied(ctx)



async def setup(merx):
    await merx.add_cog(NickCommandCog(merx))
