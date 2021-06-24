import asyncio

from discord import Embed, Color
from discord import Member, User
from discord import utils

from discord.ext import commands, tasks
from discord.ext.commands import Context, Cog

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from typing import Union, Optional, Dict
from datetime import datetime

class Onboarding(Cog):
    """Help command and some other helper commands"""
    def __init__(self, bot):
        self.bot = bot
        self.humans = MongoClient(bot.MONGO).captcha.list
        self.refresh_roles.start()
        self.MSG = self.bot.RESPONSES['WELCOME_MESSAGE']
        self.ERR = self.bot.RESPONSES['VERIFICATION_ERROR']

    @Cog.listener()
    async def on_member_join(self, member: Union[User, Member]):
        record = await self.humans.find_one({"_id": member.id})
        channel = member.guild.get_channel(791703335060635649) #810180622165213214
        if record and record['human']:
            welcome_text = self.MSG['DESC'].replace("{user}", member.mention)
            e = Embed(
                title="Welcome to the TECommons!",
                description=welcome_text,
                color=0xdefb48,
                url="http://tecommons.org/")
            for link in self.MSG['LINKS']:
                e.add_field(
                    name=link[0],
                    value=link[1],
                    inline=False
                )
            e.set_author(
                name="Token Engineering Commons",
                icon_url="https://media.discordapp.net/attachments/842458522562068500/850718445452394516/TEC_twitter.png"
            )
            e.add_field(name='\u200b', value=self.MSG['FOOTER'], inline=False)
            try:
                await member.send(embed=e)
            except:
                await channel.send(f"{member.mention} - Wasn't able to DM you. Welcome to the TEC!", embed=e)

            await self.humans.update_one(
                record,
                {"$set": {
                    "joined_at": datetime.now().timestamp(),
                }}
            )
        else:
            welcome_text = self.ERR.replace("{user}", member.mention)
            e = Embed(
                title="Welcome to the TECommons!",
                description=welcome_text,
                color=0xdefb48,
                url="https://discord.tecommons.org/"
            )
            try:
                await member.send(embed=e)
                await member.guild.kick(member)
            except:
                await channel.send(f"{member.mention} - Wasn't able to DM you. Welcome to the TEC!", embed=e)


    @tasks.loop(hours=48.0)
    async def refresh_roles(self):
        server = self.bot.get_guild(810180621930070088)
        role = server.get_role(824363970852290600)
        for member in role.members:
            if ((datetime.now() - member.joined_at).days >= 14):
                await member.remove_roles(role, reason="Onboarding Completed... Welcome to the TEC!!")
                await asyncio.sleep(5)

    @refresh_roles.before_loop
    async def before_refresh_roles(self):
        print("Role Refresh loop standing by...")
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Onboarding(bot))
