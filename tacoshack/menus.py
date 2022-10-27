import asyncio
import logging
from typing import Dict, List, Tuple, Optional, Any, Iterable
from redbot.core import commands
from redbot.core.commands import Context

import discord
from redbot.core.utils.chat_formatting import escape, humanize_number
from redbot.vendored.discord.ext import menus
from redbot.vendored.discord.ext.menus import First, Last, button

log = logging.getLogger("red.cogs.tacoshack.menus")


class TacoLeaderboardSource(menus.ListPageSource):
    def __init__(self, entries: List[Tuple[int, Dict]]):
        super().__init__(entries, per_page=10)

    def is_paginating(self):
        return True

    async def format_page(self, menu: menus.MenuPages, entries: List[Tuple[int, Dict]]):
        ctx = menu.ctx
        tacos_len = len(humanize_number(entries[0][1]["tacos"]))
        start_position = (menu.current_page * self.per_page) + 1
        pos_len = len(str(start_position + 9)) + 2
        tacos_len = (len("Tacos") if len("Tacos") > tacos_len else tacos_len) + 2
        header = (
            f"{'#':{pos_len}}{'Tacos':{tacos_len}}{'User':2}"
        )
        author = ctx.author

        if getattr(ctx, "guild", None):
            guild = ctx.guild
        else:
            guild = None

        players = []
        for position, acc in enumerate(entries, start=start_position):
            user_id = acc[0]
            account_data = acc[1]
            if guild is not None:
                member = guild.get_member(user_id)
            else:
                member = None

            if member is not None:
                username = member.display_name
            else:
                user = menu.ctx.bot.get_user(user_id)
                if user is None:
                    username = f"{user_id}"
                else:
                    username = user.name
            username = escape(username, formatting=True)

            if user_id == author.id:
                # Highlight the author's position
                username = f"<<{username}>>"

            pos_str = position
            tacos = humanize_number(account_data["tacos"])
            data = (
                f"{f'{pos_str}.':{pos_len}}"
                f"{tacos:{tacos_len}}"
                f"{username}"
            )

            players.append(data)

        embed = discord.Embed(
            title="TacoShack Leaderboard",
            color=await menu.ctx.embed_color(),
            description="```md\n{}``` ```md\n{}```".format(
                header,
                "\n".join(players),
            ),
        )
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed

class ScoreboardSource(TacoLeaderboardSource):
    def __init__(self, entries: List[Tuple[int, Dict]], stat: Optional[str] = None):
        super().__init__(entries)
        self._stat = stat or "tacos"
        self._legend = None

    def is_paginating(self):
        return True

    async def format_page(self, menu: menus.MenuPages, entries: List[Tuple[int, Dict]]):
        ctx = menu.ctx
        # if self._legend is None:
            # self._legend = (
                # "React with the following to go to the specified filter:\n"
                # "\N{TACO}: Taco scoreboard\n"
                # "\N{MONEY WITH WINGS}: Income scoreboard\n"
                # "\U0001F4B5: Balance scoreboard\n"
                # "\U0001F4B0: Tips scoreboard\n"
            # )
        stats_len = len(humanize_number(entries[0][1][self._stat])) + 3
        start_position = (menu.current_page * self.per_page) + 1
        pos_len = len(str(start_position + 9)) + 2
        stats_plural = self._stat if self._stat.endswith("s") else f"{self._stat}s"
        stats_len = (len(stats_plural) if len(stats_plural) > stats_len else stats_len) + 2
        header = f"{'#':{pos_len}}{stats_plural.title().ljust(stats_len)}{'User':2}"
        author = ctx.author

        if getattr(ctx, "guild", None):
            guild = ctx.guild
        else:
            guild = None

        players = []
        for (position, (user_id, account_data)) in enumerate(entries, start=start_position):
            if guild is not None:
                member = guild.get_member(user_id)
            else:
                member = None

            if member is not None:
                username = member.display_name
            else:
                user = menu.ctx.bot.get_user(user_id)
                if user is None:
                    username = user_id
                else:
                    username = user.name
            username = escape(str(username), formatting=True)
            if user_id == author.id:
                # Highlight the author's position
                username = f"<<{username}>>"

            pos_str = position
            stats_value = humanize_number(account_data[self._stat.lower()])
            
            data = f"{f'{pos_str}.':{pos_len}}" f"{stats_value:{stats_len}}" f"{username}"
            players.append(data)

        embed = discord.Embed(
            title=f"TacoShack {self._stat.title()} Scoreboard",
            color=await menu.ctx.embed_color(),
            description="```md\n{}``` ```md\n{}```".format(
                header,
                "\n".join(players),
            ),
        )
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return {"embed": embed, "content": self._legend}
        
## https://github.com/Drapersniper/Red-DiscordBot/blob/V3/edge/redbot/core/utils/_dpy_menus_utils.py - Files used in V3/Edge

class CannotReadMessage(menus.MenuError):
    def __init__(self):
        super().__init__("Bot does not have Read Message permissions in this channel.")
class HybridMenu(menus.MenuPages, inherit_buttons=False):
    def __init__(
        self,
        source: menus.PageSource,
        cog: Optional[commands.Cog] = None,
        clear_reactions_after: bool = True,
        delete_message_after: bool = True,
        add_reactions: bool = True,
        using_custom_emoji: bool = False,
        using_embeds: bool = False,
        keyword_to_reaction_mapping: Optional[Dict[str, Iterable[str]]] = None,
        timeout: int = 60,
        message: discord.Message = None,
        **kwargs: Any,
    ) -> None:
        self._add_reactions = add_reactions
        self._using_custom_emoji = using_custom_emoji
        super().__init__(
            source,
            clear_reactions_after=clear_reactions_after,
            delete_message_after=delete_message_after,
            check_embeds=using_embeds,
            timeout=timeout,
            message=message,
            **kwargs,
        )
        if (
            bad_stop := menus._cast_emoji(
                "\N{BLACK SQUARE FOR STOP}\N{VARIATION SELECTOR-16}"
            )
        ) and bad_stop in self._buttons:
            del self._buttons[bad_stop]
        self.cog = cog
        self.__keyword_to_reaction_mapping = keyword_to_reaction_mapping
        self._actions = {}
        self.__tasks = self._Menu__tasks

    def _register_keyword(self):
        if isinstance(self.__keyword_to_reaction_mapping, dict):
            for k, v in self.__keyword_to_reaction_mapping.items():
                if k not in self._actions:
                    self._actions[k] = []
                for e in v:
                    emoji = menus._cast_emoji(e)
                    if emoji not in self.buttons:
                        continue
                    self._actions[k].append(emoji)

    def should_add_reactions(self):
        if self._add_reactions:
            return len(self.buttons)

    def _verify_permissions(self, ctx, channel, permissions):
        if not permissions.send_messages:
            raise menus.CannotSendMessages()

        if self.check_embeds and not permissions.embed_links:
            raise menus.CannotEmbedLinks()

        self._can_remove_reactions = permissions.manage_messages

        if self.should_add_reactions():
            if not permissions.add_reactions:
                raise menus.CannotAddReactions()
            if self._using_custom_emoji and not permissions.external_emojis:
                raise menus.CannotAddReactions()

        if not permissions.read_message_history:
            raise menus.CannotReadMessageHistory()

        if self._actions and not permissions.read_messages:
            raise CannotReadMessage()

    async def show_checked_page(self, page_number: int) -> None:
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number)
            elif page_number >= max_pages:
                await self.show_page(0)
            elif page_number < 0:
                await self.show_page(max_pages - 1)
            elif max_pages > page_number >= 0:
                await self.show_page(page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def finalize(self, timed_out):
        """|coro|
        A coroutine that is called when the menu loop has completed
        its run. This is useful if some asynchronous clean-up is
        required after the fact.
        Parameters
        --------------
        timed_out: :class:`bool`
            Whether the menu completed due to timing out.
        """
        if timed_out and self.delete_message_after:
            self.delete_message_after = False

    def _skip_single_arrows(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages == 1

    def _skip_single_arrows_has_external_emojis_perm(self):
        if self._skip_single_arrows():
            return True
        return self._has_external_emojis_perms()

    def _skip_single_arrows_has_not_external_emojis_perm(self):
        if self._skip_single_arrows():
            return True
        return self._has_not_external_emojis_perm()

    def _skip_double_arrows_has_external_emojis_perm(self):
        if self._skip_double_triangle_buttons():
            return True
        return self._has_external_emojis_perms()

    def _skip_double_arrows_has_not_external_emojis_perm(self):
        if self._skip_double_triangle_buttons():
            return True
        return self._has_not_external_emojis_perm()

    def _has_external_emojis_perms(self):
        return self.ctx.channel.permissions_for(self.ctx.me).external_emojis

    def _has_not_external_emojis_perm(self):
        return not self._has_external_emojis_perms()

    def _skip_double_triangle_buttons(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 2

    def reaction_check(self, payload):
        """Just extends the default reaction_check to use owner_ids"""
        if payload.message_id != self.message.id:
            return False
        if payload.user_id not in (*self.bot.owner_ids, self._author_id):
            return False
        return payload.emoji in self.buttons

    def message_check(self, message: discord.Message):
        if message.author.bot or message.author.id not in (*self.bot.owner_ids, self._author_id):
            return False
        return message.content.lower() in self._actions

    async def _internal_loop(self):
        try:
            self.__timed_out = False
            loop = self.bot.loop
            # Ensure the name exists for the cancellation handling
            tasks = []
            while self._running:
                tasks = [
                    asyncio.ensure_future(
                        self.bot.wait_for("raw_reaction_add", check=self.reaction_check)
                    ),
                    asyncio.ensure_future(
                        self.bot.wait_for("raw_reaction_remove", check=self.reaction_check)
                    ),
                ]
                if self._actions:
                    tasks.append(
                        asyncio.ensure_future(
                            self.bot.wait_for("message_without_command", check=self.message_check)
                        )
                    )

                done, pending = await asyncio.wait(
                    tasks, timeout=self.timeout, return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()

                if len(done) == 0:
                    raise asyncio.TimeoutError()

                # Exception will propagate if e.g. cancelled or timed out
                payload = done.pop().result()
                loop.create_task(self.update(payload))

                # NOTE: Removing the reaction ourselves after it's been done when
                # mixed with the checks above is incredibly racy.
                # There is no guarantee when the MESSAGE_REACTION_REMOVE event will
                # be called, and chances are when it does happen it'll always be
                # after the remove_reaction HTTP call has returned back to the caller
                # which means that the stuff above will catch the reaction that we
                # just removed.

                # For the future sake of myself and to save myself the hours in the future
                # consider this my warning.

        except asyncio.TimeoutError:
            self.__timed_out = True
        finally:
            self._event.set()

            # Cancel any outstanding tasks (if any)
            for task in tasks:
                task.cancel()

            try:
                await self.finalize(self.__timed_out)
            except Exception:
                pass
            finally:
                self.__timed_out = False

            # Can't do any requests if the bot is closed
            if self.bot.is_closed():
                return

            # Wrap it in another block anyway just to ensure
            # nothing leaks out during clean-up
            try:
                if self.delete_message_after:
                    return await self.message.delete()

                if self.clear_reactions_after:
                    if self._can_remove_reactions:
                        return await self.message.clear_reactions()

                    for button_emoji in self.buttons:
                        try:
                            await self.message.remove_reaction(button_emoji, self.__me)
                        except discord.HTTPException:
                            continue
            except Exception:
                pass

    async def update(self, payload):
        """
        Updates the menu after an event has been received.
        Parameters
        -----------
        payload: :class:`discord.RawReactionActionEvent`
            The reaction event that triggered this update.
        """
        if isinstance(payload, discord.RawReactionActionEvent):
            button = self.buttons[payload.emoji]
            if not self._running:
                return

            try:
                if button.lock:
                    async with self._lock:
                        if self._running:
                            await button(self, payload)
                else:
                    await button(self, payload)
            except Exception:
                # TODO: logging?
                import traceback

                traceback.print_exc()
        elif isinstance(payload, discord.Message):
            emojis = self._actions.get(payload.content, [])
            for emoji in emojis:
                if not emoji or emoji not in self.buttons:
                    continue
                button = self.buttons[emoji]
                if not self._running:
                    continue
                try:
                    if button.lock:
                        async with self._lock:
                            if self._running:
                                await button(self, payload)
                    else:
                        await button(self, payload)
                except Exception:
                    # TODO: logging?
                    import traceback

                    traceback.print_exc()

    async def start(self, ctx, *, channel=None, wait=False, page: int = 0):
        """
        Starts the interactive menu session.
        Parameters
        -----------
        ctx: :class:`Context`
            The invocation context to use.
        channel: :class:`discord.abc.Messageable`
            The messageable to send the message to. If not given
            then it defaults to the channel in the context.
        wait: :class:`bool`
            Whether to wait until the menu is completed before
            returning back to the caller.
        Raises
        -------
        MenuError
            An error happened when verifying permissions.
        discord.HTTPException
            Adding a reaction failed.
        """

        # Clear the buttons cache and re-compute if possible.
        try:
            del self.buttons
        except AttributeError:
            pass

        self.bot = bot = ctx.bot
        self.ctx = ctx
        self._author_id = ctx.author.id
        channel = channel or ctx.channel
        is_guild = isinstance(channel, discord.abc.GuildChannel)
        me = ctx.guild.me if is_guild else ctx.bot.user
        permissions = channel.permissions_for(me)
        self.__me = discord.Object(id=me.id)
        self._verify_permissions(ctx, channel, permissions)
        self._event.clear()
        msg = self.message
        if msg is None:
            self.message = msg = await self.send_initial_message(ctx, channel, page=page)
        self._register_keyword()
        if self.should_add_reactions() or self._actions:
            # Start the task first so we can listen to reactions before doing anything
            for task in self.__tasks:
                task.cancel()
            self.__tasks.clear()

            self._running = True
            self.__tasks.append(bot.loop.create_task(self._internal_loop()))

            if self.should_add_reactions():

                async def add_reactions_task():
                    for emoji in self.buttons:
                        await msg.add_reaction(emoji)

                self.__tasks.append(bot.loop.create_task(add_reactions_task()))

            if wait:
                await self._event.wait()

    async def send_initial_message(
        self, ctx: Context, channel: discord.abc.Messageable, page: int = 0
    ):
        """
        The default implementation of :meth:`Menu.send_initial_message`
        for the interactive pagination session.
        This implementation shows the first page of the source.
        """
        page = await self._source.get_page(page)
        kwargs = await self._get_kwargs_from_page(page)
        return await channel.send(**kwargs)

    @button(
        "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_double_arrows_has_external_emojis_perm,
        position=First(0),
    )
    async def go_to_first_page(self, payload):
        """go to the first page"""
        await self.show_page(0)

    @button(
        "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_double_arrows_has_not_external_emojis_perm,
        position=First(0),
    )
    async def go_to_first_page_custom(self, payload):
        """go to the first page"""
        await self.show_page(0)

    @button(
        "\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_single_arrows_has_external_emojis_perm,
        position=First(1),
    )
    async def go_to_previous_page(self, payload):
        """go to the previous page"""
        await self.show_checked_page(self.current_page - 1)

    @button(
        "\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_single_arrows_has_not_external_emojis_perm,
        position=First(1),
    )
    async def go_to_previous_page_custom(self, payload):
        """go to the previous page"""
        await self.show_checked_page(self.current_page - 1)

    @button("\N{CROSS MARK}", skip_if=_has_external_emojis_perms, position=Last(0))
    async def stop_pages(self, payload: discord.RawReactionActionEvent) -> None:
        """stops the pagination session."""
        self.stop()

    @button(
        "\N{CROSS MARK}",
        skip_if=_has_not_external_emojis_perm,
        position=Last(0),
    )
    async def stop_pages_custom(self, payload: discord.RawReactionActionEvent) -> None:
        """stops the pagination session."""
        self.stop()

    @button(
        "\N{BLACK RIGHT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_single_arrows_has_external_emojis_perm,
        position=Last(1),
    )
    async def go_to_next_page(self, payload):
        """go to the next page"""
        await self.show_checked_page(self.current_page + 1)

    @button(
        "\N{BLACK RIGHT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_single_arrows_has_not_external_emojis_perm,
        position=Last(1),
    )
    async def go_to_next_page_custom(self, payload):
        """go to the next page"""
        await self.show_checked_page(self.current_page + 1)

    @button(
        "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_double_arrows_has_external_emojis_perm,
        position=Last(2),
    )
    async def go_to_last_page(self, payload):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(self._source.get_max_pages() - 1)

    @button(
        "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_double_arrows_has_not_external_emojis_perm,
        position=Last(2),
    )
    async def go_to_last_page_custom(self, payload):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(self._source.get_max_pages() - 1)

class SimpleHybridMenu(HybridMenu, inherit_buttons=True):
    def __init__(
        self,
        source: menus.PageSource,
        cog: Optional[commands.Cog] = None,
        clear_reactions_after: bool = True,
        delete_message_after: bool = True,
        add_reactions: bool = True,
        timeout: int = 60,
        accept_keywords: bool = False,
        **kwargs: Any,
    ):
        if accept_keywords:
            keyword_to_reaction_mapping = {
                ("last"): [
                    "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
                ],
                ("first"): [
                    "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
                ],
                ("next"): [
                    "\N{BLACK RIGHT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
                ],
                ("previous"): [
                    "\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
                ],
                ("prev"): [
                    "\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
                ],
                ("close"): ["\N{CROSS MARK}"],
            }
        else:
            keyword_to_reaction_mapping = None
        super().__init__(
            source=source,
            cog=cog,
            add_reactions=add_reactions,
            timeout=timeout,
            clear_reactions_after=clear_reactions_after,
            delete_message_after=delete_message_after,
            keyword_to_reaction_mapping=keyword_to_reaction_mapping,
            **kwargs,
        )
        
class BaseMenu(menus.MenuPages, inherit_buttons=False):
    def __init__(
        self,
        source: menus.PageSource,
        clear_reactions_after: bool = True,
        delete_message_after: bool = False,
        timeout: int = 60,
        message: discord.Message = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            source,
            clear_reactions_after=clear_reactions_after,
            delete_message_after=delete_message_after,
            timeout=timeout,
            message=message,
            **kwargs,
        )
        self.__tasks = self._Menu__tasks

    async def update(self, payload):
        """|coro|

        Updates the menu after an event has been received.

        Parameters
        -----------
        payload: :class:`discord.RawReactionActionEvent`
            The reaction event that triggered this update.
        """
        button = self.buttons[payload.emoji]
        if not self._running:
            return

        try:
            if button.lock:
                async with self._lock:
                    if self._running:
                        await button(self, payload)
            else:
                await button(self, payload)
        except Exception as exc:
            log.debug("Ignored exception on reaction event", exc_info=exc)

    async def start(self, ctx, *, channel=None, wait=False, page: int = 0):
        """
        Starts the interactive menu session.

        Parameters
        -----------
        ctx: :class:`Context`
            The invocation context to use.
        channel: :class:`discord.abc.Messageable`
            The messageable to send the message to. If not given
            then it defaults to the channel in the context.
        wait: :class:`bool`
            Whether to wait until the menu is completed before
            returning back to the caller.

        Raises
        -------
        MenuError
            An error happened when verifying permissions.
        discord.HTTPException
            Adding a reaction failed.
        """

        # Clear the buttons cache and re-compute if possible.
        try:
            del self.buttons
        except AttributeError:
            pass

        self.bot = bot = ctx.bot
        self.ctx = ctx
        self._author_id = ctx.author.id
        channel = channel or ctx.channel
        is_guild = isinstance(channel, discord.abc.GuildChannel)
        me = ctx.guild.me if is_guild else ctx.bot.user
        permissions = channel.permissions_for(me)
        self.__me = discord.Object(id=me.id)
        self._verify_permissions(ctx, channel, permissions)
        self._event.clear()
        msg = self.message
        if msg is None:
            self.message = msg = await self.send_initial_message(ctx, channel, page=page)
        if self.should_add_reactions():
            # Start the task first so we can listen to reactions before doing anything
            for task in self.__tasks:
                task.cancel()
            self.__tasks.clear()

            self._running = True
            self.__tasks.append(bot.loop.create_task(self._internal_loop()))

            if self.should_add_reactions():

                async def add_reactions_task():
                    for emoji in self.buttons:
                        await msg.add_reaction(emoji)

                self.__tasks.append(bot.loop.create_task(add_reactions_task()))

            if wait:
                await self._event.wait()

    async def send_initial_message(self, ctx: commands.Context, channel: discord.abc.Messageable, page: int = 0):
        """

        The default implementation of :meth:`Menu.send_initial_message`
        for the interactive pagination session.

        This implementation shows the first page of the source.
        """
        self.current_page = page
        page = await self._source.get_page(page)
        kwargs = await self._get_kwargs_from_page(page)
        return await channel.send(**kwargs)

    async def show_checked_page(self, page_number: int) -> None:
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number)
            elif page_number >= max_pages:
                await self.show_page(0)
            elif page_number < 0:
                await self.show_page(max_pages - 1)
            elif max_pages > page_number >= 0:
                await self.show_page(page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    def reaction_check(self, payload):
        """Just extends the default reaction_check to use owner_ids"""
        if payload.message_id != self.message.id:
            return False
        if payload.user_id not in (*self.bot.owner_ids, self._author_id):
            return False
        return payload.emoji in self.buttons

    def _skip_single_arrows(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages == 1

    def _skip_double_triangle_buttons(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 2

    @menus.button(
        "\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        position=menus.First(1),
        skip_if=_skip_single_arrows,
    )
    async def go_to_previous_page(self, payload):
        """go to the previous page"""
        await self.show_checked_page(self.current_page - 1)

    @menus.button(
        "\N{BLACK RIGHT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        position=menus.Last(0),
        skip_if=_skip_single_arrows,
    )
    async def go_to_next_page(self, payload):
        """go to the next page"""
        await self.show_checked_page(self.current_page + 1)

    @menus.button(
        "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        position=menus.First(0),
        skip_if=_skip_double_triangle_buttons,
    )
    async def go_to_first_page(self, payload):
        """go to the first page"""
        await self.show_page(0)

    @menus.button(
        "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        position=menus.Last(1),
        skip_if=_skip_double_triangle_buttons,
    )
    async def go_to_last_page(self, payload):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(self._source.get_max_pages() - 1)

    @menus.button("\N{CROSS MARK}")
    async def stop_pages(self, payload: discord.RawReactionActionEvent) -> None:
        """stops the pagination session."""
        self.stop()
        
class ScoreBoardMenu(BaseMenu, inherit_buttons=False):
    def __init__(
        self,
        source: menus.PageSource,
        cog: Optional[commands.Cog] = None,
        clear_reactions_after: bool = True,
        delete_message_after: bool = False,
        timeout: int = 60,
        message: discord.Message = None,
        show_global: bool = False,
        current_scoreboard: str = "tacos",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            source,
            clear_reactions_after=clear_reactions_after,
            delete_message_after=delete_message_after,
            timeout=timeout,
            message=message,
            **kwargs,
        )
        self.cog = cog
        self.show_global = show_global
        self._current = current_scoreboard

    def _skip_single_arrows(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages == 1

    def _skip_double_triangle_buttons(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 2

    @menus.button("\N{TACO}")
    async def _tacos(self, payload: discord.RawReactionActionEvent) -> None:
        if self._current == "tacos":
            return
        self._current = "tacos"
        tacos_sorted = await self.cog.get_global_scoreboard(
            guild=self.ctx.guild if not self.show_global else None, keyword=self._current
        )
        await self.change_source(source=ScoreboardSource(entries=tacos_sorted, stat=self._current))
        
    @menus.button("\N{MONEY WITH WINGS}")
    async def _income(self, payload: discord.RawReactionActionEvent) -> None:
        if self._current == "income":
            return
        self._current = "income"
        income_sorted = await self.cog.get_global_scoreboard(
            guild=self.ctx.guild if not self.show_global else None, keyword=self._current
        )
        await self.change_source(source=ScoreboardSource(entries=income_sorted, stat=self._current))
        
    @menus.button("\U0001F4B5")
    async def _balance(self, payload: discord.RawReactionActionEvent) -> None:
        if self._current == "balance":
            return
        self._current = "balance"
        balance_sorted = await self.cog.get_global_scoreboard(
            guild=self.ctx.guild if not self.show_global else None, keyword=self._current
        )
        await self.change_source(source=ScoreboardSource(entries=balance_sorted, stat=self._current))
        
    @menus.button("\U0001F4B0")
    async def _tips(self, payload: discord.RawReactionActionEvent) -> None:
        if self._current == "tips":
            return
        self._current = "tips"
        tips_sorted = await self.cog.get_global_scoreboard(
            guild=self.ctx.guild if not self.show_global else None, keyword=self._current
        )
        await self.change_source(source=ScoreboardSource(entries=tips_sorted, stat=self._current))      
        
    @menus.button(
        "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_double_triangle_buttons,
    )
    async def go_to_first_page(self, payload):
        """go to the first page"""
        await self.show_page(0)

    @menus.button(
        "\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_single_arrows,
    )
    async def go_to_previous_page(self, payload):
        """go to the previous page"""
        await self.show_checked_page(self.current_page - 1)

    @menus.button("\N{CROSS MARK}")
    async def stop_pages(self, payload: discord.RawReactionActionEvent) -> None:
        """stops the pagination session."""
        self.stop()

    @menus.button(
        "\N{BLACK RIGHT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_single_arrows,
    )
    async def go_to_next_page(self, payload):
        """go to the next page"""
        await self.show_checked_page(self.current_page + 1)

    @menus.button(
        "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\N{VARIATION SELECTOR-16}",
        skip_if=_skip_double_triangle_buttons,
    )
    async def go_to_last_page(self, payload):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(self._source.get_max_pages() - 1)
