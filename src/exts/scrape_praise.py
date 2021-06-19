import re
import csv

from discord import Embed
from discord import utils
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
        await ctx.send(f'Fetching all Praise from {ctx.channel.name}...')
        if after:
            dates = [int(char) for char in after.split('-')]
            msgs = await ctx.channel.history(after=datetime(20 + dates[2], dates[1], dates[0])).flatten()
        else:
            msgs = await ctx.channel.history(after=datetime(2021, 6, 4)).flatten()

        clean_msgs = []
        for msg in msgs:
            if msg.content.startswith('!praise'):
                for person in msg.mentions:
                    clean_msgs.append(
                        [
                            "@" + person.name,
                            msg.author.name + msg.author.discriminator,
                            re.sub(r'(<@).*?>', '', utils.escape_mentions(msg.content)[8:]).strip(),
                            msg.created_at.strftime("%b-%d-%Y"),
                            msg.channel.name
                        ]
                    )
                    print(f'Adding praise for: {person.name}')

        with open("praise.csv", 'a') as f:
            try:
                writer = csv.writer(f)
                print('Writing Praise...')
                writer.writerows(clean_msgs)
            except Exception as e:
                print(f"Error in writing Praise: {e}")

        print("Praise successfully written!")

def setup(bot):
    bot.add_cog(Praise(bot))
