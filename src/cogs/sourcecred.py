from discord import Embed, Color, File
from discord import Member, User
from discord.ext import commands
from discord.ext.commands import Context

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from typing import Union, Optional, Dict
from web3 import Web3
from table2ascii import table2ascii, Alignment

async def write_data(db, user: Union[User, Member], wallet: str):
    '''Update the user data to MongoDB'''
    _user = await db.users.find_one({'id': str(user.id)})
    if _user:
        updated_data = {"$set": {'username': user.name + '#' + user.discriminator,
                                 'wallet_address': wallet}}
        await db.users.update_one(_user, updated_data)
    else:
        await db.users.insert_one({'id': str(user.id),
                                   'username': user.name + '#' + user.discriminator,
                                   'wallet_address': wallet})


class SourceCred(commands.Cog):
    """Commands for collecting data for Form framework"""
    def __init__(self, bot):
        self.bot = bot
        self.DB = MongoClient(bot.MONGO).test_db

    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def sourcecred(self, ctx: Context, *, content: str):
        """Forms group to wrap around the commands"""
        print(content)
        print(type(content))

    @commands.command()
    async def wallet(self, ctx: Context):
        """command to associate a user's wallet with their discord"""
        if address:
            valid = Web3.isAddress(address)
            if valid:
                await write_data(self.DB,
                                 ctx.author,
                                 address)
                embed = Embed(description='Your wallet address has been updated!',
                              color=0xfd40fe)
            else:
                embed = Embed(description='The entered Wallet Address is invalid',
                              color=Color.red())
        else:
            embed = Embed(description='If you want to add your address more privately, dm the bot and use the command `TEC!wallet`',
                          color=0xfd40fe)
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
                          description='There is no record of your wallet in the database. Use `TEC!wallet [address]` to add your wallet to the db',
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
