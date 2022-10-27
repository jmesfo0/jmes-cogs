import os
import string
import logging
import random
import discord
from typing import Optional
import subprocess
import shutil
import aiohttp
import re
import time

from redbot.core import Config, commands, data_manager, checks
from redbot.core.data_manager import bundled_data_path, cog_data_path
from redbot.core.utils.chat_formatting import bold

log = logging.getLogger("red.jmes-cogs.Obfuscator")

file_path = os.path.abspath(os.path.dirname(__file__))

class Obfuscator(commands.Cog):
    """
    Lua Obfuscators ported to Red-DiscordBot by jmes
    """
    __version__ = "1.0.4" 

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2331337138)
        default_global = {
            "watermark": "",        
        }
        default_user = {
            "is_whitelisted": False,            
        }
        default_guild = {
            "obfuscator_channel": "",            
        }           
        self.config.register_global(**default_global)
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        uploads_folder = file_path + "/uploads"
        obfuscated_folder = file_path + "/obfuscated"  
        if not os.path.exists(uploads_folder):
            os.mkdir(uploads_folder)
        if not os.path.exists(obfuscated_folder):
            os.mkdir(obfuscated_folder)
            
    @commands.group(invoke_without_command=True)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)    
    async def obfuscate(self, ctx: commands.Context, type: Optional[commands.Context] = None) -> None:
        """
        Roblox/FiveM Lua Obfuscator
        
        Run the command with a file attachment or code block.
        Type is optional.
        
        """  
        type_to_string = str(type)
        x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
        
        if x or type is None:     
            return await self._jmes(ctx)
        return

    @obfuscate.command(name="luaseel")
    async def _luaseel(self, ctx: commands.Context):
        """LuaSeel obfuscation."""
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            return await self.luaseel(ctx)
        else:
            if ctx.guild is None:
                return
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                return await self.luaseel(ctx)   

    @obfuscate.command(name="menprotect")
    async def _menprotect(self, ctx: commands.Context) -> None:
        """Menprotect obfuscation."""
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            return await self.menprotect(ctx)
        else:
            if ctx.guild is None:
                return
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                return await self.menprotect(ctx)
                
    @obfuscate.command(name="prometheus")
    async def _prometheus(self, ctx: commands.Context):
        """Prometheus obfuscation."""
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            return await self.prometheus(ctx)
        else:
            if ctx.guild is None:
                return
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                return await self.prometheus(ctx)
                
    @obfuscate.command(name="ironbrew")
    async def _ironbrew(self, ctx: commands.Context):
        """IronBrew2 obfuscation."""
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            return await self.ironbrew(ctx)
        else:
            if ctx.guild is None:
                return        
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                return await self.ironbrew(ctx)
                
    @obfuscate.command(name="bytecode")
    async def _bytecode(self, ctx: commands.Context):
        """Bytecode obfuscation."""
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            return await self.bytecode(ctx)
        else:
            if ctx.guild is None:
                return
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                return await self.bytecode(ctx)  
                
    @obfuscate.command(name="jmes")
    async def _jmes(self, ctx: commands.Context) -> None:
        """jmes obfuscation."""
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            return await self.static_jmes(ctx)
        else:
            if ctx.guild is None:
                return
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                return await self.static_jmes(ctx)
                
    @obfuscate.command(name="psu")
    async def _psu(self, ctx: commands.Context, mode: Optional[str] = None) -> None:
        """
        PSU obfuscation. 
        
        Optional mode
        *Default,Chinese,Numbers,Arabic,Symbols1,Symbols2,Symbols3,HexLower,HexUpper,Korean,Emoji,Greek*
        
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            return await self.static_psu(ctx, mode)
        else:
            if ctx.guild is None:
                return
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                return await self.static_psu(ctx, mode)      
                
    @commands.group()
    async def obfuscatorset(self, ctx: commands.Context) -> None:
        """Various settings."""
        pass
    
    @checks.is_owner()
    @commands.guild_only()
    @obfuscatorset.command()
    async def channel(self, ctx: commands.context, channel: Optional[discord.TextChannel] = None) -> None:
        """Set the channel for obfuscator."""
        if channel is None:
            channel = ctx.channel
        await self.config.guild(ctx.guild).obfuscator_channel.set(channel.id)
        await ctx.send(("Obfuscator channel set to {}").format(channel.mention))
        
    @checks.is_owner()    
    @commands.guild_only()
    @obfuscatorset.command(name="user")
    async def _user(self, ctx: commands.Context, *, user: discord.Member):
        """add/remove user from direct message obfuscation."""
        if await self.config.user(user).is_whitelisted():
            await self.config.user(user).is_whitelisted.set(False)
            await ctx.send(("{} removed from direct message obfuscation.").format(user))
        else:
            await self.config.user(user).is_whitelisted.set(True)
            await ctx.send(("Direct message obfuscation enabled for {}.").format(user))

    @checks.is_owner()
    @commands.guild_only()
    @obfuscatorset.command()
    async def watermark(self, ctx: commands.context, *, value: str):
        """Set the watermark for obfuscator."""
        await self.config.watermark.set(value)
        await ctx.send(("Obfuscator watermark set to: {}").format(value))
            
    @obfuscatorset.command()
    async def version(self, ctx: commands.Context):
        """Display the version."""
        await ctx.send(("Obfuscator version: {}").format(self.__version__))

    async def luaseel(self, ctx):            
        letters = string.ascii_uppercase
        filename = ''.join(random.choice(letters) for i in range(7))
        x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
        obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
        upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
        watermark = await self.config.watermark()
        start_time = time.time()
        
        if x:
            path = upload
            if os.path.exists(path):
                os.remove(path)
            with open(path, "w") as file:
                file.write(x[0])
            self.obfuscation_luaseel(path, filename)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))         
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)             
        elif ctx.message.attachments:
            if not ctx.message.attachments[0].url.endswith(('.lua', '.txt')):
                embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                return await ctx.send(embed=embed)     
            url = ctx.message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    response = await resp.text(encoding="utf8")      
            path = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            if os.path.exists(path):
                os.remove(path)
            open(path, "w").write(response)
            self.obfuscation_luaseel(path, filename)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))  
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)
        else:
            embed = discord.Embed(title="no file or code block", color=0xED4245)
            await ctx.send(embed=embed)

    async def menprotect(self, ctx): 
        letters = string.ascii_uppercase
        filename = ''.join(random.choice(letters) for i in range(7))
        x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
        output_file = "{}/{}/{}".format(file_path, "obfuscated", "output.lua")
        obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
        upload = "{}/{}/{}".format(file_path, "uploads", "input.lua")
        watermark = await self.config.watermark()
        node_folder = "{}/{}".format(file_path, "node_modules")        
        start_time = time.time()
        
        if x:
            if os.path.exists(upload):
                os.remove(upload)
            with open(upload, "w", encoding="utf8") as file:
                file.write(x[0])
            if not os.path.exists(node_folder):
                subprocess.check_output(f"cd {file_path} && npm install",shell=True,stderr=subprocess.STDOUT)
                subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
            subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
            with open(output_file, 'r') as file:
                filedata = file.read()
            with open(obfuscated, 'w') as file:
                file.write(filedata)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))   
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)
            os.remove(output_file)
        elif ctx.message.attachments:
            if not ctx.message.attachments[0].url.endswith(('.lua', '.txt')):
                embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                return await ctx.send(embed=embed)
            url = ctx.message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    response = await resp.text(encoding="utf8")          
            if os.path.exists(upload):
                os.remove(upload)
            open(upload, "w", encoding="utf8").write(response)
            if not os.path.exists(node_folder):
                subprocess.check_output(f"cd {file_path} && npm install",shell=True,stderr=subprocess.STDOUT)
                subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
            subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
            with open(f"{file_path}//obfuscated//output.lua", 'r') as file:
                filedata = file.read()
            with open(obfuscated, 'w') as file:
                file.write(filedata)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))    
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)
            os.remove(output_file)                
        else:
            embed = discord.Embed(title="no file or code block", color=0xED4245)
            await ctx.send(embed=embed)   

    async def prometheus(self, ctx): 
        letters = string.ascii_uppercase
        filename = ''.join(random.choice(letters) for i in range(7))
        x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
        obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
        upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
        path = "{}/{}".format("./uploads", filename + ".lua")
        watermark = await self.config.watermark()
        start_time = time.time()
        
        if x:
            if os.path.exists(upload):
                os.remove(upload)
            with open(upload, "w") as file:
                file.write(x[0])
            subprocess.check_output(f'cd {file_path} && lua prometheus_cli.lua --preset Medium {path}',shell=True,stderr=subprocess.STDOUT)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))  
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)
        elif ctx.message.attachments:
            if not ctx.message.attachments[0].url.endswith(('.lua', '.txt')):
                embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                return await ctx.send(embed=embed)
            url = ctx.message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    response = await resp.text(encoding="utf8")      
            if os.path.exists(upload):
                os.remove(upload)
            open(upload, "w", encoding="utf8").write(response)
            subprocess.check_output(f'cd {file_path} && lua prometheus_cli.lua --preset Medium {path}',shell=True,stderr=subprocess.STDOUT)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))  
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)              
        else:
            embed = discord.Embed(title="no file or code block", color=0xED4245)
            await ctx.send(embed=embed)
            
    async def ironbrew(self, ctx): 
        letters = string.ascii_uppercase
        filename = ''.join(random.choice(letters) for i in range(7))
        x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
        output_file = "{}/{}/{}".format(file_path, "obfuscated", "output.lua")
        obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
        upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
        watermark = await self.config.watermark()
        path = "{}/{}".format("./uploads", filename + ".lua")
        start_time = time.time()
        
        if x:
            if os.path.exists(upload):
                os.remove(upload)
            with open(upload, "w") as file:
                file.write(x[0])
            subprocess.check_output(f"cd {file_path} && dotnet IronBrew2CLI.dll {path}",shell=True,stderr=subprocess.STDOUT)
            with open(output_file, 'r') as file:
                filedata = file.read()
            with open(obfuscated, 'w') as file:
                file.write(filedata)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))  
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)
            os.remove(output_file)
            
        elif ctx.message.attachments:
            if not ctx.message.attachments[0].url.endswith(('.lua', '.txt')):
                embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                return await ctx.send(embed=embed)
            url = ctx.message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    response = await resp.text(encoding="utf8")      
            if os.path.exists(upload):
                os.remove(upload)
            open(upload, "w", encoding="utf8").write(response)
            subprocess.check_output(f"cd {file_path} && dotnet IronBrew2CLI.dll {path}",shell=True,stderr=subprocess.STDOUT)
            with open(output_file, 'r') as file:
                filedata = file.read()
            with open(obfuscated, 'w') as file:
                file.write(filedata)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))  
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)
            os.remove(output_file)
            
        else:
            embed = discord.Embed(title="no file or code block", color=0xED4245)
            await ctx.send(embed=embed)
            
    async def bytecode(self, ctx):             
        letters = string.ascii_uppercase
        filename = ''.join(random.choice(letters) for i in range(7))
        x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
        obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
        upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
        watermark = await self.config.watermark()
        path = "./uploads/" + filename + ".lua"
        start_time = time.time()        
        if x:
            if os.path.exists(upload):
                os.remove(upload)
            with open(upload, "w") as file:
                file.write(x[0])
            subprocess.check_output(f'cd {file_path} && lua bytecode_cli.lua --cli --source {path} --output {obfuscated} --comment {ctx.message.author.display_name} --varcomment {ctx.message.author.display_name} --cryptvarcomm True --varname {ctx.message.author.display_name}',shell=True,stderr=subprocess.STDOUT)
            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))  
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)
        elif ctx.message.attachments:
            if not ctx.message.attachments[0].url.endswith(('.lua', '.txt')):
                embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                return await ctx.send(embed=embed)
            url = ctx.message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    response = await resp.text(encoding="utf8")      
            if os.path.exists(upload):
                os.remove(upload)
            open(upload, "w", encoding="utf8").write(response)
            subprocess.check_output(f'cd {file_path} && lua bytecode_cli.lua --cli --source {path} --output {obfuscated} --comment {ctx.message.author.display_name} --varcomment {ctx.message.author.display_name} --cryptvarcomm True --varname {ctx.message.author.display_name}',shell=True,stderr=subprocess.STDOUT)

            with open(obfuscated, 'r+') as fp:
                lines = fp.readlines()
                if watermark:
                    lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(self.bot.user.name,watermark))
                else:
                    lines.insert(0, ("--// Obfuscated by {}\n\n").format(self.bot.user.name))  
                fp.seek(0)
                fp.writelines(lines)
            end_time = time.time()
            time_elapsed = end_time - start_time
            embed = discord.Embed(title="File has been obfuscated", description=("\n⌛ ({}) seconds.").format(str(time_elapsed)[:5]), color=0x57F287)
            await ctx.send(embed=embed, file=discord.File(obfuscated))
            os.remove(upload)
            os.remove(obfuscated)              
        else:
            embed = discord.Embed(title="no file or code block", color=0xED4245)
            await ctx.send(embed=embed)  
            
    def obfuscation_luaseel(self, path, filename):    
        obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
        copy = "{}/{}/{}".format(file_path, "obfuscated", filename + ".lua")
        if os.path.exists(copy):
            os.remove(copy)
        shutil.copyfile(path, copy)
        text_file = open((file_path + "/luaseel_cli.lua"), "r")
        data = text_file.read()
        text_file.close()
        f = open(copy, "a")
        f.truncate(0)
        f.write(data)
        f.close()
        originalupload = open(path, "r")
        originalupload_data = originalupload.read()
        originalupload.close()
        with open(copy, "r") as in_file:
            buf = in_file.readlines()
        with open(copy, "w") as out_file:
            for line in buf:
                if line == "--SCRIPT\n":
                    line = line + originalupload_data + '\n'
                out_file.write(line)
        output = subprocess.getoutput(f'lua {copy}')
        if os.path.exists(obfuscated):
            os.remove(obfuscated)
        f = open(obfuscated, "a")
        f.write(output)
        f.close()
        os.remove(copy) 
