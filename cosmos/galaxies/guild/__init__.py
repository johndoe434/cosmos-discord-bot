from .levels import Levels
from ._models import GuildCache
from .roleshop import RoleShop
from .settings import GuildSettings


__all__ = [
    Levels,
    RoleShop,
    GuildSettings,
]


def setup(bot):
    plugin = bot.plugins.get_from_file(__file__)
    plugin.collection = bot.db[plugin.data.guild.collection_name]
    plugin.cache = GuildCache(plugin)

    plugin.load_cogs(__all__)

    bot.guild_cache = plugin.cache
