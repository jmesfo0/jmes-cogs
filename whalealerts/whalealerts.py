import discord
import logging
import time

from redbot.core import commands, Config, checks
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
from whalealert.whalealert import WhaleAlert

log = logging.getLogger("red.jmes-cogs.WhaleAlerts")

class WhaleAlerts(commands.Cog):

    __version__ = "1.0.0"
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2331337234)

    @commands.command(name="whalealerts")
    async def _whalealerts(self, ctx: commands.Context) -> None:
        """Shows latest whale transactions."""
        embeds = []
        keys = await self.bot.get_shared_api_tokens("whalealert")
        apikey = keys.get("api_key")
        try:
            whale = WhaleAlert()
            start_time = int(time.time() - 3597)
            transaction_count_limit = 100
            success, transactions, status = whale.get_transactions(start_time, api_key=apikey, limit=transaction_count_limit)
        except Exception:
            await ctx.send(self.NO_KEY_MSG)
            return
        try:
            for key in transactions:
                embed = discord.Embed()
                embed.set_thumbnail(url="https://raw.githubusercontent.com/jmesfo0/cryptocurrency-icons/master/icons/"+str(key["blockchain"])+".png")
                embed.add_field(name="Blockchain", value=str(key["blockchain"]), inline=True)
                embed.add_field(name="Type", value=str(key["transaction_type"]), inline=True)                
                if key["blockchain"] == "ethereum" and key["hash"] != "Multiple Hashes":
                    embed.add_field(name="Hash", value="["+str(key["hash"])+"](https://etherscan.io/tx/0x"+str(key["hash"])+")", inline=False)
                elif key["blockchain"] == "tron" and key["hash"] != "Multiple Hashes":
                    embed.add_field(name="Hash", value="["+str(key["hash"])+"](https://tronscan.org/#/transaction/"+str(key["hash"])+")", inline=False)
                elif key["blockchain"] == "bitcoin" and key["hash"] != "Multiple Hashes":
                    embed.add_field(name="Hash", value="["+str(key["hash"])+"](https://www.blockchain.com/btc/tx/"+str(key["hash"])+")", inline=False)
                elif key["blockchain"] == "ripple" and key["hash"] != "Multiple Hashes":
                    embed.add_field(name="Hash", value="["+str(key["hash"])+"](https://xrpscan.com/tx/"+str(key["hash"])+")", inline=False)                
                elif key["blockchain"] == "stellar" and key["hash"] != "Multiple Hashes":
                    embed.add_field(name="Hash", value="["+str(key["hash"])+"](https://stellarchain.io/transactions/"+str(key["hash"])+")", inline=False)
                else:
                    embed.add_field(name="Hash", value=str(key["hash"]), inline=False)
                embed.add_field(name="Symbol", value=str(key["symbol"]), inline=True)
                embed.add_field(name="Amount", value=str(key["amount"]), inline=True)
                embed.add_field(name="Amount USD", value="$"+str(key["amount_usd"]), inline=True)
                embeds.append(embed)
            await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=20)
        except Exception as e:
            await ctx.send(str(e))
            pass

    @commands.command()
    @checks.is_owner()
    async def whalekey(self, ctx):
        await ctx.send(self.NO_KEY_MSG)

    NO_KEY_MSG = ("**WhaleAlert API**\n"
                "1. Get a key here:\n"
                "   https://www.whale-alert.io\n"
                "2. Set the key:\n"
                "   [p]set api whalealert api_key,your-key-here")