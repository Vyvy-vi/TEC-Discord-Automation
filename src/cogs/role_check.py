from discord import Embed
from discord.ext import commands, tasks
from discord.ext.commands import Context


class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=3600)
    async def check_roles(self):
          print('1001011010')

    @commands.cog.listener()
    async def on_ready(self):
        check_calendar.start()

        @commands.command(name="alert")

    @commands.command()
    async def _test(self, ctx: Context):
        embed = Embed(title='Comms call', description=self.bot.TEMPLATES['COMMS'][1])
        embed.set_image(url=self.bot.TEMPLATES['COMMS'][0])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Alerts(bot))

