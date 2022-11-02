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
import datetime
import math

from redbot.core import Config, commands, data_manager, checks, bank
from redbot.core.data_manager import bundled_data_path, cog_data_path
from redbot.core.utils.chat_formatting import humanize_list, humanize_number, pagify, box
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS


log = logging.getLogger("red.jmes-cogs.Obfuscator")

file_path = os.path.abspath(os.path.dirname(__file__))

class Obfuscator(commands.Cog):
    """
    Lua Obfuscator for Red-DiscordBot
    
    Various types of lua obfuscation to secure Roblox/FiveM scripts.
    """
    __version__ = "1.0.7"
    __author__ = "jmes"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2331337138)
        default_global = {
            "watermark": "",      
        }
        default_user = {
            "is_whitelisted": False,
            "ironbrew": 0,
            "menprotect": 0,
            "bytecode": 0,
            "luaseel": 0,
            "prometheus": 0,
            "minify": 0,
            "xor": 0,
            "total": 0,
        }
        default_guild = {
            "watermark": "", 
            "channels": [],
            "users": [],
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
        Lua Obfuscator
        
        Run the command with a Lua file attachment or code block.
        [p]obfuscate help for more options.
        """
        if type is None:
            return await self._luaseel(ctx)      
        return
      
    @obfuscate.command(name="luaseel")
    async def _luaseel(self, ctx: commands.Context):
        """
        LuaSeel obfuscation.
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            letters = string.ascii_uppercase
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            watermark = await self.config.watermark()
            start_time = time.time()
            count = await self.config.user(ctx.author).luaseel()
            total = await self.config.user(ctx.author).total()           
            if x:
                path = upload
                if os.path.exists(path):
                    os.remove(path)
                with open(path, "w") as file:
                    file.write(x[0])
                self.obfuscation_luaseel(path, filename)
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).luaseel.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)             
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
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
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).luaseel.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).luaseel()
            total = await self.config.user(ctx.author).total()            
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return     
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
                watermark = await self.config.guild(ctx.guild).watermark()
                start_time = time.time()
                if x:
                    path = upload
                    if os.path.exists(path):
                        os.remove(path)
                    with open(path, "w") as file:
                        file.write(x[0])
                    self.obfuscation_luaseel(path, filename)
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))         
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).luaseel.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)             
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
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
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))  
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).luaseel.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)

    @obfuscate.command(name="menprotect")
    async def _menprotect(self, ctx: commands.Context) -> None:
        """
        Menprotect obfuscation.
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            letters = string.ascii_uppercase
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            output_file = "{}/{}/{}".format(file_path, "obfuscated", "output.lua")
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", "input.lua")
            watermark = await self.config.watermark()
            node_folder = "{}/{}".format(file_path, "node_modules")        
            start_time = time.time()
            count = await self.config.user(ctx.author).menprotect()
            total = await self.config.user(ctx.author).total()            
            if x:
                if os.path.exists(upload):
                    os.remove(upload)
                with open(upload, "w", encoding="utf8") as file:
                    file.write(x[0])
                try:
                    if not os.path.exists(node_folder):
                        subprocess.check_output(f"cd {file_path} && npm install",shell=True,stderr=subprocess.STDOUT)
                        subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                    subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)                 
                with open(output_file, "r") as file:
                    filedata = file.read()
                with open(obfuscated, "w") as file:
                    file.write(filedata)
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).menprotect.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)
                os.remove(output_file)
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
                    embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                    return await ctx.send(embed=embed)
                url = ctx.message.attachments[0].url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        response = await resp.text(encoding="utf8")          
                if os.path.exists(upload):
                    os.remove(upload)
                open(upload, "w", encoding="utf8").write(response)
                try:
                    if not os.path.exists(node_folder):
                        subprocess.check_output(f"cd {file_path} && npm install",shell=True,stderr=subprocess.STDOUT)
                        subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                    subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed) 
                    
                with open(output_file, "r") as file:
                    filedata = file.read()
                with open(obfuscated, "w") as file:
                    file.write(filedata)
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).menprotect.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).menprotect()
            total = await self.config.user(ctx.author).total()           
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return    
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():                 
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                output_file = "{}/{}/{}".format(file_path, "obfuscated", "output.lua")
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", "input.lua")
                watermark = await self.config.guild(ctx.guild).watermark()
                node_folder = "{}/{}".format(file_path, "node_modules")        
                start_time = time.time()                
                if x:
                    if os.path.exists(upload):
                        os.remove(upload)
                    with open(upload, "w", encoding="utf8") as file:
                        file.write(x[0])
                    try:
                        if not os.path.exists(node_folder):
                            subprocess.check_output(f"cd {file_path} && npm install",shell=True,stderr=subprocess.STDOUT)
                            subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                        subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)                    
                    with open(output_file, "r") as file:
                        filedata = file.read()
                    with open(obfuscated, "w") as file:
                        file.write(filedata)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))   
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)                    
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).menprotect.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                    os.remove(output_file)
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
                        embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                        return await ctx.send(embed=embed)
                    url = ctx.message.attachments[0].url
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            response = await resp.text(encoding="utf8")          
                    if os.path.exists(upload):
                        os.remove(upload)
                    open(upload, "w", encoding="utf8").write(response)
                    try:
                        if not os.path.exists(node_folder):
                            subprocess.check_output(f"cd {file_path} && npm install",shell=True,stderr=subprocess.STDOUT)
                            subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                        subprocess.check_output(f"cd {file_path} && node menprotect_cli.js",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)                                       
                    with open(output_file, "r") as file:
                        filedata = file.read()
                    with open(obfuscated, "w") as file:
                        file.write(filedata)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))    
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).menprotect.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                    os.remove(output_file)                
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)   
                
    @obfuscate.command(name="prometheus")
    async def _prometheus(self, ctx: commands.Context):
        """
        Prometheus obfuscation.
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            letters = string.ascii_uppercase
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            path = "{}/{}".format("./uploads", filename + ".lua")
            watermark = await self.config.watermark()
            start_time = time.time() 
            count = await self.config.user(ctx.author).prometheus()
            total = await self.config.user(ctx.author).total()
            if x:
                if os.path.exists(upload):
                    os.remove(upload)
                with open(upload, "w") as file:
                    file.write(x[0])
                try:
                    subprocess.check_output(f"cd {file_path} && lua prometheus_cli.lua --preset Medium {path}",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)                
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).prometheus.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
                    embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                    return await ctx.send(embed=embed)
                url = ctx.message.attachments[0].url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        response = await resp.text(encoding="utf8")      
                if os.path.exists(upload):
                    os.remove(upload)
                open(upload, "w", encoding="utf8").write(response)
                try:
                    subprocess.check_output(f"cd {file_path} && lua prometheus_cli.lua --preset Medium {path}",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)                
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).prometheus.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).prometheus()
            total = await self.config.user(ctx.author).total()
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance                
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return        
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():                 
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
                path = "{}/{}".format("./uploads", filename + ".lua")
                watermark = await self.config.guild(ctx.guild).watermark()
                start_time = time.time()                
                if x:
                    if os.path.exists(upload):
                        os.remove(upload)
                    with open(upload, "w") as file:
                        file.write(x[0])
                    try:
                        subprocess.check_output(f"cd {file_path} && lua prometheus_cli.lua --preset Medium {path}",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))  
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).prometheus.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
                        embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                        return await ctx.send(embed=embed)
                    url = ctx.message.attachments[0].url
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            response = await resp.text(encoding="utf8")      
                    if os.path.exists(upload):
                        os.remove(upload)
                    open(upload, "w", encoding="utf8").write(response)
                    try:
                        subprocess.check_output(f"cd {file_path} && lua prometheus_cli.lua --preset Medium {path}",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed) 
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))  
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).prometheus.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)              
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)
                
    @obfuscate.command(name="ironbrew")
    async def _ironbrew(self, ctx: commands.Context):
        """
        IronBrew2 obfuscation.
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            letters = string.ascii_uppercase
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            output_file = "{}/{}/{}".format(file_path, "obfuscated", "output.lua")
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            watermark = await self.config.guild(ctx.guild).watermark()
            path = "{}/{}".format("./uploads", filename + ".lua")
            start_time = time.time()
            count = await self.config.user(ctx.author).ironbrew()
            total = await self.config.user(ctx.author).total()
            if x:
                if os.path.exists(upload):
                    os.remove(upload)
                with open(upload, "w") as file:
                    file.write(x[0])
                try:
                    subprocess.check_output(f"cd {file_path} && dotnet IronBrew2CLI.dll {path}",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(output_file):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)                
                with open(output_file, "r") as file:
                    filedata = file.read()
                with open(obfuscated, "w") as file:
                    file.write(filedata)
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).ironbrew.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)
                os.remove(output_file)  
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
                    embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                    return await ctx.send(embed=embed)
                url = ctx.message.attachments[0].url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        response = await resp.text(encoding="utf8")      
                if os.path.exists(upload):
                    os.remove(upload)
                open(upload, "w", encoding="utf8").write(response)
                try:
                    subprocess.check_output(f"cd {file_path} && dotnet IronBrew2CLI.dll {path}",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(output_file):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(output_file, "r") as file:
                    filedata = file.read()
                with open(obfuscated, "w") as file:
                    file.write(filedata)
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).ironbrew.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).ironbrew()
            total = await self.config.user(ctx.author).total()
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return                
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():        
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                output_file = "{}/{}/{}".format(file_path, "obfuscated", "output.lua")
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
                watermark = await self.config.guild(ctx.guild).watermark()
                path = "{}/{}".format("./uploads", filename + ".lua")
                start_time = time.time()
                if x:
                    if os.path.exists(upload):
                        os.remove(upload)
                    with open(upload, "w") as file:
                        file.write(x[0])
                    try:
                        subprocess.check_output(f"cd {file_path} && dotnet IronBrew2CLI.dll {path}",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(output_file):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)                    
                    with open(output_file, "r") as file:
                        filedata = file.read()
                    with open(obfuscated, "w") as file:
                        file.write(filedata)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))  
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance) 
                    await self.config.user(ctx.author).ironbrew.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                    os.remove(output_file)
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
                        embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                        return await ctx.send(embed=embed)
                    url = ctx.message.attachments[0].url
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            response = await resp.text(encoding="utf8")      
                    if os.path.exists(upload):
                        os.remove(upload)
                    open(upload, "w", encoding="utf8").write(response)
                    try:
                        subprocess.check_output(f"cd {file_path} && dotnet IronBrew2CLI.dll {path}",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(output_file):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(output_file, "r") as file:
                        filedata = file.read()
                    with open(obfuscated, "w") as file:
                        file.write(filedata)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))  
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).ironbrew.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
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
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            watermark = await self.config.watermark()
            path = "./uploads/" + filename + ".lua"
            start_time = time.time()
            count = await self.config.user(ctx.author).bytecode()
            total = await self.config.user(ctx.author).total()
            if x:
                if os.path.exists(upload):
                    os.remove(upload)
                with open(upload, "w") as file:
                    file.write(x[0])
                try:
                    subprocess.check_output(f"cd {file_path} && lua bytecode_cli.lua --cli --source {path} --output {obfuscated} --comment {ctx.message.author.display_name} --varcomment {ctx.message.author.display_name} --cryptvarcomm True --varname {ctx.message.author.display_name}",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)                
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).bytecode.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
                    embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                    return await ctx.send(embed=embed)
                url = ctx.message.attachments[0].url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        response = await resp.text(encoding="utf8")      
                if os.path.exists(upload):
                    os.remove(upload)
                open(upload, "w", encoding="utf8").write(response)
                try:
                    subprocess.check_output(f"cd {file_path} && lua bytecode_cli.lua --cli --source {path} --output {obfuscated} --comment {ctx.message.author.display_name} --varcomment {ctx.message.author.display_name} --cryptvarcomm True --varname {ctx.message.author.display_name}",shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed) 
                with open(obfuscated, "r+") as fp:
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
                await self.config.user(ctx.author).bytecode.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).bytecode()
            total = await self.config.user(ctx.author).total()
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return                
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():                
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-obfuscated.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
                watermark = await self.config.guild(ctx.guild).watermark()
                path = "./uploads/" + filename + ".lua"
                start_time = time.time()        
                if x:
                    if os.path.exists(upload):
                        os.remove(upload)
                    with open(upload, "w") as file:
                        file.write(x[0])
                    try:
                        subprocess.check_output(f"cd {file_path} && lua bytecode_cli.lua --cli --source {path} --output {obfuscated} --comment {ctx.message.author.display_name} --varcomment {ctx.message.author.display_name} --cryptvarcomm True --varname {ctx.message.author.display_name}",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed) 
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))  
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).bytecode.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
                        embed=discord.Embed(title=f"***Wrong file extension!***", description=f"only ``.lua`` or ``.txt`` allowed", color=0xED4245)
                        return await ctx.send(embed=embed)
                    url = ctx.message.attachments[0].url
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            response = await resp.text(encoding="utf8")      
                    if os.path.exists(upload):
                        os.remove(upload)
                    open(upload, "w", encoding="utf8").write(response)
                    try:
                        subprocess.check_output(f"cd {file_path} && lua bytecode_cli.lua --cli --source {path} --output {obfuscated} --comment {ctx.message.author.display_name} --varcomment {ctx.message.author.display_name} --cryptvarcomm True --varname {ctx.message.author.display_name}",shell=True,stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed) 
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        if watermark:
                            lines.insert(0, ("--// Obfuscated by {} - {}\n\n").format(ctx.guild.name,watermark))
                        else:
                            lines.insert(0, ("--// Obfuscated by {}\n\n").format(ctx.guild.name))  
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File obfuscated", description=("\nFile obfuscated in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).bytecode.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)              
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)
                    
    @obfuscate.command(name="xor")
    async def _xor(self, ctx: commands.Context):
        """
        XOR unpacker
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            letters = string.ascii_uppercase
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-unpacked.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            start_time = time.time()
            count = await self.config.user(ctx.author).xor()
            total = await self.config.user(ctx.author).total()    
            
            if x:
                path = upload
                if os.path.exists(path):
                    os.remove(path)
                with open(path, "w") as file:
                    file.write(x[0])
                try:
                    subprocess.check_output(f"cd {file_path} && dotnet XOR.dll {path}",shell=True,stderr=subprocess.STDOUT)                    
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
                    lines = fp.readlines()       
                    fp.seek(0)
                    fp.writelines(lines)
                end_time = time.time()
                time_elapsed = end_time - start_time
                embed = discord.Embed(title="<:lua:1035116562736230400> File unpacked", description=("\nFile unpacked in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                await self.config.user(ctx.author).xor.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)             
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
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
                try:
                    subprocess.check_output(f"cd {file_path} && dotnet XOR.dll {path}",shell=True,stderr=subprocess.STDOUT)                    
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
                    lines = fp.readlines()
                    fp.seek(0)
                    fp.writelines(lines)
                end_time = time.time()
                time_elapsed = end_time - start_time
                embed = discord.Embed(title="<:lua:1035116562736230400> File unpacked", description=("\nFile unpacked in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                await self.config.user(ctx.author).xor.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).xor()
            total = await self.config.user(ctx.author).total() 
            
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return     
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-unpacked.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
                start_time = time.time()
                if x:
                    path = upload
                    if os.path.exists(path):
                        os.remove(path)
                    with open(path, "w") as file:
                        file.write(x[0])
                    try:
                        subprocess.check_output(f"cd {file_path} && dotnet XOR.dll {path}",shell=True,stderr=subprocess.STDOUT)                    
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()        
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unpacked", description=("\nFile unpacked in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unpacked", description=("\nFile unpacked in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).xor.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)             
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
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
                    try:
                        subprocess.check_output(f"cd {file_path} && dotnet XOR.dll {path}",shell=True,stderr=subprocess.STDOUT)                    
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unpacked", description=("\nFile unpacked in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unpacked", description=("\nFile unpacked in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).xor.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)
                    
    @obfuscate.command(name="minify")
    async def _minify(self, ctx: commands.Context):
        """
        Minify lua source code.
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            letters = string.ascii_uppercase
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-minified.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            minify = "{}/{}".format(file_path, "minify.lua")
            start_time = time.time()
            count = await self.config.user(ctx.author).minify()
            total = await self.config.user(ctx.author).total()    
            
            if x:
                path = upload
                if os.path.exists(path):
                    os.remove(path)
                with open(path, "w") as file:
                    file.write(x[0])
                try:
                    output = subprocess.getoutput(f"lua {minify} minify {path} > {obfuscated}")
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
                    lines = fp.readlines()       
                    fp.seek(0)
                    fp.writelines(lines)
                end_time = time.time()
                time_elapsed = end_time - start_time
                embed = discord.Embed(title="<:lua:1035116562736230400> File minified", description=("\nFile minified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                await self.config.user(ctx.author).minify.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)             
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
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
                try:
                    output = subprocess.getoutput(f"lua {minify} minify {path} > {obfuscated}")
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
                    lines = fp.readlines()
                    fp.seek(0)
                    fp.writelines(lines)
                end_time = time.time()
                time_elapsed = end_time - start_time
                embed = discord.Embed(title="<:lua:1035116562736230400> File minified", description=("\nFile minified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                await self.config.user(ctx.author).minify.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).minify()
            total = await self.config.user(ctx.author).total() 
            minify = "{}/{}".format(file_path, "minify.lua")
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return     
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-minified.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
                start_time = time.time()
                if x:
                    path = upload
                    if os.path.exists(path):
                        os.remove(path)
                    with open(path, "w") as file:
                        file.write(x[0])
                    try:
                        output = subprocess.getoutput(f"lua {minify} minify {path} > {obfuscated}")
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()        
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File minified", description=("\nFile minified in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File minified", description=("\nFile minified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).minify.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)             
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
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
                    try:
                        output = subprocess.getoutput(f"lua {minify} minify {path} > {obfuscated}")
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File minified", description=("\nFile minified in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File minified", description=("\nFile minified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).minify.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)
                    
    @obfuscate.command(name="unminify")
    async def _unminify(self, ctx: commands.Context):
        """
        Unminify lua source code.
        """
        if await self.config.user(ctx.author).is_whitelisted() and ctx.message.channel.type is discord.ChannelType.private:
            letters = string.ascii_uppercase
            filename = "".join(random.choice(letters) for i in range(7))
            x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
            obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-unminified.lua")
            upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
            minify = "{}/{}".format(file_path, "minify.lua")
            start_time = time.time()
            count = await self.config.user(ctx.author).minify()
            total = await self.config.user(ctx.author).total()    
            
            if x:
                path = upload
                if os.path.exists(path):
                    os.remove(path)
                with open(path, "w") as file:
                    file.write(x[0])
                try:
                    output = subprocess.getoutput(f"lua {minify} unminify {path} > {obfuscated}")
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
                    lines = fp.readlines()       
                    fp.seek(0)
                    fp.writelines(lines)
                end_time = time.time()
                time_elapsed = end_time - start_time
                embed = discord.Embed(title="<:lua:1035116562736230400> File unminified", description=("\nFile unminified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                await self.config.user(ctx.author).minify.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
                os.remove(upload)
                os.remove(obfuscated)             
            elif ctx.message.attachments:
                if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                    ctx.command.reset_cooldown(ctx)
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
                try:
                    output = subprocess.getoutput(f"lua {minify} unminify {path} > {obfuscated}")
                except subprocess.CalledProcessError as err:
                    log.error(f"{err}")
                if not os.path.exists(obfuscated):
                    ctx.command.reset_cooldown(ctx)
                    embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                    return await ctx.send(embed=embed)
                with open(obfuscated, "r+") as fp:
                    lines = fp.readlines() 
                    fp.seek(0)
                    fp.writelines(lines)
                end_time = time.time()
                time_elapsed = end_time - start_time
                embed = discord.Embed(title="<:lua:1035116562736230400> File unminified", description=("\nFile unminified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                await ctx.send(embed=embed, file=discord.File(obfuscated))
                await self.config.user(ctx.author).minify.set(count + 1)
                await self.config.user(ctx.author).total.set(total + 1)
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
            count = await self.config.user(ctx.author).minify()
            total = await self.config.user(ctx.author).total()
            minify = "{}/{}".format(file_path, "minify.lua")
            if await self.config.user(ctx.author).is_whitelisted():
                cost = 0
                new_balance = balance
            if not await bank.can_spend(ctx.author, cost):
                await ctx.send(("You don't have enough {} ({}). Obfuscator cost: {} {}.").format(currency,balance,cost,currency))
                return     
            if not ctx.message.author.bot and ctx.message.channel.id in await self.config.guild(ctx.guild).channels():
                letters = string.ascii_uppercase
                filename = "".join(random.choice(letters) for i in range(7))
                x = re.findall(r"(?<=```)[\S\s]*(?=```)", ctx.message.content)
                obfuscated = "{}/{}/{}".format(file_path, "obfuscated", filename + "-unminified.lua")
                upload = "{}/{}/{}".format(file_path, "uploads", filename + ".lua")
                start_time = time.time()
                if x:
                    path = upload
                    if os.path.exists(path):
                        os.remove(path)
                    with open(path, "w") as file:
                        file.write(x[0])
                    try:
                        output = subprocess.getoutput(f"lua {minify} unminify {path} > {obfuscated}")
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines()         
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unminified", description=("\nFile unminified in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unminified", description=("\nFile unminified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).minify.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)             
                elif ctx.message.attachments:
                    if not ctx.message.attachments[0].url.endswith((".lua", ".txt")):
                        ctx.command.reset_cooldown(ctx)
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
                    try:
                        output = subprocess.getoutput(f"lua {minify} unminify {path} > {obfuscated}")
                    except subprocess.CalledProcessError as err:
                        log.error(f"{err}")
                    if not os.path.exists(obfuscated):
                        ctx.command.reset_cooldown(ctx)
                        embed = discord.Embed(title="Error", description="\nVerify your syntax is correct and try again.", color=0xED4245)
                        return await ctx.send(embed=embed)
                    with open(obfuscated, "r+") as fp:
                        lines = fp.readlines() 
                        fp.seek(0)
                        fp.writelines(lines)
                    end_time = time.time()
                    time_elapsed = end_time - start_time
                    if cost > 0:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unminified", description=("\nFile unminified in ⌛({}) seconds.\n{}, You have {} {} remaining.").format(str(time_elapsed)[:5],ctx.author.mention,new_balance,currency), color=0x000088)
                    else:
                        embed = discord.Embed(title="<:lua:1035116562736230400> File unminified", description=("\nFile unminified in ⌛({}) seconds.").format(str(time_elapsed)[:5]), color=0x000088)                    
                    await ctx.send(embed=embed, file=discord.File(obfuscated))
                    await bank.set_balance(ctx.author, new_balance)
                    await self.config.user(ctx.author).minify.set(count + 1)
                    await self.config.user(ctx.author).total.set(total + 1)
                    os.remove(upload)
                    os.remove(obfuscated)
                else:
                    embed = discord.Embed(title="No file or code block", color=0xED4245)
                    ctx.command.reset_cooldown(ctx)
                    await ctx.send(embed=embed)
     
    @commands.group(name="obfuscatorset", aliases=["obfuscateset"])
    async def obfuscatorset(self, ctx: commands.Context) -> None:
        """
        Obfuscator settings.
        """
        pass
    
    @checks.is_owner()
    @commands.guild_only()
    @obfuscatorset.command(name="channel")
    async def obfuscation_channel(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None) -> None:
        """Set the channels for obfuscator."""
        if channel is None:
            channel = ctx.channel
        
        if channel.id in await self.config.guild(ctx.guild).channels():
            async with self.config.guild(ctx.guild).channels() as data:
                data.remove(channel.id)
            await ctx.send(("{} removed from obfuscator channels.").format(channel.mention))
        else:
            async with self.config.guild(ctx.guild).channels() as data:
                data.append(channel.id)
            await ctx.send(("{} added to obfuscator channels.").format(channel.mention))    
        
    @checks.is_owner()
    @commands.guild_only()
    @obfuscatorset.command(name="cost")
    async def obfuscation_cost(self, ctx: commands.context, *, amount: Optional[int] = 0) -> 0:
        """Set the cost of obfuscator."""
        currency = await bank.get_currency_name(ctx.guild)
        await self.config.guild(ctx.guild).cost.set(amount)
        await ctx.send(("Obfuscator cost: {} {}.").format(amount,currency))
        
    @checks.is_owner()    
    @commands.guild_only()
    @obfuscatorset.command(name="user")
    async def obfuscation_user(self, ctx: commands.Context, *, user: discord.Member):
        """add/remove user from direct message obfuscation."""
        if await self.config.user(user).is_whitelisted() or user in await self.config.guild(ctx.guild).users():
            async with self.config.guild(ctx.guild).users() as data:
                if user.id in data:
                    data.remove(user.id)
                pass
            await self.config.user(user).is_whitelisted.set(False)
            await ctx.send(("{} removed from obfuscator whitelist.").format(user.mention))
        else:
            async with self.config.guild(ctx.guild).users() as data:
                data.append(user.id)
            await self.config.user(user).is_whitelisted.set(True)
            await ctx.send(("{} added to obfuscator whitelist.").format(user.mention))
            
    @checks.is_owner()
    @obfuscatorset.group(name="watermark")
    async def watermark(self, ctx: commands.Context) -> None:
        """
        Obfuscator watermark settings.
        """
        pass

    @checks.is_owner()
    @watermark.command(name="global")
    async def global_watermark(self, ctx: commands.context, *, value: Optional[str] = None) -> None:
        """Set the global watermark for obfuscator."""
        if value is None:
            await ctx.send(("Obfuscator global watermark reset."))
            return await self.config.watermark.clear()
        await self.config.watermark.set(value)
        await ctx.send(("Obfuscator global watermark: {}").format(value))
        
    @checks.is_owner()
    @commands.guild_only()
    @watermark.command(name="guild")
    async def guild_watermark(self, ctx: commands.context, *, value: Optional[str] = None) -> None:
        """Set the guild watermark for obfuscator."""
        if value is None:
            await ctx.send(("Obfuscator guild watermark reset."))
            return await self.config.guild(ctx.guild).watermark.clear()
        await self.config.guild(ctx.guild).watermark.set(value)
        await ctx.send(("Obfuscator guild watermark: {}").format(value))
            
    @obfuscatorset.command(name="version", aliases=["about"])
    async def obfuscation_version(self, ctx: commands.Context):
        """Display version information."""
        embed = discord.Embed(title="Version/About", description=("\nObfuscator version: {}\nCog author: [{}](https://discordapp.com/users/309536563161989120)").format(self.__version__,self.__author__), color=0x000088)
        embed.set_thumbnail(url="https://github.com/jmesfo0/jmes-cogs/raw/main/obfuscator/lua.png")
        await ctx.send(embed=embed)
        
    @obfuscate.command(name="help")
    async def obfuscation_help(self, ctx: commands.Context):
        """Display help information."""
        embed = discord.Embed(title="Obfuscator Commands", colour=0x000088)
        embed.set_thumbnail(url="https://github.com/jmesfo0/jmes-cogs/raw/main/obfuscator/lua.png")
        embed.add_field(name="obfuscate", value="the default obfuscator command", inline=False) 
        embed.add_field(name="obfuscate luaseel", value="LuaSeel Obfuscator (default)", inline=False)        
        embed.add_field(name="obfuscate menprotect", value="Menprotect Obfuscator", inline=False)        
        embed.add_field(name="obfuscate prometheus", value="Prometheus Obfuscator", inline=False)        
        embed.add_field(name="obfuscate ironbrew", value="IronBrew Obfuscator", inline=False)        
        embed.add_field(name="obfuscate bytecode", value="Bytecode Obfuscator", inline=False)
        embed.add_field(name="obfuscate minify/unminify", value="Minifier", inline=False)
        embed.add_field(name="obfuscate xor", value="XOR unpacker", inline=False)
        embed.set_footer(text=("Obfuscator ({})").format(self.__version__), icon_url="https://github.com/jmesfo0/jmes-cogs/raw/main/obfuscator/lua.png")        
        await ctx.send(embed=embed)
        
    @obfuscate.command(name="stats", aliases=["view"])
    async def _stats(self, ctx: commands.Context, *, user: Optional[discord.Member]) -> None:
        """View user stats"""
        if not user:
            ironbrew = await self.config.user(ctx.author).ironbrew()
            luaseel = await self.config.user(ctx.author).luaseel()
            menprotect = await self.config.user(ctx.author).menprotect()
            prometheus = await self.config.user(ctx.author).prometheus()
            bytecode = await self.config.user(ctx.author).bytecode()
            minify = await self.config.user(ctx.author).minify()
            xor = await self.config.user(ctx.author).xor()
            whitelisted = await self.config.user(ctx.author).is_whitelisted()
            total = ironbrew + luaseel + menprotect + prometheus + bytecode + minify
            if total == 0:
                return await ctx.send("You have no stats.")
            embed = discord.Embed(title=("<:lua:1035116562736230400> Obfuscator Stats for {}").format(ctx.author.display_name), colour=0x000088)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name="IronBrew", value=str(ironbrew), inline=True)
            embed.add_field(name="Menprotect", value=str(menprotect), inline=True)
            embed.add_field(name="LuaSeel", value=str(luaseel), inline=True)
            embed.add_field(name="ByteCode", value=str(bytecode), inline=True)
            embed.add_field(name="Prometheus", value=str(prometheus), inline=True)
            embed.add_field(name="Minifier", value=str(minify), inline=True)
            embed.add_field(name="XOR", value=str(xor), inline=True)
            embed.add_field(name="Total Uses", value=str(total), inline=True)
            if whitelisted is True:
                embed.add_field(name="Whitelisted?", value="✅", inline=True)
            else:
                embed.add_field(name="Whitelisted?", value="❌", inline=True) 
            await ctx.send(embed=embed)
        else:
            ironbrew = await self.config.user(user).ironbrew()
            luaseel = await self.config.user(user).luaseel()
            menprotect = await self.config.user(user).menprotect()
            prometheus = await self.config.user(user).prometheus()
            bytecode = await self.config.user(user).bytecode()
            minify = await self.config.user(ctx.author).minify()
            xor = await self.config.user(ctx.author).xor()
            whitelisted = await self.config.user(user).is_whitelisted()
            total = ironbrew + luaseel + menprotect + prometheus + bytecode + minify
            if total == 0:
                return await ctx.send("No stats for that user.")                
            embed = discord.Embed(title=("<:lua:1035116562736230400> Obfuscator Stats for {}").format(user.display_name), colour=0x000088)
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="IronBrew", value=str(ironbrew), inline=True)
            embed.add_field(name="Menprotect", value=str(menprotect), inline=True)
            embed.add_field(name="LuaSeel", value=str(luaseel), inline=True)
            embed.add_field(name="ByteCode", value=str(bytecode), inline=True)
            embed.add_field(name="Prometheus", value=str(prometheus), inline=True)
            embed.add_field(name="Minifier", value=str(minify), inline=True)
            embed.add_field(name="XOR", value=str(xor), inline=True)
            embed.add_field(name="Total Uses", value=str(total), inline=True)
            if whitelisted is True:
                embed.add_field(name="Whitelisted?", value="✅", inline=True)
            else:
                embed.add_field(name="Whitelisted?", value="❌", inline=True)   
            await ctx.send(embed=embed)
            
    @obfuscate.command(name="leaderboard")
    @commands.guild_only()
    async def leaderboard(self, ctx):
        """Show the Obfuscator leaderboard."""
        userinfo = await self.config._all_from_scope(scope="USER")
        if not userinfo:
            return await ctx.reply("No one has obfuscated any files.")
        async with ctx.typing():
            sorted_acc = sorted(userinfo.items(), key=lambda x: x[1]["total"], reverse=True)
        # Leaderboard logic from https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/economy/economy.py#L445
        pound_len = len(str(len(sorted_acc)))
        total_len = 10
        header = "{pound:{pound_len}}{total:{total_len}}{name:2}\n".format(
            pound="#",
            pound_len=pound_len + 3,
            total="Files",
            total_len=total_len + 6,
            name="\N{THIN SPACE}" + "Name"
            if not str(ctx.author.mobile_status) in ["online", "idle", "dnd"]
            else "Name",
        )
        temp_msg = header
        for pos, account in enumerate(sorted_acc):
            if account[1]["total"] == 0:
                continue
            user_obj = await self.bot.fetch_user(account[0])
            _user_name = discord.utils.escape_markdown(user_obj.name)
            user_name = f"{_user_name}#{user_obj.discriminator}"
            if len(user_name) > 28:
                user_name = f"{_user_name[:19]}...#{user_obj.discriminator}"
            user_idx = pos + 1
            if user_obj == ctx.author:
                temp_msg += (
                    f"{f'{user_idx}.': <{pound_len + 2}} "
                    f"{humanize_number(account[1]['total']) + ' 📜 ': <{total_len + 4}} <<{user_name}>>\n"
                )
            else:
                temp_msg += (
                    f"{f'{user_idx}.': <{pound_len + 2}} "
                    f"{humanize_number(account[1]['total']) + ' 📜 ': <{total_len + 4}} {user_name}\n"
                )

        page_list = []
        pages = 1
        for page in pagify(temp_msg, delims=["\n"], page_length=1000):
            embed = discord.Embed(
                colour=0x000088,
                title="<:lua:1035116562736230400> Obfuscator Leaderboard",
                description=box(page, lang="md"),
            )
            embed.set_footer(text=f"Page {humanize_number(pages)}/{humanize_number(math.ceil(len(temp_msg) / 1500))}")
            pages += 1
            page_list.append(embed)
        return await menu(ctx, page_list, DEFAULT_CONTROLS)
            
    @checks.is_owner()
    @commands.guild_only()
    @obfuscatorset.command(name="settings")            
    async def obfuscatorset_settings(self, ctx: commands.Context):
        """View current settings."""
        data = await self.config.all()
        guild_data = await self.config.guild(ctx.guild).all()
        user_data = await self.config.all_users()
        currency = await bank.get_currency_name(ctx.guild)
        if not guild_data["channels"]:
            channel_names = ["No channels set."]
        else:
            channel_names = []
            for channel_id in guild_data["channels"]:
                channel_obj = self.bot.get_channel(channel_id)
                if channel_obj:
                    channel_names.append("#"+channel_obj.mention)
        if not guild_data["users"]:
            user_names = ["No users."]
        else:
            user_names = []
            for user_id in guild_data["users"]:
                user_obj = self.bot.get_user(user_id)
                if user_obj:
                    user_names.append(user_obj.mention)
                          
        watermark = guild_data["watermark"]     
        cost = guild_data["cost"]
        channels = humanize_list(channel_names)
        users = humanize_list(user_names)

        embed = discord.Embed(colour=0x000088)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = "**__Obfuscator settings:__**"
        if watermark:
            embed.add_field(name="Watermark:", value=str(watermark), inline=False)
        embed.add_field(name="Cost:", value=("{} {}").format(str(cost),currency), inline=False)
        embed.add_field(name="Channels:", value="\n".join(channel_names))
        embed.add_field(name="Whitelist:", value="\n".join(user_names))
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
                    line = line + originalupload_data + "\n"
                out_file.write(line)
        try:
            output = subprocess.getoutput(f"lua {copy}")
        except subprocess.CalledProcessError as err:
            log.error(f"{err}")
        if os.path.exists(obfuscated):
            os.remove(obfuscated)
        f = open(obfuscated, "a")
        f.write(output)
        f.close()
        os.remove(copy)
