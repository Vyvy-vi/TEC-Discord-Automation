import discord.utils

from discord import Embed, Color, File
from discord import Member, User
from discord.ext import commands
from discord.ext.commands import Context

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from typing import Union, Optional
from web3 import Web3
from table2ascii import table2ascii, Alignment

async def write_data(db, user: Union[User, Member], wallet: str):
    '''Update the user data to MongoDB'''
    _user = await db.users.find_one({'id': str(user.id)})
    if _user:
        updated_data = {"$set": {'username': user.name + user.discriminator,
                                 'wallet_address': wallet}}
        await db.users.update_one(_user, updated_data)
    else:
        await db.users.insert_one({'id': str(user.id),
                                   'username': user.name + user.discriminator,
                                   'wallet_address': wallet})


class Sourcecred(commands.Cog):
    """Commands for collecting data for SourceCred or wallet lists"""
    def __init__(self, bot):
        self.bot = bot
        self.DB = MongoClient(bot.MONGO).test_db


    @commands.command()
    async def wallet(self, ctx: Context, address: Optional[str]):
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

    @commands.command()
    async def myinfo(self, ctx: Context):
        """command that displays all the user data the bot stores"""
        info = await self.DB.users.find_one({'id': str(ctx.author.id)})
        if info:
            text = [f'**{i}**: {info[i]}' for i in info if i != '_id']
            embed = Embed(title='Your Wallet Info',
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

    @commands.command()
    @commands.has_any_role('Stewards', 'Admin')
    async def wallet_remove(self, ctx: Context, user: Union[Member, User]):
        """commmand that removes a wallet entry from the database"""
        info = await self.DB.users.find_one({'id': str(user.id)})
        if info:
            await self.DB.users.delete_one({'id': str(user.id)})
            embed = Embed(description='Succesfully removed that wallet from the db.',
                          color=Color.green())
        else:
            embed = Embed(description='There is no record of that wallet in the database.',
                          color=Color.red())
        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_any_role('Stewards', 'Admin')
    async def wallet_list(self, ctx: Context):
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
    bot.add_cog(Sourcecred(bot))
