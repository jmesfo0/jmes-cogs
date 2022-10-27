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

from redbot.core import Config, commands, data_manager, checks, bank
from redbot.core.data_manager import bundled_data_path, cog_data_path
from redbot.core.utils.chat_formatting import bold

log = logging.getLogger("red.jmes-cogs.Obfuscator")

file_path = os.path.abspath(os.path.dirname(__file__))

class Obfuscator(commands.Cog):
    """
    Lua Obfuscators ported to Red-DiscordBot by jmes
    """
    __version__ = "1.0.5"
    __author__ = "jmes"

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
            "cost": 0,
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
        if type is None:
            return await self._luaseel(ctx)      
        return

    @obfuscate.command(name="luaseel")
    async def _luaseel(self, ctx: commands.Context):
        """LuaSeel obfuscation."""

        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                os.remove(upload)
                os.remove(obfuscated)
            else:
                embed = discord.Embed(title="No file or code block", color=0xED4245)
                ctx.command.reset_cooldown(ctx)
                await ctx.send(embed=embed)
        else:
            if ctx.guild is None:
                return
            cost = await self.config.guild(ctx.guild).cost()
            balance = await bank.get_balance(ctx.author)
            currency = await bank.get_currency_name(ctx.guild)        
            new_balance = balance - cost
            
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
                
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator costs {} {}.").format(currency,balance,cost,currency))
                return     
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():
                 
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    os.remove(upload)
                    os.remove(obfuscated)
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)

    @obfuscate.command(name="menprotect")
    async def _menprotect(self, ctx: commands.Context) -> None:
        """Menprotect obfuscation."""

        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                os.remove(upload)
                os.remove(obfuscated)
                os.remove(output_file)                
            else:
                embed = discord.Embed(title="No file or code block", color=0xED4245)
                ctx.command.reset_cooldown(ctx)
                await ctx.send(embed=embed)   

        else:
            if ctx.guild is None:
                return
            cost = await self.config.guild(ctx.guild).cost()
            balance = await bank.get_balance(ctx.author)
            currency = await bank.get_currency_name(ctx.guild)
            new_balance = balance - cost
            
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator costs {} {}.").format(currency,balance,cost,currency))
                return    
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():
                 
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    os.remove(upload)
                    os.remove(obfuscated)
                    os.remove(output_file)                
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)   

                
    @obfuscate.command(name="prometheus")
    async def _prometheus(self, ctx: commands.Context):
        """Prometheus obfuscation."""
        
        
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                os.remove(upload)
                os.remove(obfuscated)              
            else:
                embed = discord.Embed(title="No file or code block", color=0xED4245)
                ctx.command.reset_cooldown(ctx)
                await ctx.send(embed=embed)

        else:
            if ctx.guild is None:
                return
            cost = await self.config.guild(ctx.guild).cost()
            balance = await bank.get_balance(ctx.author)
            currency = await bank.get_currency_name(ctx.guild)
            new_balance = balance - cost
            
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
                
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator costs {} {}.").format(currency,balance,cost,currency))
                return        
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():
                 
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    os.remove(upload)
                    os.remove(obfuscated)              
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)

                
    @obfuscate.command(name="ironbrew")
    async def _ironbrew(self, ctx: commands.Context):
        """IronBrew2 obfuscation."""
        
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                os.remove(upload)
                os.remove(obfuscated)
                os.remove(output_file)
                
            else:
                embed = discord.Embed(title="No file or code block", color=0xED4245)
                ctx.command.reset_cooldown(ctx)
                await ctx.send(embed=embed)

        else:
            if ctx.guild is None:
                return   
            cost = await self.config.guild(ctx.guild).cost()
            balance = await bank.get_balance(ctx.author)
            currency = await bank.get_currency_name(ctx.guild)
            new_balance = balance - cost
            
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
                
            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():    
                
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance) 
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance) 
                    os.remove(upload)
                    os.remove(obfuscated)
                    os.remove(output_file)
                    
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)

                
    @obfuscate.command(name="bytecode")
    async def _bytecode(self, ctx: commands.Context):
        """
        Bytecode obfuscation.
        """     
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
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
                embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                os.remove(upload)
                os.remove(obfuscated)              
            else:
                embed = discord.Embed(title="No file or code block", color=0xED4245)
                ctx.command.reset_cooldown(ctx)
                await ctx.send(embed=embed)  

        else:
            if ctx.guild is None:
                return
            cost = await self.config.guild(ctx.guild).cost()
            balance = await bank.get_balance(ctx.author)
            currency = await bank.get_currency_name(ctx.guild)
            new_balance = balance - cost
            
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance

            if not ctx.message.author.bot and ctx.message.channel.id == await self.config.guild(ctx.guild).obfuscator_channel():
                
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.message.channel.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
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
                    embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\nYour new balance is {} {}.").format(str(time_elapsed)[:5],new_balance,currency), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    os.remove(upload)
                    os.remove(obfuscated)              
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)
             
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
        await ctx.send(("Obfuscator channel: {}").format(channel.mention))
        
    @checks.is_owner()
    @commands.guild_only()
    @obfuscatorset.command()
    async def cost(self, ctx: commands.context, *, amount: Optional[int] = 0) -> 0:
        """Set the cost of obfuscator."""
        currency = await bank.get_currency_name(ctx.guild)
        await self.config.guild(ctx.guild).cost.set(amount)
        await ctx.send(("Obfuscator cost: {} {}.").format(amount,currency))
        
    @checks.is_owner()    
    @commands.guild_only()
    @obfuscatorset.command(name="user")
    async def _user(self, ctx: commands.Context, *, user: discord.Member):
        """add/remove user from direct message obfuscation."""
        if await self.config.user(user).is_whitelisted():
            await self.config.user(user).is_whitelisted.set(False)
            await ctx.send(("Obfuscator whitelist/DMs disabled for: {}.").format(user))
        else:
            await self.config.user(user).is_whitelisted.set(True)
            await ctx.send(("Obfuscator whitelist/DMs enabled for: {}.").format(user))

    @checks.is_owner()
    @commands.guild_only()
    @obfuscatorset.command()
    async def watermark(self, ctx: commands.context, *, value: str):
        """Set the watermark for obfuscator."""
        await self.config.watermark.set(value)
        await ctx.send(("Obfuscator watermark: {}").format(value))
            
    @obfuscate.command(name="version", aliases=["about"])
    async def version(self, ctx: commands.Context):
        """Display version information."""
        embed = discord.Embed(title="Version/About", description=("\nObfuscator version: {}\nCog author: [{}](https://discordapp.com/users/309536563161989120)").format(self.__version__,self.__author__), color=0x000088)
        embed.set_thumbnail(url="https://github.com/jmesfo0/jmes-cogs/raw/main/obfuscator/lua.png")
        await ctx.send(embed=embed)
        
    @obfuscate.command(name="help")
    async def help(self, ctx: commands.Context):
        """Display help information."""
        embed = discord.Embed(title="Obfuscator Commands", colour=0x000088)
        embed.set_thumbnail(url="https://github.com/jmesfo0/jmes-cogs/raw/main/obfuscator/lua.png")
        embed.add_field(name="obfuscate", value="the default obfuscator command", inline=False) 
        embed.add_field(name="obfuscate luaseel", value="LuaSeel Obfuscator (default)", inline=False)        
        embed.add_field(name="obfuscate menprotect", value="Menprotect Obfuscator", inline=False)        
        embed.add_field(name="obfuscate prometheus", value="Prometheus Obfuscator", inline=False)        
        embed.add_field(name="obfuscate ironbrew", value="IronBrew Obfuscator", inline=False)        
        embed.add_field(name="obfuscate bytecode", value="Bytecode Obfuscator", inline=False)
        embed.set_footer(text=("Obfuscator ({})").format(self.__version__), icon_url="https://github.com/jmesfo0/jmes-cogs/raw/main/obfuscator/lua.png")        
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
