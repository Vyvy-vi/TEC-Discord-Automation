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
        self.DB = MongoClient(bot.MONGO).test_db
        self.refresh_roles.start()
        self.MSG = self.bot.RESPONSES['WELCOME_MESSAGE']

    @tasks.loop(hours=18.0)
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
