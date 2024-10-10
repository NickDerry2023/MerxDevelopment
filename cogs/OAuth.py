import discord
import requests
from discord.ext import commands
from utils.constants import MerxConstants

constants = MerxConstants()

BOT_TOKEN = constants.merx_token_setup()
CLIENT_ID = constants.merx_client_id_setup()
CLIENT_SECRET = constants.merx_client_secret_setup()
REDIRECT_URI = constants.merx_redirect_uri_setup()

# Step 1: Generate OAuth2 URL
def get_oauth2_url():
    scopes = ['identify', 'guilds', 'roles']
    oauth_url = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={' '.join(scopes)}"
    return oauth_url

# Step 2: Exchange code for OAuth2 token
def exchange_code_for_token(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post("https://discord.com/api/oauth2/token", data=data)
    return response.json()

# Step 3: Fetch user's guilds
def get_user_guilds(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)
    return response.json()

# Step 4: Fetch user's roles in a specific guild
def get_user_roles(guild_id, user_id):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
    }
    response = requests.get(f"https://discord.com/api/guilds/{guild_id}/members/{user_id}", headers=headers)
    return response.json()


class OAuthCommandCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
        self.constants = MerxConstants()  # Access constants for MongoDB setup
        

    @commands.hybrid_command(descriptions="Run the command to sign in for linked roles.", with_app_command=True, extras={"category": "Administration"})
    async def sign_in(self, ctx):
        # Step 1: Provide OAuth2 URL for sign-in
        oauth_url = get_oauth2_url()
        await ctx.send(f"Please sign in using this URL: {oauth_url}")

    @commands.hybrid_command(descriptions="Run the command to assign linked roles.", with_app_command=True, extras={"category": "Administration"})
    async def assign_role(self, ctx, code: str, member: discord.Member):
        # Step 2: Exchange the code for an OAuth2 token
        token_data = exchange_code_for_token(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            await ctx.send("Failed to authenticate. Please try again.")
            return
        
        # Step 3: Fetch user roles from the guild
        guild_id = ctx.guild.id
        user_roles_data = get_user_roles(guild_id, member.id)
        user_roles = [role['id'] for role in user_roles_data['roles']]
        
        # Step 4: Check if user has the 'Merx Staff' role and assign linked roles
        merx_staff_role = discord.utils.get(ctx.guild.roles, name="Merx Staff")
        linked_role = discord.utils.get(ctx.guild.roles, name="Development Team")
        
        if str(merx_staff_role.id) in user_roles:
            await member.add_roles(linked_role)
            await ctx.send(f"{member.display_name} has been assigned the Development Team role!")
        else:
            await ctx.send(f"{member.display_name} does not have the Merx Staff role.")


async def setup(merx):
    await merx.add_cog(OAuthCommandCog(merx))
