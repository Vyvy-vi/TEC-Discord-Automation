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


class Forms(commands.Cog):
    """Commands for collecting data for SourceCred or wallet lists"""
    def __init__(self, bot):
        self.bot = bot
        self.DB = MongoClient(bot.MONGO).test_db
        self.form_history = []

    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def forms(self, ctx: Context, name: Optional[str]):
        """Forms group to wrap around the commands"""
        if name:
            await self.info(ctx, name)
        else:
            await self.list(ctx)


    @forms.command()
    async def list(self, ctx: Context):
        """Lists out all the available forms"""
        form_list = await self.DB.forms.find_one({'_id': "__form_list__"})
        if form_list and len(form_list['forms']) != 0:
            embed = Embed(title='Forms', description='\n'.join(form_list['forms']), color = 16597246)
        else:
            embed = Embed(title='Forms', description='There are no forms present in the application', color=Color.red())
        await ctx.send(embed=embed)


    @forms.command()
    async def info(self, ctx: Context, name: str):
        """Returns for data for form passed as param"""
        form = await self.DB.forms.find_one({'_id': name})
        if form:
            embed = Embed(title=form['_id'],
                          description=form['description'] + f"\nTo start filling this form, use the command- `TEC!forms start {name}`",
                          color=form['color'])
            embed.set_image(url=form['img'])
        else:
            embed = Embed(description=f"The mentioned form - `{name}` doesn't exist.",
                          color=Color.red())
        await ctx.send(embed=embed)


    @forms.command()
    async def load(self, ctx: Context, name: str):
        """Sends the form content"""
        form = await self.DB.forms.find_one({'_id': name})
        if form:
            text = '\n'.join([f"**Q. {i[0]}**" for i in form['questions']])
            embed = Embed(title=form['_id'],
                          description=f"{form['description']}\nTo start filling this form, use the command- `TEC!forms start {name}`\n{text}",
                          color=form['color'])
            embed.set_image(url=form['img'])
        else:
            embed = Embed(description=f"The mentioned form - `{name}` doesn't exist.",
                          color=Color.red())
        await ctx.send(embed=embed)

    async def form_runner(self, ctx: Context, name: str, form: Dict):
        record = await self.DB.form_data.find_one({'_id': name})
        _author = ctx.author
        entries = {}
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        for i in form['questions']:
            embed = Embed(title=i[1], description=f"**{i[0]}**", color=form['color'])
            await ctx.send(embed=embed)
            try:
                msg = await self.bot.wait_for('message', check=check)
                if msg:
                    entries[i[1]] = str(msg.content)
            except asyncio.TimeoutError:
                embed = Embed(description="Session timed out, maybe try re-filling the form later..",
                              color=Color.red())
                await ctx.send(embed=embed)
                break

        if record:
            return_obj = {}
            if str(_author.id) not in record:
                await self.DB.form_data.update_one(record, {"$set": {f"data.{str(_author.id)}": {"username": _author.name + '#' + _author.discriminator}}})
                record = await self.DB.form_data.find_one({'_id': name})
            return_obj[f'data.{str(_author.id)}.username'] = _author.name + '#' + _author.discriminator
            for i in entries:
                return_obj[f'data.{str(_author.id)}.{i}'] = entries[i]
            await self.DB.form_data.update_one(record, {"$set": return_obj})

        else:
            return_obj = {
                    '_id': name,
                    'data': {str(_author.id): {'username': _author.name + '#' + _author.discriminator}}
                    }
            for i in entries:
                return_obj['data'][str(_author.id)][i] = entries[i]
            print(return_obj)
            await self.DB.form_data.insert_one(return_obj)

    @forms.command()
    async def start(self, ctx: Context, name: str):
        """Starts the form process"""
        form = await self.DB.forms.find_one({'_id': name})
        if form:
            await self.form_runner(ctx, name, form)
        else:
            embed = Embed(description=f"The mentioned form - `{name}` doesn't exist.",
                          color=Color.red())
            await ctx.send(embed=embed)



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
    bot.add_cog(Forms(bot))
