import discord
from discord.ext import commands

class LockChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="lock", description="Locks the current channel.")
    async def lock_channel(self, ctx):
        role = ctx.guild.default_role  # @everyone role
        channel = ctx.channel
        await channel.set_permissions(role, send_messages=False)
        await ctx.respond(f"🔒 {channel.mention} has been locked.")

def setup(bot):
    bot.add_cog(LockChannel(bot))
