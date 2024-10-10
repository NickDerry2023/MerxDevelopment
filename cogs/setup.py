import discord
from discord import Interaction
from discord.ext import commands
from utils.constants import MerxConstants, setup_col
from utils.modals import BotConfigModal, PluginConfigModal
from utils.embeds import SuccessEmbed, InfoEmbed, ExitSetupEmbed
import uuid

constants = MerxConstants()

embed_color = constants.merx_embed_color_setup()


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
            options.append(discord.SelectOption(label="🛠️ Merx Configuration", value="bot_config", description=""))
            
        if show_plugin_config:
            options.append(discord.SelectOption(label="📦 Plugins Configuration", value="plugin_config", description=""))
            
        # if show_moderation_config:
        #     options.append(discord.SelectOption(label="Moderation Config", value="moderation_config", description="Configure moderation settings"))
            
        # if show_administration_config:
        #    options.append(discord.SelectOption(label="Administration Config", value="administration_config", description="Configure administration settings"))
            

        super().__init__(placeholder="Select a setup option...", min_values=1, max_values=1, options=options)
        
        
        
    async def callback(self, interaction: discord.Interaction):
        
        
        # Handle the interaction based on what the user selects
        
        # await interaction.response.defer()

        if self.values[0] == "bot_config":
            await interaction.response.send_modal(BotConfigModal(self.view.merx, str(uuid.uuid4()), interaction.guild.id))
            await interaction.message.edit() # DONT REMOVE IT RESETS THE DROPDOWN
            
            
        elif self.values[0] == "plugin_config":
            available_plugins = ["Welcome Messages", "Automod"]

            # Show the PluginConfigView for plugin selection
            view = PluginConfigView(self.merx, available_plugins)
            
            setup_embed = InfoEmbed(
                title="Plugin Configuration",
                description="Select the plugins you want to enable from the dropdown menu.",
                color=embed_color
            )

            await interaction.response.send_message(embed=setup_embed, view=view)
            await interaction.message.edit() # DONT REMOVE IT RESETS THE DROPDOWN
            
        # elif self.values[0] == "moderation_config":
        #     await interaction.response.send_modal(PluginConfigModal(self.view.merx, str(uuid.uuid4()), interaction.guild.id))
        #     await interaction.message.edit() # DONT REMOVE IT RESETS THE DROPDOWN
            
        # elif self.values[0] == "administration_config":
        #    await interaction.response.send_modal(PluginConfigModal(self.view.merx, str(uuid.uuid4()), interaction.guild.id))
        #    await interaction.message.edit() # DONT REMOVE IT RESETS THE DROPDOWN
        
        
        
class PluginDropdown(discord.ui.Select):
    
    def __init__(self, merx, available_plugins):
        
        self.merx = merx
        self.selected_plugins = []  # List to store selected plugins

        # Define the plugin options
        options = [discord.SelectOption(label=plugin, value=plugin) for plugin in available_plugins]

        super().__init__(placeholder="Select plugins to enable...", min_values=1, max_values=len(options), options=options)



    async def callback(self, interaction: discord.Interaction):
        # Add selected plugins to the list
        self.selected_plugins = self.values
        
        # Acknowledge the interaction and inform the user
        await interaction.response.send_message(
            f"<:whitecheck:1285350764595773451> Selected Plugins: {', '.join(self.selected_plugins)}. You can now save your configuration.",
            ephemeral=True
        )
            
            

class PluginConfigView(discord.ui.View):
    def __init__(self, merx, available_plugins):
        super().__init__(timeout=None)
        self.plugin_dropdown = PluginDropdown(merx, available_plugins)
        self.add_item(self.plugin_dropdown)
        self.add_item(SavePluginsButton(self.plugin_dropdown))



class SavePluginsButton(discord.ui.Button):
    def __init__(self, plugin_dropdown):
        super().__init__(label="Save Configuration", style=discord.ButtonStyle.primary)
        self.plugin_dropdown = plugin_dropdown

    async def callback(self, interaction: discord.Interaction):
        selected_plugins = self.plugin_dropdown.selected_plugins
        
        # Save the selected plugins to MongoDB
        if selected_plugins:
            guild_id = interaction.guild.id
            await setup_col.update_one(
                {"guild_id": guild_id},
                {"$set": {"plugins": ", ".join(selected_plugins)}},
                upsert=True
            )
            await interaction.response.send_message(f"<:whitecheck:1285350764595773451> Plugins saved: {', '.join(selected_plugins)}", ephemeral=True)
        else:
            await interaction.response.send_message("<:xmark:1285350796841582612> No plugins selected to save.", ephemeral=True)



class SetupCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
        self.setup_message_id = None
        self.constants = MerxConstants()
        
        
        
    # This is the actual setup command, it shows a disclaimer telling the user they need the right permissions and info
    # we do this so that if they arent the intended user they can back out and let the right user set the bot up. This
    # command now support reconfigurations as well.

    @commands.hybrid_command(description="Set up the bot configuration.", with_app_command=True, extras={"category": "Setup"})
    async def setup(self, ctx: commands.Context, reconfig: bool = False):
        await ctx.defer(ephemeral=False)


        # Checks to see if the reconfigure parameter is passed in the command for example /setup reconfigure if its not then
        # treat it like normal setup.

        if reconfig:
            disclaimer_embed = InfoEmbed(
                title="Merx Reconfiguration",
                description="This will guide you through reconfiguring Merx's settings. You may want to do this incase something is not working as intended or you want to change certain settings. \n\nClick '**Continue**' to start.",
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



    # This fetches the guild config we do this so that we can get the banner information as well as prefix
    # and guild info this allows the checking of existing data to prevent resetting shit up and creating
    # duplicate entries.

    async def fetch_guild_config(self, guild_id: int) -> dict:
        bot_config = await setup_col.find_one({"guild_id": guild_id, "prefix": {"$exists": True}})
        plugins_config = await setup_col.find_one({"guild_id": guild_id, "plugins": {"$exists": True}})
        return {
            "prefix": bot_config.get("prefix") if bot_config else None,
            "theme_color": bot_config.get("theme_color") if bot_config else None,
            "plugins": plugins_config.get("plugins") if plugins_config else None
        }


    # This is the start setup function which kick starts the setup process.

    async def start_setup(self, interaction: Interaction):
        
        
        guild_id = interaction.guild.id
        guild_config = await self.fetch_guild_config(guild_id)
        
        
        # Informs the user setup is already complete and checks to see if it truly is complete.
        # this is so that suers cant make several duplicate entries into Mongo as they are stored
        # uniquely with a different ID each time setup is run.

        if guild_config.get("prefix") and guild_config.get("plugins") and not interaction.data.get("reconfigure"):
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
            show_plugin_config=not guild_config.get("plugins"),
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
    
    
