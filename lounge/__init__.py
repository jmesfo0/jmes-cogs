import json
from pathlib import Path

from redbot.core.bot import Red

from .lounge import Lounge

async def setup(bot: Red) -> None:
    await bot.add_cog(Lounge(bot))
