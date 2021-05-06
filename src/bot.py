import os
import discord
import asyncio
import logging

from dotenv import load_dotenv
from discord.ext import commands
intents = discord.Intents.all()

load_dotenv()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
MONGO = os.environ['MONGO_URI']

logging.basicConfig(level=logging.INFO)


class Bot(commands.Bot):
    """Main Bot class"""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True

        super().__init__(command_prefix='TEC!',
                         intents=intents)

    def load_cogs(self) -> None:
        """Loads all the cogs for the bot"""
        cogs = ['src.cogs.ban',
                'src.cogs.sourcecred',
                'src.cogs.icebreakers',
                'src.cogs.help']
        self.MONGO = MONGO
        for extension in cogs:
            self.load_extension(extension)
            logging.info(f'Loaded cog - {extension}')

    def run(self) -> None:
        """Runs the bot"""
        if TOKEN is None:
            raise EnvironmentError("Token value not found in .env")
        self.load_cogs()
        super().run(TOKEN)

    async def on_ready(self):
        logging.info('Starting...')
