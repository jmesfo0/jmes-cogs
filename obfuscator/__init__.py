from .obfuscator import Obfuscator


def setup(bot):
    bot.add_cog(Obfuscator(bot))