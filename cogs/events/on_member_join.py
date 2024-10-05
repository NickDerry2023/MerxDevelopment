import discord
from discord.ext import commands
from utils.constants import MerxConstants

CHANNEL_NAME_FOR_WELCOME = ["chat", "general"]
constants = MerxConstants()

class OnMemberJoin(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
            

    if constants.merx_environment_type() == "Production":
        @commands.Cog.listener()
        async def on_member_join(self, member: discord.Member):
            welcome_channel = discord.utils.get(member.guild.text_channels, name=CHANNEL_NAME_FOR_WELCOME)
            welcome_channel = None
            for channel_name in CHANNEL_NAME_FOR_WELCOME:
                welcome_channel = discord.utils.get(member.guild.text_channels, name=channel_name)
                if welcome_channel:
                    break
            
            if welcome_channel:
                member_count = member.guild.member_count
                await welcome_channel.send(f"{member.mention} Welcome to **{member.guild.name}**! Feel free to explore. We now have **{member_count}** members. 🎉")         
                

async def setup(merx):
  await merx.add_cog(OnMemberJoin(merx))