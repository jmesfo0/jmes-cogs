import discord
from discord.ext import tasks
import contextlib
import logging
import math
import random
from typing import Literal, List, Optional
import asyncio
import aioschedule as schedule
import time
import datetime

from redbot.core import commands, checks, Config, bank
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import bold
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS, start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils import AsyncIter
from .menus import TacoLeaderboardSource, ScoreboardSource, SimpleHybridMenu, ScoreBoardMenu

log = logging.getLogger("red.jmes-cogs.TacoShack")

class TacoShack(commands.Cog):
    """
    TacoShack Classic for Red
    """
    __version__ = "1.0.0"
    __author__ = "jmes"
    
    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord", "owner", "user", "user_strict"],
        user_id: int,
    ):
        await self.config.user_from_id(user_id).clear()
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2331337184, force_registration=True)
        default_user = { 
            "shack": {
                "name": "",
                "slogan": "",  
                "balance": 0,
                "income": 0,
                "tacos": 0,
                "tips": 0,
                "joined": "",                     
                "has_founded": False,                
                "upgrades": {
                    "121": 0,
                    "122": 0,
                    "123": 0,
                    "124": 0,
                    "125": 0,
                    "126": 0
                },
                "employees": {
                    "231": 0,
                    "232": 0,
                    "233": 0,
                    "234": 0,
                    "235": 0,
                    "236": 0,
                    "237": 0
                }
            }
        }        
        default_global = {
            "upgrades": {
                "121": {
                    "name": "New Paint",
                    "price": 250,
                    "boost": 10,
                    "max": 13
                },
                "122": {
                    "name": "New Furniture",
                    "price": 600,
                    "boost": 20,
                    "max": 13
                },
                "123": {
                    "name": "Better Appliances",
                    "price": 1200,
                    "boost": 40,
                    "max": 15
                },
                "124": {
                    "name": "Nicer Bathrooms",
                    "price": 800,
                    "boost": 25,
                    "max": 12
                },
                "125": {
                    "name": "Billboard",
                    "price": 1000,
                    "boost": 35,
                    "max": 15
                },
                "126": {
                    "name": "Cooler Tip Jar",
                    "price": 500,
                    "boost": 15,
                    "max": 13
                }            
            },
            "employees": {
                "231": {
                    "name": "Apprentice Chef",
                    "price": 250,
                    "boost": 10,
                    "max": 15
                },
                "232": {
                    "name": "Cook",
                    "price": 600,
                    "boost": 20,
                    "max": 15
                },
                "233": {
                    "name": "Sous Chef",
                    "price": 1200,
                    "boost": 40,
                    "max": 13
                },
                "234": {
                    "name": "Head Chef",
                    "price": 2000,
                    "boost": 65,
                    "max": 13
                },
                "235": {
                    "name": "Executive Chef",
                    "price": 5000,
                    "boost": 150,
                    "max": 12
                },
                "236": {
                    "name": "Advertiser",
                    "price": 100,
                    "boost": 50,
                    "max": 13
                },
                "237": {
                    "name": "Greeter",
                    "price": 100,
                    "boost": 50,
                    "max": 13
                }                        
            }
        }   
        self.config.register_user(**default_user)        
        self.config.register_global(**default_global)
        
        log.info("TacoShack loaded.")
        schedule.every().hour.at(":00").do(self.update_balance)
        self.hourly_income.start()
        
    @tasks.loop(seconds=1)
    async def hourly_income(self):
        await asyncio.wait(schedule.run_pending())

    def cog_unload(self) -> None:
        self.hourly_income.cancel()
        schedule.clear()
        log.info("TacoShack unloaded.")
        
    async def update_balance(self):
        for x in await self.config.all_users():
            user = self.bot.get_user(x)
            if not user:
                return
            income = await self.config.user(user).shack.income()
            balance = await self.config.user(user).shack.balance()
            new_balance = balance + income
            await self.config.user(user).shack.balance.set(new_balance)
        log.info("TacoShack hourly incomes sent.")

    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.group(name="tacoshack", aliases=["ts", "shack", "taco"])
    async def _shack(self, ctx: commands.Context) -> None:
        """Various TacoShack commands."""
        pass
    
    @_shack.command(name="found", aliases=["create"])
    async def _found(self, ctx: commands.Context):
        """Found your shack."""          
        if not await self.config.user(ctx.author).shack.has_founded():
            await self.config.user(ctx.author).shack.name.set(str(ctx.author.display_name)+"'s TacoShack")
            await self.config.user(ctx.author).shack.slogan.set("")
            await self.config.user(ctx.author).shack.balance.set(1000)
            await self.config.user(ctx.author).shack.income.set(100)
            await self.config.user(ctx.author).shack.tacos.set(0)
            await self.config.user(ctx.author).shack.tips.set(0)
            await self.config.user(ctx.author).shack.joined.set(str(datetime.date.today()))
            await self.config.user(ctx.author).shack.has_founded.set(True)            
            await ctx.send("Your shack was created! Check your DM for more info!")
            
            embed = discord.Embed(colour=0x1ed606, description=
            "🌮 __**Your brand new taco shack is now in business!**__ 🌮\n"+
            "🔹 You are in charge of running your taco shack! You will get **hourly income** to pay for things.\n"+
            "🔹 You can increase your income by purchasing **upgrades** or hiring **employees**!\n"+
            "🔹 You yourself can also work every **10** minutes, and collect tips every **5** minutes to make some cash.\n"+
            "🔸 Become the most sucessful taco shack around by reaching the **top of the leaderboard**!\n"+
            "🔸 Either top the **Most Tacos Sold** or the **Richest** leaderboard for bragging rights.")
            await ctx.author.send(embed=embed)
        else:
            await ctx.send("You already own a shack")
            
    @_shack.command(name="balance")
    async def _balance(self, ctx: commands.Context, *, user: Optional[discord.Member]) -> None:
        """View your shack balance."""
        if not user:
            user = ctx.author # thank you @sravan1946 ;)
        if not await self.config.user(user).shack.has_founded():
            return await ctx.send("First you must 'found' your shack.")
        name = await self.config.user(user).shack.name()
        slogan = await self.config.user(user).shack.slogan()              
        balance = await self.config.user(user).shack.balance()
        embed = discord.Embed(title=str(name), colour=0xf9a422)
        embed.set_thumbnail(url=ctx.author.display_avatar)
        embed.add_field(name="Name", value="🔺 "+str(name)+" 🏛\n"+str(slogan), inline=False)
        embed.add_field(name="Balance", value="💵 $" + str(balance), inline=False)
        await ctx.send(embed=embed)
        
    @_shack.command(name="shack", aliases=["myshack"])
    async def _myshack(self, ctx: commands.Context, *, user: Optional[discord.Member]) -> None:
        """View your shack."""
        if not user:
            user = ctx.author # thank you @sravan1946 ;)
        if not await self.config.user(user).shack.has_founded():
            return await ctx.send("First you must 'found' your shack.")
        today = datetime.date.today()
        joined = await self.config.user(user).shack.joined()
        joined_date = datetime.datetime.strptime(joined, '%Y-%m-%d').date()
        delta = today - joined_date
        name = await self.config.user(user).shack.name()
        slogan = await self.config.user(user).shack.slogan()              
        balance = await self.config.user(user).shack.balance()
        income = await self.config.user(user).shack.income()
        tips = await self.config.user(user).shack.tips()
        tacos = await self.config.user(user).shack.tacos()
        embed = discord.Embed(title=str(name), colour=0xf9a422)
        embed.set_thumbnail(url=ctx.author.display_avatar)
        embed.add_field(name="Name", value="🔺 "+str(name)+" 🏛\n"+str(slogan), inline=False)
        embed.add_field(name="Balance", value="💵 $" + str(balance), inline=False)
        embed.add_field(name="Income", value="💸 $" + str(income) + "/hour", inline=False)
        embed.add_field(name="Total Tips", value="💰 $" + str(tips), inline=False)
        embed.add_field(name="Total Tacos", value="🌮 " + str(tacos), inline=False)
        embed.add_field(name="Shack Age", value="⌛ "+ str(delta.days) + " days", inline=False)
        await ctx.send(embed=embed)

    @_shack.command(name="leaderboard", aliases=["scoreboard", "top"])
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    @commands.guild_only()
    async def leaderboard(self, ctx: commands.Context, show_global: bool = False):
        """View the scoreboard."""
        tacos_sorted = await self.get_global_scoreboard(guild=ctx.guild if not show_global else None, keyword="tacos")
        if tacos_sorted:
            await ScoreBoardMenu(
                source=ScoreboardSource(entries=tacos_sorted, stat="tacos"),
                delete_message_after=True,
                clear_reactions_after=True,
                timeout=60,
                cog=self,
                show_global=show_global,
            ).start(ctx=ctx)
        else:
            await ctx.send("There are no shacks in the server.")

    @_shack.command(name="shacks")
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    @commands.guild_only()
    async def _shacks(self, ctx: commands.Context) -> None:
        """List of all shacks."""
        embeds = []
        all_users = await self.config.all_users()
        if not all_users:
            return await ctx.send("There are no shacks.")
            
        async for (k, v) in AsyncIter(all_users.items(), steps=200):
            today = datetime.date.today()
            joined = str(v["shack"]["joined"])
            joined_date = datetime.datetime.strptime(joined, '%Y-%m-%d').date()
            delta = today - joined_date                
            name = str(v["shack"]["name"])
            balance = str(v["shack"]["balance"])
            slogan = str(v["shack"]["slogan"])     
            income = str(v["shack"]["income"])
            tips = str(v["shack"]["tips"])
            tacos = str(v["shack"]["tacos"])
            embed = discord.Embed(title=str(name), colour=0xf9a422)                     
            embed.add_field(name="Name", value="🔺 "+name+" 🏛\n"+slogan)
            embed.add_field(name="Balance", value="💵 $" + balance)
            embed.add_field(name="Income", value="💸 $" + income + "/hour")
            embed.add_field(name="Total Tips", value="💰 $" + tips)
            embed.add_field(name="Total Tacos", value="🌮 " + tacos)
            embed.add_field(name="Shack Age", value="⌛ "+ str(delta.days) + " days")
            embeds.append(embed)
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=20)

    @_shack.command(name="version", hidden=True)
    async def _version(self, ctx: commands.Context):
        """Display the version."""
        await ctx.send(("TacoShack Classic for Red v{} by {}").format(self.__version__,self.__author__))
        
    @_shack.command(name="help")
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def _help(self, ctx: commands.Context):
        """View all commands and their descriptions."""
        embed = discord.Embed(title="All Commands", colour=0xf9a422)
        embed.set_thumbnail(url="https://cdn.dribbble.com/users/72556/screenshots/1711901/8bit-taco.jpg")
        embed.add_field(name="help", value="View all commands and their descriptions", inline=False)        
        embed.add_field(name="found/create", value="Found your taco shack", inline=False)
        embed.add_field(name="shack/myshack", value="View info about your shack", inline=False)
        embed.add_field(name="deposit", value="Deposit from bank to shack balance", inline=False)
        embed.add_field(name="withdraw", value="Withdraw from shack to bank balance", inline=False)
        embed.add_field(name="leaderboard", value="View leaderboard", inline=False)
        embed.add_field(name="shack [user]", value="View info about a users shack", inline=False)
        embed.add_field(name="upgrades", value="View all upgrades for your taco shack", inline=False)
        embed.add_field(name="buy [id]", value="Purchase an upgrade", inline=False)
        embed.add_field(name="hire", value="View all hireable employees", inline=False)
        embed.add_field(name="hire [id]", value="Hire an employee", inline=False)
        embed.add_field(name="work", value="Cook some tacos and make some cash", inline=False)
        embed.add_field(name="tips", value="Check for tips", inline=False)
        embed.add_field(name="daily", value="Collect your daily gift", inline=False)
        embed.add_field(name="name/rename", value="Change the name of your taco shack", inline=False)
        embed.add_field(name="slogan", value="Change the slogan of your taco shack", inline=False)
        embed.add_field(name="reset/restart", value="Delete all your taco shack data", inline=False)
        embed.set_footer(text=("TacoShack Classic for Red ({})").format(self.__version__), icon_url="https://cdn.dribbble.com/users/72556/screenshots/1711901/8bit-taco.jpg")
        await ctx.send(embed=embed)
                
    @_shack.command(name="name", aliases=["rename"])
    async def _name(self, ctx: commands.Context, *, str):
        """Name/rename your shack."""
        if not await self.config.user(ctx.author).shack.has_founded():
            return await ctx.send("First you must 'found' your shack.")
        await self.config.user(ctx.author).shack.name.set(str)
        await ctx.send(("Your shack name has been set to: **{}**").format(str))
        
    @_shack.command(name="slogan")
    async def _slogan(self, ctx: commands.Context, *, str):
        """Set your shack slogan."""
        if not await self.config.user(ctx.author).shack.has_founded():
            return await ctx.send("First you must 'found' your shack.")
        await self.config.user(ctx.author).shack.slogan.set(str)
        await ctx.send(("Your shack slogan has been set to: **{}**").format(str))
  
    @_shack.command(name="work", aliases=["w"])
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.user)
    async def _work(self, ctx: commands.Context):
        """Work your shack."""
        if not await self.config.user(ctx.author).shack.has_founded():
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("First you must 'found' your shack.")
             
        balance =  await self.config.user(ctx.author).shack.balance()
        tacos_made =  await self.config.user(ctx.author).shack.tacos()
        
        tacos = math.floor(random.random() * (30 - 5)) + 5
        money = math.floor(random.random() * (100 - 20)) + 20
        
        new_tacos = tacos_made + tacos
        new_balance = balance + money
        
        await self.config.user(ctx.author).shack.balance.set(new_balance)
        await self.config.user(ctx.author).shack.tacos.set(new_tacos)
        await ctx.send(("You cooked **{}** 🌮 tacos and earned **${}** 💵 while working!").format(tacos,money))
        
    @_shack.command(name="tips", aliases=["t"])
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
    async def _tips(self, ctx: commands.Context):
        """Collect tips from your shack."""
        if not await self.config.user(ctx.author).shack.has_founded():
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("First you must 'found' your shack.")
             
        balance =  await self.config.user(ctx.author).shack.balance()
        tips =  await self.config.user(ctx.author).shack.tips()
        
        tip = math.floor(random.random() * (50 - 10)) + 10
        
        new_balance = balance + tip
        new_tips = tips + tip
        
        await self.config.user(ctx.author).shack.balance.set(new_balance)
        await self.config.user(ctx.author).shack.tips.set(new_tips)
        await ctx.send(("You collected ${} 💰 in tips!").format(tip))
        
    @_shack.command(name="daily", aliases=["d"])
    @commands.cooldown(rate=1, per=86400, type=commands.BucketType.user)
    async def _daily(self, ctx: commands.Context):
        """Collect daily reward."""
        if not await self.config.user(ctx.author).shack.has_founded():
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("First you must 'found' your shack.")

        balance =  await self.config.user(ctx.author).shack.balance()
        amount = 250
        new_balance = balance + amount       
        await self.config.user(ctx.author).shack.balance.set(new_balance)
        await ctx.send(("You have claimed your daily reward of **${}** 💰!").format(amount))
            
    @_shack.command(name="deposit")
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.user)
    @commands.guild_only()
    async def _deposit(self, ctx: commands.Context, amount: int):
        """Deposit bank currency into shack balance."""
        if amount <= 0:
            return await ctx.send("Uh oh, amount has to be more than 0.")

        currency = await bank.get_currency_name(ctx.guild)

        if not await self._can_spend(False, ctx.author, amount):
            return await ctx.send(f"Uh oh, you cannot afford this.")

        await bank.withdraw_credits(ctx.author, amount)
        new_balance = int(amount * 0.5)
        await self.deposit_balance(ctx.author, new_balance)
        return await ctx.send(
            f"You take {amount} {currency} and deposit ${new_balance} 💵 to your shack balance."
        )

    @_shack.command(name="withdraw")
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.user)
    @commands.guild_only()
    async def _withdraw(self, ctx: commands.Context, amount: int):
        """Withdraw shack balance into bank currency."""
        if amount <= 0:
            return await ctx.send("Uh oh, amount has to be more than 0.")
        
        currency = await bank.get_currency_name(ctx.guild)

        if not await self._can_spend(True, ctx.author, amount):
            return await ctx.send(f"Uh oh, you cannot afford this.")

        new_currency = int(amount / 0.5)
        try:
            await bank.deposit_credits(ctx.author, new_currency)
        except errors.BalanceTooHigh:
            return await ctx.send(f"Uh oh, your bank balance would be way too high.")
        await self.withdraw_balance(ctx.author, amount)
        return await ctx.send(
            f"You withdrew ${amount} 💵 from your shack balance and got {new_currency} {currency}."
        )
                    
    @_shack.command(name="reset", aliases=["restart"])
    @commands.cooldown(rate=1, per=3600, type=commands.BucketType.user)    
    async def _reset(self, ctx: commands.Context):
        """Reset your shack."""
        if not await self.config.user(ctx.author).shack.has_founded():
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You don't own a shack.")
        name = await self.config.user(ctx.author).shack.name()            
        dmsg = await ctx.send(
        (
            "{author}, this will delete all your shack data for {shack}\n"
            "Do you want to proceed?"
        ).format(
            author=bold(ctx.author.display_name),
            shack=bold(str(name))
            )
        )
        start_adding_reactions(dmsg, ReactionPredicate.YES_OR_NO_EMOJIS)
        pred = ReactionPredicate.yes_or_no(dmsg, ctx.author)
        
        try:
            await ctx.bot.wait_for("reaction_add", check=pred, timeout=60)
        except asyncio.TimeoutError:
            return await self._clear_react(dmsg)
        if not pred.result:
            with contextlib.suppress(discord.HTTPException):
                await dmsg.edit(
                content=("Ok, I won't delete your shack data.")
                )
                ctx.command.reset_cooldown(ctx)
                return await self._clear_react(dmsg)
        await ctx.send(("Deleting shack data for {}").format(bold(str(name))))
        await self.red_delete_data_for_user(requester="user", user_id=ctx.author.id)
        await ctx.send("Your shack settings have all been removed")    
        
    @_shack.command(name="upgrades", aliases=["upgrade", "up"])
    async def _upgrades(self, ctx: commands.Context):
        """View upgrades for your shack."""
        if not await self.config.user(ctx.author).shack.has_founded():
            return await ctx.send("First you must 'found' your shack.")
             
        upgrades = await self.config.upgrades()
        user = await self.config.user(ctx.author).shack()         
        
        embed = discord.Embed(title="Upgrades", colour=0x1ced31, description=f""+
        "**New Paint**  (" + str(user["upgrades"]["121"]) + "/" + str(upgrades["121"]["max"]) + ")"+
        "\nCost: $" + str(self.costcalc(upgrades["121"]["price"], user["upgrades"]["121"])) + 
        "\nBoost: +$"+str(upgrades["121"]["boost"])+"/hr \nID: 121\n\n"+
        
        "**New Furniture**  (" + str(user["upgrades"]["122"]) + "/" + str(upgrades["122"]["max"]) + ")"+
        "\nCost: $" + str(self.costcalc(upgrades["122"]["price"], user["upgrades"]["122"])) + 
        "\nBoost: +$"+str(upgrades["122"]["boost"])+"/hr \nID: 122\n\n"+
        
        "**Better Appliances**  (" + str(user["upgrades"]["123"]) + "/" + str(upgrades["123"]["max"]) + ")"+
        "\nCost: $" + str(self.costcalc(upgrades["123"]["price"], user["upgrades"]["123"])) + 
        "\nBoost: +$"+str(upgrades["123"]["boost"])+"/hr \nID: 123\n\n"+
        
        "**Nicer Bathrooms**  (" + str(user["upgrades"]["124"]) + "/" + str(upgrades["124"]["max"]) + ")"+
        "\nCost: $" + str(self.costcalc(upgrades["124"]["price"], user["upgrades"]["124"])) + 
        "\nBoost: +$"+str(upgrades["124"]["boost"])+"/hr \nID: 124\n\n"+
        
        "**Billboard**  (" + str(user["upgrades"]["125"]) + "/" + str(upgrades["125"]["max"]) + ")"+
        "\nCost: $" + str(self.costcalc(upgrades["125"]["price"], user["upgrades"]["125"])) + 
        "\nBoost: +$"+str(upgrades["125"]["boost"])+"/hr \nID: 125\n\n"+
        
        "**Cooler Tip Jar**  (" + str(user["upgrades"]["126"]) + "/" + str(upgrades["126"]["max"]) + ")"+
        "\nCost: $" + str(self.costcalc(upgrades["126"]["price"], user["upgrades"]["126"])) + 
        "\nBoost: +$"+str(upgrades["126"]["boost"])+"/hr \nID: 126\n\n"+
        "Use **buy [ID]** to purchase an item!\n"+
        "Use **hire** to hire new employees for more boosts!"
        )
        embed.set_thumbnail(url='https://cdn.dribbble.com/users/72556/screenshots/1711901/8bit-taco.jpg')
        await ctx.send(embed=embed)
        
    @_shack.command(name="buy")
    async def _buy(self, ctx: commands.Context, *, id) -> None:
        """Buy upgrades for your shack."""
        if not await self.config.user(ctx.author).shack.has_founded():
             return await ctx.send("First you must 'found' your shack.")
             
        if not id.isnumeric():
            return await ctx.send("Please use a valid ID!")
             
        upgrades = await self.config.upgrades()
        user = await self.config.user(ctx.author).shack()
        
        if (int(id) > 230 and int(id) < 238):
            return await ctx.send("That is an employee! Use hire [ID] to hire!")
            
        if not id in upgrades:
            return await ctx.send("Please use a valid ID!")

        cost = self.costcalc(upgrades[id]["price"], user["upgrades"][id])

        if user["balance"] < cost:
            return await ctx.send("You don't have enough money!")
        if user["upgrades"][id] >= upgrades[id]["max"]:
            return await ctx.send("You already have purchased the maximum amount!")

        purchase_balance = user["balance"] - cost
        purchase_boost = user["income"] + upgrades[id]["boost"]
        purcahse_upgrade = user["upgrades"][id] + 1
        
        await self.config.user(ctx.author).shack.upgrades.set_raw(id, value=purcahse_upgrade)
        await self.config.user(ctx.author).shack.income.set(purchase_boost)
        await self.config.user(ctx.author).shack.balance.set(purchase_balance)
        await ctx.send(("✅ You have purchased **{}** for $**{}**").format(str(upgrades[id]["name"]), cost))

    @_shack.command(name="hire")
    async def _hire(self, ctx: commands.Context, id: Optional[str] = None) -> None:
        """Hire employees for your shack."""
        if not await self.config.user(ctx.author).shack.has_founded():
             return await ctx.send("First you must 'found' your shack.")       
            
        if id is None:
            employees = await self.config.employees()
            user = await self.config.user(ctx.author).shack()
            embed = discord.Embed(title="Employees", colour=0x3477e2, description=f""+
            "**Apprentice Chef**  (" + str(user["employees"]["231"]) + "/" + str(employees["231"]["max"]) + ")"+
            "\nCost: $" + str(self.costcalc(employees["231"]["price"], user["employees"]["231"])) + 
            "\nBoost: +$"+str(employees["231"]["boost"])+"/hr \nID: 231\n\n"+
            
            "**Cook**  (" + str(user["employees"]["232"]) + "/" + str(employees["232"]["max"]) + ")"+
            "\nCost: $" + str(self.costcalc(employees["232"]["price"], user["employees"]["232"])) + 
            "\nBoost: +$"+str(employees["232"]["boost"])+"/hr \nID: 232\n\n"+
            
            "**Sous Chef**  (" + str(user["employees"]["233"]) + "/" + str(employees["233"]["max"]) + ")"+
            "\nCost: $" + str(self.costcalc(employees["233"]["price"], user["employees"]["233"])) + 
            "\nBoost: +$"+str(employees["233"]["boost"])+"/hr \nID: 233\n\n"+
            
            "**Head Chef**  (" + str(user["employees"]["234"]) + "/" + str(employees["234"]["max"]) + ")"+
            "\nCost: $" + str(self.costcalc(employees["234"]["price"], user["employees"]["234"])) + 
            "\nBoost: +$"+str(employees["234"]["boost"])+"/hr \nID: 234\n\n"+
            
            "**Executive Chef**  (" + str(user["employees"]["235"]) + "/" + str(employees["235"]["max"]) + ")"+
            "\nCost: $" + str(self.costcalc(employees["235"]["price"], user["employees"]["235"])) + 
            "\nBoost: +$"+str(employees["235"]["boost"])+"/hr \nID: 235\n\n"+
            
            "**Advertiser**  (" + str(user["employees"]["236"]) + "/" + str(employees["236"]["max"]) + ")"+
            "\nCost: $" + str(self.costcalc(employees["236"]["price"], user["employees"]["236"])) + 
            "\nBoost: +$"+str(employees["236"]["boost"])+"/hr \nID: 236\n\n"+
            
            "**Greeter**  (" + str(user["employees"]["237"]) + "/" + str(employees["237"]["max"]) + ")"+
            "\nCost: $" + str(self.costcalc(employees["237"]["price"], user["employees"]["237"])) + 
            "\nBoost: +$"+str(employees["237"]["boost"])+"/hr \nID: 237\n\n"+
            "Use **hire [ID]** to hire a(n) employee!\n"+
            "Use **upgrades** to view more boosts!"
            )
            embed.set_thumbnail(url='https://cdn.dribbble.com/users/72556/screenshots/1711901/8bit-taco.jpg')
            return await ctx.send(embed=embed) 
             
        if not id.isnumeric():
            return await ctx.send("Please use a valid ID!")   
            
        employees = await self.config.employees()
        user = await self.config.user(ctx.author).shack()
        
        if (int(id) > 120 and int(id) < 127):
            return await ctx.send("That is an upgrade! Use buy [ID] to purchase!")
            
        if not id in employees:
            return await ctx.send("Please use a valid ID!")

        cost = self.costcalc(employees[id]["price"], user["employees"][id])

        if user["balance"] < cost:
            return await ctx.send("You don't have enough money!")
        if user["employees"][id] >= employees[id]["max"]:
            return await ctx.send("You already have hired the maximum amount!")

        purchase_balance = user["balance"] - cost
        purchase_boost = user["income"] + employees[id]["boost"]
        purcahse_upgrade = user["employees"][id] + 1
        
        await self.config.user(ctx.author).shack.employees.set_raw(id, value=purcahse_upgrade)
        await self.config.user(ctx.author).shack.income.set(purchase_boost)
        await self.config.user(ctx.author).shack.balance.set(purchase_balance)
        await ctx.send(("✅ You have hired a(n) **{}** for $**{}**").format(str(employees[id]["name"]), cost))         
        

    def costcalc(self, cost, amount):
        amountT = int(amount) + 1
        amountTotal = amountT * amountT
        price = amountTotal * int(cost)
        return price
       
    async def get_global_scoreboard(self, positions: int = None, guild: discord.Guild = None, keyword: str = None) -> List[tuple]:
        if keyword is None:
            keyword = "tacos"
        raw_accounts = await self.config.all_users()
        if guild is not None:
            tmp = raw_accounts.copy()
            for acc in tmp:
                if not guild.get_member(acc):
                    del raw_accounts[acc]
        raw_accounts_new = {}
        async for (k, v) in AsyncIter(raw_accounts.items(), steps=200):
            user_data = {}
            for (vk, vi) in v["shack"].items():
                if vk in ["tacos"]:
                    user_data.update({vk: vi})
                elif vk in ["income"]:
                    user_data.update({vk: vi})
                elif vk in ["balance"]:
                    user_data.update({vk: vi})
                elif vk in ["tips"]:
                    user_data.update({vk: vi})
            if user_data:
                user_data = {k: user_data}
            raw_accounts_new.update(user_data)
        sorted_acc = sorted(
            raw_accounts_new.items(),
            key=lambda x: (x[1].get(keyword, 0), x[1].get("tacos", 0)),
            reverse=True,
        )
        if positions is None:
            return sorted_acc
        else:
            return sorted_acc[:positions]
            
    async def _clear_react(self, msg: discord.Message):
        with contextlib.suppress(discord.HTTPException):
            await msg.clear_reactions()
            
    async def can_spend(self, user, amount):
        return await self.config.user(user).shack.balance() >= amount

    async def _can_spend(self, to_currency, user, amount):
        if to_currency:
            return bool(await self.can_spend(user, amount))
        return bool(await bank.can_spend(user, amount))

    async def withdraw_balance(self, user, amount):
        balance = await self.config.user(user).shack.balance() - amount
        await self.config.user(user).shack.balance.set(balance)

    async def deposit_balance(self, user, amount):
        balance = await self.config.user(user).shack.balance() + amount
        await self.config.user(user).shack.balance.set(balance)

    async def get_balance(self, user):
        conf = (
            self.config.user(user)
        )
        return await conf.shack.balance()
