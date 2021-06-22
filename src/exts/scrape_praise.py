import re
import csv

from asyncio import sleep
from datetime import datetime, timedelta

from discord import utils, File
from discord.ext import commands
from discord.ext.commands import Context
from discord.errors import Forbidden, HTTPException

class PraiseScrape(commands.Cog):
    """Commands for scraping old praise from the server"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_praise(self, ctx: Context, after: str = None):
        await ctx.send(f'Fetching all Praise from {ctx.guild.name}...')

        if after:
            dates = [int(char) for char in after.split('-')]
            after = datetime(dates[2], dates[1], dates[0])
        else:
            # praise from 18 days ago from now
            after=datetime.now() - timedelta(days=18)

        clean_msgs = [["To", "From", "Reason for Dishing", "Date", "Room"]]
        for channel in ctx.guild.text_channels:
            await sleep(2)
            try:
                await ctx.send(f"Attempting to get praise from - {channel.name}")
                msgs = await channel.history(after=after).flatten()
                for msg in msgs:
                    if msg.content.startswith('!praise'):
                        for person in msg.mentions:
                            clean_msgs.append(
                                [
                                    "@" + person.name,
                                    msg.author.name + msg.author.discriminator,
                                    re.sub(r'(<@).*?>', '', utils.escape_mentions(msg.content)[8:]).strip().replace('\n', ' '),
                                    msg.created_at.strftime("%b-%d-%Y"),
                                    msg.channel.name
                                ]
                            )
                            print(f'Adding praise for: {person.name}')
            except Forbidden:
                await ctx.send(f"Missing perms... Skipping channel - {channel.name}")
                continue

        with open(f"praise_{ctx.guild.id}.csv", 'w') as f:
            try:
                writer = csv.writer(f)
                print('Writing Praise...')
                writer.writerows(clean_msgs)
            except Exception as e:
                print(f"Error in writing Praise: {e}")

            print("Praise successfully written!")
        await ctx.send("Praise written!")
        await ctx.send(
            f"Praise written! Here's all of the Praise since {(datetime.now() - after).days} days ago",
            file = File(f'praise_{ctx.guild.id}.csv', f'{ctx.guild.name} praise.csv')
        )
    @get_praise.error
    async def get_praise_error(self, ctx: Context, error):
        if isinstance(error.original, HTTPException):
            await ctx.send("An error occured, the date format might be wrong.")
        print(f"An error occured\n{error}")

def setup(bot):
    bot.add_cog(PraiseScrape(bot))
