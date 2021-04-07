from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context

class Bans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role("Can Ban", "Tissue")
    async def hammer(ctx: Context, reg: str):
        gather_list = list([member for member in ctx.message.guild.members if member.display_name.startswith(reg)])
        await ctx.send(embed=Embed(title='Swinging Hammer on...', description='```diff\n- '+ ' | '.join([str(i) for i in gather_list]) +'```'))
        for i in gather_list:
            await asyncio.sleep(30)
            await ctx.send(f'Banning {str(i)}#{i}')
            await ctx.guild.ban(i)

    @commands.command()
    @commands.has_any_role("Admin", "can ban", "Tissue")
    async def gather(ctx: Context, reg: str):
        gather_list = list([[member.name, member.id] for member in ctx.message.guild.members if member.display_name.startswith(reg)])
        await ctx.send(embed=Embed(description='```fix\n'+ ' | '.join([str(i) for i in gather_list]) +'```'))


def setup(bot):
    bot.add_cog(Bans(cog))

