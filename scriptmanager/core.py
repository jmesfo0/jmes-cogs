import aiohttp
import discord
import json
import logging
from redbot.core import Config, checks, commands
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
import requests
from typing import Optional, List, Tuple

log = logging.getLogger("red.jmes-cogs.scriptmanager")

class ScriptManager(commands.Cog):
    """
    Script Manager for organizing Roblox/FiveM scripts.
    """
    
    __version__ = "1.0.0"
    __author__ = "jmes"
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 34234245643, force_registration=True)
        default_global = {
            "scripts": {}
        }
        self.config.register_global(**default_global)
        
    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"
    
    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return
    
    @commands.command(name="script", aliases=["scripts"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def script(self, ctx: commands.Context):
        """
        Displays scripts in Script Manager database.
        
        """
        embeds = []
        async with self.config.scripts() as data:
        
            if data is None:
                return await ctx.send(f"There are no scripts in the database.\nYou can add one by typing `{ctx.clean_prefix}scriptset add`")
        
            for x in data:
                name = data[x]['name']
                description = data[x]['description']
                gameid = data[x]['gameid']
                thumbnail = data[x]["thumbnail"]
                loadstring = data[x]["loadstring"]
                api = requests.get(f"https://thumbnails.roblox.com/v1/places/gameicons?placeIds={gameid}&returnPolicy=PlaceHolder&size=256x256&format=Png&isCircular=false")
                imagedata = json.loads(api.text)
                embed = discord.Embed(title=f"{name}", description=f"{description}", colour=0x00ff00)
                embed.add_field(name="", value=f"```{loadstring}```", inline=False)
                if thumbnail:
                    embed.set_thumbnail(url=imagedata["data"][0]["imageUrl"])
                    embed.set_image(url=thumbnail)
                else:
                    embed.set_thumbnail(url=imagedata["data"][0]["imageUrl"])
                embeds.append(embed)
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=20)
        
    @checks.is_owner()    
    @commands.group(name="scriptset")
    async def scriptset(self, ctx: commands.Context) -> None:
        """
        Various Script Manager settings.
        """
        pass
    
    @checks.is_owner()    
    @scriptset.command(name="add", aliases=["new"])
    async def _add(self, ctx: commands.Context, name: str, description: str, gameid: int, loadstring: str, thumbnail: Optional[str] = None):
        """
        Add a script to the Script Manager
        """
        async with self.config.scripts() as data:
            if name in data:
                return await ctx.send(f"Script name {name} already listed.")
                
            data[name] = {
                "name": name,
                "gameid": gameid,
                "description": description,                   
                "thumbnail": thumbnail,
                "loadstring": loadstring,
              }
            await ctx.send(f"Script {name} successfully added to the database.")
            
    @checks.is_owner()    
    @scriptset.command(name="del", aliases=["delete", "remove"])
    async def _del(self, ctx: commands.Context, name: str):
        """
        Delete a script from the Script Manager
        """
        async with self.config.scripts() as data:
            if name in data:
                del data[name]
                return await ctx.send(f"Script name {name} was successfully deleted from the database.")
            else:
                return await ctx.send(f"Script name {name} was not found in the database.")
                
    @checks.is_owner()    
    @scriptset.group(name="edit")
    async def _edit(self, ctx: commands.Context) -> None:
        """
        Script Manager edit commands.
        """
        pass

    @checks.is_owner()    
    @_edit.command(name="description", aliases=["d"])
    async def _description(self, ctx: commands.Context, name: str, description: Optional[str]):
        """
        Edit a script description
        """
        await self.script_edit(ctx, name, description=description)
        
    @checks.is_owner()    
    @_edit.command(name="gameid", aliases=["g"])
    async def _gameid(self, ctx: commands.Context, name: str, gameid: Optional[int]):
        """
        Edit a script gameid
        """
        await self.script_edit(ctx, name, gameid=gameid)
        
    @checks.is_owner()    
    @_edit.command(name="loadstring", aliases=["l"])
    async def _loadstring(self, ctx: commands.Context, name: str, loadstring: Optional[str]):
        """
        Edit a script loadstring
        """
        await self.script_edit(ctx, name, loadstring=loadstring)
        
    @checks.is_owner()    
    @_edit.command(name="thumbnail", aliases=["t"])
    async def _thumbnail(self, ctx: commands.Context, name: str, thumbnail: Optional[str]):
        """
        Edit a script thumbnail
        """
        await self.script_edit(ctx, name, thumbnail=thumbnail)
                
                
    async def script_edit(self, ctx, name: str, description=None, gameid=None, loadstring=None, thumbnail=None) -> dict:
        """
        Runs multiple database queries to obtain the player's information
        """
        async with self.config.scripts() as data:
            if name in data:
                if description:
                    data[name] = {
                        "description": description,                   
                      }
                    await ctx.send(f"{name} description successfully updated.")                      
                if gameid:      
                    data[name] = {
                        "gameid": gameid,
                      }
                    await ctx.send(f"{name} gameid successfully updated.")
                if loadstring:      
                    data[name] = {                 
                        "loadstring": loadstring,
                      }
                    await ctx.send(f"{name} loadstring successfully updated.")
                if thumbnail:      
                    data[name] = {                 
                        "thumbnail": thumbnail,
                      }
                    await ctx.send(f"{name} thumbnail successfully updated.")
            else:
                await ctx.send(f"Script {name} not found in database.")
