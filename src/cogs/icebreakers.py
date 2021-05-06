import random

from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Context

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from typing import Union, Optional

class IceBreakers(commands.Cog):
    """Commands for running icebreakers"""
    def __init__(self, bot):
        self.bot = bot
        self.DB = MongoClient(bot.MONGO).test_db

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def ice_breaker(self, ctx: Context, num: int = None):
        """Runs the ice breakers subcommands

        If a subcommand isn't found, then this will run the standard command
        """
        ice = await self.DB.icebreakers.find_one({'type': 'rapid'})
        if num:
            txt = '\n'.join(ice['text'])
        else:
            card = "https%3A%2F%2Fi.imgur.com%2FdAVNfx9.png"
            txt = random.choice(ice['text']).replace(' ', '%20')
            url = f"https://textoverimage.moesif.com/image?image_url={card}&text={txt}&text_color=0f0d1aff&y_align=middle&x_align=center"

            embed = Embed(title='Break the ice',
                          color=0x00ffff)
            embed.set_image(url=url)

        await ctx.send(embed=embed)

    @ice_breaker.command(aliases=['ls'])
    @commands.guild_only()
    async def list(self, ctx: Context, _type: str = 'rapid'):
        ice = await self.DB.icebreakers.find_one({'type': _type})
        await ctx.send('\n'.join(ice['text']))

    @ice_breaker.command(aliases=['short', 'quick'])
    async def rapid(self, ctx: Context, num: int = None):
        """ice_breaker subcommond to run rapid(short) icebreaker sessions(10min or less)"""
        ice = await self.DB.icebreakers.find_one({'type': 'rapid'})
        if num:
            txt = '\n'.join(ice['text'])
        else:
            card = "https%3A%2F%2Fi.imgur.com%2FdAVNfx9.png"
            txt = random.choice(ice['text']).replace(' ', '%20')
            url = f"https://textoverimage.moesif.com/image?image_url={card}&text={txt}&text_color=0f0d1aff&y_align=middle&x_align=center"

            embed = Embed(title='Break the ice',
                          color=0x00ffff)
            embed.set_image(url=url)

        await ctx.send(embed=embed)

    @ice_breaker.command(aliases=['intro'])
    async def getintouch(self, ctx: Context):
        """ice_breaker subcommond to run fully featured getting in touch icebreaker sessions(30min-1h)"""
        embed = Embed(title='Break the ice',
                      color=0x00ffff)
        await ctx.send(embed=embed)

    @ice_breaker.command(aliases=['full'])
    async def long(self, ctx: Context):
        """ice_breaker subcommond to run longer icebreaker sessions(1h-3h)"""
        ice = await self.DB.icebreakers.find_one({'type': 'long'})
        if num:
            txt = '\n'.join(ice['text'])
        else:
            card = "https%3A%2F%2Fi.imgur.com%2FdAVNfx9.png"
            txt = random.choice(ice['text']).replace(' ', '%20')
            url = f"https://textoverimage.moesif.com/image?image_url={card}&text={txt}&text_color=0f0d1aff&y_align=middle&x_align=center"

            embed = Embed(title='Break the ice',
                          color=0x00ffff)
            embed.set_image(url=url)

        await ctx.send(embed=embed)

    @ice_breaker.command()
    async def add(self, ctx: Context, *, icebreaker: str):
        if icebreaker:
            ice = await self.DB.icebreakers.find_one({'type': 'rapid'})
            added_ice = {"$set": {'text': ice['text'] + [icebreaker]}}
            await self.DB.icebreakers.update_one(ice, added_ice)
            embed = Embed(description="Added icebreaker to list", color=Color.green())
        else:
            embed = Embed(description="Please specifiy the icebreaker.", color=Color.red())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(IceBreakers(bot))
