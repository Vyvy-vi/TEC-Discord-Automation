from discord import Embed, Color, File
from discord import Member, User
from discord.ext import commands
from discord.ext.commands import Context

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from typing import Union, Optional, Dict
from web3 import Web3

class Forms(commands.Cog):
    """Commands for collecting data for Form framework"""
    def __init__(self, bot):
        self.bot = bot
        self.DB = MongoClient(bot.MONGO).test_db

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
                return
        embed = Embed(description=f"Thanks for filling the `{name}` form!",
                      color=form['color'])
        embed.set_image(url=form['img'])
        await ctx.send(embed=embed)
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

def setup(bot):
    bot.add_cog(Forms(bot))
