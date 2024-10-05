import discord
import uuid
from discord.ext import commands
from utils.constants import cases


class WarnCommandCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx


    @commands.hybrid_command(description="You can run this command to warn a user in your server.", with_app_command=True, extras={"category": "Moderation"})
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        # Sends a DM to the user
        
        try:
            dm_message = f"<:warning:1285350764595773451> **{case_number} - You have been warned in {ctx.guild.name}** for {reason}."
            await member.send(dm_message)
        except discord.Forbidden:
            await ctx.send(f"<:xmark:1285350796841582612> Unable to send a DM to {member.mention}; warning the user in the server.")



        # Log to MongoDB, This will put the warning into the database.
        
        warn_entry = {
            "case_number": case_number,
            "guild_id": ctx.guild.id,
            "user_id": member.id,
            "moderator_id": ctx.author.id,
            "reason": reason,
            "timestamp": ctx.message.created_at.isoformat()
        }
        await cases.insert_one(warn_entry)


        await ctx.send(f"<:warning:1285350764595773451> **{case_number} - {member}** has been warned for {reason}.")



async def setup(merx):
    await merx.add_cog(WarnCommandCog(merx))