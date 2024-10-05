from discord.ext import commands
from utils.embeds import SuccessEmbed, AfkEmbed
from utils.constants import MerxConstants, afks
 

constants = MerxConstants()


class AfkCommandCog(commands.Cog):
    def __init__(self, merx):
        self.merx = merx
        
        

    @commands.hybrid_command(name="afk", description="Set your AFK status with an optional reason.")
    async def afk(self, ctx, *, reason: str = "No reason provided."):
        await afks.update_one(
            {"user_id": ctx.author.id},
            {"$set": {"user_id": ctx.author.id, "reason": reason}},
            upsert=True
        )
        
        
        await ctx.send(embed=SuccessEmbed(
            title="AFK Status Set",
            description=f"<:whitecheck:1285350764595773451> You are now AFK. Reason: {reason}"
        ))
        
        

    @commands.Cog.listener()
    async def on_message(self, message):
        
        
        if message.author.bot:
            return

        if message.mentions:
            for user in message.mentions:
                afk_data = await afks.find_one({"user_id": user.id})
                
                
                if afk_data:
                    await message.channel.send(embed=AfkEmbed(user, afk_data["reason"]))

            
            

    @commands.hybrid_command(name="back", description="Set your status back to online.")
    async def back(self, ctx):

        afk_data = await afks.find_one({"user_id": ctx.author.id})
        

        if afk_data:
            
            await afks.delete_one({"user_id": ctx.author.id})
            
            
            await ctx.send(embed=SuccessEmbed(
                title="AFK Status Removed",
                description="<:whitecheck:1285350764595773451> You are now back online!"
            ))
            
            
        else:
            await ctx.send("You are not AFK.")



async def setup(merx):
    await merx.add_cog(AfkCommandCog(merx))
