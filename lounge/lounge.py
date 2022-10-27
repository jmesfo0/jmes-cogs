import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config

class Lounge(commands.Cog):
    """
    The Lounge
    
    A custom cog for THE_LOUNGE discord server.
    
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=534233345,
            force_registration=True,
        )
    
    @commands.command(name="nsfw")
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _nsfw(self, ctx: commands.Context):
        """..."""
        embed = discord.Embed(
            description=f"Check your inbox you cheeky sausage.\n"+ 
                        "No NSFW here!\n"+
                        "<:pepeYikes:926749952959455293>", 
            color=0xED4245
        )
        await ctx.send(embed=embed)
        await ctx.author.send(
            "We are a 21+ General Server!\n"+
            "**NO NSFW**\n\n"+
            "Accept <#944203218907439154> to join!\n\n"+
            "But, if you're looking for The NSFW Lounge...\n"+
            "Let us show you the way.\n"+
            "www.discord.gg/the-lounge\n\n"+
            "Come back if you're bored & want to chat!\n"+
            "You're Welcome!\n"+
            "<:pepevibepepe:926749433608159312>"
        )
