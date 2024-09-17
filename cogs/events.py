import discord
import datetime
import time
import json
import os
from discord.ext import tasks, commands
from discord.ext.commands.context import Context


class MerxEvents(commands.Cog):
    def __init__(self, merx):
        self.merx = merx

    @commands.Cog.listener()
    async def on_ready(self, ctx: commands.Context = None):
        await self.merx.change_presence(activity=discord.Activity(name="mb-help | beta.merxbot.xyz", type=discord.ActivityType.watching))
        print(self.merx.user.name + " is ready.")
            
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if welcome_channel:
            member_count = member.guild.member_count
            await welcome_channel.send(f"> {member.mention} Welcome to **{member.guild.name}**! We now have {member_count} members. 🎉 ")            


async def setup(merx):
  await merx.add_cog(MerxEvents(merx))