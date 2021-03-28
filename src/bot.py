import os
import discord
import asyncio
import logging

from dotenv import load_dotenv
from discord.ext import commands
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='TEC!',
                   intents=intents)

load_dotenv()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
logging.basicConfig(level=logging.INFO)

class Bot(commands.Bot):
    """Main Bot class"""
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True

        super().__init__(command_prefix='TEC!',
                         intents=intents)
        self.load_cogs()

    def load_cogs(self) -> None:
        """Loads all the cogs for the bot"""
        cogs = []
        for extension in cogs:
            self.load_extension(extension)
            logging.info(f'Loaded cog - {Extension}')

    def run(self) -> None:
        """Runs the bot"""
        if TOKEN is None:
            raise EnvironmentError("Token value not found in .env")
        super().run(TOKEN)

    async def on_ready(self):
        logging.info('Starting...')
