from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context

def format_data(author, address):
    data = {'user_ID': author.id,
            'Discord Username': author.name,
            'Wallet Address': address}
    return data

def write_data(data):
    return

class Sourcecred(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = []

    @commands.command()
    @commands.has_role("Acknowledged CC")
    async def wallet(self, ctx: Context, address: str = None):
        """command to associate a user's wallet with their discord"""
        print(ctx.author)
        if address:
            data = format_data(ctx.author, address)
            self.data.append(str(data))
            await ctx.send('\n'.join([f'{i} - {data[i]}' for i in data]))
        else:
            await ctx.send('If you want to add your address more privately, dm the bot and use the command `wallet`')

    @commands.command()
    @commands.has_any_role('Stewards', 'Admin')
    async def wallet_list(self, ctx: Context):
        """command to fetch wallet address data"""
        await ctx.send('\n'.join(self.data))

def setup(bot):
    bot.add_cog(Sourcecred(bot))
