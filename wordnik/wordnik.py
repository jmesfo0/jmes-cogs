import discord
import logging
import aiohttp
import asyncio

from redbot.core import commands, Config, checks
from redbot.core.bot import Red
from redbot.core.config import Config

log = logging.getLogger("red.jmes-cogs.Wordnik")

class Wordnik(commands.Cog):
    """
    Wordnik is the world's biggest online English dictionary, by number of words.
    """
    __version__ = "1.0.0"
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=2331337142,
            force_registration=True,
        )
    @commands.group(name="wordnik", aliases=["wn", "wrdnk"])
    async def _wordnik(self, ctx: commands.Context) -> None:
        """Wordnik commands."""
        pass

    @_wordnik.command(name="random")        
    async def _random(self, ctx):
        """Random word"""
        keys = await self.bot.get_shared_api_tokens("wordnik")
        apikey = keys.get("api_key")

        try:
        
            async with aiohttp.ClientSession() as session:
                wordnik_url = f'http://api.wordnik.com/v4/words.json/randomWord?api_key={apikey}'
                async with session.get(wordnik_url) as resp:
                    wotd = await resp.json()
                    word = wotd['word']
                     
            await ctx.send("Here's a random word:\n**" + word + "**")
        except Exception:
            await ctx.send(self.NO_KEY_MSG)
            return
        
    @_wordnik.command(name="wotd", aliases=["wordoftheday"])        
    async def _wotd(self, ctx):
        """Word of the day"""
        keys = await self.bot.get_shared_api_tokens("wordnik")
        apikey = keys.get("api_key")

        try:
        
            async with aiohttp.ClientSession() as session:
                wordnik_url = f'http://api.wordnik.com/v4/words.json/wordOfTheDay?api_key={apikey}'
                async with session.get(wordnik_url) as resp:
                    wotd = await resp.json()
                    word = wotd['word']
                    definition = wotd['definitions'][0]['text']
                     
            await ctx.send("\n**" + word + "** \n*" + definition + "*")
        except Exception:
            await ctx.send(self.NO_KEY_MSG)
            return
            
    @_wordnik.command()
    async def version(self, ctx: commands.Context):
        """Display the version."""
        await ctx.send(("Wordnik version: {}").format(self.__version__))
        
    @commands.command(hidden=True)
    @checks.is_owner()
    async def wordnikkey(self, ctx):
        await ctx.send(self.NO_KEY_MSG)

    NO_KEY_MSG = ("**Wordnik API**\n"
                "1. Get a key here:\n"
                "   https://developer.wordnik.com/\n"
                "2. Set the key:\n"
                "   [p]set api wordnik api_key,your-key-here")
