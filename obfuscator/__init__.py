from .obfuscator import Obfuscator


async def setup(bot):
    await bot.add_cog(Obfuscator(bot))
