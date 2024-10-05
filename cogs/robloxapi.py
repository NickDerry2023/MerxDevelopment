import discord
import logging
import random
import aiohttp
from discord.ext import commands, tasks
from discord.ui import View, Button
from utils.constants import MerxConstants, verify_waiting
# from cogs.utils.embeds


constants = MerxConstants()
ROBLOX_API_URL = "https://users.roblox.com/v1/users/search?keyword="


class VerifyButtons(discord.ui.View):
    def __init__(self, merx):
        super().__init__(timeout=None)
        self.merx = merx
        self.emoji_list = [
            "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😉", "😊",
            "😋", "😎", "😍", "😘", "😗", "😙", "😚", "🙂", "🙃", "😉",
            "😇", "🥰", "😋", "😌", "😏", "😒", "😞", "😔", "😟", "😕",
            "😲", "😳", "😵", "😡", "😠", "😤", "😢", "😭", "😧", "😨",
            "😩", "😱", "😳", "😵‍💫", "😶", "😶‍🌫️", "😴", "😪", "😵", "🤯",
            "🥳", "🥸", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿",
            "😾", "👻", "💀", "👽", "🤖", "🎃", "🌈", "✨", "💫", "🌟",
            "🔥", "💧", "🌊", "🍀", "🌹", "🌻", "🌼", "🍁", "🍂", "🍃"
        ]

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.primary, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        verification_code = self.get_verification_code()
        modal = VerifyModal(merx=self.merx, code=verification_code)
        await interaction.response.send_modal(modal)

    

    def get_verification_code(self):
        code = ""
        for emoji in random.sample(self.emoji_list, 10):
            code = code+emoji
        return code
    
class VerifyModal(discord.ui.Modal, title="Verification"):
    roblox_username = discord.ui.TextInput(label="Enter your Roblox Username", required=True)

    def __init__(self, merx, code):
        super().__init__()
        self.merx = merx
        self.verification_code = code
        self.custom_id="verify_modal"

    async def on_submit(self, interaction: discord.Interaction):
        username = self.roblox_username.value
        user = interaction.user

        async with aiohttp.ClientSession() as session: 
            # try:
            search_url = f"{ROBLOX_API_URL}{username}"
            async with session.get(search_url) as search_response:
                if not search_response.status == 200:
                    logging.error(f"Failed to search user. Status Code: {search_response.status}")
                    await interaction.response.send_message(f"Error fetching that user. Status code `{search_response.status}`", ephemeral=True)
                    return
                search_data = await search_response.json()
                if not search_data['data']:
                    logging.error(f"User: {username} not found.")
                    await interaction.response.send_message(f"Please enter a valid username.", ephemeral=True)
                    return
                global user_id
                user_id = search_data['data'][0]['id']
            # except Exception as e:
            #     logging.error(f"Error fetching user {username}: {e}")
            #     await interaction.response.send_message("Error fetching user.", ephemeral=True)
            #     return
            
            data = {
                "roblox_username": username,
                "roblox_id": user_id,
                "discord_user_id": user.id,
                "code": self.verification_code
            }

            verify_waiting.insert_one(data)

            await interaction.response.send_message(f"Your verification code is: `{self.verification_code}`. \n Please add this to your roblox bio.",  ephemeral=True)
                    

    
class Verification(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
    
    @commands.hybrid_command(description='Verify your roblox account.', with_app_command=True, extras={"category": "Other"})
    async def verify(self, ctx: commands.Context):
        view = VerifyButtons(merx=self.merx)

        await ctx.send("Please select your verification method.", view=view, ephemeral=True)
    
    @tasks.loop(seconds=30)
    async def check_for_waiting(self):
        async def check_roblox_bio(userid, code):
            async with aiohttp.ClientSession() as session:
                try:
                    bio_url = f'https://users.roblox.com/v1/users/{userid}'
                    async with session.get(bio_url) as bio_response:
                        if not bio_response.status == 200:
                            logging.error(f"Error fetching {userid}. Status Code: {bio_response.status}")
                        bio_data = await bio_response.json()
                        roblox_bio = bio_data.get("description", "")
                        if code in roblox_bio:
                            return True
                        else:
                            return False
                except Exception as e:
                    logging.error(f"Error fetching data for {userid}: {e}")
                    return False

        async for user in verify_waiting.find({}):
            if await check_roblox_bio(user.result.get('id'), user.result.get('code')):
                self.merx



async def setup(merx):
    await merx.add_cog(Verification(merx))
    merx.add_view(VerifyButtons(merx))