from discord import Embed, Color, File
from discord import Member, User
from discord.ext import commands
from discord.ext.commands import Context

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from typing import Union, Optional, Dict
from web3 import Web3
from table2ascii import table2ascii, Alignment

async def write_data(db, user: Union[User, Member], data: Dict):
    '''Update the user data to MongoDB'''
    _user = await db.users.find_one({'id': str(user.id)})
    if _user:
        for i in _user:
            if i not in data:
                data[i] = _user[i]
        updated_data = {"$set": {'username': user.name + '#' + user.discriminator,
                                 'wallet_address': data.get("wallet_address", "NULL"),
                                 'forum_username': data.get("forum_username", "NULL"),
                                 'github_username': data.get("github_username", "NULL")}}
        await db.users.update_one(_user, updated_data)
    else:
        await db.users.insert_one({ 'id': str(user.id),
                                    'username': user.name + '#' + user.discriminator,
                                    'wallet_address': data.get("wallet_address", "NULL"),
                                    'forum_username': data.get("forum_username", "NULL"),
                                    'github_username': data.get("github_username", "NULL")})


class SourceCred(commands.Cog):
    """Commands for collecting data for SourceCred"""
    def __init__(self, bot):
        self.bot = bot
        self.DB = MongoClient(bot.MONGO).test_db

    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def sourcecred(self, ctx: Context, *, socials: str):
        """Forms group to wrap around the commands"""
        data = {}
        socials = socials.split('\n')
        embed = Embed(description="Your details have been entered succesfully...", color=Color.green())
        for field in socials:
            if field.lower().startswith('github'):
                data['github_username'] = field.split(' ')[1]
            if field.lower().startswith('forum'):
                data['forum_username'] = field.split(' ')[1]
            if field.lower().startswith('wallet'):
                address = field.split(' ')[1]
                if Web3.isAddress(address):
                    data['wallet_address'] = field.split(' ')[1]
                else:
                    embed = Embed(description="The entered ETH wallet address is invalid", color=Color.red())
        await write_data(self.DB, ctx.author, data)
        await ctx.send(embed=embed)


    @sourcecred.command()
    async def myinfo(self, ctx: Context):
        """command that displays all the user data the bot stores"""
        info = await self.DB.users.find_one({'id': str(ctx.author.id)})
        if info:
            text = [f'**{i}**: {info[i]}' for i in info if i != '_id']
            embed = Embed(title='Your Sourcecred Info',
                          color=ctx.author.color)
            for field in info:
                if field != "_id":
                    embed.add_field(name=field, value=info[field], inline=False)
        else:
            embed = Embed(title='Your Wallet Info',
                          description='There is no record of you in the sourcecred database. Use `TEC!sourcecred` to add your wallet to the db',
                          color=Color.red())
            embed.set_footer(text='For any name or address issues, contact a Steward or an Admin')
        await ctx.send(embed=embed)


    @sourcecred.command()
    @commands.has_any_role('Stewards', 'Admin')
    async def data(self, ctx: Context):
        """command to fetch wallet address data"""
        data = []
        users = self.DB.users.find()
        async for user in users:
            data.append([user['id'], user['username'], user['wallet_address']])
        output = table2ascii(
                    header=["id", "Username", "Wallet Address"],
                    body=data,
                    first_col_heading=True,
                    alignments=[Alignment.LEFT] + [Alignment.RIGHT] * 2)
        with open('temp-wallet.txt', 'w+') as f:
            f.write(output)
        await ctx.send(file=File('temp-wallet.txt'))

def setup(bot):
    bot.add_cog(SourceCred(bot))
