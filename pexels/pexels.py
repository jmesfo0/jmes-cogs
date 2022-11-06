import logging

import discord
from pypexels import PyPexels
from redbot.core import Config, checks, commands
from redbot.core.utils.menus import DEFAULT_CONTROLS, commands, menu

log = logging.getLogger("red.jmes-cogs.Pexels")


class Pexels(commands.Cog):

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2331337137)

    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.group(name="pexels", aliases=["px", "pex"])
    async def _pexels(self, ctx: commands.Context) -> None:
        """Free stock photos & videos you can use everywhere. Browse millions of high-quality royalty free stock images & copyright free pictures."""
        pass

    @_pexels.command(name="search")
    async def _search(self, ctx: commands.Context, *, query) -> None:
        """Search for photos from Pexels."""
        embeds = []
        keys = await self.bot.get_shared_api_tokens("pexels")
        apikey = keys.get("api_key")
        try:
            py_pexel = PyPexels(api_key=apikey)
            search_results = py_pexel.search(query=query, per_page=40)
        except Exception:
            await ctx.send(self.NO_KEY_MSG)
            return
        try:
            for photo in search_results.entries:
                embed = discord.Embed()
                embed.title = "{} ({})".format(photo.photographer, photo.id)
                if photo.url:
                    embed.set_image(url=photo.src.get("large"))
                embed.set_footer(text="Powered by pexels.com")
                embeds.append(embed)
            await menu(
                ctx,
                pages=embeds,
                controls=DEFAULT_CONTROLS,
                message=None,
                page=0,
                timeout=20,
            )
        except Exception:
            await ctx.send("I couldn't find anything!")
            pass

    @_pexels.command(name="random")
    async def _random(self, ctx: commands.Context) -> None:
        """Display a random photo from Pexels."""
        embeds = []
        keys = await self.bot.get_shared_api_tokens("pexels")
        apikey = keys.get("api_key")
        try:
            py_pexel = PyPexels(api_key=apikey)
            random_photos_page = py_pexel.random(per_page=1)
        except Exception:
            await ctx.send(self.NO_KEY_MSG)
            return
        try:
            for photo in random_photos_page.entries:
                embed = discord.Embed()
                embed.title = "{} ({})".format(photo.photographer, photo.id)
                if photo.url:
                    embed.set_image(url=photo.src.get("large"))
                embed.set_footer(text="Powered by pexels.com")
                embeds.append(embed)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("I couldn't find anything!")
            pass

    @_pexels.command(name="popular")
    async def _popular(self, ctx: commands.Context) -> None:
        """Display popular photos from Pexels."""
        embeds = []
        keys = await self.bot.get_shared_api_tokens("pexels")
        apikey = keys.get("api_key")
        try:
            py_pexel = PyPexels(api_key=apikey)
            popular_results = py_pexel.popular(per_page=40)
        except Exception:
            await ctx.send(self.NO_KEY_MSG)
            return
        try:
            for photo in popular_results.entries:
                embed = discord.Embed()
                embed.title = "{} ({})".format(photo.photographer, photo.id)
                if photo.url:
                    embed.set_image(url=photo.src.get("large"))
                embed.set_footer(text="Powered by pexels.com")
                embeds.append(embed)
            await menu(
                ctx,
                pages=embeds,
                controls=DEFAULT_CONTROLS,
                message=None,
                page=0,
                timeout=20,
            )
        except Exception:
            await ctx.send("I couldn't find anything!")
            pass

    @_pexels.command(name="curated")
    async def _curated(self, ctx: commands.Context) -> None:
        """Display curated photos from Pexels."""
        embeds = []
        keys = await self.bot.get_shared_api_tokens("pexels")
        apikey = keys.get("api_key")
        try:
            py_pexel = PyPexels(api_key=apikey)
            curated_results = py_pexel.curated(per_page=40)
        except Exception:
            await ctx.send(self.NO_KEY_MSG)
            return
        try:
            for photo in curated_results.entries:
                embed = discord.Embed()
                embed.title = "{} ({})".format(photo.photographer, photo.id)
                if photo.url:
                    embed.set_image(url=photo.src.get("large"))
                embed.set_footer(text="Powered by pexels.com")
                embeds.append(embed)
            await menu(
                ctx,
                pages=embeds,
                controls=DEFAULT_CONTROLS,
                message=None,
                page=0,
                timeout=60,
            )
        except Exception:
            await ctx.send("I couldn't find anything!")
            pass

    @_pexels.command()
    async def version(self, ctx: commands.Context):
        """Display the version."""
        await ctx.send(("Pexels version: {}").format(self.__version__))

    @commands.command()
    @checks.is_owner()
    async def pexelskey(self, ctx):
        await ctx.send(self.NO_KEY_MSG)

    NO_KEY_MSG = (
        "**Pexels API**\n"
        "1. Get a key here:\n"
        "   https://www.pexels.com/join\n"
        "2. Set the key:\n"
        "   [p]set api pexels api_key,your-key-here"
    )
