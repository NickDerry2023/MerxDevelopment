import discord
from discord.ext import commands

class UnlockChannel(commands.Cog):
    def __init__(self, bot, lock_cog):
        self.bot = bot
        self.lock_cog = lock_cog

    @commands.slash_command(name="unlock", description="Unlocks the current channel and restores original permissions.")
    async def unlock_channel(self, ctx):
        role = ctx.guild.default_role
        channel = ctx.channel
        if channel.id in self.lock_cog.locked_channels:
            original_permission = self.lock_cog.locked_channels.pop(channel.id)
            await channel.set_permissions(role, send_messages=original_permission)
            await ctx.respond(f"🔓 {channel.mention} has been unlocked and permissions restored.")
        else:
            await ctx.respond(f"Channel {channel.mention} is not locked.")

def setup(bot):
    lock_cog = bot.get_cog("LockChannel")
    bot.add_cog(UnlockChannel(bot, lock_cog))
