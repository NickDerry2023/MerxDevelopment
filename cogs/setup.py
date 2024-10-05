import discord
from discord import Interaction
from discord.ext import commands
from utils.constants import MerxConstants, setup_col
from utils.modals import BotConfigModal, PluginConfigModal
from utils.embeds import SuccessEmbed, InfoEmbed, ExitSetupEmbed
import uuid

constants = MerxConstants()


# Omg this file was fucking hell to get working. There are some issues with it still
# when the user submits their entries in the modal it says "Something went wrong" in
# discord but the data still submits and everything works as intended. I may fix this
# at a late date or someone else can cause fuck python.


class SetupOptionsView(discord.ui.View):
    def __init__(self, merx, show_bot_config, show_plugin_config, show_moderation_config, show_administration_config):
        self.merx = merx
        super().__init__(timeout=None)
        self.add_item(SetupDropdown(merx, show_bot_config, show_plugin_config, show_moderation_config, show_administration_config))



class SetupDropdown(discord.ui.Select):
    def __init__(self, merx, show_bot_config, show_plugin_config, show_moderation_config, show_administration_config):
        self.merx = merx
        
        
        # Define the options for the dropdown menu
        
        options = []
        
        if show_bot_config:
            options.append(discord.SelectOption(label="Bot Config", value="bot_config", description="Configure the bot's settings"))
            
        if show_plugin_config:
            options.append(discord.SelectOption(label="Plugin Config", value="plugin_config", description="Configure plugins"))
            
        if show_moderation_config:
            options.append(discord.SelectOption(label="Moderation Config", value="moderation_config", description="Configure moderation settings"))
            
        if show_administration_config:
            options.append(discord.SelectOption(label="Administration Config", value="administration_config", description="Configure administration settings"))
            

        super().__init__(placeholder="Select a setup option...", min_values=1, max_values=1, options=options)
        
        

    async def callback(self, interaction: discord.Interaction):
        
        
        # Handle the interaction based on what the user selects
        
        # await interaction.response.defer()

        if self.values[0] == "bot_config":
            await interaction.response.send_modal(BotConfigModal(self.view.merx, str(uuid.uuid4()), interaction.guild.id))
            
            
        elif self.values[0] == "plugin_config":
            await interaction.response.send_modal(PluginConfigModal(self.view.merx, str(uuid.uuid4()), interaction.guild.id))
            
            
        elif self.values[0] == "moderation_config":
            await interaction.response.send_modal(PluginConfigModal(self.view.merx, str(uuid.uuid4()), interaction.guild.id))
            
            
        elif self.values[0] == "administration_config":
            await interaction.response.send_modal(PluginConfigModal(self.view.merx, str(uuid.uuid4()), interaction.guild.id))



class SetupCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
        self.setup_message_id = None
        self.constants = MerxConstants()



    # This gets the embed color from the Mongo DB collection setup for users who want a custom embed
    # color so that they can make the bot their own. Uses DEFAULT_EMBED_COLOR from the checks file
    # to set Merx Purple fall back color in case one is not set of it the bot is brand new.

    async def fetch_embed_color(self, guild_id: int) -> discord.Color:
        return discord.Color.default()



    # This fetches the guild config we do this so that we can get the banner information as well as prefix
    # and guild info this allows the checking of existing data to prevent resetting shit up and creating
    # duplicate entries.

    async def fetch_guild_config(self, guild_id: int) -> dict:
        bot_config = await setup_col.find_one({"guild_id": guild_id, "prefix": {"$exists": True}})
        return {
            "prefix": bot_config.get("prefix") if bot_config else None,
            "theme_color": bot_config.get("theme_color") if bot_config else None
        }
        
        
        
    # This is the actual setup command, it shows a disclaimer telling the user they need the right permissions and info
    # we do this so that if they arent the intended user they can back out and let the right user set the bot up. This
    # command now support reconfigurations as well.

    @commands.hybrid_command(description="Set up the bot configuration.", with_app_command=True, extras={"category": "Setup"})
    async def setup(self, ctx: commands.Context, reconfigure: bool = False):
        await ctx.defer(ephemeral=False)
        embed_color = await self.fetch_embed_color(ctx.guild.id)


        # Checks to see if the reconfigure parameter is passed in the command for example /setup reconfigure if its not then
        # treat it like normal setup.

        if reconfigure:
            disclaimer_embed = InfoEmbed(
                title="Merx Reconfiguration",
                description="This will guide you through reconfiguring your bot's settings.",
                color=embed_color
            )
        else:
            disclaimer_embed = InfoEmbed(
                title="Merx Setup",
                description=(
                    "Welcome to the Merx setup process! This will guide you through configuring your bot's prefix, theme color, "
                    "plugin settings, and other bot features. Make sure you have the necessary permissions and information. \n\nClick '**Continue**' to start."
                ),
                color=embed_color
            )
            
            
        # This is now updated with a custom class so that we arent recalling the same things for embeds each time.

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Continue", style=discord.ButtonStyle.primary, custom_id="continue"))
        self.setup_message_id = (await ctx.send(embed=disclaimer_embed, view=view)).id



    # This is the start setup function which kick starts the setup process.

    async def start_setup(self, interaction: Interaction):
        
        
        guild_id = interaction.guild.id
        guild_config = await self.fetch_guild_config(guild_id)
        embed_color = await self.fetch_embed_color(guild_id)
        
        
        # Informs the user setup is already complete and checks to see if it truly is complete.
        # this is so that suers cant make several duplicate entries into Mongo as they are stored
        # uniquely with a different ID each time setup is run.

        if guild_config.get("prefix") and guild_config.get("banner_url") and not interaction.data.get("reconfigure"):
            embed = SuccessEmbed(
                title="Setup Completed",
                description="The setup process is already complete. No further action is needed."
            )
            
            
            if self.setup_message_id:
                setup_message = await interaction.channel.fetch_message(self.setup_message_id)
                await setup_message.edit(embed=embed, view=None)
                
                
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return



        # We are now using the custom class for Success and Error embeds as well and the new custom error handler.

        view = SetupOptionsView(
            merx=self.merx,
            show_bot_config=not guild_config.get("prefix"),
            show_plugin_config=not guild_config.get("enabled_plugins"),
            show_moderation_config=not guild_config.get("moderation_config"),
            show_administration_config=not guild_config.get("administration_config")
        )


        setup_embed = InfoEmbed(
            title="Merx Setup",
            description="Choose an option to proceed or exit the setup process.",
            color=embed_color
        )


        # Embed pre operation? nick i cant understand ur spelling for jack shit not much to add here. Dont remove this.

        if self.setup_message_id:
            setup_message = await interaction.channel.fetch_message(self.setup_message_id)
            await setup_message.edit(embed=setup_embed, view=view)
            
            
        else:
            await interaction.response.send_message(embed=setup_embed, view=view)
            
            

    # On Interaction Function

    async def on_interaction(self, interaction: Interaction):
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id")

            if interaction.response.is_done():
                return

            if custom_id == "continue":
                await interaction.response.defer()
                await self.start_setup(interaction)
            elif custom_id == "exit":
                await interaction.response.defer()
                await self.exit_setup_callback(interaction)



    # This is the exit setup callback to listen to see if the user exits setup or is forced out
    # of setup. This also includes a embed saying setup was cancelled.

    async def exit_setup_callback(self, interaction: Interaction):
        exit_embed = ExitSetupEmbed()

        if self.setup_message_id:
            try:
                setup_message = await interaction.channel.fetch_message(self.setup_message_id)
                await setup_message.edit(embed=exit_embed, view=None)
            except discord.NotFound:
                await interaction.response.send_message(embed=exit_embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=exit_embed)



async def setup(merx):
    cog = SetupCog(merx)
    await merx.add_cog(cog)
    merx.add_listener(cog.on_interaction, "on_interaction")
    
    
