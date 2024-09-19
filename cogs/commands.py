import discord
import platform
import uuid
import shortuuid
from datetime import datetime
from discord import Interaction
from discord.ext import commands
from discord.ui import View, Button
from cogs.utils.constants import MerxConstants
from cogs.utils.embeds import AboutEmbed, AboutWithButtons


DEFAULT_EMBED_COLOR = discord.Color.from_str('#dfa4ff')


# The main commands Cog.

class CommandsCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
        self.constants = MerxConstants()
        


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
        
        
        
        mongo_db = await self.constants.mongo_setup()

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



        embed = AboutEmbed.create_info_embed(
            uptime=self.merx.start_time,
            guilds=guilds,
            users=users,
            latency=self.merx.latency,
            version=version,
            bot_name=ctx.guild.name,
            bot_icon=ctx.guild.icon,
            thumbnail_url="https://cdn.discordapp.com/avatars/1285105979947749406/3a8b148f12e07c1d83c32d4ed26f618e.png"
        )

        view = AboutWithButtons.create_view()

        await ctx.send(embed=embed, view=view)
        
        
        
    # This is a server information command that will show information about a server
    # in an easy to read emebed similar to circle bot.
    
    @commands.hybrid_command(description="Displays information about the current server.", with_app_command=True, extras={"category": "General"})
    async def serverinfo(self, ctx):
        
        # This sets the predefined values so that we can call them in the emebed.
        
        guild = ctx.guild
        owner = guild.owner
        member_count = guild.member_count
        created_at = guild.created_at.strftime("%B %d, %Y")
        role_count = len(guild.roles)
        emoji_count = len(guild.emojis)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        announcement_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel) and c.is_news()])
        forum_channels = len(guild.forums)
        verification_level = str(guild.verification_level).capitalize()
        explicit_content_filter = str(guild.explicit_content_filter).replace('_', ' ').capitalize()
        two_factor_auth = "Enabled" if guild.mfa_level == 1 else "Disabled"
        boosts = guild.premium_subscription_count
        boost_tier = guild.premium_tier
        icon_url = guild.icon.url if guild.icon else None

        embed = discord.Embed(
            title=f"Server Info - {guild.name}",
            color=DEFAULT_EMBED_COLOR,
            timestamp=datetime.utcnow()
        )

        # Add fields to the embed (organized vertically)
        
        embed.set_thumbnail(url=icon_url)
        embed.add_field(name="Server Owner", value=f"{owner}", inline=False)
        embed.add_field(name="Member Count", value=f"{member_count}", inline=False)
        embed.add_field(name="Creation Date", value=f"{created_at}", inline=False)
        embed.add_field(name="Verification Level", value=f"{verification_level}", inline=False)
        embed.add_field(name="2FA Status", value=f"{two_factor_auth}", inline=False)
        embed.add_field(name="Explicit Content Filter", value=f"{explicit_content_filter}", inline=False)

        # Channel breakdown
        
        embed.add_field(
            name="Channels",
            value=f"Text: {text_channels}\nVoice: {voice_channels}\nAnnouncements: {announcement_channels}\nForum: {forum_channels}",
            inline=False
        )

        # Roles (show only a few for brevity and a count)
        
        roles_list = ', '.join([role.mention for role in guild.roles[1:20]])
        if role_count > 20:
            roles_list += f"... and {role_count - 20} more roles."
        embed.add_field(name=f"Roles ({role_count})", value=roles_list, inline=False)

        # Emojis
        
        emoji_list = ', '.join([str(emoji) for emoji in guild.emojis[:20]])
        if emoji_count > 20:
            emoji_list += f"... and {emoji_count - 20} more emojis."
        embed.add_field(name=f"Emojis ({emoji_count})", value=emoji_list, inline=False)

        # Boost info
        
        embed.add_field(name="Boosts", value=f"{boosts} (Tier {boost_tier})", inline=False)
        await ctx.send(embed=embed)



async def setup(merx):
    await merx.add_cog(CommandsCog(merx))
