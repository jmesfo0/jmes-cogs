from .whalealerts import WhaleAlerts

def setup(bot):
    bot.add_cog(WhaleAlerts(bot))