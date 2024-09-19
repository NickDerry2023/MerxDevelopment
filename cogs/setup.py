import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput
from cogs.utils.constants import MerxConstants

constants = MerxConstants()


class RoleSelect(discord.ui.Select):
    def __init__(self, placeholder, options):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)



    async def callback(self, interaction: discord.Interaction):
        self.view.selected_role = self.values[0]
        await interaction.response.send_message(f"You selected: {self.values[0]}", ephemeral=True)



class SetupCommandCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx



    @commands.hybrid_command(description="Use this command to set the bot up to your liking.", with_app_command=True, extras={"category": "General"})
    async def setup(self, ctx):
        
        embed = discord.Embed(title="Setup Merx for your server", description="This setup wizard will walk you through setting up Merx Bot. Click the buttons below to set up each section of the bot. If you get suck feel free to contact support.")
        await ctx.send(embed=embed, view=self.setup_view())



    def setup_view(self):
        view = View()


        # Button to set roles
        
        roles_button = discord.ui.Button(label="Set Roles", style=discord.ButtonStyle.primary)
        roles_button.callback = self.set_roles
        view.add_item(roles_button)


        # Button to set embed color
        
        color_button = discord.ui.Button(label="Set Embed Color", style=discord.ButtonStyle.secondary)
        color_button.callback = self.set_embed_color
        view.add_item(color_button)


        # Button to set welcome message
        
        welcome_button = discord.ui.Button(label="Set Welcome Message", style=discord.ButtonStyle.secondary)
        welcome_button.callback = self.set_welcome_message
        view.add_item(welcome_button)

        return view



    async def set_roles(self, interaction: discord.Interaction):


        roles = [discord.SelectOption(label=role.name, value=str(role.id)) for role in interaction.guild.roles if role.name != "@everyone"]
        

        roles = roles[:25]  


        if not roles:
            await interaction.response.send_message("No roles available to select.", ephemeral=True)
            return
        
        
        select = RoleSelect(placeholder="Select a role...", options=roles)
        view = View()
        view.add_item(select)


        await interaction.response.send_message("Select the roles you want to configure:", view=view)



    async def set_embed_color(self, interaction: discord.Interaction):


        modal = Modal(title="Embed Color")
        embed_color_input = TextInput(label="Embed Color (Hex Code)", style=discord.TextStyle.short, placeholder="#RRGGBB")
        modal.add_item(embed_color_input)



        async def modal_callback(modal_interaction: discord.Interaction):
            embed_color = embed_color_input.value
            await modal_interaction.response.send_message(f"Embed color set to: {embed_color}", ephemeral=True)



        modal.callback = modal_callback
        await interaction.response.send_modal(modal)



    async def set_welcome_message(self, interaction: discord.Interaction):


        modal = Modal(title="Welcome Message")
        welcome_message_input = TextInput(label="Welcome Message", style=discord.TextStyle.long, placeholder="Enter your welcome message here...")
        modal.add_item(welcome_message_input)


        async def modal_callback(modal_interaction: discord.Interaction):
            welcome_message = welcome_message_input.value
            await modal_interaction.response.send_message(f"Welcome message set to: {welcome_message}", ephemeral=True)


        modal.callback = modal_callback
        await interaction.response.send_modal(modal)



async def setup(merx):
    await merx.add_cog(SetupCommandCog(merx))
