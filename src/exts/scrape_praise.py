import csv

from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime

class Praise(commands.Cog):
    """Commands for scraping old praise from the server"""
    def __init__(self, bot):
        self.bot = bot
        print(datetime(21, 6, 4))

    @commands.command()
    async def get_praise(self, ctx, after: str = None):
        await ctx.send('Fetching all Praise...')
        if after:
            dates = after.split('-')
            msgs = await ctx.channel.history(after=datetime(20 + dates[2], dates[1], dates[0])).flatten()
        else:
            msgs = await ctx.channel.history(after=datetime(2021, 6, 4)).flatten()

        clean_msgs = [['To', 'From', 'Reason for Dishing', 'Date', 'Room']]
        for msg in msgs:
            for person in msg.mentions:
                clean_msgs.append(
                    [
                        "@" + person.name,
                        msg.author.name + msg.author.discriminator,
                        msg.content,
                        msg.created_at.strftime("%b-%d-%Y"),
                        msg.channel.name
                    ]
                )
                print(f'Adding praise for: {person.name}')

        with open("praise.csv", 'w') as f:
            writer = csv.writer(f)
            print('Writing Praise...')
            writer.writerows(clean_msgs)

def setup(bot):
    bot.add_cog(Praise(bot))
