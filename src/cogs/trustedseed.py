import asyncio

from discord import Embed, Color, File
from discord import Member, User
from discord.ext import commands
from discord.ext.commands import Context

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from typing import Optional, Dict
from web3 import Web3

def meta_embed(meta):
    embed = Embed(
        title="The Trusted Seed",
        description=meta['description'].replace('\\n', '\n'),
        colour=meta['color'],
    )
    embed.set_image(url=meta['img'])
    embed.set_footer(text="The Commons Stack")
    return embed

def default_embed(desc: str, _type: str):
    col = {"error": Color.red(), "success": Color.green()}
    return Embed(description=desc, color=col[_type])


class TrustedSeed(commands.Cog):
    """Commands for collecting data for Form framework"""
    def __init__(self, bot):
        self.bot = bot
        self.DB = MongoClient(bot.MONGO).test_db
        self.SEED_FORM = bot.SEED_FORM

    @commands.group(invoke_without_command=True,
                    case_insensitive=True,
                    aliases=["trusted-seed", "trusted_seed"])
    async def trustedseed(self, ctx: Context):
        """Forms group to wrap around the commands"""
        await self.start(ctx)

    @trustedseed.command()
    async def info(self, ctx: Context):
        """Gives info about the TrustedSeed form"""
        e = meta_embed(self.SEED_FORM['META'])
        e.add_field(name="\u200b", value="**To start filling this form, run the `TEC!trustedseed` command**")
        await ctx.send(embed=e)

    async def form_runner(self, ctx: Context, data: Dict, refill: bool = False):
        """helper function for running the form"""
        _colo = data['META']['color']
        _author = ctx.author
        _data = data['QUESTIONS']
        entries = {}

        message_check = lambda m: m.channel == ctx.channel and m.author == _author

        # fetch user record
        record = await self.DB.trusted_seed.find_one({'id': _author.id})
        if record and not refill:
            msg = await ctx.send(embed=default_embed('Entry already exists. To re-fill the form, react to this message with 📝', 'error'))
            try:
                await msg.add_reaction('📝')
                await self.bot.wait_for(
                        'reaction_add',
                        check=lambda u, r: u == _author and str(r.emoji) == '📝')
            except asyncio.TimeoutError:
                await msg.remove_reaction('📝', self.bot.user)
                return
            else:
                await self.form_runner(ctx, data, True)
                return

        for key, fields in _data.items():
            if key == "skills": pass
            def react_check(r, u):
                self.index = fields['emojis'].index(str(r.emoji))
                return u == _author and str(r.emoji) in fields['emojis']
            e = Embed(title=key,
                      description=fields['text'],
                      color=_colo)
            e.set_footer(text=f'form for {_author.name}')
            if 'required' in fields and fields['required'] == True:
                required = True
                e.add_field(name="\u200b", value="*This question is required")
            elif "choices" not in fields:
                required = False
                e.add_field(name="\u200b", value="To skip, reply with `skip`")

            if 'choices' in fields:
                try:
                    options = '\n'.join([f"{fields['emojis'][i]} - {fields['choices'][i]}" for i in range(len(fields['choices']))])
                    e.add_field(name="Options", value=f"React with the following emojis to make a choice-\n{options}", inline=False)
                    msg = await ctx.send(embed=e)
                    for i in fields['emojis']:
                        await msg.add_reaction(i)
                    await self.bot.wait_for('reaction_add', timeout=120.0, check=react_check)
                except asyncio.TimeoutError:
                    await ctx.send(embed=default_embed('Session timed out, please re-fill the form', 'error'))
                    return
                else:
                   entries[key] = {
                       'question': fields['text'],
                       'answer': fields['choices'][self.index]
                   }
                   if key == "contribution":
                       if self.index in [0, 3]:
                           entries["skills"] = await listen_selections(ctx, _data)
                           continue
            else:
                await ctx.send(embed=e)
                try:
                    response = await self.bot.wait_for('message', check=message_check)
                except asyncio.TimeoutError:
                    await ctx.send(embed=default_embed("Session timed out, maybe try re-filling the form later...", "error"))
                else:
                    if required and response.content.startswith('skip'):
                        await ctx.send(embed=default_embed('That argument is required... You\'ll have to restart', "error"))
                    else:
                        entries[key] = {
                            'question': fields['text'],
                            'answer': response.content.replace('skip', '')
                        }
        print(entries)

    @trustedseed.command()
    async def start(self, ctx: Context):
        """Starts the form process"""
        embed = meta_embed(self.SEED_FORM['META'])
        embed.add_field(
            name='\u200b',
            value="**To start filling the form, react to this message with 📝**")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('📝')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '📝'

        try:
            reaction = await self.bot.wait_for('reaction_add', timeout=90.0, check=check)
        except asyncio.TimeoutError:
            await msg.remove_reaction('📝', self.bot.user)
            e = default_embed('The form timed out. To fill the form, run the command again', "error")
            await ctx.send(embed=e)
        else:
            e = default_embed("You can fill the Trusted-Seed form now.\n\
If an option is **not required** and you don't want to fill it, you can reply with \
`skip` to leave it blank.", "success")
            await ctx.send(embed=e)
            await self.form_runner(ctx, self.SEED_FORM)

    @trustedseed.command()
    async def data(self, ctx: Context, user: Member = None):
        if not user:
            user = ctx.message.author
        await ctx.send(user.mention)

def setup(bot):
    bot.add_cog(TrustedSeed(bot))
