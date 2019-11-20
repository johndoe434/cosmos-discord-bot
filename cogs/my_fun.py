import asyncio

from discord.ext import commands


class MyFun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if ("shibu" in message.content.lower() or "bu " in message.content.lower()) and ("cosmos" in message.content.lower() or "cosmo" in message.content.lower()):
            await message.add_reaction('😡')

    @commands.Cog.listener()
    async def on_member_update(self, old, new):
        if old.nick != new.nick:
            if ("shibu" in new.nick.lower() or "bu " in new.nick.lower()) and ("cosmos" in new.nick.lower() or "cosmo" in new.nick.lower()):
                await new.edit(nick="😡 | Gross")


def setup(bot):
    bot.add_cog(MyFun(bot))