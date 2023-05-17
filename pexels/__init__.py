from .pexels import Pexels

async def setup(bot):
    await bot.add_cog(Pexels(bot))
