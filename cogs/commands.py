import discord
import platform
import uuid
import shortuuid
import datetime
from datetime import datetime
from discord import Interaction
from discord.ext import commands
from discord.ui import View, Button
from cogs.utils.constants import MerxConstants
from cogs.utils.embeds import AboutEmbed, AboutWithButtons, ServerInformationEmbed
from cogs.utils.errors import send_error_embed


constants = MerxConstants()


# The main commands Cog.

class CommandsCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
        


    # This is the info Command for merx. Place every other command before this one, this should be the last command in
    # this file for readability purposes.

    @commands.hybrid_command(description="Provides important information about merx.", with_app_command=True, extras={"category": "Other"})
    async def about(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)
        
        
        # Try to delete the command message to clean up the discord response so that its not as messy
        
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass
        
        
        
        mongo_db = await constants.mongo_setup()

        if mongo_db is None:
            await ctx.send("<:xmark:1285350796841582612> Failed to connect to the database. Please try again later.", ephemeral=True)
            return
        
        
        
        # Collect information for the embed such as the bots uptime, hosting information, database information
        # user information and server information so that users can see the growth of the bot.
        
        uptime_seconds = getattr(self.merx, 'uptime', 0)
        uptime_formatted = f"<t:{int((self.merx.start_time.timestamp()))}:R>"
        guilds = len(self.merx.guilds)
        users = sum(guild.member_count for guild in self.merx.guilds)
        version_info = await mongo_db.command('buildInfo')
        version = version_info.get('version', 'Unknown')
        shards = self.merx.shard_count or 1
        cluster = 0
        environment = constants.merx_environment_type()
        
        
        # Formats the date and time
        
        command_run_time = datetime.now()
        formatted_time = command_run_time.strftime("Today at %I:%M %p UTC")


        # This builds the emebed.

        embed = AboutEmbed.create_info_embed(
            uptime=self.merx.start_time,
            guilds=guilds,
            users=users,
            latency=self.merx.latency,
            version=version,
            bot_name=ctx.guild.name,
            bot_icon=ctx.guild.icon,
            shards=shards,
            cluster=cluster,
            environment=environment,
            command_run_time=formatted_time,
            thumbnail_url="https://cdn.discordapp.com/avatars/1285105979947749406/3a8b148f12e07c1d83c32d4ed26f618e.png"
        )


        # Send the emebed to view.

        view = AboutWithButtons.create_view()

        await ctx.send(embed=embed, view=view)
        
        
        
    # This is a server information command that will show information about a server
    # in an easy to read emebed similar to circle bot.
    
    @commands.hybrid_command(description="Displays information about the current server.", with_app_command=True, extras={"category": "General"})
    async def serverinfo(self, ctx):

        try:

            embed = ServerInformationEmbed(ctx.guild, constants).create_embed()

            if isinstance(ctx, Interaction):
                
                await ctx.response.send_message(embed=embed)
                
            elif isinstance(ctx, commands.Context):
                
                await ctx.send(embed=embed)
            
            
        except Exception as e:
            error_id = shortuuid.ShortUUID().random(length=8)
            print(f"Exception occurred: {e}")
            await send_error_embed(ctx, e, error_id)
            
            
    
    # This is the space for the ping command which will allow users to ping.
    
    @commands.hybrid_command(name="ping", description="Check the bot's latency and uptime.")
    async def ping(self, ctx: commands.Context):
  
        # Calculate latency and uptime
  
        websocket_latency = round(self.merx.ws.latency * 1000)
        uptime_seconds = (datetime.now() - self.merx.start_time).total_seconds()
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, _ = divmod(remainder, 60)


        # Create the embed using the SuccessEmbed class
        
        embed = SuccessEmbed(
            title="Bot Status",
            description="Here are the bot's current stats:",
            color=discord.Color.green()
        )
        
        
        embed.add_field(name="Latency", value=f"{self.merx.latency}ms", inline=False)
        embed.add_field(name="Websocket Latency", value=f"{self.merx.latency}ms", inline=False)
        embed.add_field(name="Uptime", value=f"{int(hours)} hours, {int(minutes)} minutes", inline=False)

        await ctx.send(embed=embed)
        


async def setup(merx):
    await merx.add_cog(CommandsCog(merx))
