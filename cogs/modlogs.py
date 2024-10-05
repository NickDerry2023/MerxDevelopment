import discord
from discord.ext import commands
from utils.constants import cases

class ModLogsCommandCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx

    @commands.hybrid_group(description="Group command")
    async def modlogs(self, ctx: commands.Context):
        return
    
    @modlogs.command(description="View all modlogs for certain user", with_app_command=True, extras={"category": "Moderation"})
    async def view(self, ctx, member: discord.Member):  
        description=""
        number = 0
        
        embed = discord.Embed(title=f"{number} Logs", description=description, color=discord.Color.blue())
        results = cases.find({'user_id': member.id, "guild_id": ctx.guild.id})
        async for result in results:
            number += 1
            embed.add_field(name=f"{result.get('case_id')} | {result.get('type')}", value=f"Reason: {result.get('reason')}\nModerator: <@{result.get('moderator_id')}>\nDate: <t:{results.get('timestamp')}:F>")
        
        try:
            embed.set_author(name=f"{member.name}\'s Modlogs", icon_url=member.avatar.url)
        except:
            embed.set_author(name=f"{member.name}\'s Modlogs", icon_url=member.default_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        await ctx.send(embed=embed)

    @modlogs.command(description="Transfer all modlogs to a different user", with_app_command=True, extras={"category": "Moderation"})
    async def transfermodlogs(self, ctx, olduser: discord.Member = None, newuser: discord.Member = None):  
        await ctx.send(f"All moderation logs for **{olduser.name}** have been transfered to **{newuser}**")
    
    @modlogs.command(description="Clear all modlogs for a certain user", with_app_command=True, extras={"category": "Moderation"})
    async def clearmodlogs(self, ctx, member: discord.Member = None):
        await ctx.send(f"All moderation logs have been cleared for **{member.name}**.")



async def setup(merx):
    await merx.add_cog(ModLogsCommandCog(merx))