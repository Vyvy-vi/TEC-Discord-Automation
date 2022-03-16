import re
import json

from asyncio import sleep
from datetime import datetime, timedelta

from discord import utils, File
from discord import Reaction, User, PartialEmoji
from discord.ext import commands
from discord.ext.commands import Context
from discord.errors import Forbidden, HTTPException

from typing import List, Dict


async def get_reactions(reactions: List[Reaction]) -> List[Dict]:
    reactions_ls = []
    for reaction in reactions:
        users = await reaction.users().flatten()
        users = list(
            map(
                lambda user: {
                    "id": user.id,
                    "username": user.name + "#" + user.discriminator
                },
                users
            )
        )
        emoji = reaction.emoji
        if (type(emoji) != str):
            emoji = emoji.name
        reactions_ls.append({
            "emoji": emoji,
            "count": reaction.count,
            "users": users,
        })
    return reactions_ls


def get_receivers(mentions):
    return list(
        map(
            lambda user: {
                "id": user.id,
                "username": user.name + "#" + user.discriminator
            },
            mentions
        )
    )


def get_parsed_message(content: str):
    return re.sub(r'(<@).*?>', '', utils.escape_mentions(content)[8:]).strip().replace('\n', ' ')


class PraiseSampleScrape(commands.Cog):
    """Commands for scraping praise samples from the server"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_praise_samples(self, ctx: Context, after: str = None):
        await ctx.send(f'Fetching Praise Samples from {ctx.guild.name}...')

        if after:
            dates = [int(char) for char in after.split('-')]
            after = datetime(dates[2], dates[1], dates[0])
        else:
            # praise from 20 days ago from now
            after = datetime.now() - timedelta(days=20)

        praise_data = []

        for channel in ctx.guild.text_channels:
            await sleep(5)
            try:
                await ctx.send(f"Attempting to get praise samples from - {channel.name}")
                msgs = await channel.history(after=after, limit=None).flatten()
                for msg in msgs:
                    if msg.content.startswith('!praise'):
                        reactions_list = await get_reactions(msg.reactions)
                        praise_data.append({
                            "sender": {
                                "id": msg.author.id,
                                "username": msg.author.name + "#" + msg.author.discriminator
                            },
                            "message_content": msg.clean_content,
                            "receivers_parsed": get_receivers(msg.mentions),
                            "praise_message_parsed": get_parsed_message(msg.content),
                            "reactions": reactions_list,
                            "channel": msg.channel.name,
                            "timestamp": msg.created_at.timestamp()
                        })
                        print(f"Praise added from: {msg.author.id}")
            except Forbidden:
                await ctx.send(f"Missing perms... Skipping channel - {channel.name}")
                continue

        with open(f"praise_samples_{ctx.guild.id}.json", 'w', encoding="utf-8") as f:
            try:
                json.dump(praise_data, f, indent=4)
            except Exception as e:
                print(f"Error in writing Praise Samples: {e}")

        await ctx.send(
            f"Here's your Praise sample since {(datetime.now() - after).days} days ago",
            file=File(f'praise_samples_{ctx.guild.id}.json', f'praise_samples_{ctx.guild.id}.json')
        )

    @get_praise_samples.error
    async def get_praise_error(self, ctx: Context, error):
        if isinstance(error.original, HTTPException):
            await ctx.send("An error occured, the date format might be wrong.")
        print(f"An error occured\n{error}")


def setup(bot):
    bot.add_cog(PraiseSampleScrape(bot))
